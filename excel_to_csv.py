import pandas as pd
import os

excel_path = 'Credit_Risk_Analytics_Database_Clean.xlsx'
output_dir = 'excel_sheets_csv'
os.makedirs(output_dir, exist_ok=True)

# Load the Excel file
excel_file = pd.ExcelFile(excel_path)

# Export each sheet to a separate CSV file
for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    csv_path = os.path.join(output_dir, f'{sheet_name}.csv')
    df.to_csv(csv_path, index=False)

print(f'Exported {len(excel_file.sheet_names)} sheets to CSV files in "{output_dir}".')
