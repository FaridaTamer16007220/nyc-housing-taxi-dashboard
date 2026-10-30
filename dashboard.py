
from pathlib import Path
from io import StringIO

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, dash_table

# =====================================================
# 1. LOAD DATA
# =====================================================

DATA = Path(__file__).parent / "data"

housing = pd.read_csv(DATA / "housing_clean.csv")
taxi = pd.read_csv(DATA / "taxi_clean.csv")

housing["project_completion_date"] = pd.to_datetime(
    housing["project_completion_date"], errors="coerce"
)
housing["project_completion_year"] = (
    housing["project_completion_date"].dt.year
)
housing["borough"] = (
    housing["borough"].fillna("").astype(str).str.upper()
)

taxi["pickup_month"] = pd.to_datetime(
    taxi["pickup_month"], errors="coerce"
)
taxi["year"] = taxi["pickup_month"].dt.year
taxi["month_number"] = taxi["pickup_month"].dt.month
taxi["month_name"] = taxi["pickup_month"].dt.strftime("%B")
taxi["taxi_borough"] = (
    taxi["taxi_borough"].fillna("").astype(str).str.upper()
)

BOROUGHS = [
    "BRONX", "BROOKLYN", "MANHATTAN",
    "QUEENS", "STATEN ISLAND"
]

MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# Use the years available in both datasets when possible.
housing_years = set(
    housing["project_completion_year"].dropna().astype(int)
)
taxi_years = set(taxi["year"].dropna().astype(int))
YEARS = sorted(housing_years & taxi_years)

if not YEARS:
    YEARS = sorted(housing_years | taxi_years)

HOUSING_CATEGORY_COLUMN = "reporting_construction_type"
TAXI_CATEGORY_COLUMN = "zone_name"

HOUSING_CATEGORIES = sorted(
    housing[HOUSING_CATEGORY_COLUMN].dropna().astype(str).unique()
) if HOUSING_CATEGORY_COLUMN in housing.columns else []

TAXI_CATEGORIES = sorted(
    taxi[TAXI_CATEGORY_COLUMN].dropna().astype(str).unique()
) if TAXI_CATEGORY_COLUMN in taxi.columns else []

# =====================================================
# 2. STYLING AND HELPER FUNCTIONS
# =====================================================

app = Dash(__name__)
app.title = "NYC Housing & Taxi Dashboard"

PAGE_STYLE = {
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f3f6fb",
    "minHeight": "100vh",
    "padding": "28px",
    "color": "#182235",
}

CARD_STYLE = {
    "backgroundColor": "white",
    "padding": "20px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
    "flex": "1",
    "minWidth": "220px",
}

FILTER_STYLE = {"flex": "1", "minWidth": "200px"}


def make_card(title, value, description):
    return html.Div(
        [
            html.P(title, style={"color": "#64748b"}),
            html.H2(value, style={"margin": "0", "color": "#173b70"}),
            html.P(
                description,
                style={"fontSize": "12px", "color": "#64748b"},
            ),
        ],
        style=CARD_STYLE,
    )


def style_figure(fig):
    fig.update_layout(
        template="plotly_white",
        title_x=0.03,
        margin=dict(l=25, r=20, t=65, b=45),
    )
    return fig


def dropdown_options(values, all_label):
    return (
        [{"label": all_label, "value": "ALL"}]
        + [
            {"label": str(value), "value": str(value)}
            for value in values
        ]
    )


def apply_search(df, search_text, columns):
    """Search each word across the specified columns."""
    if not search_text or not search_text.strip():
        return df

    result = df.copy()

    for word in search_text.strip().split():
        matches = pd.Series(False, index=result.index)

        for column in columns:
            if column in result.columns:
                matches |= (
                    result[column]
                    .fillna("")
                    .astype(str)
                    .str.contains(word, case=False, regex=False)
                )

        result = result[matches]

    return result


