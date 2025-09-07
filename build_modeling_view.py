import pandas as pd
import numpy as np
import os

# Load all CSVs
base = 'excel_sheets_csv'
files = {
    'banking': 'Banking_Relationship.csv',
    'collateral': 'Collateral_Security.csv',
    'bureau': 'Credit_Bureau_Data.csv',
    'employment': 'Employment_Income.csv',
    'external': 'External_Data_Sources.csv',
    'obligations': 'Financial_Obligations.csv',
    'loan': 'Loan_Application_Details.csv',
    'demographics': 'Personal_Demographics.csv',
    'regulatory': 'Regulatory_Compliance.csv',
    'risk': 'Risk_Assessment_Scores.csv',
}

df = {}
for k, v in files.items():
    df[k] = pd.read_csv(os.path.join(base, v))

# Merge all sheets into one modeling view
model = df['loan']
model = model.merge(df['demographics'], on='Applicant_ID', how='left')
model = model.merge(df['employment'], on='Applicant_ID', how='left')
model = model.merge(df['obligations'], on='Applicant_ID', how='left')
model = model.merge(df['bureau'], on='Applicant_ID', how='left')
model = model.merge(df['collateral'], on='Application_ID', how='left')
model = model.merge(df['banking'], on='Applicant_ID', how='left')
model = model.merge(df['external'], on='Applicant_ID', how='left')
model = model.merge(df['regulatory'], on='Application_ID', how='left')
model = model.merge(df['risk'], on=['Application_ID','Applicant_ID'], how='left')

# PHASE 1: Create Default_12m (synthetic, using Probability_of_Default)
np.random.seed(42)
model['Default_12m'] = (np.random.rand(len(model)) < model['Probability_of_Default']).astype(int)

# PHASE 1: Time-based split
model['Period'] = np.where(
    pd.to_datetime(model['Application_Date']) <= pd.Timestamp('2023-06-30'), 'Train',
    np.where(pd.to_datetime(model['Application_Date']) <= pd.Timestamp('2023-12-31'), 'Validation', 'OOT')
)

# PHASE 2: Remove leakage columns
leakage_cols = [
    'Final_Decision','Internal_Risk_Score','Probability_of_Default','Loss_Given_Default',
    'Exposure_at_Default','Expected_Loss','Manual_Override_Flag','Decision_Date'
]
model = model.drop(columns=[c for c in leakage_cols if c in model.columns])

# PHASE 3: Feature engineering
# DTI
model['DTI'] = model['Total_Monthly_Obligations'] / model['Net_Monthly_Income']
model['DTI'] = model['DTI'].clip(upper=1.5)
# LTV
model['LTV'] = np.where(model['Collateral_Value']>0, model['Requested_Loan_Amount']/model['Collateral_Value'], 0)
model['LTV'] = model['LTV'].clip(upper=1.2)
# Utilization buckets
def util_bucket(u):
    if u < 0.1: return '0-10%'
    elif u < 0.3: return '10-30%'
    elif u < 0.5: return '30-50%'
    elif u < 0.8: return '50-80%'
    else: return '>80%'
model['Utilization_Bucket'] = model['Credit_Utilization_Ratio'].apply(util_bucket)
# Late pay bucket
def late_bucket(x):
    if x == 0: return '0'
    elif x == 1: return '1'
    elif x <= 3: return '2-3'
    else: return '>3'
model['Late_Pay_Bucket'] = model['Number_of_Late_Payments'].apply(late_bucket)
# Inquiry bucket
def inq_bucket(x):
    if x <= 1: return '0-1'
    elif x <= 3: return '2-3'
    elif x <= 6: return '4-6'
    else: return '>6'
model['Inq_Bucket'] = model['Credit_Inquiries_Last_12_Months'].apply(inq_bucket)
# Income stability
model['Income_Stability'] = np.where(model['Years_in_Current_Job']>=3, 'High',
    np.where(model['Years_in_Current_Job']>=1, 'Medium', 'Low'))
