"""
Configuration file for GetIntent - Keyword definitions for intent detection.

This file contains the keywords used to detect:
1. Purchase intention (購買意願)
2. Service request needs (專人服務)

Each keyword has an associated weight that contributes to the intent score.
Higher weights indicate stronger signals of intent.

You can customize these keywords to match your specific use case.
"""

# =============================================================================
# PURCHASE INTENTION KEYWORDS (購買意願)
# =============================================================================
# Keywords that indicate the customer wants to buy something
# Weights: Higher = stronger purchase signal

PURCHASE_INTENT_KEYWORDS = {
    # Direct purchase expressions (高權重 - 直接購買表達)
    "下訂單": 10,
    "我要買": 10,
    "我想買": 8,
    "想購買": 8,
    "要購買": 10,
    "想訂購": 8,
    "要訂購": 10,
    "下單": 8,
    "訂購": 7,
    "購買": 6,
    "結帳": 8,
    "付款": 7,
    "刷卡": 7,
    "匯款": 7,
    "轉帳": 6,

    # Interest expressions (中權重 - 興趣表達)
    "有興趣": 5,
    "想了解": 4,
    "怎麼買": 6,
    "如何購買": 6,
    "哪裡買": 5,
    "多少錢": 4,
    "價格": 3,
    "報價": 5,
    "優惠": 4,
    "折扣": 4,
    "促銷": 3,

    # Quantity and selection expressions (訂購數量相關)
    "幾個": 3,
    "幾件": 3,
    "幾組": 3,
    "幾台": 3,
    "幾箱": 3,
    "數量": 3,
    "我要": 4,
    "給我": 4,
    "來一個": 5,
    "來一份": 5,

    # Confirmation expressions (確認購買意願)
    "確定要": 6,
    "決定買": 8,
    "就這個": 5,
    "就買這": 7,
    "選這個": 5,

    # Urgency expressions (緊急需求)
    "趕快": 4,
    "盡快": 4,
    "馬上": 4,
    "立刻": 4,
    "今天": 3,
    "急需": 5,

    # Delivery related (寄送相關 - 表示即將購買)
    "寄到": 5,
    "送到": 5,
    "配送": 4,
    "運費": 4,
    "宅配": 4,
    "取貨": 4,
    "自取": 4,
}

# =============================================================================
# SERVICE REQUEST KEYWORDS (專人服務)
# =============================================================================
# Keywords that indicate the customer needs dedicated/personal service
# Weights: Higher = stronger service request signal

SERVICE_REQUEST_KEYWORDS = {
    # Direct service requests (直接服務請求)
    "專人服務": 10,
    "專人處理": 10,
    "真人服務": 10,
    "人工服務": 10,
    "人工客服": 10,
    "轉接專人": 10,
    "轉接客服": 9,
    "轉接人工": 9,
    "找客服": 8,
    "找專人": 8,
    "找真人": 8,

    # Service-related expressions (服務相關表達)
    "服務人員": 7,
    "客服人員": 7,
    "業務人員": 7,
    "專員": 6,
    "業務": 5,
    "客服": 5,

    # Help and support requests (協助請求)
    "需要協助": 6,
    "需要幫忙": 6,
    "需要幫助": 6,
    "請幫我": 5,
    "幫我處理": 6,
    "麻煩幫我": 6,
    "可以幫我": 5,

    # Complex issue expressions (複雜問題)
    "很複雜": 5,
    "比較複雜": 5,
    "問題很多": 5,
    "搞不懂": 4,
    "聽不懂": 4,
    "看不懂": 4,
    "不會操作": 5,
    "不會用": 4,

    # Callback requests (回電請求)
    "回電": 7,
    "回撥": 7,
    "打給我": 7,
    "聯絡我": 6,
    "電話聯繫": 6,
    "打電話": 5,

    # Dissatisfaction with automated service (對自動服務不滿)
    "語音": 3,
    "按鍵": 3,
    "機器人": 4,
    "自動": 3,
    "轉人工": 9,
    "不要語音": 6,
    "不要機器": 6,

    # Appointment requests (預約相關)
    "預約": 5,
    "約時間": 6,
    "安排時間": 6,
    "什麼時候方便": 5,

    # Technical support (技術支援)
    "技術支援": 6,
    "技術問題": 5,
    "系統問題": 5,
    "故障": 5,
    "維修": 5,
    "報修": 6,
}

# =============================================================================
# INTENSITY MODIFIERS (強度修飾詞)
# =============================================================================
# These words modify the confidence level when present in the statement
# Positive values increase confidence, negative values decrease it

INTENSITY_MODIFIERS = {
    # Strong positive modifiers (強烈正面修飾)
    "一定要": 3,
    "必須": 3,
    "絕對": 3,
    "肯定": 2,
    "確定": 2,
    "馬上": 2,
    "立刻": 2,
    "現在": 2,
    "今天": 2,
    "急": 2,
    "趕": 2,

    # Moderate positive modifiers (中等正面修飾)
    "希望": 1,
    "想要": 1,
    "需要": 1,
    "拜託": 1,
    "麻煩": 1,

    # Negative modifiers (降低意願的詞)
    "考慮": -2,
    "再說": -3,
    "以後": -2,
    "不確定": -2,
    "可能": -1,
    "也許": -1,
    "如果": -1,
    "假如": -1,
    "先不": -3,
    "暫時不": -3,
    "不用了": -5,
    "不需要": -4,
    "不要": -3,
}

# =============================================================================
# ADDITIONAL SETTINGS
# =============================================================================

# Minimum statement length to analyze (characters)
MIN_STATEMENT_LENGTH = 3

# Maximum statement length to include in results (will be truncated)
MAX_STATEMENT_LENGTH = 200
