from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
from data_utils import load_dataset
from adaptation import recommend_views, choose_layout, log_interaction

st.set_page_config(page_title="Adaptive Healthcare Analytics", page_icon="🏥", layout="wide")

if "interaction_history" not in st.session_state:
    st.session_state.interaction_history = []
if "last_logged_view" not in st.session_state:
    st.session_state.last_logged_view = None

st.title("🏥 Adaptive Healthcare Analytics")
st.caption("An explainable, role-aware dashboard using CMS Timely and Effective Care measures")

with st.sidebar:
    st.header("Personalize your workspace")
    role = st.radio("Primary role", ["Hospital Administrator", "Healthcare Data Analyst"], index=0)
    large_text = st.toggle("Larger text", value=False)
    high_contrast = st.toggle("High-contrast mode", value=False)
    simplified = st.toggle("Simplified layout", value=False)
    st.caption("Preferences are applied in this session. No user profile is sent to an external service.")

css = ""
if large_text:
    css += "html, body, [class*='css'] { font-size: 1.12rem !important; }"
if high_contrast:
    css += """
    .stApp { background: #ffffff; color: #111111; }
    [data-testid="stMetric"] { border: 2px solid #111111; padding: 0.6rem; }
    """
if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.divider()
    uploaded = st.file_uploader("Optional: upload CMS CSV", type=["csv"])
    local_path = str(Path(__file__).resolve().parent / "data" / "cms_hospital_raw.csv")
    if uploaded is not None:
        try:
            raw_df = pd.read_csv(uploaded, low_memory=False)
            from data_utils import clean_cms_data
            df = clean_cms_data(raw_df)
            data_source = f"Uploaded CSV: {uploaded.name}"
        except Exception as e:
            st.error(f"Could not read uploaded CSV: {e}")
            df, data_source = load_dataset()
    else:
        df, data_source = load_dataset(local_path)

st.info(f"**Data source:** {data_source}. Demo data, if used, is synthetic and must not be interpreted as real hospital performance.")

if df.empty:
    st.error("No rows are available. Upload a CMS CSV to continue.")
    st.stop()

states = sorted([x for x in df["state"].dropna().unique().tolist() if x])
conditions = sorted([x for x in df["condition"].dropna().unique().tolist() if x])
with st.sidebar:
    selected_states = st.multiselect("State filter", states, default=states[:min(3, len(states))])
    selected_conditions = st.multiselect("Measure category", conditions, default=conditions)

filtered = df.copy()
if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]
if selected_conditions:
    filtered = filtered[filtered["condition"].isin(selected_conditions)]

valid_scores = filtered[filtered["score_numeric"].notna()].copy()
hospital_count = filtered.loc[filtered["facility_id"].astype(str).str.len() > 0, "facility_id"].nunique()
measure_count = filtered["measure_id"].nunique()
score_count = int(filtered["score_numeric"].notna().sum())

layout = choose_layout(role, simplified)
k1, k2, k3 = st.columns(3)
k1.metric("Hospitals represented", f"{hospital_count:,}")
k2.metric("Distinct measures", f"{measure_count:,}")
k3.metric("Numeric scores", f"{score_count:,}")

# Adapt available views and default selection to the current user profile.
available_views = ["KPI summary", "Hospital comparison", "State overview", "Measure trends", "Detailed data table", "Measure distribution"]
if simplified:
    # In simplified mode, remove the densest view to reduce interface complexity.
    available_views = [v for v in available_views if v != "Detailed data table"]

initial_recommendations = recommend_views(role, st.session_state.interaction_history, limit=3)
default_view = initial_recommendations[0] if initial_recommendations and initial_recommendations[0] in available_views else available_views[0]
view = st.selectbox("Explore a view", available_views, index=available_views.index(default_view), key=f"view_selector_{role}_{simplified}")
if view != st.session_state.last_logged_view:
    st.session_state.interaction_history = log_interaction(st.session_state.interaction_history, view)
    st.session_state.last_logged_view = view

# Recompute after logging the current selection so recommendations respond on this run.
recommendations = recommend_views(role, st.session_state.interaction_history, limit=3)
st.subheader("Your adaptive workspace")
st.write(f"**Selected role:** {role}")
st.write("**Recommended views:** " + " · ".join(recommendations))
if st.session_state.interaction_history:
    st.caption("Recommendations combine the current role, text similarity between view descriptions, and views selected during this session.")
