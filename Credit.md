PHASE 1: Define targets and samples

Create Default_12m (ground-truth label)

If you have realized outcome data (e.g., repayment history, 90+ DPD within 12 months):

In a new column Default_12m on the Risk Assessment sheet (or a new “Outcomes” sheet joined by Application_ID), set:

Default_12m = 1 if any of: Days_Past_Due >= 90 within 12 months after Decision_Date, write-off, bankruptcy, foreclosure.

Default_12m = 0 otherwise.

If you don’t have realized outcomes (synthetic for testing only):

Use Probability_of_Default (PD) provided as a propensity. For each row:

In Excel: =IF(RAND() < [PD], 1, 0) to simulate labels. Freeze once generated: Copy → Paste Values.

Important: Only use this for experimentation; not for production.

Time-based split: Train/Validation/OOT

On Loan Application Details sheet, ensure Application_Date exists.

Add a Period column:

Example cut: Train = apps dated up to 2023-06-30; Validation = 2023-07-01 to 2023-12-31; OOT = 2024-01-01 onward. Use dates relevant to your dataset.

Excel formula: =IF([@Application_Date] <= DATE(2023,6,30),"Train", IF([@Application_Date] <= DATE(2023,12,31),"Validation","OOT"))

Use Excel Filters to create three filtered views or copy filtered records into three separate tabs (Train, Validation, OOT) to simplify modeling/evaluation.

PHASE 2: Sanitize variables for Application PD

Remove leakage (fields not known at decision time)

Exclude columns like Final_Decision, Internal PD/LGD/EAD, Expected_Loss, Manual_Override_Flag, Collection outcomes, any fields populated after Decision_Date.

Practical step:

Create a “Feature_Dictionary” sheet listing each column, Available_at_Application? (Yes/No). Filter to Yes to define your model input set.

Keep only: demographics, income/employment, bureau, obligations, loan details, collateral inputs, relationship history (prior to app), external risk signals available at app.

Align “as-of” dates

For relationship/account balances, only use values as of or before Application_Date.

If your data has monthly snapshots: VLOOKUP the most recent date <= Application_Date.

Excel trick: Use MAXIFS to find the latest snapshot date <= Application_Date, then INDEX/XLOOKUP to bring the value from that date.

PHASE 3: Feature set and engineering

Compute DTI (Debt-to-Income)

DTI = Total_Monthly_Obligations / Net_Monthly_Income.

Excel: =[@Total_Monthly_Obligations]/[@Net_Monthly_Income]

Cap at, say, 1.5: =MIN(calculated_DTI,1.5)

Compute LTV (Loan-to-Value) for secured loans

LTV = Requested_Loan_Amount / Collateral_Value.

Excel: =IF([@Collateral_Value]>0,[@Requested_Loan_Amount]/[@Collateral_Value],0)

Cap at 1.2: =MIN(LTV,1.2)

Utilization buckets (from bureau)

If Credit_Utilization_Ratio exists, create buckets:

0-10%, 10-30%, 30-50%, 50-80%, >80%.

Excel: =IF(U<0.1,"0-10%", IF(U<0.3,"10-30%", IF(U<0.5,"30-50%", IF(U<0.8,"50-80%",">80%"))))

Delinquency counts/inquiries

Use Number_of_Late_Payments and Credit_Inquiries_Last_12_Months.

Create buckets:

Late_Pay_Bucket: 0, 1, 2-3, >3

Inq_Bucket: 0-1, 2-3, 4-6, >6

Excel example (late): =IF(Late=0,"0", IF(Late=1,"1", IF(Late<=3,"2-3",">3")))

Income stability band

From Years_in_Current_Job and Net_Monthly_Income variance if available. If no variance, use tenure only:

Income_Stability = IF(Years_in_Current_Job>=3,"High", IF(Years_in_Current_Job>=1,"Medium","Low"))

Geolocation/device risk buckets

If Geolocation_Risk_Score is numeric 0-1:

=IF(Score<0.2,"Very Low", IF(Score<0.4,"Low", IF(Score<0.6,"Medium", IF(Score<0.8,"High","Very High"))))

