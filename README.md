# NYC Affordable Housing & Yellow Taxi Activity Dashboard

## Project Overview
This project explores the relationship between affordable housing production and yellow taxi pickup activity across New York City boroughs during 2024.

The interactive dashboard allows users to filter the datasets, explore visualizations, search for specific information, and generate a report.

## Research Question
How does affordable housing production in NYC compare with yellow taxi pickup activity across boroughs and throughout 2024?

## Datasets
- **Affordable Housing Production by Building:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Housing-New-York-Units-by-Building/hg8x-zxpr)
- **2024 Yellow Taxi Trip Data:** [NYC Open Data](https://data.cityofnewyork.us/Transportation/2024-Yellow-Taxi-Trip-Data/rwwi-khbc)

## Technologies
- Python
- Pandas
- Plotly
- Dash

## Dashboard Features
- Interactive filters for borough, year, housing category, taxi pickup zone, and month.
- Search functionality to narrow the results.
- A Generate Report button for exporting filtered results.
- Interactive charts showing monthly and borough-level patterns.
- A scatter plot comparing housing units with taxi pickup activity.
- A storytelling section explaining findings, limitations, and the potential benefit to NYC.

## Project Structure
```text
nyc-housing-taxi-dashboard/
├── app.py
├── requirements.txt
├── README.md
└── data/
    ├── housing_clean.csv
    └── taxi_clean.csv
```

## Setup Instructions
1. Install Python.
2. Download or clone this repository.
3. Install the required packages:
   `pip install -r requirements.txt`
4. Run the dashboard:
   `python app.py`
5. Open `http://127.0.0.1:8050/` in your browser.

## Deployment
The dashboard is intended to be deployed as a web service using Render.

## Team Contributions
Add each team member's actual contribution before submission:
## Website Development Contributions


| Farida Nada — 16007220 | Dashboard planning, research question presentation, and housing visualization integration |
| Menna Kassem — 16002792 | Taxi data visualization and monthly activity charts |
| Mariam Farahat — 16001862 | Summary cards, dashboard findings, and limitations section |
| Adham Sameh — 16002948 | Dash application structure, layout design, and website implementation |
| Habiba Salah — 16001573 | Interactive filters, search functionality, and Generate Report feature |
| Abdulrahman Ahmed — 16006387 | README documentation, deployment configuration, and final testing |

All team members contributed to reviewing the dashboard and checking that the website presents the project's findings clearly.

## Limitations
Housing production and taxi pickup activity represent different types of data. A comparison between them does not establish that housing production causes changes in taxi activity. Taxi pickups are aggregated by month and pickup zone, and some records may not be mapped to a borough.
