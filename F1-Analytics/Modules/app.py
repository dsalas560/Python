import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from modules.dashboard import (
    get_driver_standings,
    get_constructor_standings,
    get_race_schedule,
    get_race_results,
    CURRENT_SEASON
)
from modules.cache import cached_call
from modules.strategy import get_race_strategy, get_pit_stops

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "F1 Analytics"

# ── Team colors ──────────────────────────────────────────────────────────────
TEAM_COLORS = {
    "Red Bull": "#3671C6",
    "Ferrari": "#E8002D",
    "Mercedes": "#27F4D2",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine": "#FF87BC",
    "Williams": "#64C4FF",
    "RB": "#6692FF",
    "Kick Sauber": "#52E252",
    "Haas F1 Team": "#B6BABD",
}

COMPOUND_COLORS = {
    "SOFT": "#FF3333",
    "MEDIUM": "#FFF200",
    "HARD": "#EBEBEB",
    "INTERMEDIATE": "#39B54A",
    "WET": "#0067FF",
    "UNKNOWN": "#999999"
}

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),

    # Navbar
    html.Div([
        html.Span("🏎 F1 Analytics", style={"fontSize": "20px", "fontWeight": "bold", "color": "#E8002D"}),
        html.Div([
            dcc.Link("Dashboard", href="/", style={"marginRight": "24px"}),
            dcc.Link("Strategy", href="/strategy", style={"marginRight": "24px"}),
            dcc.Link("History", href="/history", style={"marginRight": "24px"}),
            dcc.Link("Circuits", href="/circuits"),
        ], style={"display": "flex", "alignItems": "center"})
    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "padding": "12px 32px",
        "backgroundColor": "#15151E",
        "borderBottom": "2px solid #E8002D"
    }),

    # Page content
    html.Div(id="page-content", style={"padding": "24px", "backgroundColor": "#1E1E2E", "minHeight": "100vh"})

], style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#1E1E2E", "color": "#FFFFFF"})


# ── Router ────────────────────────────────────────────────────────────────────
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/strategy":
        return strategy_layout()
    elif pathname == "/history":
        return history_layout()
    elif pathname == "/circuits":
        return circuits_layout()
    else:
        return dashboard_layout()


# ── Dashboard page ────────────────────────────────────────────────────────────
def dashboard_layout():
    seasons = list(range(2000, CURRENT_SEASON + 1))[::-1]
    return html.Div([
        html.H2(f"Season Dashboard", style={"color": "#E8002D"}),

        # Season selector
        html.Div([
            html.Label("Select Season:", style={"marginRight": "12px"}),
            dcc.Dropdown(
                id="dashboard-season",
                options=[{"label": str(s), "value": s} for s in seasons],
                value=CURRENT_SEASON,
                clearable=False,
                style={"width": "160px", "color": "#000"}
            )
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "24px"}),

        # Standings charts
        html.Div([
            dcc.Graph(id="driver-standings-chart", style={"flex": "1"}),
            dcc.Graph(id="constructor-standings-chart", style={"flex": "1"})
        ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

        # Race schedule table
        html.H3("Race Calendar", style={"color": "#E8002D"}),
        html.Div(id="race-schedule-table"),

        # Race results
        html.H3("Race Results", style={"color": "#E8002D", "marginTop": "24px"}),
        html.Div([
            html.Label("Select Round:", style={"marginRight": "12px"}),
            dcc.Dropdown(
                id="round-selector",
                placeholder="Select a round...",
                style={"width": "300px", "color": "#000"}
            )
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "16px"}),
        html.Div(id="race-results-table")
    ])


@app.callback(
    Output("driver-standings-chart", "figure"),
    Output("constructor-standings-chart", "figure"),
    Output("race-schedule-table", "children"),
    Output("round-selector", "options"),
    Input("dashboard-season", "value")
)
def update_dashboard(season):
    # Driver standings
    drivers = cached_call(f"driver_standings_{season}", get_driver_standings, season)
    df_drivers = pd.DataFrame(drivers)
    df_drivers["points"] = pd.to_numeric(df_drivers["points"])
    fig_drivers = px.bar(
        df_drivers, x="driver", y="points",
        color="constructor",
        color_discrete_map=TEAM_COLORS,
        title=f"{season} Driver Championship",
        template="plotly_dark"
    )
    fig_drivers.update_layout(
        plot_bgcolor="#15151E", paper_bgcolor="#15151E",
        xaxis_tickangle=-45, showlegend=False
    )

    # Constructor standings
    constructors = cached_call(f"constructor_standings_{season}", get_constructor_standings, season)
    df_constructors = pd.DataFrame(constructors)
    df_constructors["points"] = pd.to_numeric(df_constructors["points"])
    fig_constructors = px.bar(
        df_constructors, x="constructor", y="points",
        color="constructor",
        color_discrete_map=TEAM_COLORS,
        title=f"{season} Constructor Championship",
        template="plotly_dark"
    )
    fig_constructors.update_layout(
        plot_bgcolor="#15151E", paper_bgcolor="#15151E",
        xaxis_tickangle=-45, showlegend=False
    )

    # Race schedule table
    schedule = cached_call(f"schedule_{season}", get_race_schedule, season)
    df_schedule = pd.DataFrame(schedule)
    table = dash_table.DataTable(
        data=df_schedule.to_dict("records"),
        columns=[{"name": c.title(), "id": c} for c in df_schedule.columns],
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#15151E", "color": "#FFF", "border": "1px solid #333", "textAlign": "left", "padding": "8px"},
        style_header={"backgroundColor": "#E8002D", "color": "#FFF", "fontWeight": "bold"},
        page_size=12
    )

    # Round selector options
    round_options = [{"label": f"Round {r['round']} - {r['race']}", "value": r["round"]} for r in schedule]

    return fig_drivers, fig_constructors, table, round_options


@app.callback(
    Output("race-results-table", "children"),
    Input("round-selector", "value"),
    Input("dashboard-season", "value")
)
def update_race_results(round_num, season):
    if not round_num:
        return html.P("Select a round to see results.", style={"color": "#888"})
    results = cached_call(f"results_{season}_{round_num}", get_race_results, season, round_num)
    if not results:
        return html.P("No results available yet.", style={"color": "#888"})
    df = pd.DataFrame(results)
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c.title(), "id": c} for c in df.columns],
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#15151E", "color": "#FFF", "border": "1px solid #333", "textAlign": "left", "padding": "8px"},
        style_header={"backgroundColor": "#E8002D", "color": "#FFF", "fontWeight": "bold"},
    )


