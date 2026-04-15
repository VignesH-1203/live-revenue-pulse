# Live Revenue Pulse

**Real-Time Sales Command Center** — a war-room-style dashboard that simulates live sales data, auto-refreshes every 30 seconds, and integrates weather data from the Open-Meteo API to show how weather conditions may affect sales in Indian cities.

## Features

- **Simulated Live Sales Engine** — generates 1-3 fake sales every 30 seconds with realistic products, prices, cities, and payment methods
- **War Room Dark Theme** — custom CSS dark command center aesthetic with styled metric cards, terminal-style live feed, and professional Plotly charts
- **Top-Level KPIs** — Total Revenue, Total Orders, Average Order Value, Orders in Last 5 Minutes, Top Selling City
- **Interactive Charts** — Revenue by City (bar), Revenue by Category (donut), Cumulative Orders over Time (line), Revenue Trend (area)
- **Live Sales Feed** — scrolling table of the last 20 transactions in reverse chronological order
- **Weather Integration** — fetches real-time weather for 6 Indian cities via Open-Meteo API, flags rain, storms, and extreme heat with alert banners
- **City Weather + Sales Summary** — at-a-glance table combining weather conditions and sales performance per city
- **Sidebar Filters** — filter by City, Category, and Payment Method (filters apply to charts and feed, not KPIs)
- **Auto-Refresh** — no manual clicks needed; the dashboard updates itself every 30 seconds

## Tech Stack

- **Python**
- **Streamlit** — web app framework
- **Plotly** — interactive dark-themed charts
- **Pandas** — data manipulation
- **Requests** — Open-Meteo API calls
- **Open-Meteo API** — free weather data, no API key required

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the dashboard:

   ```bash
   py -m streamlit run app.py
   ```

   Or on macOS/Linux:

   ```bash
   streamlit run app.py
   ```

3. Open the URL shown in the terminal (usually `http://localhost:8501`)

## Screenshots

*Screenshots placeholder — run the app to see the live dashboard.*

## Note

This is a **simulated dashboard** built for learning and demonstration purposes. All sales data is randomly generated in-memory. Weather data is real, fetched from the free Open-Meteo API. No database or API keys are required.
