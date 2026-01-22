import json
import re


def extract_json_from_response(text):
    # Try to find JSON in code blocks first
    json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(json_pattern, text)

    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # Try to parse the entire response as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find JSON object pattern in text
    json_obj_pattern = r'\{[\s\S]*\}'
    match = re.search(json_obj_pattern, text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def extract_sql_from_text(text):
    # Look for SQL in code blocks
    sql_pattern = r'```(?:sql)?\s*(SELECT[\s\S]*?)```'
    match = re.search(sql_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Look for SELECT statement directly
    select_pattern = r'(SELECT\s+[\s\S]+?)(?:;|$)'
    match = re.search(select_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip().rstrip(';')

    return None


def parse_llm_response(response_text):
    parsed = extract_json_from_response(response_text)

    if parsed and "sql" in parsed:
        viz = parsed.get("visualization", {})
        visualization = {
            "needed": viz.get("needed", False),
            "chart_type": viz.get("chart_type"),
            "x_column": viz.get("x_column"),
            "y_column": viz.get("y_column"),
            "title": viz.get("title")
        }

        return {
            "sql": parsed["sql"],
            "visualization": visualization,
            "explanation": parsed.get("explanation", "")
        }

    # Fallback: try to extract SQL directly
    sql = extract_sql_from_text(response_text)
    if sql:
        return {
            "sql": sql,
            "visualization": {
                "needed": False,
                "chart_type": None,
                "x_column": None,
                "y_column": None,
                "title": None
            },
            "explanation": "SQL extracted from response (visualization config not available)"
        }

    raise ValueError(f"Could not parse LLM response: {response_text[:500]}...")
