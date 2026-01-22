# GetIntent - 客戶意圖提取工具

Extract customer purchase intentions and service requests from call CSV files using keyword matching or GPT AI analysis.

從通話 CSV 檔案中提取客戶購買意願和專人服務需求，支援關鍵字匹配或 GPT AI 分析。

## Features 功能

- **Two Detection Modes 雙重偵測模式**:
  - **Keyword Mode 關鍵字模式**: Fast, no API required (預設，快速，不需API)
  - **GPT Mode GPT模式**: More accurate AI-powered analysis (更準確的AI分析)
- **Purchase Intent Detection (購買意願識別)**: Detects statements where customers express intent to purchase
- **Service Request Detection (專人服務識別)**: Detects statements where customers need dedicated human service
- **Confidence Levels (信心等級)**: Assigns a 1-5 level indicating the strength of intent
- **Batch Processing (批次處理)**: Process hundreds of CSV files at once
- **Chinese Language Support (中文支援)**: Optimized for Traditional Chinese

## Installation 安裝

```bash
# Clone the repository
git clone <repository-url>
cd GetIntent

# Install dependencies (required for GPT mode)
pip install -r requirements.txt
```

## Usage 使用方法

### Keyword Mode (Default) 關鍵字模式

Fast processing using predefined keywords. No API required.

```bash
# Process all CSV files in a folder
python get_intent.py ./call_data

# Specify output file
python get_intent.py ./call_data --output results.csv
python get_intent.py ./call_data -o my_results.csv
```

### GPT Mode GPT模式

More accurate analysis using OpenAI GPT models.

```bash
# Using API key as argument
python get_intent.py ./call_data --mode gpt --api-key YOUR_API_KEY

# Using environment variable (recommended)
export OPENAI_API_KEY="your-api-key"
python get_intent.py ./call_data --mode gpt

# Using GPT-4 for best accuracy
python get_intent.py ./call_data --mode gpt --model gpt-4

# Using custom API endpoint (Azure OpenAI, local models, etc.)
python get_intent.py ./call_data --mode gpt --base-url https://your-endpoint.com/v1
```

### Command Line Options 命令列選項

| Option | Description | 說明 |
|--------|-------------|------|
| `input_folder` | Path to CSV files folder | CSV檔案資料夾路徑 |
| `-o, --output` | Output file path (default: intent_results.csv) | 輸出檔案路徑 |
| `-m, --mode` | Detection mode: `keyword` or `gpt` | 偵測模式 |
| `--api-key` | OpenAI API key | OpenAI API金鑰 |
| `--model` | GPT model (default: gpt-3.5-turbo) | GPT模型選擇 |
| `--base-url` | Custom API endpoint URL | 自訂API端點 |

## Output Format 輸出格式

### Keyword Mode Output

| Column | Description |
|--------|-------------|
| csv | Source CSV filename |
| 客戶語句 | Customer statement |
| 購買意願或專人服務 | Intent type |
| 等級 | Confidence level 1-5 |

### GPT Mode Output (includes reasoning)

| Column | Description |
|--------|-------------|
| csv | Source CSV filename |
| 客戶語句 | Customer statement |
| 購買意願或專人服務 | Intent type |
| 等級 | Confidence level 1-5 |
| 判斷原因 | GPT's reasoning |

### Example Output 輸出範例

```csv
csv,客戶語句,購買意願或專人服務,等級,判斷原因
1111.csv,我要下訂單,購買意願,5,明確表達要下單
1112.csv,請幫我轉接專人服務,專人服務,5,要求轉接專人
1113.csv,這個產品多少錢,購買意願,3,詢問價格
1114.csv,我不會操作可以幫我嗎,專人服務,4,需要人工協助
```

## Confidence Levels 信心等級說明

| Level | Description | 說明 |
|-------|-------------|------|
| 5 | Very strong intent, immediate action needed | 非常強烈意願，需立即處理 |
| 4 | Strong intent, high priority | 強烈意願，高優先級 |
| 3 | Moderate intent, follow-up recommended | 中等意願，建議跟進 |
| 2 | Weak intent, may need nurturing | 較弱意願，需要培養 |
| 1 | Minimal intent detected | 最低意願 |

## GPT Mode Details GPT模式說明

### How it Works 運作原理

1. **Batch Processing 批次處理**: Statements are sent to GPT in batches of 10 for efficiency
2. **Structured Output 結構化輸出**: GPT returns JSON with intent type, level, and reasoning
3. **Rate Limiting 速率限制**: Built-in delays to avoid API rate limits

### Cost Estimation 費用估算

For 800 CSV files with approximately 10 statements each:
- ~8,000 statements total
- ~800 API calls (10 statements per batch)
- Estimated cost: ~$0.50-$2.00 USD (gpt-3.5-turbo)

### Supported Models 支援模型

| Model | Accuracy | Speed | Cost |
|-------|----------|-------|------|
| gpt-3.5-turbo | Good | Fast | Low |
| gpt-4 | Best | Slower | Higher |
| gpt-4-turbo | Very Good | Fast | Medium |

## Customization 自訂設定

### Keyword Configuration (for keyword mode)

Edit `config.py` to customize keywords:

```python
PURCHASE_INTENT_KEYWORDS = {
    "下訂單": 10,  # Weight: 10 (very strong signal)
    "我要買": 10,
    "想購買": 8,
    # Add your own keywords...
}

SERVICE_REQUEST_KEYWORDS = {
    "專人服務": 10,
    "轉接客服": 9,
    # Add your own keywords...
}
```

### GPT Prompt Customization

To customize the GPT analysis, edit the `SYSTEM_PROMPT` in `get_intent.py`:

```python
class GPTIntentDetector:
    SYSTEM_PROMPT = """你是一個專門分析客戶通話內容的AI助手..."""
```

## Examples 範例

### Processing 800 files with GPT

```bash
export OPENAI_API_KEY="sk-..."
python get_intent.py /path/to/800/csv/files -o all_intents.csv --mode gpt
```

Output:
```
Found 800 CSV files to process...
Mode: GPT API
Using GPT model: gpt-3.5-turbo
Reading file 100/800...
Reading file 200/800...
...
Extracted 8234 statements. Analyzing with GPT...
Analyzing statement 100/8234...
Analyzing statement 200/8234...
...
Processing complete. Found 1523 intent matches.
Results written to: all_intents.csv

==================================================
RESULTS SUMMARY 結果摘要
==================================================
Total matches found 總匹配數: 1523
  - Purchase intention 購買意願: 892
  - Service request 專人服務: 631

By confidence level 按信心等級:
  Level 5: 234 matches
  Level 4: 412 matches
  Level 3: 567 matches
  Level 2: 210 matches
  Level 1: 100 matches
==================================================
```

## Comparison: Keyword vs GPT Mode 模式比較

| Feature | Keyword Mode | GPT Mode |
|---------|--------------|----------|
| Speed 速度 | Very Fast | Slower |
| Cost 費用 | Free | API費用 |
| Accuracy 準確度 | Good for clear keywords | Better for nuanced text |
| Setup 設定 | None | API key required |
| Offline 離線使用 | Yes | No |
| Reasoning 判斷原因 | No | Yes |

## License

MIT License
