#!/usr/bin/env python3
"""
GetIntent - Extract customer purchase intentions and service requests from call CSV files.

This tool processes CSV files containing call transcripts and identifies statements
that indicate:
1. Purchase intention (購買意願)
2. Need for dedicated service support (需要專人服務)

Supports two modes:
- Keyword-based detection (default, no API required)
- GPT-based detection (more accurate, requires OpenAI API key)

Usage:
    python get_intent.py <input_folder> [--output <output_file>]
    python get_intent.py ./call_data --output results.csv
    python get_intent.py ./call_data --mode gpt --api-key YOUR_API_KEY
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from config import PURCHASE_INTENT_KEYWORDS, SERVICE_REQUEST_KEYWORDS, INTENSITY_MODIFIERS

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class IntentMatch:
    """Represents a detected intent match."""
    csv_file: str
    statement: str
    intent_type: str  # "購買意願", "專人服務", or "無意圖"
    level: int  # 1-5 confidence level
    reason: str = ""  # GPT's reasoning (optional)


class KeywordIntentDetector:
    """Detects customer purchase intentions and service requests using keywords."""

    def __init__(self):
        self.purchase_keywords = PURCHASE_INTENT_KEYWORDS
        self.service_keywords = SERVICE_REQUEST_KEYWORDS
        self.intensity_modifiers = INTENSITY_MODIFIERS

    def detect_intent(self, statement: str) -> Optional[Tuple[str, int, str]]:
        """
        Detect intent from a customer statement.

        Args:
            statement: The customer statement to analyze

        Returns:
            Tuple of (intent_type, confidence_level, reason) or None if no intent detected
        """
        statement_lower = statement.lower()

        # Check for purchase intention
        purchase_score = self._calculate_intent_score(statement_lower, self.purchase_keywords)

        # Check for service request
        service_score = self._calculate_intent_score(statement_lower, self.service_keywords)

        # Return the higher scoring intent
        if purchase_score > 0 and purchase_score >= service_score:
            level = self._calculate_level(purchase_score, statement_lower)
            return ("購買意願", level, "關鍵字匹配")
        elif service_score > 0:
            level = self._calculate_level(service_score, statement_lower)
            return ("專人服務", level, "關鍵字匹配")

        return None

    def _calculate_intent_score(self, statement: str, keywords: Dict[str, int]) -> int:
        """Calculate intent score based on keyword matches."""
        score = 0
        for keyword, weight in keywords.items():
            if keyword in statement:
                score += weight
        return score

    def _calculate_level(self, base_score: int, statement: str) -> int:
        """Calculate confidence level (1-5) based on score and intensity modifiers."""
        modifier = 0
        for mod_keyword, mod_value in self.intensity_modifiers.items():
            if mod_keyword in statement:
                modifier += mod_value

        total_score = base_score + modifier

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


class GPTIntentDetector:
    """Detects customer purchase intentions and service requests using GPT."""

    SYSTEM_PROMPT = """你是一個專門分析客戶通話內容的AI助手。你的任務是判斷客戶的語句是否表達了以下意圖：

1. **購買意願** - 客戶想要購買產品或服務的意圖，例如：
   - 直接表達要買/訂購/下單
   - 詢問價格、付款方式
   - 詢問如何購買
   - 確認訂單細節

2. **專人服務** - 客戶需要真人客服協助的意圖，例如：
   - 要求轉接專人/客服
   - 表示問題複雜需要人工處理
   - 對自動服務不滿意
   - 要求回電或預約服務

