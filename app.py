"""Text-to-SQL Data Query Assistant"""

import streamlit as st
import pandas as pd

import config
from database import execute_query, get_table_names
from llm import generate_sql_response
from utils import validate_sql, sanitize_sql
from visualization import create_chart

st.set_page_config(
    page_title="Text-to-SQL Data Query Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; }

    .social-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 15px;
        padding: 10px 20px;
        margin-bottom: 10px;
    }
    .social-link {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #888;
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s ease;
    }
    .social-link:hover { color: #FAFAFA; }
    .social-link svg { width: 20px; height: 20px; fill: currentColor; }

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FAFAFA;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .developer-credit-top {
        text-align: center;
        color: #666;
        font-size: 0.85rem;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    .developer-credit-top a { color: #888; text-decoration: none; }
    .developer-credit-top a:hover { color: #FAFAFA; }

    .stTextArea textarea {
        background-color: #1E1E1E;
        color: #FAFAFA;
        border: 2px solid #333;
        border-radius: 8px;
        font-size: 1rem;
    }
    .stTextArea textarea:focus { border-color: #636EFA; }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #333, transparent);
        margin: 1.5rem 0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #1E1E1E;
    }
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 300px;
        max-width: 300px;
    }
</style>
""", unsafe_allow_html=True)

EXAMPLE_QUERIES = {
    "Bar Charts": [
        {"query": "How many tracks are in each genre?", "desc": "Track count by genre"},
        {"query": "Top 10 best selling artists", "desc": "Revenue by artist"},
        {"query": "Number of customers by country", "desc": "Customer distribution"},
        {"query": "Total sales by employee", "desc": "Employee performance"},
    ],
    "Pie Charts": [
        {"query": "What is the distribution of media types?", "desc": "Media type breakdown"},
        {"query": "Show percentage of tracks by genre for top 5 genres", "desc": "Genre distribution"},
        {"query": "Distribution of invoice totals by country for top 5 countries", "desc": "Sales by region"},
    ],
    "Line Charts": [
        {"query": "Show monthly sales trend over time", "desc": "Revenue over time"},
        {"query": "Monthly number of invoices over time", "desc": "Order volume trend"},
        {"query": "Show yearly total sales", "desc": "Annual revenue"},
    ],
    "Table Results": [
        {"query": "List all customers from USA", "desc": "US customer list"},
        {"query": "Show all albums by AC/DC", "desc": "Artist albums"},
        {"query": "Find tracks longer than 5 minutes", "desc": "Long tracks"},
        {"query": "List employees and their managers", "desc": "Org structure"},
    ]
}


def init_session_state():
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "run_query" not in st.session_state:
        st.session_state.run_query = None


def check_api_keys():
    provider = st.session_state.get("llm_provider", config.LLM_PROVIDER)
    if provider == "anthropic" and not config.ANTHROPIC_API_KEY:
        return False, "ANTHROPIC_API_KEY not configured"
    elif provider == "openai" and not config.OPENAI_API_KEY:
        return False, "OPENAI_API_KEY not configured"
    return True, ""


def process_query(user_question):
    result = {
        "success": False, "sql": None, "data": None,
        "chart": None, "explanation": None, "error": None,
        "question": user_question
    }

    try:
        provider = st.session_state.get("llm_provider", config.LLM_PROVIDER)
        llm_response = generate_sql_response(user_question, provider=provider)

        sql = llm_response["sql"]
        result["sql"] = sql
        result["explanation"] = llm_response.get("explanation", "")

        is_valid, error_msg = validate_sql(sql)
        if not is_valid:
            result["error"] = f"SQL validation failed: {error_msg}"
            return result

        df = execute_query(sanitize_sql(sql))
        result["data"] = df
        result["success"] = True

        viz_config = llm_response.get("visualization", {})
        result["viz_config"] = viz_config
        if viz_config.get("needed"):
            result["chart"] = create_chart(df, viz_config)

    except Exception as e:
        result["error"] = str(e)

    return result


def run_example_query(query):
    st.session_state.run_query = query


def render_social_links():
    st.markdown("""
    <div class="social-bar">
        <a href="https://github.com/surajmurari02" target="_blank" class="social-link">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
        </a>
        <a href="https://www.linkedin.com/in/suraj-murari" target="_blank" class="social-link">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
            LinkedIn
        </a>
    </div>
    """, unsafe_allow_html=True)


def render_header():
    render_social_links()
    st.markdown('<h1 class="main-header">Text-to-SQL Data Query Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform natural language into SQL queries instantly</p>', unsafe_allow_html=True)
    st.markdown('<p class="developer-credit-top">Developed with ❤️ by <a href="https://www.linkedin.com/in/suraj-murari" target="_blank">Suraj Murari</a></p>', unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("### Settings")

        provider_options = ["openai", "anthropic"]
        current_provider = st.session_state.get("llm_provider", config.LLM_PROVIDER)

        selected_provider = st.selectbox(
            "LLM Provider", options=provider_options,
            index=provider_options.index(current_provider) if current_provider in provider_options else 0,
            help="Select the AI model to use"
        )
        st.session_state.llm_provider = selected_provider

        model_name = config.OPENAI_MODEL if selected_provider == "openai" else config.ANTHROPIC_MODEL
        st.caption(f"Model: `{model_name}`")

        api_ok, _ = check_api_keys()
        if api_ok:
            st.success("API Connected")
        else:
            st.error("API Key Missing")

        st.markdown("---")
        st.markdown("### Database")

        try:
            tables = get_table_names()
            st.caption(f"Chinook Music Store - {len(tables)} tables")
            with st.expander("View Schema", expanded=False):
                for table in tables:
                    st.markdown(f"- `{table}`")
        except Exception as e:
            st.error(f"Database error: {e}")

        st.markdown("---")
        st.markdown("### Recent Queries")

        if st.session_state.query_history:
            for i, item in enumerate(reversed(st.session_state.query_history[-5:])):
                q = item["question"][:35] + "..." if len(item["question"]) > 35 else item["question"]
                if st.button(q, key=f"history_{i}", use_container_width=True):
                    run_example_query(item["question"])
        else:
            st.caption("No queries yet")


def render_example_buttons():
    st.markdown("### Try an Example")
    tabs = st.tabs(list(EXAMPLE_QUERIES.keys()))

    for tab, (category, queries) in zip(tabs, EXAMPLE_QUERIES.items()):
        with tab:
            cols = st.columns(2)
            for i, item in enumerate(queries):
                with cols[i % 2]:
                    if st.button(item['desc'], key=f"ex_{category}_{i}",
                                use_container_width=True, help=item['query']):
                        run_example_query(item['query'])


def render_query_input():
    user_question = st.text_area(
        "Ask a question about your data:",
        placeholder="e.g., How many tracks are in each genre?",
        height=100, key="query_input"
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit_button = st.button("Run Query", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.last_result = None
            st.session_state.run_query = None
            st.rerun()

    return user_question, submit_button


def render_results(result):
    if result["error"]:
        st.error(f"Error: {result['error']}")
        return

    st.markdown(f"**Question:** {result.get('question', 'N/A')}")

    with st.expander("Generated SQL", expanded=False):
        st.code(result["sql"], language="sql")

    if result["explanation"]:
        st.info(result['explanation'])

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if result["data"] is not None and not result["data"].empty:
        df = result["data"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", len(df))
        col2.metric("Columns", len(df.columns))
        viz_type = result.get("viz_config", {}).get("chart_type", "table")
        col3.metric("Chart Type", viz_type.title() if viz_type else "Table")
        col4.metric("Status", "Success")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if result["chart"]:
            chart_col, table_col = st.columns([3, 2])
            with chart_col:
                st.markdown("#### Visualization")
                st.plotly_chart(result["chart"], use_container_width=True)
            with table_col:
                st.markdown("#### Data")
                st.dataframe(df, use_container_width=True, height=400)
        else:
            st.markdown("#### Results")
            st.dataframe(df, use_container_width=True)

        st.download_button("Download CSV", df.to_csv(index=False),
                          "query_results.csv", "text/csv")

    elif result["data"] is not None and result["data"].empty:
        st.warning("Query executed successfully but returned no results.")


def main():
    init_session_state()
    render_header()
    render_sidebar()

    api_ok, api_error = check_api_keys()
    if not api_ok:
        st.warning(f"{api_error}. Please configure your API key in the `.env` file.")

    render_example_buttons()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("### Your Query")
    user_question, submit = render_query_input()

    query_to_run = None
    if st.session_state.run_query:
        query_to_run = st.session_state.run_query
        st.session_state.run_query = None
    elif submit and user_question:
        query_to_run = user_question

    if query_to_run:
        if not api_ok:
            st.error("Please configure your API key before submitting queries.")
            return

        with st.spinner("Generating SQL and executing query..."):
            result = process_query(query_to_run)
            st.session_state.last_result = result

            if not st.session_state.query_history or \
               st.session_state.query_history[-1]["question"] != query_to_run:
                st.session_state.query_history.append({
                    "question": query_to_run, "result": result
                })

    if st.session_state.last_result:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### Results")
        render_results(st.session_state.last_result)


if __name__ == "__main__":
    main()
