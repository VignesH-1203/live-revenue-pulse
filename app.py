import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import random
import time
from datetime import datetime, timedelta, timezone

# ──────────────────────────────────────────────
# Timezone — IST (UTC+5:30)
# ──────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Live Revenue Pulse",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS — War Room Dark Theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Main dark background */
    .stApp {
        background-color: #0a0e17;
        color: #e0e0e0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1a2332;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e0e6ed !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1e2d3d;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 0 15px rgba(0, 255, 170, 0.04);
    }
    div[data-testid="stMetric"] label {
        color: #8899aa !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00ffaa !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Dataframe / table styling */
    .stDataFrame {
        border: 1px solid #1e2d3d;
        border-radius: 8px;
    }
    .stDataFrame table {
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.82rem;
    }

    /* Alert banners */
    .weather-alert {
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .alert-rain {
        background-color: #0c2d48;
        border-left: 4px solid #3b82f6;
        color: #93c5fd;
    }
    .alert-heat {
        background-color: #431407;
        border-left: 4px solid #f59e0b;
        color: #fcd34d;
    }
    .alert-storm {
        background-color: #1e1b4b;
        border-left: 4px solid #8b5cf6;
        color: #c4b5fd;
    }

    /* Weather card */
    .weather-card {
        background-color: #111827;
        border: 1px solid #1e2d3d;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        margin-bottom: 8px;
    }
    .weather-card .city-name {
        font-size: 1rem;
        font-weight: 600;
        color: #e0e6ed;
        margin-bottom: 4px;
    }
    .weather-card .temp {
        font-size: 1.6rem;
        font-weight: 700;
        color: #00ffaa;
    }
    .weather-card .condition {
        font-size: 0.85rem;
        color: #8899aa;
    }

    /* Section dividers */
    hr {
        border-color: #1e2d3d;
    }

    /* Plotly chart container */
    .stPlotlyChart {
        background-color: #111827;
        border: 1px solid #1e2d3d;
        border-radius: 10px;
        padding: 4px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0e17;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e2d3d;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Product Catalog
# ──────────────────────────────────────────────
PRODUCT_CATALOG = [
    {"product": "iPhone 15",        "category": "Electronics",      "base_price": 79900},
    {"product": "Samsung Galaxy S24","category": "Electronics",     "base_price": 69999},
    {"product": "Sony WH-1000XM5",  "category": "Electronics",      "base_price": 29990},
    {"product": "Levi's Denim Jacket","category": "Clothing",       "base_price": 4499},
    {"product": "Nike Air Max",     "category": "Clothing",          "base_price": 8995},
    {"product": "Organic Green Tea","category": "Food & Beverage",   "base_price": 450},
    {"product": "Protein Bar Pack", "category": "Food & Beverage",   "base_price": 899},
    {"product": "Cold Brew Coffee", "category": "Food & Beverage",   "base_price": 299},
    {"product": "Dyson V15 Vacuum", "category": "Home & Kitchen",    "base_price": 52900},
    {"product": "Instant Pot Duo",  "category": "Home & Kitchen",    "base_price": 8999},
]

CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata"]

CITY_COORDS = {
    "Mumbai":    {"lat": 19.0760, "lon": 72.8777},
    "Delhi":     {"lat": 28.6139, "lon": 77.2090},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai":   {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Kolkata":   {"lat": 22.5726, "lon": 88.3639},
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery"]

CHART_COLORS = ["#00ffaa", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899",
                "#14b8a6", "#f97316", "#06b6d4", "#a3e635"]


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def generate_sale(order_num, ts=None):
    """Generate a single sale record."""
    item = random.choice(PRODUCT_CATALOG)
    variation = random.uniform(0.85, 1.15)
    price = round(item["base_price"] * variation, 2)
    qty = random.randint(1, 3)
    return {
        "Timestamp": ts or datetime.now(IST),
        "OrderID": f"ORD-{order_num:04d}",
        "Product": item["product"],
        "Category": item["category"],
        "Price": price,
        "Quantity": qty,
        "Revenue": round(price * qty, 2),
        "City": random.choice(CITIES),
        "PaymentMethod": random.choice(PAYMENT_METHODS),
    }


def generate_seed_sales(count=18):
    """Generate initial seed sales spread over the last 15 minutes."""
    sales = []
    now = datetime.now(IST)
    for i in range(count):
        minutes_ago = random.uniform(1, 15)
        ts = now - timedelta(minutes=minutes_ago)
        sales.append(generate_sale(i + 1, ts))
    sales.sort(key=lambda s: s["Timestamp"])
    return sales


def classify_weather(code, temp):
    """Classify weather condition from WMO code and temperature."""
    if code in range(95, 100):
        return "Storm", "storm"
    rain_codes = set(range(51, 68)) | set(range(71, 78)) | set(range(80, 83)) | set(range(95, 100))
    if code in rain_codes:
        return "Rain", "rain"
    if temp > 40:
        return "Extreme Heat", "heat"
    return "Normal", "normal"


def weather_emoji(condition):
    emojis = {"Rain": "\U0001f327\ufe0f", "Storm": "\u26c8\ufe0f",
              "Extreme Heat": "\U0001f525", "Normal": "\u2600\ufe0f"}
    return emojis.get(condition, "\u2600\ufe0f")


def fetch_weather_data():
    """Fetch current weather for all cities from Open-Meteo. Cached for 5 minutes."""
    now = time.time()
    if "weather_data" in st.session_state and "weather_ts" in st.session_state:
        if now - st.session_state.weather_ts < 300:
            return st.session_state.weather_data

    weather = {}
    for city, coords in CITY_COORDS.items():
        try:
            resp = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "current_weather": "true",
                },
                timeout=5,
            )
            data = resp.json().get("current_weather", {})
            temp = data.get("temperature", 0)
            wind = data.get("windspeed", 0)
            code = data.get("weathercode", 0)
            condition, ctype = classify_weather(code, temp)
            weather[city] = {
                "temp": temp,
                "windspeed": wind,
                "code": code,
                "condition": condition,
                "type": ctype,
                "emoji": weather_emoji(condition),
            }
        except Exception:
            weather[city] = {
                "temp": None,
                "windspeed": None,
                "code": None,
                "condition": "Unavailable",
                "type": "normal",
                "emoji": "\u2753",
            }

    st.session_state.weather_data = weather
    st.session_state.weather_ts = now
    return weather


def format_inr(val):
    """Format number in Indian Rupee style (lakhs/crores)."""
    if val >= 10_000_000:
        return f"\u20b9{val / 10_000_000:.2f} Cr"
    if val >= 100_000:
        return f"\u20b9{val / 100_000:.2f} L"
    return f"\u20b9{val:,.0f}"


# ──────────────────────────────────────────────
# Initialize Session State
# ──────────────────────────────────────────────
if "sales" not in st.session_state:
    st.session_state.sales = generate_seed_sales()
    st.session_state.next_order = len(st.session_state.sales) + 1

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## \U0001f3af Live Revenue Pulse")
    st.caption("Real-Time Sales Command Center")
    st.markdown("---")

    if st.button("\U0001f504 Reset Dashboard", use_container_width=True):
        st.session_state.sales = generate_seed_sales()
        st.session_state.next_order = len(st.session_state.sales) + 1
        if "weather_data" in st.session_state:
            del st.session_state.weather_data
        if "weather_ts" in st.session_state:
            del st.session_state.weather_ts
        st.rerun()

    st.markdown("### Filters")
    filter_cities = st.multiselect("City", CITIES, default=CITIES)
    all_categories = sorted(set(p["category"] for p in PRODUCT_CATALOG))
    filter_categories = st.multiselect("Category", all_categories, default=all_categories)
    filter_payment = st.multiselect("Payment Method", PAYMENT_METHODS, default=PAYMENT_METHODS)

    st.markdown("---")
    st.caption(f"Last Updated: {datetime.now(IST).strftime('%H:%M:%S')}")
    st.caption("Auto-refreshes every 30 seconds")

# ──────────────────────────────────────────────
# Main Dashboard — Auto-Refresh Loop
# ──────────────────────────────────────────────
placeholder = st.empty()

while True:
    # Generate 1-3 new sales each cycle
    new_count = random.randint(1, 3)
    for _ in range(new_count):
        sale = generate_sale(st.session_state.next_order)
        st.session_state.sales.append(sale)
        st.session_state.next_order += 1

    # Build DataFrames
    df_all = pd.DataFrame(st.session_state.sales)
    df_all["Timestamp"] = pd.to_datetime(df_all["Timestamp"])

    # Filtered DataFrame (for charts & feed)
    df_filtered = df_all[
        (df_all["City"].isin(filter_cities)) &
        (df_all["Category"].isin(filter_categories)) &
        (df_all["PaymentMethod"].isin(filter_payment))
    ]

    # Fetch weather
    weather = fetch_weather_data()

    with placeholder.container():
        # ──────────────── HEADER ────────────────
        st.markdown(
            "<h1 style='text-align:center; color:#00ffaa; margin-bottom:0;'>"
            "\U0001f3af LIVE REVENUE PULSE</h1>"
            "<p style='text-align:center; color:#5a6a7a; margin-top:0; font-size:0.95rem;'>"
            "Real-Time Sales Command Center &nbsp;|&nbsp; "
            f"<span style='color:#00ffaa;'>\u25cf</span> LIVE &mdash; {datetime.now(IST).strftime('%d %b %Y, %H:%M:%S')}"
            "</p>",
            unsafe_allow_html=True,
        )

        # ──────────────── KPI ROW ────────────────
        total_revenue = df_all["Revenue"].sum()
        total_orders = len(df_all)
        avg_order = total_revenue / total_orders if total_orders else 0
        five_min_ago = datetime.now(IST) - timedelta(minutes=5)
        recent_orders = len(df_all[df_all["Timestamp"] >= five_min_ago])
        top_city = df_all.groupby("City")["Revenue"].sum().idxmax() if total_orders else "—"

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("\U0001f7e2 Total Revenue", format_inr(total_revenue))
        k2.metric("\U0001f4e6 Total Orders", f"{total_orders}")
        k3.metric("\U0001f4c8 Avg Order Value", f"\u20b9{avg_order:,.0f}")
        k4.metric("\U0001f550 Orders (Last 5 min)", f"{recent_orders}")
        k5.metric("\U0001f525 Top City", top_city)

        st.markdown("---")

        # ──────────────── CHARTS ────────────────
        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown("##### Revenue by City")
            city_rev = df_filtered.groupby("City")["Revenue"].sum().sort_values()
            fig_city = px.bar(
                x=city_rev.values, y=city_rev.index,
                orientation="h",
                template="plotly_dark",
                color=city_rev.index,
                color_discrete_sequence=CHART_COLORS,
            )
            fig_city.update_layout(
                showlegend=False, xaxis_title="Revenue (\u20b9)", yaxis_title="",
                plot_bgcolor="#111827", paper_bgcolor="#111827",
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                xaxis=dict(gridcolor="#1e2d3d"),
            )
            st.plotly_chart(fig_city, use_container_width=True)

        with chart2:
            st.markdown("##### Revenue by Category")
            cat_rev = df_filtered.groupby("Category")["Revenue"].sum()
            fig_cat = px.pie(
                values=cat_rev.values, names=cat_rev.index,
                hole=0.45,
                template="plotly_dark",
                color_discrete_sequence=CHART_COLORS,
            )
            fig_cat.update_layout(
                plot_bgcolor="#111827", paper_bgcolor="#111827",
                margin=dict(l=10, r=10, t=10, b=30), height=300,
                legend=dict(font=dict(size=11)),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        chart3, chart4 = st.columns(2)

        with chart3:
            st.markdown("##### Cumulative Orders Over Time")
            df_time = df_filtered.sort_values("Timestamp").copy()
            df_time["CumulativeOrders"] = range(1, len(df_time) + 1)
            fig_orders = px.line(
                df_time, x="Timestamp", y="CumulativeOrders",
                template="plotly_dark",
            )
            fig_orders.update_traces(line_color="#3b82f6", line_width=2)
            fig_orders.update_layout(
                plot_bgcolor="#111827", paper_bgcolor="#111827",
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                xaxis=dict(gridcolor="#1e2d3d"), yaxis=dict(gridcolor="#1e2d3d"),
                xaxis_title="", yaxis_title="Orders",
            )
            st.plotly_chart(fig_orders, use_container_width=True)

        with chart4:
            st.markdown("##### Revenue Trend")
            df_rev_trend = df_filtered.sort_values("Timestamp").copy()
            df_rev_trend["CumulativeRevenue"] = df_rev_trend["Revenue"].cumsum()
            fig_rev = px.area(
                df_rev_trend, x="Timestamp", y="CumulativeRevenue",
                template="plotly_dark",
            )
            fig_rev.update_traces(line_color="#00ffaa", fillcolor="rgba(0,255,170,0.1)")
            fig_rev.update_layout(
                plot_bgcolor="#111827", paper_bgcolor="#111827",
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                xaxis=dict(gridcolor="#1e2d3d"), yaxis=dict(gridcolor="#1e2d3d"),
                xaxis_title="", yaxis_title="Revenue (\u20b9)",
            )
            st.plotly_chart(fig_rev, use_container_width=True)

        st.markdown("---")

        # ──────────────── WEATHER SECTION ────────────────
        st.markdown("### \U0001f30d Weather Impact Analysis")

        # Weather cards
        w_cols = st.columns(6)
        for i, city in enumerate(CITIES):
            w = weather.get(city, {})
            temp_str = f"{w['temp']}\u00b0C" if w.get("temp") is not None else "N/A"
            wind_str = f"{w['windspeed']} km/h" if w.get("windspeed") is not None else ""
            emoji = w.get("emoji", "\u2753")
            cond = w.get("condition", "N/A")
            with w_cols[i]:
                st.markdown(
                    f"<div class='weather-card'>"
                    f"<div class='city-name'>{city}</div>"
                    f"<div class='temp'>{temp_str}</div>"
                    f"<div class='condition'>{emoji} {cond}</div>"
                    f"<div class='condition'>Wind: {wind_str}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Weather alerts
        alerts_shown = False
        for city in CITIES:
            w = weather.get(city, {})
            wtype = w.get("type", "normal")
            if wtype == "rain":
                st.markdown(
                    f"<div class='weather-alert alert-rain'>"
                    f"\u26a0\ufe0f \U0001f327\ufe0f Rain detected in <b>{city}</b> "
                    f"— may impact delivery times</div>",
                    unsafe_allow_html=True,
                )
                alerts_shown = True
            elif wtype == "heat":
                st.markdown(
                    f"<div class='weather-alert alert-heat'>"
                    f"\U0001f525 Extreme heat in <b>{city}</b> ({w['temp']}\u00b0C) "
                    f"— expect higher beverage sales</div>",
                    unsafe_allow_html=True,
                )
                alerts_shown = True
            elif wtype == "storm":
                st.markdown(
                    f"<div class='weather-alert alert-storm'>"
                    f"\u26c8\ufe0f Storm warning in <b>{city}</b> "
                    f"— potential logistics disruption</div>",
                    unsafe_allow_html=True,
                )
                alerts_shown = True

        if not alerts_shown:
            st.markdown(
                "<div class='weather-alert' style='background:#0d1f0d; border-left:4px solid #00ffaa; color:#86efac;'>"
                "\u2705 All cities reporting normal weather conditions</div>",
                unsafe_allow_html=True,
            )

        # City Weather + Sales summary table
        st.markdown("##### City Weather + Sales Summary")
        summary_rows = []
        for city in CITIES:
            w = weather.get(city, {})
            city_data = df_all[df_all["City"] == city]
            summary_rows.append({
                "City": city,
                "Weather": f"{w.get('emoji', '')} {w.get('condition', 'N/A')}",
                "Temp (\u00b0C)": w.get("temp", "N/A"),
                "Wind (km/h)": w.get("windspeed", "N/A"),
                "Orders": len(city_data),
                "Revenue (\u20b9)": f"{city_data['Revenue'].sum():,.0f}",
            })
        st.dataframe(
            pd.DataFrame(summary_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # ──────────────── LIVE SALES FEED ────────────────
        st.markdown("### \U0001f4e1 Live Sales Feed")

        feed_df = df_filtered.sort_values("Timestamp", ascending=False).head(20).copy()
        feed_df["Time"] = feed_df["Timestamp"].dt.strftime("%H:%M:%S")
        feed_df["Revenue (\u20b9)"] = feed_df["Revenue"].apply(lambda x: f"{x:,.0f}")
        feed_display = feed_df[["Time", "OrderID", "Product", "City", "Revenue (\u20b9)", "PaymentMethod"]]
        feed_display = feed_display.rename(columns={"PaymentMethod": "Payment"})

        st.dataframe(
            feed_display,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"Showing latest {len(feed_display)} transactions "
            f"| Next refresh in ~30 seconds "
            f"| Total records: {len(df_all)}"
        )

    # Wait 30 seconds, then loop
    time.sleep(30)
