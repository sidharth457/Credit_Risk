import streamlit as st
# Gemini integration
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="Credit Risk Applicant Dashboard", layout="wide")
model = pd.read_csv('modeling_view_with_risk.csv')

st.title("Credit Risk Applicant Dashboard")
st.write("""
Select an Applicant ID from the dropdown to view their risk profile, scorecard analysis, and key risk drivers. 
Visualizations and summary cards update automatically for each applicant.
""")

applicant_ids = model['Applicant_ID'].unique()
selected_id = st.selectbox("Select Applicant ID", sorted(applicant_ids))
row = model[model['Applicant_ID'] == selected_id]

if not row.empty:
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.metric("Risk Grade", row['Grade'].values[0])
        st.metric("Risk Score (PD_hat)", f"{row['PD_hat'].values[0]:.3f}")
        st.metric("Total Points", int(row['Total_Points'].values[0]))
    with col2:
        st.metric("DTI", f"{row['DTI'].values[0]:.2f}")
        st.metric("LTV", f"{row['LTV'].values[0]:.2f}")
        st.metric("Income Stability", row['Income_Stability'].values[0])
    with col3:
        st.metric("Utilization Bucket", row['Utilization_Bucket'].values[0])
        st.metric("Late Pay Bucket", row['Late_Pay_Bucket'].values[0])
        st.metric("Tenure Bucket", row['Tenure_Bucket'].values[0])

    st.subheader(f"Applicant Profile: {row['Full_Name'].values[0]}")
    st.markdown(f"**Age:** {row['Age'].values[0]} | **Gender:** {row['Gender'].values[0]} | **Education:** {row['Education_Level'].values[0]}")
    st.markdown(f"**Employment Status:** {row['Employment_Status'].values[0]} | **Net Monthly Income:** {row['Net_Monthly_Income'].values[0]} | **Total Monthly Obligations:** {row['Total_Monthly_Obligations'].values[0]}")
    st.markdown(f"**Risk Profile:** {row['Risk_Profile'].values[0]}")

    st.markdown("---")
    st.subheader("Risk Score and Grade Visualization")
    fig, ax = plt.subplots(1,2, figsize=(10,4))
    ax[0].bar(['Risk Score'], [row['PD_hat'].values[0]], color='orange')
    ax[0].set_ylim(0, 0.2)
    ax[0].set_ylabel('PD_hat')
    ax[0].set_title('Estimated Risk Score')
    ax[1].pie([1], labels=[row['Grade'].values[0]], colors=['lightblue'], autopct='%1.1f%%')
    ax[1].set_title('Risk Grade')
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("Key Risk Drivers (Scorecard Feature Points)")
    points_cols = ['Points_DTI','Points_Utilization','Points_LatePay','Points_Inquiry','Points_IncomeStability','Points_LTV','Points_Tenure']
    points = row[points_cols].iloc[0]
    fig2, ax2 = plt.subplots(figsize=(8,4))
    sns.barplot(x=points.index, y=points.values, palette='viridis', ax=ax2)
    ax2.set_title('Scorecard Feature Points')
    ax2.set_ylabel('Points (Higher = More Risk)')
    ax2.set_xticklabels(points.index, rotation=30)
    st.pyplot(fig2)

    # Explanation of risk drivers
    st.markdown("**Feature Explanation:**")
    st.markdown("""
    - **DTI (Debt-to-Income):** Higher DTI means more monthly obligations relative to income.
    - **LTV (Loan-to-Value):** Higher LTV means larger loan compared to collateral value.
    - **Utilization Bucket:** Higher utilization means more credit used.
    - **Late Pay Bucket:** More late payments increase risk.
    - **Income Stability:** Lower stability increases risk.
    - **Tenure Bucket:** Shorter tenure with bank increases risk.
    """)

    st.markdown("---")
    st.subheader("AI Agent: Explain & Advise (Gemini API)")
    user_question = st.text_area("Ask the agent about this applicant's risk profile, features, or suggestions:", "Why is this applicant's risk profile high?")
    if st.button("Get Explanation"):
        api_key = "AIzaSyBiVPBAb1rkbnIlutNlc7vQY4-dAdmQxko"
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": api_key
        }
        applicant_data = row.to_dict(orient='records')[0]
        prompt = (
    "You are a senior credit risk analyst. Analyze the following applicant's data, which includes features from 10 different data sources: "
    "demographics, employment/income, financial obligations, credit bureau, loan application details, collateral, banking relationship, external risk signals, regulatory compliance, and risk assessment scores.\n\n"
    "For each feature, provide:\n"
    "- A definition and its importance in credit risk assessment (industry context)\n"
    "- The applicant's value and how it compares to industry benchmarks or best practices\n"
    "- Why this value increases or decreases risk (with examples)\n"
    "- Actionable recommendations for improvement\n\n"
    "Structure your report as follows:\n"
    "1. Executive Summary: Overall risk profile and key findings\n"
    "2. Feature-by-Feature Analysis: For each feature, provide the above details\n"
    "3. Segment Analysis: Highlight any segment-specific risks (e.g., product, branch, source)\n"
    "4. Regulatory and Policy Flags: Note any compliance issues\n"
    "5. Recommendations: Practical steps for the applicant to improve their risk profile\n"
    "6. Conclusion: Final assessment and advice\n\n"
    "Applicant data:\n"
    f"{applicant_data}\n"
    "User question:\n"
    f"{user_question}\n"
    "Please provide a detailed, professional report suitable for a credit risk committee review."
)
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.ok:
                result = response.json()
                explanation = result['candidates'][0]['content']['parts'][0]['text']
                st.info(explanation)
            else:
                st.error(f"Gemini API error: {response.text}")
        except Exception as e:
            st.error(f"Gemini API error: {e}")
else:
    st.warning("Applicant not found.")
