/**
 * HTML Sanitization Utilities - Prevent XSS attacks
 *
 * Provides functions to safely handle user-generated content and prevent
 * cross-site scripting (XSS) vulnerabilities.
 */

/**
 * Allowed HTML tags for sanitized content
 */
const ALLOWED_TAGS = new Set([
    'p', 'br', 'strong', 'em', 'b', 'i', 'u',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'a', 'span', 'div'
]);

/**
 * Allowed attributes per tag
 */
const ALLOWED_ATTRIBUTES = {
    'a': new Set(['href', 'title', 'target', 'rel']),
    'span': new Set(['class']),
    'div': new Set(['class']),
    'p': new Set(['class']),
    'h1': new Set(['class']),
    'h2': new Set(['class']),
    'h3': new Set(['class']),
    'h4': new Set(['class']),
    'h5': new Set(['class']),
    'h6': new Set(['class']),
    'ul': new Set(['class']),
    'ol': new Set(['class']),
    'li': new Set(['class'])
};

/**
 * Safe URL protocols for links
 */
const SAFE_URL_PROTOCOLS = new Set([
    'http:',
    'https:',
    'mailto:',
    'tel:'
]);

/**
 * Escape HTML special characters to prevent XSS
 *
 * @param {string} text - Text to escape
 * @returns {string} Escaped text safe for HTML insertion
 */
function escapeHtml(text) {
    if (typeof text !== 'string') {
        return '';
    }

    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Validate and sanitize a URL to prevent javascript: and data: URIs
 *
 * @param {string} url - URL to validate
 * @returns {string|null} Sanitized URL or null if invalid
 */
function sanitizeUrl(url) {
    if (typeof url !== 'string') {
        return null;
    }

    // Trim whitespace
    url = url.trim();

    if (!url) {
        return null;
    }

    // Check for dangerous protocols
    const lowerUrl = url.toLowerCase();

    // Block javascript:, data:, vbscript:, file:, etc.
    if (lowerUrl.startsWith('javascript:') ||
        lowerUrl.startsWith('data:') ||
        lowerUrl.startsWith('vbscript:') ||
        lowerUrl.startsWith('file:')) {
        console.warn('Blocked potentially dangerous URL:', url);
        return null;
    }

    // For URLs with protocols, validate they're safe
    try {
        const urlObj = new URL(url, window.location.href);

        if (!SAFE_URL_PROTOCOLS.has(urlObj.protocol)) {
            console.warn('Blocked URL with unsafe protocol:', urlObj.protocol);
            return null;
        }

        return urlObj.href;
    } catch (e) {
        // Relative URLs or malformed - treat as relative path
        // Still need to check for dangerous patterns
        if (lowerUrl.includes('javascript:') || lowerUrl.includes('data:')) {
            console.warn('Blocked malformed URL with dangerous pattern:', url);
            return null;
        }

        return url;
    }
}

/**
 * Sanitize HTML by parsing and filtering allowed tags/attributes
 *
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
function sanitizeHtml(html) {
    if (typeof html !== 'string') {
        return '';
    }

    // Create a temporary DOM to parse HTML
    const temp = document.createElement('div');
    temp.innerHTML = html;

    // Recursively sanitize nodes
    const sanitize = (node) => {
        // Text nodes are safe
        if (node.nodeType === Node.TEXT_NODE) {
            return node.cloneNode(false);
        }

        // Only allow element nodes
        if (node.nodeType !== Node.ELEMENT_NODE) {
            return null;
        }

        const tagName = node.tagName.toLowerCase();

        // Check if tag is allowed
        if (!ALLOWED_TAGS.has(tagName)) {
            // Return text content only for disallowed tags
            return document.createTextNode(node.textContent || '');
        }

        // Create new clean element
        const clean = document.createElement(tagName);

        // Copy allowed attributes
        const allowedAttrs = ALLOWED_ATTRIBUTES[tagName] || new Set();

        for (const attr of node.attributes) {
            const attrName = attr.name.toLowerCase();

            if (allowedAttrs.has(attrName)) {
                let attrValue = attr.value;

                // Special handling for URLs
                if (attrName === 'href') {
                    attrValue = sanitizeUrl(attrValue);
                    if (!attrValue) {
                        continue; // Skip invalid URLs
                    }
                }

                // Special handling for target attribute
                if (attrName === 'target' && attrValue === '_blank') {
                    // Force rel="noopener noreferrer" for security
                    clean.setAttribute('rel', 'noopener noreferrer');
                }

                clean.setAttribute(attrName, attrValue);
            }
        }

        // Recursively sanitize child nodes
        for (const child of node.childNodes) {
            const sanitized = sanitize(child);
            if (sanitized) {
                clean.appendChild(sanitized);
            }
        }

        return clean;
    };

    const fragment = document.createDocumentFragment();

    for (const child of temp.childNodes) {
        const sanitized = sanitize(child);
        if (sanitized) {
            fragment.appendChild(sanitized);
        }
    }

    // Convert back to HTML string
    const container = document.createElement('div');
    container.appendChild(fragment);
    return container.innerHTML;
}

/**
 * Convert markdown to HTML with XSS protection
 *
 * @param {string} markdown - Markdown text
 * @returns {string} Sanitized HTML
 */
function markdownToHtmlSafe(markdown) {
    if (typeof markdown !== 'string') {
        return '';
    }

    // First, escape any HTML that might be in the markdown
    let text = escapeHtml(markdown);

    // Headers
    text = text.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold mt-6 mb-3">$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-6 mb-4">$1</h1>');

    // Bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Links - [text](url)
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, linkText, url) => {
        const safeUrl = sanitizeUrl(url);
        if (!safeUrl) {
            return escapeHtml(linkText); // Just return text if URL is invalid
        }
        return `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(linkText)}</a>`;
    });

    // Unordered lists
    const lines = text.split('\n');
    let inList = false;
    const processedLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const listMatch = line.match(/^[\s]*[-*]\s+(.*)$/);

        if (listMatch) {
            if (!inList) {
                processedLines.push('<ul class="list-disc list-inside ml-4 mb-3 space-y-1">');
                inList = true;
            }
            processedLines.push(`<li class="text-gray-700">${listMatch[1]}</li>`);
        } else {
            if (inList) {
                processedLines.push('</ul>');
                inList = false;
            }
            processedLines.push(line);
        }
    }

    if (inList) {
        processedLines.push('</ul>');
    }

    text = processedLines.join('\n');

    // Paragraphs (double line breaks)
    text = text.split('\n\n').map(para => {
        const trimmed = para.trim();
        if (!trimmed) return '';
        if (trimmed.startsWith('<h') || trimmed.startsWith('<ul')) return trimmed;
        return `<p class="mb-3 text-gray-700 leading-relaxed">${trimmed}</p>`;
    }).join('\n');

    // Final sanitization pass to ensure no XSS
    return sanitizeHtml(text);
}

/**
 * Safely set innerHTML with automatic sanitization
 *
 * @param {HTMLElement} element - Element to set content on
 * @param {string} html - HTML content to set
 */
function setInnerHTMLSafe(element, html) {
    if (!element || !(element instanceof HTMLElement)) {
        console.error('Invalid element provided to setInnerHTMLSafe');
        return;
    }

    element.innerHTML = sanitizeHtml(html);
}

/**
 * Safely set text content (no HTML parsing)
 *
 * @param {HTMLElement} element - Element to set content on
 * @param {string} text - Text content to set
 */
function setTextContentSafe(element, text) {
    if (!element || !(element instanceof HTMLElement)) {
        console.error('Invalid element provided to setTextContentSafe');
        return;
    }

    element.textContent = text || '';
}
