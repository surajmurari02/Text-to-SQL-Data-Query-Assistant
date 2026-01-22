import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "chinook.db"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
OPENAI_MODEL = "gpt-4.1-mini"

LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048
MAX_RESULT_ROWS = 1000
QUERY_TIMEOUT_SECONDS = 30

FORBIDDEN_SQL_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "EXEC", "EXECUTE", "GRANT", "REVOKE",
    "COMMIT", "ROLLBACK", "SAVEPOINT", "MERGE", "REPLACE"
]
