# Text-to-SQL Data Query Assistant

A Streamlit-based application that converts natural language questions into SQL queries using AI (OpenAI GPT-4 or Anthropic Claude), executes them on a SQLite database, and displays results with automatic visualizations.

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Setup Instructions](#setup-instructions)
6. [Configuration](#configuration)
7. [Database Schema](#database-schema)
8. [Example Queries](#example-queries)
9. [Security Features](#security-features)
10. [Tech Stack](#tech-stack)
11. [Author](#author)

---

## Overview

This application allows users to query a database using plain English instead of writing SQL. The AI understands your question, generates the appropriate SQL query, executes it, and presents the results with automatic chart visualization when appropriate.

**Key Features:**
- Natural language to SQL conversion
- Support for multiple LLM providers (OpenAI, Anthropic)
- Automatic chart generation (Bar, Pie, Line)
- Query history
- CSV export
- SQL injection prevention

---

## How It Works

### Flow Diagram

```
┌─────────────────┐
│  User Question  │
│  (Plain English)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM Module    │
│  (GPT-4/Claude) │
│                 │
│ - Receives DB   │
│   schema        │
│ - Few-shot      │
│   examples      │
│ - Generates SQL │
│ - Suggests chart│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validator     │
│                 │
│ - Only SELECT   │
│ - No dangerous  │
│   keywords      │
│ - Single query  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (SQLite)      │
│                 │
│ - Execute query │
│ - Return data   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │
│                 │
│ - Auto-detect   │
│   chart type    │
│ - Generate      │
│   Plotly chart  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Streamlit UI  │
│                 │
│ - Display chart │
│ - Display table │
│ - Download CSV  │
└─────────────────┘
```

### Step-by-Step Process

1. **User Input**: User types a question like "How many tracks are in each genre?"

2. **Schema Injection**: The system extracts the database schema (table names, columns, relationships) and injects it into the LLM prompt.

3. **SQL Generation**: The LLM receives:
   - Database schema
   - Table relationships
   - Few-shot examples (5 examples covering different chart types)
   - User's question

   It returns a JSON response with:
   ```json
   {
     "sql": "SELECT ... FROM ...",
     "visualization": {
       "needed": true,
       "chart_type": "bar",
       "x_column": "genre",
       "y_column": "count",
       "title": "Tracks by Genre"
     },
     "explanation": "Brief description"
   }
   ```

4. **Validation**: The SQL is validated to ensure:
   - Only SELECT queries (no INSERT, UPDATE, DELETE, DROP)
   - No SQL injection patterns
   - Single statement only

5. **Execution**: The validated SQL runs against the SQLite database with:
   - Automatic LIMIT clause (max 1000 rows)
   - Timeout protection (30 seconds)

6. **Visualization**: Based on the LLM's suggestion:
   - Bar chart: For categorical comparisons
   - Pie chart: For part-to-whole (≤10 categories)
   - Line chart: For time-series data
   - Table only: For raw listings

7. **Display**: Results shown in Streamlit with chart + data table side by side.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py (Main)                        │
│                    Streamlit Application                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   database/   │    │     llm/      │    │visualization/ │
│               │    │               │    │               │
│ connection.py │    │  client.py    │    │  charts.py    │
│ schema.py     │    │  prompts.py   │    │               │
│               │    │  parser.py    │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  chinook.db   │    │ OpenAI/Claude │    │    Plotly     │
│   (SQLite)    │    │     API       │    │    Charts     │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## Project Structure

```
text-to-sql-app/
│
├── app.py                  # Main Streamlit application
│                           # - UI rendering
│                           # - Query processing flow
│                           # - Session state management
│
├── config.py               # Configuration settings
│                           # - API keys (from environment)
│                           # - Model settings
│                           # - Query limits
│
├── requirements.txt        # Python dependencies
│
├── .env.example            # Environment variable template
│
├── chinook.db              # SQLite database (music store)
│
├── database/               # Database module
│   ├── connection.py       # SQLite connection handler
│   │                       # - Context manager for connections
│   │                       # - Query execution with pandas
│   │                       # - Automatic LIMIT injection
│   │
│   └── schema.py           # Schema extraction
│                           # - Get table names
│                           # - Get column info
│                           # - Format schema for LLM
│                           # - Table relationships
│
├── llm/                    # LLM module
│   ├── client.py           # API client
│   │                       # - OpenAI GPT-4 support
│   │                       # - Anthropic Claude support
│   │                       # - Provider selection
│   │
│   ├── prompts.py          # Prompt engineering
│   │                       # - System prompt template
│   │                       # - Few-shot examples (5)
│   │                       # - JSON response format
│   │
│   └── parser.py           # Response parsing
│                           # - JSON extraction
│                           # - SQL extraction fallback
│                           # - Visualization config parsing
│
├── visualization/          # Visualization module
│   ├── __init__.py
│   └── charts.py           # Chart generation
│                           # - Bar chart (Plotly)
│                           # - Pie chart (Plotly)
│                           # - Line chart (Plotly)
│                           # - Auto-detection logic
│                           # - Dark theme styling
│
├── utils/                  # Utility module
│   ├── __init__.py
│   └── validators.py       # SQL validation
│                           # - SELECT-only check
│                           # - Forbidden keywords
│                           # - Injection prevention
│
└── .streamlit/
    └── config.toml         # Streamlit theme config
                            # - Dark theme colors
                            # - Layout settings
```

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key OR Anthropic API key
- Git (for deployment)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/surajmurari02/text-to-sql-app.git
   cd text-to-sql-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Linux/Mac:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` file:
   ```
   OPENAI_API_KEY=sk-your-openai-key-here
   LLM_PROVIDER=openai
   ```

   OR for Anthropic:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   LLM_PROVIDER=anthropic
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   ```
   http://localhost:8501
   ```

### Streamlit Cloud Deployment

1. Push code to GitHub (public repository)

2. Go to https://share.streamlit.io

3. Click "New app" and select your repository

4. Add secrets in Advanced Settings:
   ```
   OPENAI_API_KEY = "sk-your-key"
   LLM_PROVIDER = "openai"
   ```

5. Deploy - your app will be live at:
   ```
   https://your-username-app-name.streamlit.app
   ```

---

## Configuration

### config.py Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_PROVIDER` | "openai" | LLM provider: "openai" or "anthropic" |
| `OPENAI_MODEL` | "gpt-4.1-mini" | OpenAI model to use |
| `ANTHROPIC_MODEL` | "claude-sonnet-4-20250514" | Anthropic model to use |
| `LLM_TEMPERATURE` | 0.1 | Low for consistent SQL generation |
| `MAX_RESULT_ROWS` | 1000 | Maximum rows returned |
| `QUERY_TIMEOUT_SECONDS` | 30 | Query timeout limit |

### Forbidden SQL Keywords

The following keywords are blocked for security:
- INSERT, UPDATE, DELETE, DROP
- CREATE, ALTER, TRUNCATE
- EXEC, EXECUTE, GRANT, REVOKE
- COMMIT, ROLLBACK, MERGE, REPLACE

---

## Database Schema

The application uses the **Chinook Database** - a sample digital music store database.

### Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `artists` | Music artists | ArtistId, Name |
| `albums` | Albums by artists | AlbumId, Title, ArtistId |
| `tracks` | Individual songs | TrackId, Name, AlbumId, GenreId, Milliseconds, UnitPrice |
| `genres` | Music genres | GenreId, Name |
| `media_types` | File formats | MediaTypeId, Name |
| `playlists` | User playlists | PlaylistId, Name |
| `playlist_track` | Playlist contents | PlaylistId, TrackId |
| `customers` | Customer info | CustomerId, FirstName, LastName, Country, Email |
| `employees` | Staff info | EmployeeId, FirstName, LastName, Title, ReportsTo |
| `invoices` | Sales records | InvoiceId, CustomerId, InvoiceDate, Total |
| `invoice_items` | Line items | InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity |

### Relationships

```
artists ──< albums ──< tracks >── genres
                         │
                         ├── media_types
                         │
                         └──< invoice_items >── invoices >── customers
                                                               │
                                                               └── employees
```

---

## Example Queries

### Bar Chart Queries
- "How many tracks are in each genre?"
- "Top 10 best selling artists"
- "Number of customers by country"
- "Total sales by employee"

### Pie Chart Queries
- "What is the distribution of media types?"
- "Show percentage of tracks by genre for top 5 genres"
- "Distribution of invoice totals by country"

### Line Chart Queries
- "Show monthly sales trend over time"
- "Monthly number of invoices over time"
- "Show yearly total sales"

### Table Queries
- "List all customers from USA"
- "Show all albums by AC/DC"
- "Find tracks longer than 5 minutes"
- "List employees and their managers"

---

## Security Features

1. **SELECT-Only Queries**
   - Only SELECT statements are allowed
   - All other SQL commands are blocked

2. **Keyword Blacklist**
   - Dangerous keywords (DROP, DELETE, etc.) are detected and blocked

3. **Single Statement**
   - Multiple SQL statements (separated by ;) are rejected
   - Prevents SQL injection via statement chaining

4. **Query Timeout**
   - 30-second timeout prevents long-running queries

5. **Row Limit**
   - Maximum 1000 rows returned
   - Prevents memory issues with large results

6. **Input Sanitization**
   - SQL comments are stripped
   - Whitespace is normalized

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM | OpenAI GPT-4 / Anthropic Claude |
| Database | SQLite |
| Data Processing | Pandas |
| Visualization | Plotly |
| Styling | Custom CSS |

### Dependencies

```
streamlit>=1.28.0      # Web framework
anthropic>=0.18.0      # Anthropic API client
openai>=1.0.0          # OpenAI API client
pandas>=2.0.0          # Data manipulation
plotly>=5.18.0         # Interactive charts
python-dotenv>=1.0.0   # Environment variables
```

---

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `.env` file exists with correct key
   - Check key has sufficient credits

2. **Database Not Found**
   - Verify `chinook.db` is in the project root
   - Check file permissions

3. **Chart Not Displaying**
   - LLM might suggest no visualization needed
   - Check if data has appropriate columns

4. **Query Returns No Results**
   - SQL might be correct but data doesn't exist
   - Check the explanation for query logic

---

## Author

Developed with ❤️ by **Suraj Murari**

- GitHub: [@surajmurari02](https://github.com/surajmurari02)
- LinkedIn: [suraj-murari](https://www.linkedin.com/in/suraj-murari)

---