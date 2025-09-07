import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the modeling view
model = pd.read_csv('modeling_view_with_risk.csv')

# Function to show applicant profile and visualize
def show_applicant_profile(applicant_id):
    row = model[model['Applicant_ID'] == applicant_id]
    if row.empty:
        print(f"Applicant_ID {applicant_id} not found.")
        return
    # Print profile summary
    print("\n--- Applicant Profile ---")
    print(row[['Applicant_ID','Application_ID','Full_Name','Age','Gender','Education_Level','Employment_Status',
              'Net_Monthly_Income','Total_Monthly_Obligations','DTI','LTV','Utilization_Bucket','Late_Pay_Bucket',
              'Income_Stability','Tenure_Bucket','Avg_Balance_Bucket','PD_hat','Grade','Risk_Profile']].to_string(index=False))
    # Visualize risk score and grade
    fig, ax = plt.subplots(1,2, figsize=(10,4))
    # Risk score bar
    ax[0].bar(['Risk Score'], [row['PD_hat'].values[0]], color='orange')
    ax[0].set_ylim(0, 0.2)
    ax[0].set_ylabel('PD_hat')
    ax[0].set_title('Estimated Risk Score')
    # Grade pie
    ax[1].pie([1], labels=[row['Grade'].values[0]], colors=['lightblue'], autopct='%1.1f%%')
    ax[1].set_title('Risk Grade')
    plt.tight_layout()
    plt.show()
    # Feature importance (points breakdown)
    points_cols = ['Points_DTI','Points_Utilization','Points_LatePay','Points_Inquiry','Points_IncomeStability','Points_LTV','Points_Tenure']
    points = row[points_cols].iloc[0]
    plt.figure(figsize=(8,4))
    sns.barplot(x=points.index, y=points.values, palette='viridis')
    plt.title('Scorecard Feature Points')
    plt.ylabel('Points')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

# Example usage:
# show_applicant_profile(1001)

if __name__ == "__main__":
    try:
        applicant_id = int(input("Enter Applicant_ID to analyze: "))
        show_applicant_profile(applicant_id)
    except Exception as e:
        print("Error:", e)
