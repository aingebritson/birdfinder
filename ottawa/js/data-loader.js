/**
 * Data Loader - Robust data fetching with error recovery and retry logic
 *
 * Provides automatic retry with exponential backoff for transient failures,
 * user-friendly error messages, and retry UI for permanent failures.
 */

/**
 * Retry configuration
 */
const RETRY_CONFIG = {
    maxAttempts: 3,
    initialDelayMs: 1000,
    maxDelayMs: 5000,
    backoffMultiplier: 2
};

/**
 * Error types for different failure scenarios
 */
const ErrorType = {
    NETWORK: 'network',        // Network connectivity issues (retryable)
    NOT_FOUND: 'not_found',    // 404 errors (not retryable)
    SERVER: 'server',          // 5xx errors (retryable)
    PARSE: 'parse',            // JSON parsing errors (not retryable)
    TIMEOUT: 'timeout'         // Request timeout (retryable)
};

/**
 * Custom error class with additional context
 */
class DataLoadError extends Error {
    constructor(message, type, statusCode = null, retryable = false) {
        super(message);
        this.name = 'DataLoadError';
        this.type = type;
        this.statusCode = statusCode;
        this.retryable = retryable;
    }
}

/**
 * Sleep helper for retry delays
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Fetch JSON data with error recovery and retry logic
 *
 * @param {string} url - URL to fetch from
 * @param {Object} options - Configuration options
 * @param {number} options.timeoutMs - Request timeout in milliseconds (default: 10000)
 * @param {boolean} options.autoRetry - Whether to auto-retry on failure (default: true)
 * @param {Function} options.onRetry - Callback called before each retry (attempt, maxAttempts) => void
 * @param {Function} options.onProgress - Callback for progress updates (message) => void
 * @returns {Promise<any>} Parsed JSON data
 * @throws {DataLoadError} If all retry attempts fail
 */
async function fetchWithRetry(url, options = {}) {
    const {
        timeoutMs = 10000,
        autoRetry = true,
        onRetry = null,
        onProgress = null
    } = options;

    const maxAttempts = autoRetry ? RETRY_CONFIG.maxAttempts : 1;
    let lastError = null;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            if (onProgress) {
                onProgress(attempt === 1 ? 'Loading data...' : `Retrying... (attempt ${attempt}/${maxAttempts})`);
            }

            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

            try {
                // Fetch with timeout
                const response = await fetch(url, {
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                // Check HTTP status
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new DataLoadError(
                            `Data file not found: ${url}`,
                            ErrorType.NOT_FOUND,
                            404,
                            false
                        );
                    } else if (response.status >= 500) {
                        throw new DataLoadError(
                            `Server error (${response.status}): ${response.statusText}`,
                            ErrorType.SERVER,
                            response.status,
                            true
                        );
                    } else {
                        throw new DataLoadError(
                            `HTTP error ${response.status}: ${response.statusText}`,
                            ErrorType.NETWORK,
                            response.status,
                            false
                        );
                    }
                }

                // Parse JSON
                let data;
                try {
                    data = await response.json();
                } catch (parseError) {
                    throw new DataLoadError(
                        `Failed to parse JSON: ${parseError.message}`,
                        ErrorType.PARSE,
                        null,
                        false
                    );
                }

                // Success!
                if (onProgress) {
                    onProgress('Data loaded successfully');
                }
                return data;

            } catch (fetchError) {
                clearTimeout(timeoutId);

                // Handle abort (timeout)
                if (fetchError.name === 'AbortError') {
                    throw new DataLoadError(
                        `Request timeout after ${timeoutMs}ms`,
                        ErrorType.TIMEOUT,
                        null,
                        true
                    );
                }

                // Re-throw if already a DataLoadError
                if (fetchError instanceof DataLoadError) {
                    throw fetchError;
                }

                // Network error (offline, DNS failure, etc.)
                throw new DataLoadError(
                    `Network error: ${fetchError.message}`,
                    ErrorType.NETWORK,
                    null,
                    true
                );
            }

        } catch (error) {
            lastError = error;

            // Don't retry if error is not retryable
            if (error instanceof DataLoadError && !error.retryable) {
                throw error;
            }

            // Don't retry if this was the last attempt
            if (attempt >= maxAttempts) {
                throw error;
            }

            // Calculate delay with exponential backoff
            const delay = Math.min(
                RETRY_CONFIG.initialDelayMs * Math.pow(RETRY_CONFIG.backoffMultiplier, attempt - 1),
                RETRY_CONFIG.maxDelayMs
            );

            console.warn(`Attempt ${attempt} failed: ${error.message}. Retrying in ${delay}ms...`);

            if (onRetry) {
                onRetry(attempt, maxAttempts);
            }

            await sleep(delay);
        }
    }

    // Should never reach here, but just in case
    throw lastError;
}

