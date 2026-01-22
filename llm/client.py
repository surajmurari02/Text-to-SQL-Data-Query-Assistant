import config
from database.schema import get_schema_for_llm
from .parser import parse_llm_response
from .prompts import get_system_prompt


def _call_anthropic(user_question, system_prompt):
    from anthropic import Anthropic

    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not configured")

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        temperature=config.LLM_TEMPERATURE,
        system=system_prompt,
        messages=[{"role": "user", "content": user_question}]
    )

    return response.content[0].text


def _call_openai(user_question, system_prompt):
    from openai import OpenAI

    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured")

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        temperature=config.LLM_TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content


def generate_sql_response(user_question, provider=None):
    provider = provider or config.LLM_PROVIDER

    schema = get_schema_for_llm()
    system_prompt = get_system_prompt(schema)

    if provider == "anthropic":
        response_text = _call_anthropic(user_question, system_prompt)
    elif provider == "openai":
        response_text = _call_openai(user_question, system_prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    return parse_llm_response(response_text)
