#!/usr/bin/env python3
"""
GetIntent - Extract customer purchase intentions and service requests from call CSV files.

This tool processes CSV files containing call transcripts and identifies statements
that indicate:
1. Purchase intention (購買意願)
2. Need for dedicated service support (需要專人服務)

Usage:
    python get_intent.py <input_folder> [--output <output_file>]
    python get_intent.py ./call_data --output results.csv
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from config import PURCHASE_INTENT_KEYWORDS, SERVICE_REQUEST_KEYWORDS, INTENSITY_MODIFIERS


@dataclass
class IntentMatch:
    """Represents a detected intent match."""
    csv_file: str
    statement: str
    intent_type: str  # "購買意願" or "專人服務"
    level: int  # 1-5 confidence level


class IntentDetector:
    """Detects customer purchase intentions and service requests from statements."""

    def __init__(self):
        self.purchase_keywords = PURCHASE_INTENT_KEYWORDS
        self.service_keywords = SERVICE_REQUEST_KEYWORDS
        self.intensity_modifiers = INTENSITY_MODIFIERS

    def detect_intent(self, statement: str) -> Optional[Tuple[str, int]]:
        """
        Detect intent from a customer statement.

        Args:
            statement: The customer statement to analyze

        Returns:
            Tuple of (intent_type, confidence_level) or None if no intent detected
        """
        statement_lower = statement.lower()

        # Check for purchase intention
        purchase_score = self._calculate_intent_score(statement_lower, self.purchase_keywords)

        # Check for service request
        service_score = self._calculate_intent_score(statement_lower, self.service_keywords)

        # Return the higher scoring intent
        if purchase_score > 0 and purchase_score >= service_score:
            level = self._calculate_level(purchase_score, statement_lower)
            return ("購買意願", level)
        elif service_score > 0:
            level = self._calculate_level(service_score, statement_lower)
            return ("專人服務", level)

        return None

    def _calculate_intent_score(self, statement: str, keywords: Dict[str, int]) -> int:
        """Calculate intent score based on keyword matches."""
        score = 0
        for keyword, weight in keywords.items():
            if keyword in statement:
                score += weight
        return score

    def _calculate_level(self, base_score: int, statement: str) -> int:
        """
        Calculate confidence level (1-5) based on score and intensity modifiers.

        Level interpretation:
        - 5: Very strong intent, immediate action needed
        - 4: Strong intent, high priority
        - 3: Moderate intent, follow-up recommended
        - 2: Weak intent, may need nurturing
        - 1: Minimal intent detected
        """
        # Apply intensity modifiers
        modifier = 0
        for mod_keyword, mod_value in self.intensity_modifiers.items():
            if mod_keyword in statement:
                modifier += mod_value

        total_score = base_score + modifier

        # Map score to level 1-5
        if total_score >= 15:
            return 5
        elif total_score >= 10:
            return 4
        elif total_score >= 6:
            return 3
        elif total_score >= 3:
            return 2
        else:
            return 1


class CSVProcessor:
    """Processes CSV call files to extract customer statements."""

    def __init__(self, detector: IntentDetector):
        self.detector = detector

    def process_file(self, file_path: Path) -> List[IntentMatch]:
        """
        Process a single CSV file and extract intent matches.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of IntentMatch objects
        """
        matches = []

        try:
            # Try different encodings commonly used for Chinese text
            encodings = ['utf-8', 'utf-8-sig', 'big5', 'gb2312', 'gbk']
            content_lines = None

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content_lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue

            if content_lines is None:
                print(f"Warning: Could not decode {file_path} with any supported encoding")
                return matches

            # Process each line/row
            for line in content_lines:
                line = line.strip()
                if not line:
                    continue

                # Try to parse as CSV or treat as plain text
                statements = self._extract_statements(line)

                for statement in statements:
                    result = self.detector.detect_intent(statement)
                    if result:
                        intent_type, level = result
                        matches.append(IntentMatch(
                            csv_file=file_path.name,
                            statement=statement,
                            intent_type=intent_type,
                            level=level
                        ))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return matches

    def _extract_statements(self, line: str) -> List[str]:
        """Extract individual statements from a CSV line."""
        statements = []

        # Try to parse as CSV
        try:
            reader = csv.reader([line])
            for row in reader:
                for cell in row:
                    cell = cell.strip()
                    if cell and len(cell) > 2:  # Skip empty or very short cells
                        statements.append(cell)
        except:
            # If CSV parsing fails, treat as plain text
            if len(line) > 2:
                statements.append(line)

        return statements

    def process_folder(self, folder_path: Path) -> List[IntentMatch]:
        """
        Process all CSV files in a folder.

        Args:
            folder_path: Path to the folder containing CSV files

        Returns:
            List of all IntentMatch objects from all files
        """
        all_matches = []
        csv_files = list(folder_path.glob('*.csv'))

        print(f"Found {len(csv_files)} CSV files to process...")

        for i, csv_file in enumerate(csv_files, 1):
            if i % 100 == 0:
                print(f"Processing file {i}/{len(csv_files)}...")

            matches = self.process_file(csv_file)
            all_matches.extend(matches)

        print(f"Processing complete. Found {len(all_matches)} intent matches.")
        return all_matches


class ResultsWriter:
    """Writes intent detection results to output files."""

    @staticmethod
    def write_csv(matches: List[IntentMatch], output_path: Path):
        """Write results to a CSV file."""
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['csv', '客戶語句', '購買意願或專人服務', '等級'])

            # Write data rows
            for match in matches:
                writer.writerow([
                    match.csv_file,
                    match.statement,
                    match.intent_type,
                    match.level
                ])

        print(f"Results written to: {output_path}")

    @staticmethod
    def print_summary(matches: List[IntentMatch]):
        """Print a summary of the results."""
        if not matches:
            print("\nNo intent matches found.")
            return

        purchase_count = sum(1 for m in matches if m.intent_type == "購買意願")
        service_count = sum(1 for m in matches if m.intent_type == "專人服務")

        level_counts = {i: 0 for i in range(1, 6)}
        for m in matches:
            level_counts[m.level] += 1

        print("\n" + "=" * 50)
        print("RESULTS SUMMARY")
        print("=" * 50)
        print(f"Total matches found: {len(matches)}")
        print(f"  - Purchase intention (購買意願): {purchase_count}")
        print(f"  - Service request (專人服務): {service_count}")
        print("\nBy confidence level:")
        for level in range(5, 0, -1):
            print(f"  Level {level}: {level_counts[level]} matches")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='Extract customer purchase intentions and service requests from call CSV files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python get_intent.py ./call_data
    python get_intent.py ./call_data --output results.csv
    python get_intent.py /path/to/csv/files -o my_results.csv
        """
    )

    parser.add_argument(
        'input_folder',
        type=str,
        help='Path to the folder containing CSV call files'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='intent_results.csv',
        help='Output CSV file path (default: intent_results.csv)'
    )

    args = parser.parse_args()

    # Validate input folder
    input_path = Path(args.input_folder)
    if not input_path.exists():
        print(f"Error: Input folder does not exist: {input_path}")
        sys.exit(1)

    if not input_path.is_dir():
        print(f"Error: Input path is not a directory: {input_path}")
        sys.exit(1)

    # Initialize components
    detector = IntentDetector()
    processor = CSVProcessor(detector)

    # Process files
    print(f"Processing CSV files from: {input_path}")
    matches = processor.process_folder(input_path)

    # Write results
    output_path = Path(args.output)
    ResultsWriter.write_csv(matches, output_path)
    ResultsWriter.print_summary(matches)


if __name__ == '__main__':
    main()
