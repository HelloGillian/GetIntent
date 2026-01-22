# GetIntent - 客戶意圖提取工具

Extract customer purchase intentions and service requests from call CSV files.

從通話 CSV 檔案中提取客戶購買意願和專人服務需求。

## Features 功能

- **Purchase Intent Detection (購買意願識別)**: Detects statements where customers express intent to purchase
- **Service Request Detection (專人服務識別)**: Detects statements where customers need dedicated human service
- **Confidence Levels (信心等級)**: Assigns a 1-5 level indicating the strength of intent
- **Batch Processing (批次處理)**: Process hundreds of CSV files at once
- **Chinese Language Support (中文支援)**: Optimized for Traditional Chinese keywords

## Installation 安裝

No external dependencies required. Uses Python 3.6+ standard library only.

```bash
# Clone the repository
git clone <repository-url>
cd GetIntent

# Run the tool
python get_intent.py <input_folder>
```

## Usage 使用方法

### Basic Usage 基本使用

```bash
# Process all CSV files in a folder
python get_intent.py ./call_data

# Specify output file
python get_intent.py ./call_data --output results.csv
python get_intent.py ./call_data -o my_results.csv
```

### Output Format 輸出格式

The tool generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| csv | Source CSV filename (來源檔案名稱) |
| 客戶語句 | Customer statement (客戶語句) |
| 購買意願或專人服務 | Intent type: "購買意願" or "專人服務" |
| 等級 | Confidence level 1-5 (信心等級 1-5) |

### Example Output 輸出範例

```csv
csv,客戶語句,購買意願或專人服務,等級
1111.csv,我要下訂單,購買意願,5
1112.csv,請幫我轉接專人服務,專人服務,5
1113.csv,這個產品多少錢,購買意願,3
1114.csv,我不會操作可以幫我嗎,專人服務,4
```

## Confidence Levels 信心等級說明

| Level | Description | 說明 |
|-------|-------------|------|
| 5 | Very strong intent, immediate action needed | 非常強烈意願，需立即處理 |
| 4 | Strong intent, high priority | 強烈意願，高優先級 |
| 3 | Moderate intent, follow-up recommended | 中等意願，建議跟進 |
| 2 | Weak intent, may need nurturing | 較弱意願，需要培養 |
| 1 | Minimal intent detected | 最低意願 |

## Customization 自訂設定

Edit `config.py` to customize the keyword dictionaries:

### Purchase Intent Keywords 購買意願關鍵字

```python
PURCHASE_INTENT_KEYWORDS = {
    "下訂單": 10,  # Weight: 10 (very strong signal)
    "我要買": 10,
    "想購買": 8,
    # Add your own keywords...
}
```

### Service Request Keywords 專人服務關鍵字

```python
SERVICE_REQUEST_KEYWORDS = {
    "專人服務": 10,
    "轉接客服": 9,
    "需要幫忙": 6,
    # Add your own keywords...
}
```

### Intensity Modifiers 強度修飾詞

These modify the confidence level:

```python
INTENSITY_MODIFIERS = {
    "一定要": 3,   # Increases confidence
    "馬上": 2,     # Increases confidence
    "考慮": -2,    # Decreases confidence
    "以後再說": -3, # Decreases confidence
}
```

## CSV File Format 檔案格式

The tool supports:
- UTF-8, UTF-8 BOM, Big5, GB2312, GBK encoded files
- Standard CSV format
- Plain text files with .csv extension

Each cell/line in the CSV is analyzed for customer intent.

## Examples 範例

### Processing 800 files

```bash
python get_intent.py /path/to/800/csv/files -o all_intents.csv
```

Output:
```
Found 800 CSV files to process...
Processing file 100/800...
Processing file 200/800...
...
Processing complete. Found 1523 intent matches.
Results written to: all_intents.csv

==================================================
RESULTS SUMMARY
==================================================
Total matches found: 1523
  - Purchase intention (購買意願): 892
  - Service request (專人服務): 631

By confidence level:
  Level 5: 234 matches
  Level 4: 412 matches
  Level 3: 567 matches
  Level 2: 210 matches
  Level 1: 100 matches
==================================================
```

## License

MIT License
