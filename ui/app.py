import streamlit as st
import requests
import pandas as pd

API_URL = "http://api:8000" # fast api backend


st.set_page_config(page_title="💰 FinOps Copilot", layout="wide")
st.title("💰 FinOps Copilot")

# --------------------
# Helper function to call API
# --------------------
def call_api(endpoint: str, method="GET", payload=None, params=None):
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", params=params)
        else:
            response = requests.post(f"{API_URL}{endpoint}", json=payload)

        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            return result["data"]
        else:
            st.error(result.get("error", "Unknown API error"))
            return None
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

# --------------------
# Layout
# --------------------
tab1, tab2, tab3 = st.tabs(["📊 KPIs", "❓ Ask a Question", "💡 Recommendations"])

# --------------------
# KPIs
# --------------------
with tab1:
    st.subheader("Key Performance Indicators")

    data = call_api("/kpis")
    if data:
        st.write("📈 Six-Month Trend")
        st.dataframe(pd.DataFrame(data["six_month_trend"]))

        st.write("🔥 Top 5 Cost Drivers")
        st.dataframe(pd.DataFrame(data["top_5_cost_drivers"]))

        st.write("🛠 Monthly Cost by Service")
        st.dataframe(pd.DataFrame(data["monthly_cost_by_service"]))

# --------------------
# Ask a Question
# --------------------
with tab2:
    st.subheader("Ask FinOps Copilot")
    question = st.text_input("Enter your question")

    if st.button("Ask"):
        if question.strip():
            data = call_api("/ask", method="POST", payload={"question": question})
            if data:
                st.success(data["answer"])
                with st.expander("📚 Sources"):
                    for src in data["sources"]:
                        st.markdown(f"- {src}")
        else:
            st.warning("Please enter a question.")

# --------------------
# Recommendations
# --------------------
with tab3:
    st.subheader("FinOps Recommendations")

    month = st.text_input("Enter Month (YYYY-MM)", value="2025-09")
    if st.button("Get Recommendations"):
        data = call_api("/recommendations", params={"month": month})
        if data:
            st.write(f"📌 {data['recommendation_type']}")
            st.dataframe(pd.DataFrame(data["details"]))