/**
 * Get user-friendly error message for display
 *
 * @param {DataLoadError} error - The error to format
 * @returns {Object} Object with title and message
 */
function formatErrorMessage(error) {
    if (!(error instanceof DataLoadError)) {
        return {
            title: 'Unexpected Error',
            message: error.message || 'An unknown error occurred',
            canRetry: false
        };
    }

    switch (error.type) {
        case ErrorType.NOT_FOUND:
            return {
                title: 'Data Not Found',
                message: 'The requested data file could not be found. This may indicate a configuration issue.',
                canRetry: false
            };

        case ErrorType.NETWORK:
            return {
                title: 'Network Error',
                message: 'Unable to load data due to a network problem. Please check your internet connection and try again.',
                canRetry: true
            };

        case ErrorType.SERVER:
            return {
                title: 'Server Error',
                message: `The server encountered an error (${error.statusCode}). Please try again in a moment.`,
                canRetry: true
            };

        case ErrorType.TIMEOUT:
            return {
                title: 'Request Timeout',
                message: 'The request took too long to complete. Please check your connection and try again.',
                canRetry: true
            };

        case ErrorType.PARSE:
            return {
                title: 'Data Format Error',
                message: 'The data file is corrupted or in an unexpected format.',
                canRetry: false
            };

        default:
            return {
                title: 'Error Loading Data',
                message: error.message || 'An error occurred while loading data',
                canRetry: error.retryable
            };
    }
}

/**
 * Show error UI with optional retry button
 *
 * @param {HTMLElement} container - Container to show error in
 * @param {DataLoadError} error - The error to display
 * @param {Function} onRetry - Callback when retry button is clicked
 */
function showErrorUI(container, error, onRetry = null) {
    const { title, message, canRetry } = formatErrorMessage(error);

    const retryButton = (canRetry && onRetry) ? `
        <button id="retry-button" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Try Again
        </button>
    ` : '';

    container.innerHTML = `
        <div class="error-state text-center py-12 px-4">
            <div class="text-6xl mb-4">⚠️</div>
            <h2 class="text-2xl font-bold text-gray-900 mb-2">${title}</h2>
            <p class="text-gray-600 mb-2 max-w-md mx-auto">${message}</p>
            ${error.statusCode ? `<p class="text-sm text-gray-500 mb-4">Error code: ${error.statusCode}</p>` : ''}
            ${retryButton}
        </div>
    `;

    // Attach retry handler if button exists
    if (canRetry && onRetry) {
        const button = container.querySelector('#retry-button');
        if (button) {
            button.addEventListener('click', onRetry);
        }
    }
}

/**
 * Show loading UI
 *
 * @param {HTMLElement} container - Container to show loading state in
 * @param {string} message - Loading message (default: "Loading data...")
 */
function showLoadingUI(container, message = 'Loading data...') {
    container.innerHTML = `
        <div class="loading-state text-center py-12 px-4">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p class="text-gray-600">${message}</p>
        </div>
    `;
}
