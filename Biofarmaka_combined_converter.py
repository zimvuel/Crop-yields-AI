import pandas as pd
import numpy as np
from pathlib import Path
import calendar
import re
import os

input_folder_path = Path("raw_data")
output_folder_path = Path("filtered_data")
FILE_2023 = input_folder_path / "Produksi Tanaman Biofarmaka Menurut Provinsi dan Jenis Tanaman, 2023.csv"
FILE_2024 = input_folder_path / "Produksi Tanaman Biofarmaka Menurut Provinsi dan Jenis Tanaman , 2024.csv'"
OUTPUT_FILE = output_folder_path / "Biofarmaka_Production_Daily_Combined.csv"

np.random.seed(42)

def generate_noise(n, scale=0.1):
    return np.random.normal(loc=1.0, scale=scale, size=n)

def distribute_cumulative(yearly_total, year, target_months):
    if yearly_total <= 0:
        results = []
        for m in target_months:
            days_in_month = calendar.monthrange(year, m)[1]
            for d in range(1, days_in_month + 1):
                date_str = f"{year}-{m:02d}-{d:02d}"
                results.append({'Date': date_str, 'Value': 0.0})
        return results

    base_month_avg = yearly_total / 12.0
    month_noise = generate_noise(12, scale=0.1)
    monthly_values = base_month_avg * month_noise
    
    monthly_values = np.maximum(monthly_values, 0)
    
    current_sum = np.sum(monthly_values)
    if current_sum > 0:
        monthly_values = monthly_values * (yearly_total / current_sum)
    
    daily_data = []

    for month_idx in target_months:
        monthly_val = monthly_values[month_idx - 1]
        days_in_month = calendar.monthrange(year, month_idx)[1]
        
        base_day_avg = monthly_val / days_in_month
        day_noise = generate_noise(days_in_month, scale=0.1)
        daily_vals = base_day_avg * day_noise
        
        daily_vals = np.maximum(daily_vals, 0)
        
        day_sum = np.sum(daily_vals)
        if day_sum > 0:
            daily_vals = daily_vals * (monthly_val / day_sum)
            
        for day_num, val in enumerate(daily_vals, start=1):
            date_str = f"{year}-{month_idx:02d}-{day_num:02d}"
            daily_data.append({'Date': date_str, 'Value': val})
            
    return daily_data

def clean_column_name(col_name):
    name = re.sub(r'Produksi\s+', '', col_name, flags=re.IGNORECASE)
    name = re.sub(r'\(.*?\)', '', name)
    return name.strip()

def clean_number(val):
    if pd.isna(val) or val == '-' or val == '...':
        return 0.0
    if isinstance(val, str):
        return float(val.replace(',', ''))
    return float(val)

def process_file(filepath, year, target_months):
    print(f"Processing {year} data from {filepath}...")
    
    if not os.path.exists(filepath):
         print(f"Error: File {filepath} not found.")
         return []

    df = pd.read_csv(filepath)
    
    prod_cols = [c for c in df.columns if 'Produksi' in c]
    
    processed_rows = []
    
    for _, row in df.iterrows():
        prov = row.get('Provinsi', row.get('provinsi'))
        
        if pd.isna(prov) or str(prov).lower() == 'indonesia' or str(prov).strip() == '':
            continue
            
        prov = str(prov).strip()
        
        for col in prod_cols:
            crop_name = clean_column_name(col)
            yearly_total = clean_number(row[col])
            
            daily_series = distribute_cumulative(yearly_total, year, target_months)
            
            for entry in daily_series:
                processed_rows.append({
                    'Date': entry['Date'],
                    'Province': prov,
                    'Crop': crop_name,
                    'Production_Kg': round(entry['Value'], 2),
                })
                
    return processed_rows

os.makedirs(output_folder_path, exist_ok=True)

data_2023 = process_file(FILE_2023, 2023, [11, 12])

data_2024 = process_file(FILE_2024, 2024, list(range(1, 13)))

all_data = data_2023 + data_2024
if all_data:
    final_df = pd.DataFrame(all_data)

    print(f"Saving {len(final_df)} rows to {OUTPUT_FILE}...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    print("Done!")
else:
    print("No data processed.")