# Geolocation risk bucket
model['Geolocation_Risk_Bucket'] = pd.cut(model['Geolocation_Risk_Score'],
    bins=[-np.inf,0.2,0.4,0.6,0.8,np.inf],
    labels=['Very Low','Low','Medium','High','Very High'])
# Tenure with bank
model['Tenure_Months'] = ((pd.to_datetime(model['Application_Date']) - pd.to_datetime(model['Customer_Since'])).dt.days/30).clip(lower=0)
def tenure_bucket(x):
    if x < 6: return '<6'
    elif x < 12: return '6-12'
    elif x < 24: return '12-24'
    else: return '>24'
model['Tenure_Bucket'] = model['Tenure_Months'].apply(tenure_bucket)
# Average balance bucket
model['Avg_Balance_Bucket'] = pd.cut(model['Average_Monthly_Balance'],
    bins=[-np.inf,25000,75000,np.inf],
    labels=['Low','Medium','High'])

# Fill missing values
for col in model.select_dtypes(include='number').columns:
    model[col] = model[col].fillna(model[col].median())
for col in model.select_dtypes(include='object').columns:
    model[col] = model[col].fillna('Unknown')

# Save modeling view

# PHASE 4: Scorecard points assignment
base_score = 600
def points_dti(dti):
    if dti <= 0.25: return 0
    elif dti <= 0.35: return 10
    elif dti <= 0.5: return 25
    else: return 45
def points_util(u):
    if u == '0-10%': return 0
    elif u == '10-30%': return 10
    elif u == '30-50%': return 20
    elif u == '50-80%': return 35
    else: return 55
def points_late(x):
    if x == '0': return 0
    elif x == '1': return 15
    elif x == '2-3': return 35
    else: return 60
def points_inq(x):
    if x == '0-1': return 0
    elif x == '2-3': return 10
    elif x == '4-6': return 25
    else: return 45
def points_income(x):
    if x == 'High': return 0
    elif x == 'Medium': return 10
    else: return 25
def points_ltv(ltv):
    if ltv <= 0.6: return 0
    elif ltv <= 0.8: return 15
    elif ltv <= 1.0: return 35
    else: return 60
def points_tenure(x):
    if x == '>24': return 0
    elif x == '12-24': return 10
    elif x == '6-12': return 20
    else: return 35

model['Points_DTI'] = model['DTI'].apply(points_dti)
model['Points_Utilization'] = model['Utilization_Bucket'].apply(points_util)
model['Points_LatePay'] = model['Late_Pay_Bucket'].apply(points_late)
model['Points_Inquiry'] = model['Inq_Bucket'].apply(points_inq)
model['Points_IncomeStability'] = model['Income_Stability'].apply(points_income)
model['Points_LTV'] = model['LTV'].apply(points_ltv)
model['Points_Tenure'] = model['Tenure_Bucket'].apply(points_tenure)

model['Total_Points'] = (
    model['Points_DTI'] + model['Points_Utilization'] + model['Points_LatePay'] +
    model['Points_Inquiry'] + model['Points_IncomeStability'] + model['Points_LTV'] + model['Points_Tenure']
)
model['Total_Score'] = base_score - model['Total_Points']

# PHASE 6: Grade mapping
def grade_map(pd):
    if pd < 0.01: return 'Prime'
    elif pd < 0.03: return 'Near-prime'
    elif pd < 0.07: return 'Sub-prime'
    else: return 'High-risk'
# Simple calibration: map Total_Points to PD_hat
def calibrate_pd(points):
    # Example mapping, can be replaced with empirical calibration
    if points <= 50: return 0.005
    elif points <= 100: return 0.02
    elif points <= 150: return 0.045
    elif points <= 200: return 0.09
    else: return 0.15
model['PD_hat'] = model['Total_Points'].apply(calibrate_pd)
model['Grade'] = model['PD_hat'].apply(grade_map)

# Risk profile summary
model['Risk_Profile'] = model['Grade'] + ' | PD_hat: ' + model['PD_hat'].round(3).astype(str)

# Save final output
model.to_csv('modeling_view_with_risk.csv', index=False)
print('Final modeling view with risk profile created: modeling_view_with_risk.csv')