else:
    st.caption("Recommendations start with role-specific defaults and update as you explore the dashboard.")

if view == "KPI summary":
    st.markdown("#### KPI summary")
    st.write("Use the filters to scope the quality measures included in the summary.")
    st.dataframe(filtered[["facility_name","state","condition","measure_name","score_raw"]].head(25), use_container_width=True)
elif view == "Hospital comparison":
    st.markdown("#### Hospital comparison")
    if valid_scores.empty:
        st.warning("No numeric scores are available for the selected filters.")
    else:
        measure_options = sorted(valid_scores["measure_name"].dropna().unique().tolist())
        chosen_measure = st.selectbox("Measure to compare", measure_options)
        comp = valid_scores[valid_scores["measure_name"] == chosen_measure].groupby(
            ["facility_name","state"], dropna=False
        )["score_numeric"].mean().reset_index().sort_values("score_numeric", ascending=False).head(20)
        fig = px.bar(comp, x="facility_name", y="score_numeric", color="state", title=f"Numeric scores: {chosen_measure}")
        fig.update_layout(xaxis_title="Hospital", yaxis_title="Published numeric score", xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Scores may have different units and directions across measures. Compare hospitals only within the same measure and check CMS footnotes.")
elif view == "State overview":
    st.markdown("#### State overview")
    if valid_scores.empty:
        st.warning("No numeric scores are available for the selected filters.")
    else:
        state_summary = valid_scores.groupby("state", dropna=False).agg(
            numeric_records=("score_numeric","count"),
            mean_published_score=("score_numeric","mean"),
            hospitals=("facility_id","nunique")
        ).reset_index()
        st.dataframe(state_summary, use_container_width=True)
        st.plotly_chart(px.bar(state_summary, x="state", y="numeric_records", title="Numeric records by state"), use_container_width=True)
elif view == "Measure trends":
    st.markdown("#### Measure trends")
    if "start_date" in filtered.columns:
        trend = filtered.copy()
        trend["start_date"] = pd.to_datetime(trend["start_date"], errors="coerce")
        trend = trend.dropna(subset=["start_date","score_numeric"])
        if trend.empty:
            st.warning("The selected data does not contain numeric scores with usable start dates.")
        else:
            trend = trend.groupby([pd.Grouper(key="start_date", freq="YS"),"measure_name"])["score_numeric"].mean().reset_index()
            st.plotly_chart(px.line(trend, x="start_date", y="score_numeric", color="measure_name", title="Average published numeric score over reporting periods"), use_container_width=True)
    else:
        st.warning("Start-date data is not available.")
elif view == "Detailed data table":
    st.markdown("#### Detailed data table")
    cols = [c for c in ["facility_id","facility_name","city","state","condition","measure_id","measure_name","score_raw","sample","footnote"] if c in filtered.columns]
    st.dataframe(filtered[cols], use_container_width=True, hide_index=True)
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"), "filtered_healthcare_measures.csv", "text/csv")
elif view == "Measure distribution":
    st.markdown("#### Measure distribution")
    if valid_scores.empty:
        st.warning("No numeric scores are available for the selected filters.")
    else:
        fig = px.histogram(valid_scores, x="score_numeric", color="condition", nbins=25, title="Distribution of numeric published scores")
        st.plotly_chart(fig, use_container_width=True)

with st.expander("How the adaptation works"):
    st.markdown("""
    - **Role adaptation:** the selected role changes the default recommended views.
    - **Interaction adaptation:** selected views are recorded in bounded session history and influence recommendations.
    - **Accessibility adaptation:** larger text and high contrast are user-controlled; simplified mode removes the detailed-table view to reduce information density.
    - **Transparency and control:** the app displays recommendations and lets users choose any available view manually.
    - **Privacy:** interaction labels stay in Streamlit session state; this demo does not send them to an external AI service or persist them after the session.

    The recommendation component uses a lightweight content-based model built with TF-IDF and cosine similarity, combined with role defaults and session interaction frequency. It is not a generative AI system or a clinically validated model.
    """)

st.caption("Educational prototype. Not a clinical decision-support system. CMS scores may be categorical, unavailable, or measured in different units; avoid comparing unlike measures.")
