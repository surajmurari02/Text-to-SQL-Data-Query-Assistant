import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DARK_THEME = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#FAFAFA",
    "colorway": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
                 "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
}


def validate_columns(df, x_col, y_col):
    return x_col in df.columns and y_col in df.columns


def auto_detect_chart_type(df):
    if df.empty or len(df.columns) < 2:
        return None

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    if not numeric_cols:
        return None

    if non_numeric_cols and numeric_cols:
        x_col = non_numeric_cols[0]
        y_col = numeric_cols[0]

        x_sample = str(df[x_col].iloc[0]) if len(df) > 0 else ""
        is_time_series = any(pattern in x_sample for pattern in ['-', '/', '20', '19'])

        if is_time_series:
            return {
                "chart_type": "line",
                "x_column": x_col,
                "y_column": y_col,
                "title": f"{y_col} over {x_col}"
            }

        unique_count = df[x_col].nunique()
        if unique_count <= 10 and 'percent' in y_col.lower() or 'distribution' in y_col.lower():
            return {
                "chart_type": "pie",
                "x_column": x_col,
                "y_column": y_col,
                "title": f"Distribution of {y_col}"
            }

        return {
            "chart_type": "bar",
            "x_column": x_col,
            "y_column": y_col,
            "title": f"{y_col} by {x_col}"
        }

    return None


def create_bar_chart(df, x_col, y_col, title="Bar Chart"):
    fig = px.bar(
        df, x=x_col, y=y_col, title=title,
        template=DARK_THEME["template"]
    )

    fig.update_layout(
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        plot_bgcolor=DARK_THEME["plot_bgcolor"],
        font=dict(color=DARK_THEME["font_color"]),
        xaxis_title=x_col.replace("_", " ").title(),
        yaxis_title=y_col.replace("_", " ").title(),
        showlegend=False
    )

    if len(df) > 8:
        fig.update_xaxes(tickangle=45)

    return fig


def create_pie_chart(df, x_col, y_col, title="Pie Chart"):
    fig = px.pie(
        df, names=x_col, values=y_col, title=title,
        template=DARK_THEME["template"]
    )

    fig.update_layout(
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        plot_bgcolor=DARK_THEME["plot_bgcolor"],
        font=dict(color=DARK_THEME["font_color"]),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def create_line_chart(df, x_col, y_col, title="Line Chart"):
    fig = px.line(
        df, x=x_col, y=y_col, title=title,
        template=DARK_THEME["template"],
        markers=True
    )

    fig.update_layout(
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        plot_bgcolor=DARK_THEME["plot_bgcolor"],
        font=dict(color=DARK_THEME["font_color"]),
        xaxis_title=x_col.replace("_", " ").title(),
        yaxis_title=y_col.replace("_", " ").title(),
        showlegend=False
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

    return fig


def create_chart(df, viz_config):
    if not viz_config.get("needed", False):
        return None

    chart_type = viz_config.get("chart_type")
    x_col = viz_config.get("x_column")
    y_col = viz_config.get("y_column")
    title = viz_config.get("title", "Chart")

    if not x_col or not y_col:
        auto_config = auto_detect_chart_type(df)
        if auto_config:
            chart_type = chart_type or auto_config["chart_type"]
            x_col = x_col or auto_config["x_column"]
            y_col = y_col or auto_config["y_column"]
            title = title or auto_config["title"]
        else:
            return None

    if not validate_columns(df, x_col, y_col):
        col_map = {c.lower(): c for c in df.columns}
        x_col = col_map.get(x_col.lower(), x_col) if x_col else x_col
        y_col = col_map.get(y_col.lower(), y_col) if y_col else y_col

        if not validate_columns(df, x_col, y_col):
            return None

    chart_creators = {
        "bar": create_bar_chart,
        "pie": create_pie_chart,
        "line": create_line_chart
    }

    creator = chart_creators.get(chart_type)
    if creator:
        return creator(df, x_col, y_col, title)

    return None
