import re
from config import FORBIDDEN_SQL_KEYWORDS


def validate_sql(sql):
    if not sql or not sql.strip():
        return False, "SQL query cannot be empty"

    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return False, f"Forbidden keyword detected: {keyword}"

    # Check for multiple statements
    sql_no_strings = re.sub(r"'[^']*'", "", sql)
    sql_no_strings = re.sub(r'"[^"]*"', "", sql_no_strings)

    if ';' in sql_no_strings.rstrip(';'):
        return False, "Multiple SQL statements are not allowed"

    # Check for SQL injection patterns
    injection_patterns = [
        r'--',
        r'/\*',
        r'\*/',
        r'\bUNION\b.*\bSELECT\b',
    ]

    for pattern in injection_patterns:
        if re.search(pattern, sql_upper):
            if 'UNION' in pattern and 'UNION ALL' in sql_upper:
                continue
            return False, f"Potentially unsafe SQL pattern detected"

    return True, ""


def sanitize_sql(sql):
    sql = sql.strip()
    sql = sql.rstrip(';')
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    sql = ' '.join(sql.split())
    return sql