def get_filtered_data(
    selected_borough,
    selected_year,
    selected_month,
    housing_category,
    taxi_category,
    search_text,
):
    h = housing.copy()
    t = taxi.copy()

    # Borough
    if selected_borough != "ALL":
        h = h[h["borough"] == selected_borough]
        t = t[t["taxi_borough"] == selected_borough]

    # Year
    if selected_year != "ALL":
        h = h[h["project_completion_year"] == int(selected_year)]
        t = t[t["year"] == int(selected_year)]

    # Month
    if selected_month != "ALL":
        h = h[
            h["project_completion_date"].dt.month_name()
            == selected_month
        ]
        t = t[t["month_name"] == selected_month]

    # Housing category
    if (
        housing_category != "ALL"
        and HOUSING_CATEGORY_COLUMN in h.columns
    ):
        h = h[
            h[HOUSING_CATEGORY_COLUMN].fillna("").astype(str)
            == housing_category
        ]

    # Transportation category: pickup zone
    if (
        taxi_category != "ALL"
        and TAXI_CATEGORY_COLUMN in t.columns
    ):
        t = t[
            t[TAXI_CATEGORY_COLUMN].fillna("").astype(str)
            == taxi_category
        ]

    # Search housing and transportation independently.
    h = apply_search(
        h,
        search_text,
        [
            "project_name",
            "borough",
            "project_completion_year",
            HOUSING_CATEGORY_COLUMN,
        ],
    )

    t = apply_search(
        t,
        search_text,
        [
            "taxi_borough",
            "year",
            "month_name",
            TAXI_CATEGORY_COLUMN,
            "pickup_zone_id",
        ],
    )

    return h, t


# =====================================================
# 3. WEBSITE LAYOUT
# =====================================================

