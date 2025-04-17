# API configuration
DEFAULT_BASE_URL = "http://localhost:8000/"

# Task status constants
TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_RUNNING = "RUNNING"
TASK_STATUS_COMPLETED = "COMPLETED"
TASK_STATUS_FAILED = "FAILED"
TASK_STATUS_CANCELLED = "CANCELLED"

# APK build status constants
APK_STATUS_BUILDING = "BUILDING"
APK_STATUS_BUILDED = "BUILDED"
APK_STATUS_BUILDFAILED = "BUILDFAILED"

# Available models
MODELS = [
    "CLAUDE_3_5_SONNET",
    "GPT_3_5_TURBO",
    "GPT_4",
    "GPT_4_TURBO",
    "GPT_4O",
    "GPT_4O_MINI",
    "DEEPSEEK_R1"
]

# Available configurations
CONFIGURATIONS = [
    "Default",
    "Art",
    "Human",
    "Flet"
]