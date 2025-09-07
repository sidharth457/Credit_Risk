# Credit Risk

This repository contains code and sample data for a credit risk analysis project. Files include data exports, modeling scripts, and dashboard code.

## Contents
- `applicant_analysis.py` - scripts for analyzing applicant data
- `train_credit_risk_model.py` - training pipeline for the credit risk model
- `applicant_dashboard.py`, `interactive_dashboard_guide.py`, `build_modeling_view.py` - visualization and dashboard code
- `excel_sheets_csv/` - CSV exports of source data
- `Credit_Risk_Analytics_Database_Clean.xlsx` - cleaned dataset (consider storing large binaries in Git LFS)

## Quick start
1. Create a virtual environment and install dependencies:

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Convert Excel sheets to CSV (if needed):

```powershell
python excel_to_csv.py
```

3. Train the model:

```powershell
python train_credit_risk_model.py
```

4. Run the dashboard (follow dashboard scripts' instructions).

## Notes
- Large binary files like `.xlsx` are recommended to be tracked with Git LFS or stored outside the repository. The repo includes a `.gitattributes` to configure LFS for `.xlsx` files.
- If you don't have `git-lfs` installed and want to move large files out of history, the steps below show how to remove them.

## Removing large files from history (if needed)

```powershell
# Install git-filter-repo if not available (recommended over filter-branch)
# On Windows with Python available:
python -m pip install git-filter-repo

# From the repo root:
python -m git_filter_repo --strip-blobs-bigger-than 5M
# or to remove specific files:
python -m git_filter_repo --path Credit_Risk_Analytics_Database_1000_REALISTIC.xlsx --invert-paths

# Force push rewritten history (be careful — this rewrites remote history):
git push --force origin main
```

If you'd like, I can enable Git LFS and migrate the `.xlsx` files into LFS for you, or remove them from history — tell me which you'd prefer.
