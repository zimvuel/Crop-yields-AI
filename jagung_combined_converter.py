from pathlib import Path
import pandas as pd
import numpy as np
import calendar
import os

input_folder_path = Path("raw_data")
output_folder_path = Path("filtered_data")
FILE_2023 = input_folder_path / "Luas Panen, Produksi, dan Produktivitas Jagung Menurut Provinsi, 2023.csv"
FILE_2024 = input_folder_path / "Luas Panen, Produksi, dan Produktivitas Jagung Menurut Provinsi, 2024.csv"
OUTPUT_FILE = output_folder_path / "Jagung_Daily_Combined_2023_2024.csv"

np.random.seed(42)

def generate_noise(n, scale=0.1):
    return np.random.normal(loc=1.0, scale=scale, size=n)

def distribute_value(yearly_val, year, target_months, is_cumulative):
    if yearly_val <= 0:
        return []

    results = []

    if is_cumulative:
        base_month = yearly_val / 12.0
        month_noise = generate_noise(12, 0.1)
        monthly_vals = base_month * month_noise
        
        current_sum = np.sum(monthly_vals)
        if current_sum > 0:
            monthly_vals = monthly_vals * (yearly_val / current_sum)
    else:
        month_noise = generate_noise(12, 0.1)
        monthly_vals = yearly_val * month_noise

    for m_idx in target_months:
        m_val = monthly_vals[m_idx - 1]
        days_in_month = calendar.monthrange(year, m_idx)[1]

        if is_cumulative:
            base_day = m_val / days_in_month
            day_noise = generate_noise(days_in_month, 0.1)
            daily_vals = base_day * day_noise
            
            d_sum = np.sum(daily_vals)
            if d_sum > 0:
                daily_vals = daily_vals * (m_val / d_sum)
        else:
            day_noise = generate_noise(days_in_month, 0.1)
            daily_vals = m_val * day_noise

        daily_vals = np.maximum(daily_vals, 0)

        for day_num, val in enumerate(daily_vals, start=1):
            date_str = f"{year}-{m_idx:02d}-{day_num:02d}"
            results.append({'Date': date_str, 'Value': val})

    return results

def find_header_row(df):
    for i, row in df.iterrows():
        row_str = str(row.values).lower()
        if 'luas panen' in row_str and 'produksi' in row_str and 'menurut' not in row_str:
            return i
        if '(ha)' in row_str and '(ton)' in row_str:
            return i
    return -1

def clean_number(val):
    if pd.isna(val) or val == '-' or str(val).strip() == '':
        return 0.0
    try:
        return float(str(val).replace(',', ''))
    except ValueError:
        return 0.0

def process_file(filepath, year, target_months):
    print(f"Reading {filepath}...")
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return []

    df_raw = pd.read_csv(filepath, header=None)
    
    header_idx = find_header_row(df_raw)
    if header_idx == -1:
        print(f"Error: Could not find header row in {filepath}")
        return []

    df = pd.read_csv(filepath, header=header_idx)
    
    cols = [c.lower() for c in df.columns]
    try:
        col_prov = next(i for i, c in enumerate(cols) if 'provinsi' in c or i==0)
        col_area = next(i for i, c in enumerate(cols) if 'luas panen' in c)
        col_prod = next(i for i, c in enumerate(cols) if 'produksi' in c and 'produktivitas' not in c)
        col_yield = next(i for i, c in enumerate(cols) if 'produktivitas' in c)
    except StopIteration:
        print(f"Error: Could not identify required columns in {filepath}")
        return []

    processed_rows = []

    for _, row in df.iterrows():
        prov = row.iloc[col_prov]
        
        if pd.isna(prov) or str(prov).lower() == 'indonesia' or str(prov).isnumeric():
            continue

        prov = str(prov).strip()
        
        ann_area = clean_number(row.iloc[col_area])
        ann_prod = clean_number(row.iloc[col_prod])
        ann_yield = clean_number(row.iloc[col_yield])

        daily_area = distribute_value(ann_area, year, target_months, True)
        daily_prod = distribute_value(ann_prod, year, target_months, True)
        daily_yield = distribute_value(ann_yield, year, target_months, False)

        for i in range(len(daily_area)):
            processed_rows.append({
                'Date': daily_area[i]['Date'],
                'Provinsi': prov,
                'Luas_Panen_Ha': round(daily_area[i]['Value'], 2),
                'Produksi_Ton': round(daily_prod[i]['Value'], 2),
                'Produktivitas_Ku_Ha': round(daily_yield[i]['Value'], 2)
            })

    return processed_rows

print("Starting Jagung Data Processing...")

os.makedirs(output_folder_path, exist_ok=True)

rows_2023 = process_file(FILE_2023, 2023, [11, 12])

rows_2024 = process_file(FILE_2024, 2024, list(range(1, 13)))

all_data = rows_2023 + rows_2024

if all_data:
    df_final = pd.DataFrame(all_data)
    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"Success! Saved {len(df_final)} rows to {OUTPUT_FILE}")
else:
    print("No data was processed.")