from modules.strategy import get_race_strategy, get_pit_stops

def strategy_layout():
    seasons = list(range(2018, CURRENT_SEASON + 1))[::-1]
    return html.Div([
        html.H2("Race Strategy", style={"color": "#E8002D"}),

        # Selectors
        html.Div([
            html.Div([
                html.Label("Season:", style={"marginRight": "8px"}),
                dcc.Dropdown(
                    id="strategy-season",
                    options=[{"label": str(s), "value": s} for s in seasons],
                    value=CURRENT_SEASON,
                    clearable=False,
                    style={"width": "140px", "color": "#000"}
                )
            ], style={"display": "flex", "alignItems": "center", "marginRight": "24px"}),

            html.Div([
                html.Label("Round:", style={"marginRight": "8px"}),
                dcc.Dropdown(
                    id="strategy-round",
                    options=[{"label": f"Round {r}", "value": r} for r in range(1, 25)],
                    value=1,
                    clearable=False,
                    style={"width": "160px", "color": "#000"}
                )
            ], style={"display": "flex", "alignItems": "center"})
        ], style={"display": "flex", "marginBottom": "24px"}),

        # Tire strategy chart
        html.H3("Tire Strategy", style={"color": "#E8002D"}),
        dcc.Loading(
            dcc.Graph(id="tire-strategy-chart"),
            type="circle",
            color="#E8002D"
        ),

        # Pit stop table
        html.H3("Pit Stops", style={"color": "#E8002D", "marginTop": "24px"}),
        dcc.Loading(
            html.Div(id="pit-stop-table"),
            type="circle",
            color="#E8002D"
        )
    ])


@app.callback(
    Output("tire-strategy-chart", "figure"),
    Output("pit-stop-table", "children"),
    Input("strategy-season", "value"),
    Input("strategy-round", "value")
)
def update_strategy(season, round_num):
    # Tire strategy
    strategy_data = cached_call(
        f"strategy_{season}_{round_num}",
        get_race_strategy, season, round_num
    )

    fig = go.Figure()
    drivers = list(strategy_data["strategy"].keys())

    for i, driver in enumerate(drivers):
        stints = strategy_data["strategy"][driver]
        for stint in stints:
            compound = stint["compound"]
            color = COMPOUND_COLORS.get(compound, "#999999")
            fig.add_trace(go.Bar(
                x=[stint["end_lap"] - stint["start_lap"] + 1],
                y=[driver],
                base=[stint["start_lap"] - 1],
                orientation="h",
                marker_color=color,
                name=compound,
                showlegend=compound not in [t.name for t in fig.data],
                hovertemplate=f"{driver} — {compound}<br>Laps {stint['start_lap']}–{stint['end_lap']}<extra></extra>"
            ))

    fig.update_layout(
        title=f"{strategy_data['event']} {season} — Tire Strategy",
        barmode="stack",
        template="plotly_dark",
        plot_bgcolor="#15151E",
        paper_bgcolor="#15151E",
        xaxis_title="Lap",
        yaxis_title="Driver",
        height=600,
        legend_title="Compound"
    )

    # Pit stops table
    pit_stops = cached_call(
        f"pitstops_{season}_{round_num}",
        get_pit_stops, season, round_num
    )

    if not pit_stops:
        pit_table = html.P("No pit stop data available.", style={"color": "#888"})
    else:
        df_pits = pd.DataFrame(pit_stops)
        pit_table = dash_table.DataTable(
            data=df_pits.to_dict("records"),
            columns=[{"name": c.title(), "id": c} for c in df_pits.columns],
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": "#15151E", "color": "#FFF", "border": "1px solid #333", "textAlign": "left", "padding": "8px"},
            style_header={"backgroundColor": "#E8002D", "color": "#FFF", "fontWeight": "bold"},
        )

    return fig, pit_table
    
# ── Placeholder pages (we'll fill these next) ─────────────────────────────────
def history_layout():
    return html.Div(html.H2("History — coming soon", style={"color": "#E8002D"}))

def circuits_layout():
    return html.Div(html.H2("Circuits — coming soon", style={"color": "#E8002D"}))


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