請分析每句話並回傳JSON格式的結果。"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = None):
        """
        Initialize GPT detector.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
            base_url: Custom API base URL (optional, for compatible APIs)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.model = model

    def detect_intent(self, statement: str) -> Optional[Tuple[str, int, str]]:
        """
        Detect intent from a single customer statement using GPT.

        Args:
            statement: The customer statement to analyze

        Returns:
            Tuple of (intent_type, confidence_level, reason) or None if no intent detected
        """
        results = self.detect_intent_batch([statement])
        if results and results[0]:
            return results[0]
        return None

    def detect_intent_batch(self, statements: List[str], batch_size: int = 10) -> List[Optional[Tuple[str, int, str]]]:
        """
        Detect intent from multiple statements in batch for efficiency.

        Args:
            statements: List of customer statements to analyze
            batch_size: Number of statements per API call

        Returns:
            List of (intent_type, confidence_level, reason) tuples or None for each statement
        """
        all_results = []

        for i in range(0, len(statements), batch_size):
            batch = statements[i:i + batch_size]
            batch_results = self._process_batch(batch)
            all_results.extend(batch_results)

            # Rate limiting - small delay between batches
            if i + batch_size < len(statements):
                time.sleep(0.5)

        return all_results

    def _process_batch(self, statements: List[str]) -> List[Optional[Tuple[str, int, str]]]:
        """Process a batch of statements with a single API call."""
        if not statements:
            return []

        # Build the prompt with numbered statements
        numbered_statements = "\n".join(
            f"{idx + 1}. \"{stmt}\"" for idx, stmt in enumerate(statements)
        )

        user_prompt = f"""請分析以下{len(statements)}句客戶語句，判斷每句是否有「購買意願」或「專人服務」的意圖。

語句列表：
{numbered_statements}

請回傳JSON陣列格式，每個元素包含：
- "index": 語句編號 (1-{len(statements)})
- "intent": "購買意願" 或 "專人服務" 或 "無意圖"
- "level": 意圖強度 1-5 (5最強，1最弱，無意圖則為0)
- "reason": 簡短說明判斷原因 (10字以內)

範例輸出：
[
  {{"index": 1, "intent": "購買意願", "level": 5, "reason": "明確表達要下單"}},
  {{"index": 2, "intent": "無意圖", "level": 0, "reason": "一般問候語"}}
]

只回傳JSON陣列，不要其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

            results_json = json.loads(content)

            # Map results back to statements
            results = [None] * len(statements)
            for item in results_json:
                idx = item.get("index", 0) - 1
                if 0 <= idx < len(statements):
                    intent = item.get("intent", "無意圖")
                    level = item.get("level", 0)
                    reason = item.get("reason", "")

                    if intent in ["購買意願", "專人服務"] and level > 0:
                        results[idx] = (intent, level, reason)

            return results

        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse GPT response as JSON: {e}")
            return [None] * len(statements)
        except Exception as e:
            print(f"Warning: GPT API error: {e}")
            return [None] * len(statements)


class CSVProcessor:
    """Processes CSV call files to extract customer statements."""

    def __init__(self, detector, use_gpt: bool = False):
        self.detector = detector
        self.use_gpt = use_gpt

    def process_file(self, file_path: Path) -> Tuple[List[str], str]:
        """
        Extract all statements from a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (list of statements, filename)
        """
        statements = []

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
                return statements, file_path.name

            # Process each line/row
            for line in content_lines:
                line = line.strip()
                if not line:
                    continue

                # Try to parse as CSV or treat as plain text
                extracted = self._extract_statements(line)
                statements.extend(extracted)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return statements, file_path.name

    def _extract_statements(self, line: str) -> List[str]:
        """Extract individual statements from a CSV line."""
        statements = []

        try:
            reader = csv.reader([line])
            for row in reader:
                for cell in row:
                    cell = cell.strip()
                    if cell and len(cell) > 2:
                        statements.append(cell)
        except:
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
        print(f"Mode: {'GPT API' if self.use_gpt else 'Keyword matching'}")

        if self.use_gpt:
            # Collect all statements first, then batch process with GPT
            all_statements = []  # (statement, filename)

            for i, csv_file in enumerate(csv_files, 1):
                if i % 100 == 0:
                    print(f"Reading file {i}/{len(csv_files)}...")

                statements, filename = self.process_file(csv_file)
                for stmt in statements:
                    all_statements.append((stmt, filename))

            print(f"Extracted {len(all_statements)} statements. Analyzing with GPT...")

            # Process in batches
            batch_size = 10
            statements_only = [s[0] for s in all_statements]

            for i in range(0, len(statements_only), batch_size):
                if i % 100 == 0 and i > 0:
                    print(f"Analyzing statement {i}/{len(statements_only)}...")

                batch = statements_only[i:i + batch_size]
                results = self.detector.detect_intent_batch(batch)

                for j, result in enumerate(results):
                    if result:
                        intent_type, level, reason = result
                        stmt, filename = all_statements[i + j]
                        all_matches.append(IntentMatch(
                            csv_file=filename,
                            statement=stmt,
                            intent_type=intent_type,
                            level=level,
                            reason=reason
                        ))

        else:
            # Keyword-based processing (original method)
            for i, csv_file in enumerate(csv_files, 1):
                if i % 100 == 0:
                    print(f"Processing file {i}/{len(csv_files)}...")

                statements, filename = self.process_file(csv_file)

                for statement in statements:
                    result = self.detector.detect_intent(statement)
                    if result:
                        intent_type, level, reason = result
                        all_matches.append(IntentMatch(
                            csv_file=filename,
                            statement=statement,
                            intent_type=intent_type,
                            level=level,
                            reason=reason
                        ))

        print(f"Processing complete. Found {len(all_matches)} intent matches.")
        return all_matches