If categorical already, keep as is.

Tenure with bank

Tenure_Months = DATEDIF(Customer_Since, Application_Date,"M")

Bucket: <6, 6-12, 12-24, >24.

Average balance buckets

From Average_Monthly_Balance:

=IF(AMB<25000,"Low", IF(AMB<75000,"Medium","High"))

One consolidated “Modeling_View” sheet

Use XLOOKUP/INDEX-MATCH to bring all needed features from your multiple sheets into one flat table keyed by Application_ID (and Applicant_ID where needed).

Columns you want: Default_12m, Application_Date, product, demographics, income, obligations, bureau, collateral, relationship, external risk buckets, engineered features (DTI, LTV, buckets).

Ensure no blanks: Fill missing numeric with sensible caps/medians; categorical with “Unknown.” Use Data → Data Tools → Data Validation/Find & Select to check blanks. Then Copy → Paste Values to freeze calculations.

PHASE 4: Modeling in Excel (baseline scorecard-style)

Excel can’t run logistic regression natively without add-ins, but you can build a scorecard using binned features and weights. Steps:

Binning and bad rates (IV-lite approach)

For each categorical/bucketed feature:

Create a pivot table:

Rows: Feature buckets

Values: Count of records; Sum of Default_12m

Add a calculated column: Bad_Rate = Sum(Default_12m)/Count

Rank buckets by bad rate (higher = riskier). This is your monotonic check.

Assign points per bucket (manual scorecard)

Choose a base score (e.g., 600) and a target odds (e.g., Odds 50:1 at 600). For Excel simplicity:

Start with relative points proportional to log-odds difference. If that’s complex, use simpler tiered points:

For each feature, assign 0 to best bucket, increasing points to worse buckets. Example:

DTI: <=0.25 → 0 pts, 0.25-0.35 → 10, 0.35-0.5 → 25, >0.5 → 45

Utilization: 0-10% → 0, 10-30% → 10, 30-50% → 20, 50-80% → 35, >80% → 55

Late_Pay_Bucket: 0 → 0, 1 → 15, 2-3 → 35, >3 → 60

Inq_Bucket: 0-1 → 0, 2-3 → 10, 4-6 → 25, >6 → 45

Income_Stability: High → 0, Medium → 10, Low → 25

LTV: <=0.6 → 0, 0.6-0.8 → 15, 0.8-1.0 → 35, >1.0 → 60

Tenure: >24m → 0, 12-24 → 10, 6-12 → 20, <6 → 35

Put these mappings in a “Points_Lookup” sheet. Use VLOOKUP/XLOOKUP to fetch points for each feature bucket.

Total score and initial calibration to PD

Total_Score = Base_Score + SUM of feature points with negative sign (lower score = riskier or vice versa; be consistent).

Alternatively: Total_Points = SUM(points), where higher points = higher risk.

Convert points to PD with a simple calibration:

Create a two-column mapping on a “Calibration” sheet:

Points_Bucket (e.g., 0-50, 51-100, 101-150, …)

Empirical Bad_Rate from Train sample via pivot (average Default_12m by Points_Bucket).

For each record, compute PD_hat = LOOKUP(Total_Points in Calibration table Bad_Rate).

This gives you a baseline PD without running a regression.

PHASE 5: Evaluate model performance in Excel

AUC/Gini (approx, Excel-friendly)

Sort Validation sample by PD_hat descending.

Create cumulative columns:

Cum_Apps (running count), Cum_Bads (running sum of Default_12m), Cum_Goods = Cum_Apps - Cum_Bads.

Compute:

Total_Bads = SUM(Default_12m), Total_Goods = N - Total_Bads.

KS: At each row i, KS_i = |(Cum_Bads_i/Total_Bads) - (Cum_Goods_i/Total_Goods)|.

KS = MAX(KS_i).

For AUC approximation:

Create deciles by PD_hat (10 equal-sized bins).

For each decile: compute bad rate and cumulative distributions as above.

Use the trapezoid method on ROC points or use the “Somers’ D” approximation with deciles. If complex, report KS and lift (bad rate in top decile vs overall).

