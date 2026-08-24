import pandas as pd
import streamlit as st
import plotly.express as px
from analyzer import load_reviews, add_sentiment_column, get_top_words

st.set_page_config(page_title="Review Sentiment Analyzer", layout="wide")

# --- Header / styling ---
st.title("📊 Customer Review Sentiment Analyzer")
st.caption("Built for small business owners — no technical knowledge needed")

with st.expander("ℹ️ How this works", expanded=False):
    st.write("""
    Upload a CSV of your customer reviews (from Google, Yelp, or anywhere else).
    Each review is automatically scored as **Positive**, **Negative**, or **Neutral**
    using sentiment analysis. You'll see an overall breakdown, how sentiment has
    changed over time, and the words that come up most in praise and complaints —
    so you know exactly what's working and what needs fixing.
    """)

uploaded_file = st.file_uploader("Upload reviews CSV", type=["csv"])

if uploaded_file:
    df = load_reviews(uploaded_file)
    df = add_sentiment_column(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # --- Sidebar filters ---
    st.sidebar.header("🔧 Filters")

    min_stars, max_stars = int(df["stars"].min()), int(df["stars"].max())
    star_range = st.sidebar.slider(
        "Star rating range", min_stars, max_stars, (min_stars, max_stars)
    )

    valid_dates = df["date"].dropna()
    if not valid_dates.empty:
        min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
        date_range = st.sidebar.date_input(
            "Date range", (min_date, max_date), min_value=min_date, max_value=max_date
        )
    else:
        date_range = None

    # Apply filters
    filtered_df = df[(df["stars"] >= star_range[0]) & (df["stars"] <= star_range[1])]
    if date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df["date"] >= start) & (filtered_df["date"] <= end)]

    st.sidebar.write(f"Showing **{len(filtered_df)}** of {len(df)} reviews")

    # --- Metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(filtered_df))
    col2.metric("Positive %", f"{(filtered_df['sentiment']=='Positive').mean()*100:.1f}%")
    col3.metric("Negative %", f"{(filtered_df['sentiment']=='Negative').mean()*100:.1f}%")

    # --- Pie chart ---
    fig = px.pie(filtered_df, names="sentiment", title="Overall Sentiment Breakdown",
                 color="sentiment",
                 color_discrete_map={"Positive": "#2ecc71", "Negative": "#e74c3c", "Neutral": "#95a5a6"})
    st.plotly_chart(fig, use_container_width=True)

    # --- Trend over time ---
    if "date" in filtered_df.columns:
        trend = filtered_df.groupby([filtered_df["date"].dt.to_period("M"), "sentiment"]).size().reset_index(name="count")
        trend["date"] = trend["date"].astype(str)
        fig2 = px.line(trend, x="date", y="count", color="sentiment", title="Sentiment Trend Over Time")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Top words ---
    st.subheader("🔍 What customers complain about most")
    st.write(get_top_words(filtered_df, "Negative"))

    st.subheader("💚 What customers praise most")
    st.write(get_top_words(filtered_df, "Positive"))

    # --- Raw table ---
    st.subheader("Raw Reviews")
    st.dataframe(filtered_df[["text", "stars", "sentiment", "sentiment_score"]])

    # --- Download button ---
    csv_data = filtered_df[["text", "stars", "date", "sentiment", "sentiment_score"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Report (CSV)",
        data=csv_data,
        file_name="sentiment_report.csv",
        mime="text/csv",
    )

else:
    st.info("Upload a CSV to get started.")