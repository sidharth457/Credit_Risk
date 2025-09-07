import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
import joblib

# Load data
model = pd.read_csv('modeling_view_with_risk.csv')

# Select features (exclude leakage and ID columns)
features = [
    'DTI','LTV','Points_DTI','Points_Utilization','Points_LatePay','Points_Inquiry',
    'Points_IncomeStability','Points_LTV','Points_Tenure','Total_Points','Total_Score'
]
X = model[features]
y = model['Default_12m']

# Train/validation split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Validation predictions
y_pred = clf.predict(X_val)
y_prob = clf.predict_proba(X_val)[:,1]

# Metrics
auc = roc_auc_score(y_val, y_prob)
print(f"Validation ROC AUC: {auc:.3f}")
print("Classification Report:\n", classification_report(y_val, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_val, y_pred))

# Save model
joblib.dump(clf, 'credit_risk_model.pkl')

# Save predictions for dashboard
model['Model_Pred_Prob'] = clf.predict_proba(X)[:,1]
model.to_csv('modeling_view_with_predictions.csv', index=False)
print('Model trained and predictions saved to modeling_view_with_predictions.csv')