Brier Score:

=AVERAGE((PD_hat - Default_12m)^2) over Validation.

Calibration curve

Bin Validation into 10-20 PD_hat buckets.

For each bucket: avg PD_hat vs actual bad rate.

Scatter plot: X = avg PD_hat, Y = actual bad rate. Closer to y=x line is better.

Segment stability

Create pivots by Product/Branch/Source:

Columns: Segment

Values: AUC proxy (you can compare KS or lift), Avg PD_hat, Actual bad rate.

Check for large divergence across segments.

PHASE 6: Grade mapping, cutoffs, expected loss, pricing

Map PD to internal grades

Create a “Grades” sheet with PD ranges:

Grade 1 (Prime): PD < 1%

Grade 2 (Near-prime): 1%–3%

Grade 3 (Sub-prime): 3%–7%

Grade 4 (High-risk): >7%

In Modeling_View: =XLOOKUP(PD_hat, use interval logic). Excel can use nested IFs or a helper table with lower bounds and MATCH.

Set decision cutoffs

Use a “Strategy” sheet:

Try cutoffs by product. Example: Approve if Grade ≤ 2; Manual Review if Grade = 3; Reject if Grade = 4.

Compute approval rate, expected portfolio default rate.

Compute EL = PD × LGD × EAD

If you have LGD, EAD fields (placeholders allowed):

EL_per_loan = PD_hat * LGD * EAD

Portfolio EL = SUM(EL_per_loan) for approved set.

Risk-based pricing simulation

Define a pricing rule:

Base Rate + Risk Premium where Risk Premium = k × EL/Loan_Amount or PD-bucket-based add-ons.

Compute Expected Margin = Coupon_Yield - Funding_Cost - EL - Opex.

Compute RAROC = Expected Profit / Economic Capital (you can proxy capital as alpha × EAD × unexpected loss factor).

On Strategy sheet, vary cutoff and pricing rules and observe RAROC and approval rate via Data → What-If Analysis → Data Table.

PHASE 7: Policy screens

Apply KYC/AML and exposure limits

Create a “Policy_Flags” column:

Not_KYC_Compliant → Reject

AML_Fail/Sanctions/PEP high risk → Reject or Manual Review per policy

LTV over limit or DTI over limit → Reject

Implement as a final eligibility check before pricing/approval.

PHASE 8: Monitoring setup

Build dashboards (Pivot + Charts)

Approval mix: Pivot by Grade, Product, Source → count of approved apps.

Grade migration (over time): Pivot by Month(Application_Date) vs Grade distribution.

PD-to-default backtest (once actuals available):

For each origination month, compute average PD_hat and realized default rate at 12 months; line chart both.

Stability indices:

PSI (Population Stability Index) for PD_hat bins:

PSI_bin = (Actual% - Expected%) * LN(Actual% / Expected%)

Sum across bins. Do Train distribution as “Expected,” monthly/quarterly “Actual.”

Overrides:

Track Approved despite policy fail or Rejected despite low PD; show override rate by branch/segment.

PHASE 9: Optional enhancements in Excel

Simple isotonic/Platt-like calibration

Create a two-column table mapping raw PD_hat deciles to actual default rates (from Validation).

Replace PD_hat with LOOKUP-calibrated rates.

Champion-challenger (alternative bucket weights)

Duplicate Points_Lookup with slightly different weights (e.g., more emphasis on utilization, delinquency).

Recompute scores and compare KS/lift on Validation.

Practical tips

Keep a Control Panel sheet:

Date cut parameters

Grade thresholds

Policy toggles (Yes/No)

Pricing constants (funding cost, opex per loan, capital alpha)

Freeze random/synthetic elements:

After generating synthetic Default_12m with RAND(), Copy → Paste Values to make results reproducible.

Use named ranges for lookup tables (Points_Lookup, Grades, Calibration) to simplify formulas.

Color code leakage-excluded columns in Modeling_View for clarity.

Save versions: v1_train_split, v2_binning, v3_scorecard, v4_calibrated, v5_strategy.