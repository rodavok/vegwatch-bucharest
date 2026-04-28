import json
from pathlib import Path
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

DATA_FILE = Path(__file__).parent.parent / "data" / "bucharest_vegetarian_analysis.json"

st.set_page_config(page_title="Bucharest VegWatch", layout="wide")

@st.cache_data
def load_data():
    data = json.loads(DATA_FILE.read_text())
    return pd.DataFrame(data)

df = load_data()

st.title("Bucharest VegWatch")
st.markdown("Analyzing vegetarian option mentions across Bucharest restaurants")

# Sidebar filters
st.sidebar.header("Filters")
neighborhoods = ["All"] + sorted(df["neighborhood"].unique().tolist())
selected_neighborhood = st.sidebar.selectbox("Neighborhood", neighborhoods)

status_filter = st.sidebar.multiselect(
    "Vegetarian Status",
    options=df["vegetarian_status"].unique().tolist(),
    default=df["vegetarian_status"].unique().tolist()
)

# Filter data
filtered_df = df[df["vegetarian_status"].isin(status_filter)]
if selected_neighborhood != "All":
    filtered_df = filtered_df[filtered_df["neighborhood"] == selected_neighborhood]

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

has_options = len(df[df["vegetarian_status"] == "has_options"])
no_mention = len(df[df["vegetarian_status"] == "no_mention"])
mentioned_unclear = len(df[df["vegetarian_status"] == "mentioned_unclear"])

col1.metric("Total Restaurants", len(df))
col2.metric("Has Vegetarian Options", has_options)
col3.metric("No Mention", no_mention)
col4.metric("Vegetarian %", f"{has_options/len(df)*100:.1f}%")

st.divider()

# Two columns: map and chart
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Restaurant Map")

    # Create map centered on Bucharest
    m = folium.Map(location=[44.4268, 26.1025], zoom_start=12)

    # Color mapping
    color_map = {
        "has_options": "green",
        "mentioned_unclear": "orange",
        "no_mention": "gray",
        "no_options": "red"
    }

    for _, row in filtered_df.iterrows():
        if pd.notna(row["lat"]) and pd.notna(row["lng"]):
            color = color_map.get(row["vegetarian_status"], "gray")

            popup_html = f"""
            <b>{row['name']}</b><br>
            Rating: {row['rating']}⭐ ({row['total_reviews']} reviews)<br>
            Neighborhood: {row['neighborhood']}<br>
            Vegetarian: {row['vegetarian_status'].replace('_', ' ').title()}
            """

            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=8,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

    st_folium(m, width=700, height=500)

    st.markdown("""
    **Legend:**
    Green = Has vegetarian options |
    Orange = Mentioned (unclear) |
    Gray = No mention
    """)

with right_col:
    st.subheader("By Neighborhood")

    # Neighborhood breakdown
    neighborhood_stats = df.groupby("neighborhood").agg({
        "vegetarian_status": lambda x: (x == "has_options").sum(),
        "name": "count"
    }).rename(columns={"vegetarian_status": "vegetarian_friendly", "name": "total"})

    neighborhood_stats["percentage"] = (
        neighborhood_stats["vegetarian_friendly"] / neighborhood_stats["total"] * 100
    ).round(1)

    neighborhood_stats = neighborhood_stats.sort_values("percentage", ascending=False)

    st.dataframe(
        neighborhood_stats.reset_index().rename(columns={
            "neighborhood": "Neighborhood",
            "vegetarian_friendly": "Veg-Friendly",
            "total": "Total",
            "percentage": "% Veg"
        }),
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Top Vegetarian-Friendly")

    veg_restaurants = df[df["vegetarian_status"] == "has_options"][
        ["name", "neighborhood", "rating"]
    ].sort_values("rating", ascending=False).head(10)

    st.dataframe(
        veg_restaurants.rename(columns={
            "name": "Restaurant",
            "neighborhood": "Area",
            "rating": "Rating"
        }),
        hide_index=True,
        use_container_width=True
    )

st.divider()

# Restaurant details table
st.subheader("All Restaurants")

display_df = filtered_df[["name", "neighborhood", "rating", "total_reviews", "vegetarian_status", "address"]].copy()
display_df["vegetarian_status"] = display_df["vegetarian_status"].str.replace("_", " ").str.title()

st.dataframe(
    display_df.rename(columns={
        "name": "Restaurant",
        "neighborhood": "Neighborhood",
        "rating": "Rating",
        "total_reviews": "Reviews",
        "vegetarian_status": "Veg Status",
        "address": "Address"
    }),
    hide_index=True,
    use_container_width=True
)