app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.P(
                    "NYC OPEN DATA • INTERACTIVE DASHBOARD",
                    style={
                        "letterSpacing": "2px",
                        "color": "#9ec5ff",
                    },
                ),
                html.H1(
                    "Affordable Housing & Yellow Taxi Activity"
                ),
                html.P(
                    "Explore affordable housing production and yellow "
                    "taxi pickup activity across New York City.",
                    style={"fontSize": "16px", "color": "#dbeafe"},
                ),
            ],
            style={
                "backgroundColor": "#173b70",
                "color": "white",
                "padding": "28px",
                "borderRadius": "14px",
                "marginBottom": "24px",
            },
        ),

        # Filters
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Borough"),
                        dcc.Dropdown(
                            id="borough-filter",
                            options=dropdown_options(
                                BOROUGHS, "All boroughs"
                            ),
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    style=FILTER_STYLE,
                ),

                html.Div(
                    [
                        html.Label("Year"),
                        dcc.Dropdown(
                            id="year-filter",
                            options=dropdown_options(
                                YEARS, "All available years"
                            ),
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    style=FILTER_STYLE,
                ),

                html.Div(
                    [
                        html.Label("Housing Category"),
                        dcc.Dropdown(
                            id="housing-category-filter",
                            options=dropdown_options(
                                HOUSING_CATEGORIES,
                                "All housing categories",
                            ),
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    style=FILTER_STYLE,
                ),

                html.Div(
                    [
                        html.Label("Transportation Category"),
                        dcc.Dropdown(
                            id="taxi-category-filter",
                            options=dropdown_options(
                                TAXI_CATEGORIES,
                                "All pickup zones",
                            ),
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    style=FILTER_STYLE,
                ),

                html.Div(
                    [
                        html.Label("Month"),
                        dcc.Dropdown(
                            id="month-filter",
                            options=dropdown_options(
                                MONTHS, "All months"
                            ),
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    style=FILTER_STYLE,
                ),

                html.Div(
                    [
                        html.Label("Search"),
                        dcc.Input(
                            id="search-input",
                            type="text",
                            placeholder="Search project, borough, or zone...",
                            debounce=True,
                            style={
                                "width": "100%",
                                "padding": "10px",
                                "border": "1px solid #cbd5e1",
                                "borderRadius": "6px",
                                "boxSizing": "border-box",
                            },
                        ),
                    ],
                    style={**FILTER_STYLE, "flex": "2"},
                ),

                html.Button(
                    "Generate Report",
                    id="report-button",
                    n_clicks=0,
                    style={
                        "padding": "12px 20px",
                        "backgroundColor": "#173b70",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "7px",
                        "cursor": "pointer",
                        "fontWeight": "bold",
                    },
                ),

                dcc.Download(id="report-download"),
            ],
            style={
                "display": "flex",
                "gap": "18px",
                "flexWrap": "wrap",
                "backgroundColor": "white",
                "padding": "20px",
                "borderRadius": "12px",
                "marginBottom": "24px",
            },
        ),

        html.Div(
            id="filter-status",
            style={"marginBottom": "12px"},
        ),

        # Summary cards
        html.Div(
            id="summary-cards",
            style={
                "display": "flex",
                "gap": "16px",
                "flexWrap": "wrap",
                "marginBottom": "24px",
            },
        ),

        # Monthly charts
        html.Div(
            [
                html.Div(
                    dcc.Graph(id="housing-chart"),
                    style={**CARD_STYLE, "minWidth": "300px"},
                ),
                html.Div(
                    dcc.Graph(id="taxi-chart"),
                    style={**CARD_STYLE, "minWidth": "300px"},
                ),
            ],
            style={
                "display": "flex",
                "gap": "20px",
                "flexWrap": "wrap",
                "marginBottom": "20px",
            },
        ),

        # Borough charts
        html.Div(
            [
                html.Div(
                    dcc.Graph(id="housing-borough-chart"),
                    style={**CARD_STYLE, "minWidth": "300px"},
                ),
                html.Div(
                    dcc.Graph(id="taxi-borough-chart"),
                    style={**CARD_STYLE, "minWidth": "300px"},
                ),
            ],
            style={
                "display": "flex",
                "gap": "20px",
                "flexWrap": "wrap",
                "marginBottom": "20px",
            },
        ),

        # Relationship between the two datasets
        html.Div(
            dcc.Graph(id="relationship-chart"),
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),

        # Housing results
        html.Div(
            [
                html.H2("Housing Project Search Results"),
                html.P(
                    "The table displays up to 100 matching records. "
                    "You can sort and filter its columns."
                ),
                dash_table.DataTable(
                    id="housing-table",
                    page_size=10,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "padding": "9px",
                        "textAlign": "left",
                        "maxWidth": "240px",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                    },
                    style_header={
                        "backgroundColor": "#e8eef8",
                        "fontWeight": "bold",
                    },
                ),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),

        # Story section
        html.Div(
            [
                html.H2("The Story: Housing and Mobility in NYC"),

                html.H3("Research Question"),
                html.P(
                    "How does affordable housing production in NYC "
                    "compare with yellow taxi pickup activity across "
                    "boroughs and throughout the selected year?"
                ),

                html.H3("Key Findings"),
                html.P(id="story-findings"),

                html.H3("Limitations"),
                html.P(
                    "Housing records and taxi pickups measure different "
                    "things. A relationship between them does not prove "
                    "that one causes the other. Results depend on the "
                    "available dates and borough or zone mappings."
                ),

                html.H3("Benefit to NYC"),
                html.P(
                    "This comparison helps residents and planners explore "
                    "where housing production and taxi activity occur and "
                    "identify areas for further investigation."
                ),

                html.P(
                    "Sources: NYC Open Data — Affordable Housing "
                    "Production by Building and Yellow Taxi Trip Data.",
                    style={"color": "#64748b", "fontSize": "13px"},
                ),
            ],
            style={**CARD_STYLE, "marginBottom": "24px"},
        ),

        html.P(
            "NYC Housing & Taxi Activity",
            style={"textAlign": "center", "color": "#64748b"},
        ),
    ],
    style=PAGE_STYLE,
)


# =====================================================
# 4. UPDATE DASHBOARD
# =====================================================

@app.callback(
    Output("filter-status", "children"),
    Output("summary-cards", "children"),
    Output("housing-chart", "figure"),
    Output("taxi-chart", "figure"),
    Output("housing-borough-chart", "figure"),
    Output("taxi-borough-chart", "figure"),
    Output("relationship-chart", "figure"),
    Output("housing-table", "data"),
    Output("housing-table", "columns"),
    Output("story-findings", "children"),
    Input("borough-filter", "value"),
    Input("year-filter", "value"),
    Input("housing-category-filter", "value"),
    Input("taxi-category-filter", "value"),
    Input("month-filter", "value"),
    Input("search-input", "value"),
    Input("report-button", "n_clicks"),
)
def update_dashboard(
    borough, year, housing_category,
    taxi_category, month, search, report_clicks
):
    h, t = get_filtered_data(
        borough, year, month,
        housing_category, taxi_category, search
    )

    pickups = pd.to_numeric(
        t["pickup_trips"], errors="coerce"
    ).sum()

    status = (
        f"Showing {len(h):,} housing records and "
        f"{pickups:,.0f} taxi pickups. "
        f"Borough: {borough}; Year: {year}; Month: {month}."
    )

    units = pd.to_numeric(
        h["total_units"], errors="coerce"
    ).sum()

    cards = [
        make_card(
            "Housing Records",
            f"{len(h):,}",
            "Filtered records",
        ),
        make_card(
            "Unique Projects",
            f"{h['project_id'].nunique():,}",
            "Distinct project IDs",
        ),
        make_card(
            "Housing Units",
            f"{units:,.0f}",
            "Sum of total_units",
        ),
        make_card(
            "Taxi Pickups",
            f"{pickups:,.0f}",
            "Filtered taxi pickups",
        ),
    ]

    # Housing completions by month
    valid = h.dropna(subset=["project_completion_date"])

    hm = (
        valid.assign(
            month_number=valid["project_completion_date"].dt.month
        )
        .groupby("month_number")
        .size()
        .reindex(range(1, 13), fill_value=0)
        .rename("records")
        .rename_axis("month_number")
        .reset_index()
    )

    hm["month"] = hm["month_number"].map(
        dict(enumerate(MONTHS, start=1))
    )

    housing_fig = px.bar(
        hm,
        x="month",
        y="records",
        title="Housing Completion Records by Month",
        labels={"month": "Month", "records": "Housing records"},
    )
    style_figure(housing_fig)

    # Taxi pickups by month
    tm = (
        t.groupby("month_number")["pickup_trips"]
        .sum()
        .reindex(range(1, 13), fill_value=0)
        .rename_axis("month_number")
        .reset_index()
    )

    tm["month"] = tm["month_number"].map(
        dict(enumerate(MONTHS, start=1))
    )

    taxi_fig = px.line(
        tm,
        x="month",
        y="pickup_trips",
        markers=True,
        title="Yellow Taxi Pickups by Month",
        labels={"month": "Month", "pickup_trips": "Taxi pickups"},
    )
    style_figure(taxi_fig)

    # Housing records by borough
    hb = (
        h.groupby("borough")
        .size()
        .reindex(BOROUGHS, fill_value=0)
        .rename("records")
        .rename_axis("borough")
        .reset_index()
    )

    housing_borough_fig = px.bar(
        hb,
        x="borough",
        y="records",
        title="Housing Records by Borough",
        labels={"borough": "Borough", "records": "Housing records"},
    )
    style_figure(housing_borough_fig)

    # Taxi pickups by borough
    tb = (
        t.groupby("taxi_borough")["pickup_trips"]
        .sum()
        .reindex(BOROUGHS, fill_value=0)
        .rename("pickups")
        .rename_axis("borough")
        .reset_index()
    )

    taxi_borough_fig = px.bar(
        tb,
        x="borough",
        y="pickups",
        title="Yellow Taxi Pickups by Borough",
        labels={"borough": "Borough", "pickups": "Taxi pickups"},
    )
    style_figure(taxi_borough_fig)

    # Housing versus taxi pickups
    housing_relation = (
        h.groupby("borough")
        .agg(
            housing_units=("total_units", "sum"),
            housing_records=("project_id", "size"),
        )
        .reset_index()
    )

    taxi_relation = (
        t.groupby("taxi_borough")["pickup_trips"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "taxi_borough": "borough",
                "pickup_trips": "taxi_pickups",
            }
        )
    )

    relation = housing_relation.merge(
        taxi_relation, on="borough", how="outer"
    ).fillna(0)

    relation_fig = px.scatter(
        relation,
        x="housing_units",
        y="taxi_pickups",
        size="housing_records",
        color="borough",
        hover_name="borough",
        title="Housing Units vs Taxi Pickups by Borough",
        labels={
            "housing_units": "Housing units",
            "taxi_pickups": "Taxi pickups",
            "housing_records": "Housing records",
        },
    )
    style_figure(relation_fig)

    # Results table
    table_columns = [
        ("project_name", "Project"),
        ("borough", "Borough"),
        ("project_completion_date", "Completion Date"),
        (HOUSING_CATEGORY_COLUMN, "Construction Type"),
        ("total_units", "Total Units"),
        ("project_id", "Project ID"),
    ]

    columns = [
        {"name": label, "id": key}
        for key, label in table_columns
        if key in h.columns
    ]

    table = h[[col["id"] for col in columns]].head(100).copy()

    if "project_completion_date" in table.columns:
        table["project_completion_date"] = (
            table["project_completion_date"].dt.strftime("%Y-%m-%d")
        )

    table = (
        table.astype(object)
        .where(pd.notna(table), "")
        .to_dict("records")
    )

    # Dynamic story
    if not h.empty:
        top_housing = h["borough"].value_counts().index[0].title()
    else:
        top_housing = "No matching borough"

    if not t.empty:
        taxi_totals = t.groupby("taxi_borough")["pickup_trips"].sum()
        top_taxi = taxi_totals.idxmax().title()
        top_taxi_count = taxi_totals.max()
    else:
        top_taxi = "No matching borough"
        top_taxi_count = 0

    story = (
        f"With the selected filters, {top_housing} has the most "
        f"matching housing records. {top_taxi} has the most taxi "
        f"pickups ({top_taxi_count:,.0f}). These patterns describe "
        f"the selected data and do not establish causation."
    )

    return (
        status,
        cards,
        housing_fig,
        taxi_fig,
        housing_borough_fig,
        taxi_borough_fig,
        relation_fig,
        table,
        columns,
        story,
    )


# =====================================================
# 5. GENERATE COMBINED CSV REPORT
# =====================================================

@app.callback(
    Output("report-download", "data"),
    Input("report-button", "n_clicks"),
    State("borough-filter", "value"),
    State("year-filter", "value"),
    State("month-filter", "value"),
    State("housing-category-filter", "value"),
    State("taxi-category-filter", "value"),
    State("search-input", "value"),
    prevent_initial_call=True,
)
def download_report(
    clicks, borough, year, month,
    housing_category, taxi_category, search
):
    h, t = get_filtered_data(
        borough, year, month,
        housing_category, taxi_category, search
    )

    summary = pd.DataFrame({
        "Metric": [
            "Selected borough",
            "Selected year",
            "Selected month",
            "Housing category",
            "Transportation category",
            "Search query",
            "Housing records",
            "Unique projects",
            "Housing units",
            "Taxi pickups",
        ],
        "Value": [
            borough,
            year,
            month,
            housing_category,
            taxi_category,
            search or "None",
            len(h),
            h["project_id"].nunique(),
            pd.to_numeric(h["total_units"], errors="coerce").sum(),
            pd.to_numeric(t["pickup_trips"], errors="coerce").sum(),
        ],
    })

    housing_borough = (
        h.groupby("borough")
        .agg(
            housing_records=("project_id", "size"),
            housing_units=("total_units", "sum"),
        )
        .reset_index()
    )

    taxi_borough = (
        t.groupby("taxi_borough")["pickup_trips"]
        .sum()
        .reset_index()
        .rename(columns={
            "taxi_borough": "borough",
            "pickup_trips": "taxi_pickups",
        })
    )

    comparison = housing_borough.merge(
        taxi_borough,
        on="borough",
        how="outer",
    )

    # Keep the sections clearly labeled in one CSV file.
    report = StringIO()

    report.write("REPORT SUMMARY\n")
    summary.to_csv(report, index=False)

    report.write("\nHOUSING DETAILS\n")
    h.to_csv(report, index=False)

    report.write("\nTAXI DETAILS\n")
    t.to_csv(report, index=False)

    report.write("\nBOROUGH COMPARISON\n")
    comparison.to_csv(report, index=False)

    return dcc.send_string(
        report.getvalue(),
        "nyc_housing_taxi_report_2024.csv",
    )


# =====================================================
# 6. START WEBSITE
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
