# API configuration
DEFAULT_BASE_URL = "http://localhost:8000/"

# Task status constants
TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_RUNNING = "RUNNING"
TASK_STATUS_COMPLETED = "COMPLETED"
TASK_STATUS_FAILED = "FAILED"
TASK_STATUS_CANCELLED = "CANCELLED"

# Available models
MODELS = [
    "CLAUDE_3_5_SONNET",
    "GPT-3.5-TURBO",
    "GPT-4",
    # Add more models as needed
]

# Available configurations
CONFIGURATIONS = [
    "Default",
    "Art",
    "Human",
    "Flet"
]