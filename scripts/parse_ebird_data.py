#!/usr/bin/env python3
"""
Parse eBird barchart data into usable formats (CSV and JSON)
"""

import csv
import json
from pathlib import Path


def parse_ebird_barchart(input_file):
    """Parse the eBird barchart text file into structured data"""

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the header information
    num_taxa = None
    sample_sizes = []
    month_labels = []

    for i, line in enumerate(lines):
        # Get number of taxa
        if 'Number of taxa:' in line:
            num_taxa = int(line.split('\t')[1].strip())

        # Get month headers (line with Jan, Feb, Mar, etc.)
        if line.strip().startswith('Jan'):
            month_labels = [m.strip() for m in line.split('\t') if m.strip()]

        # Get sample sizes
        if line.startswith('Sample Size:'):
            sample_sizes = [float(x) for x in line.split('\t')[1:] if x.strip()]
            data_start_line = i + 2  # Data starts 2 lines after sample size
            break

    # Create week labels (4 weeks per month)
    week_labels = []
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        for week in [1, 2, 3, 4]:
            week_labels.append(f"{month}_W{week}")

    # Parse species data
    species_data = []
    for line in lines[data_start_line:]:
        if not line.strip():
            continue

        parts = line.split('\t')
        if len(parts) < 2:
            continue

        species_name = parts[0].strip()
        frequencies = []

        for val in parts[1:]:
            val = val.strip()
            if val:
                try:
                    frequencies.append(float(val))
                except ValueError:
                    pass

        # Filter out species with 'sp.' or '/' in the name
        if 'sp.' in species_name or '/' in species_name:
            continue

        if frequencies and len(frequencies) == 48:
            species_data.append({
                'species': species_name,
                'frequencies': frequencies
            })

    return {
        'num_taxa': num_taxa,
        'sample_sizes': sample_sizes,
        'week_labels': week_labels,
        'species_data': species_data
    }


def save_as_csv(data, output_file):
    """Save parsed data as CSV with species as rows and weeks as columns"""

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        header = ['Species'] + data['week_labels']
        writer.writerow(header)

        # Write each species
        for species in data['species_data']:
            row = [species['species']] + species['frequencies']
            writer.writerow(row)

    print(f"CSV saved to: {output_file}")


def save_as_long_csv(data, output_file):
    """Save as 'long' format CSV (species, week, frequency) - better for analysis"""

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['Species', 'Month', 'Week', 'Week_Label', 'Frequency', 'Sample_Size'])

        # Write each species-week combination
        for species in data['species_data']:
            for i, freq in enumerate(species['frequencies']):
                month_num = (i // 4) + 1
                week_in_month = (i % 4) + 1
                week_label = data['week_labels'][i]
                sample_size = data['sample_sizes'][i] if i < len(data['sample_sizes']) else None

                writer.writerow([
                    species['species'],
                    month_num,
                    week_in_month,
                    week_label,
                    freq,
                    sample_size
                ])

    print(f"Long-format CSV saved to: {output_file}")


def save_as_json(data, output_file):
    """Save parsed data as JSON"""

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"JSON saved to: {output_file}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 parse_ebird_data.py <region_name>")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root (go up from scripts/ if needed)
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    region_path = project_root / "regions" / region_name
    intermediate_path = region_path / "intermediate"

    # Create intermediate directory if it doesn't exist
    intermediate_path.mkdir(parents=True, exist_ok=True)

    # Find input file (ebird_*.txt)
    txt_files = list(region_path.glob("ebird_*.txt"))
    if not txt_files:
        print(f"Error: No eBird barchart file found in {region_path}")
        print(f"Expected: regions/{region_name}/ebird_*.txt")
        sys.exit(1)

    if len(txt_files) > 1:
        print(f"Warning: Multiple eBird files found. Using: {txt_files[0].name}")

    input_file = txt_files[0]

    # Output files
    csv_wide = intermediate_path / f"{region_name}_ebird_data_wide.csv"
    csv_long = intermediate_path / f"{region_name}_ebird_data_long.csv"
    json_file = intermediate_path / f"{region_name}_ebird_data.json"

    print(f"Parsing: {input_file}")
    data = parse_ebird_barchart(input_file)

    print(f"\nFound {len(data['species_data'])} species")
    print(f"Expected taxa: {data['num_taxa']}")

    # Save in multiple formats
    save_as_csv(data, csv_wide)
    save_as_long_csv(data, csv_long)
    save_as_json(data, json_file)

    print("\n✓ Data transformation complete!")
    print("\nOutput files:")
    print(f"  - {csv_wide.name} (wide format - species as rows, weeks as columns)")
    print(f"  - {csv_long.name} (long format - best for analysis/plotting)")
    print(f"  - {json_file.name} (JSON format)")


if __name__ == "__main__":
    main()