class ResultsWriter:
    """Writes intent detection results to output files."""

    @staticmethod
    def write_csv(matches: List[IntentMatch], output_path: Path, include_reason: bool = False):
        """Write results to a CSV file."""
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # Write header
            if include_reason:
                writer.writerow(['csv', '客戶語句', '購買意願或專人服務', '等級', '判斷原因'])
            else:
                writer.writerow(['csv', '客戶語句', '購買意願或專人服務', '等級'])

            # Write data rows
            for match in matches:
                row = [match.csv_file, match.statement, match.intent_type, match.level]
                if include_reason:
                    row.append(match.reason)
                writer.writerow(row)

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
        print("RESULTS SUMMARY 結果摘要")
        print("=" * 50)
        print(f"Total matches found 總匹配數: {len(matches)}")
        print(f"  - Purchase intention 購買意願: {purchase_count}")
        print(f"  - Service request 專人服務: {service_count}")
        print("\nBy confidence level 按信心等級:")
        for level in range(5, 0, -1):
            print(f"  Level {level}: {level_counts[level]} matches")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='Extract customer purchase intentions and service requests from call CSV files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples 使用範例:
    # Keyword mode (default, no API required)
    python get_intent.py ./call_data
    python get_intent.py ./call_data --output results.csv

    # GPT mode (more accurate)
    python get_intent.py ./call_data --mode gpt --api-key YOUR_API_KEY
    python get_intent.py ./call_data --mode gpt  # Uses OPENAI_API_KEY env var

    # GPT mode with custom model
    python get_intent.py ./call_data --mode gpt --model gpt-4

    # GPT mode with custom API endpoint (Azure, local, etc.)
    python get_intent.py ./call_data --mode gpt --base-url https://your-api.com/v1
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

    parser.add_argument(
        '-m', '--mode',
        type=str,
        choices=['keyword', 'gpt'],
        default='keyword',
        help='Detection mode: keyword (default) or gpt'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gpt-3.5-turbo',
        help='GPT model to use (default: gpt-3.5-turbo)'
    )

    parser.add_argument(
        '--base-url',
        type=str,
        default=None,
        help='Custom API base URL (for Azure, local models, etc.)'
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

    # Initialize detector based on mode
    use_gpt = args.mode == 'gpt'

    if use_gpt:
        # Get API key
        api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Error: GPT mode requires an API key.")
            print("Provide via --api-key or set OPENAI_API_KEY environment variable.")
            sys.exit(1)

        if not OPENAI_AVAILABLE:
            print("Error: OpenAI package not installed.")
            print("Install with: pip install openai")
            sys.exit(1)

        print(f"Using GPT model: {args.model}")
        detector = GPTIntentDetector(
            api_key=api_key,
            model=args.model,
            base_url=args.base_url
        )
    else:
        detector = KeywordIntentDetector()

    processor = CSVProcessor(detector, use_gpt=use_gpt)

    # Process files
    print(f"Processing CSV files from: {input_path}")
    matches = processor.process_folder(input_path)

    # Write results (include reason column for GPT mode)
    output_path = Path(args.output)
    ResultsWriter.write_csv(matches, output_path, include_reason=use_gpt)
    ResultsWriter.print_summary(matches)


if __name__ == '__main__':
    main()
