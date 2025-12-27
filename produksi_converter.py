from pathlib import Path
import pandas as pd
import numpy as np
import calendar
import os

input_folder_path = Path("raw_data")
output_folder_path = Path("filtered_data")
FILE_PADI = input_folder_path / "Produksi Padi Menurut Provinsi (Bulanan), 2025.xlsx - Sheet1.csv"
FILE_JAGUNG = input_folder_path / "Produksi Jagung Pipilan Kering Kadar Air 14 Persen Menurut Provinsi (Bulanan), 2025.xlsx - Sheet1.csv"

OUT_PADI = output_folder_path / "Daily_Padi_Production_2025.csv"
OUT_JAGUNG = output_folder_path / "Daily_Jagung_Production_2025.csv"

np.random.seed(42)

def convert_monthly_to_daily(input_path, output_path, crop_name):
    print(f"\n--- Processing {crop_name} ---")
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found in the current directory.")
        return

    try:
        df = pd.read_csv(input_path, header=3)
        
        df.rename(columns={df.columns[0]: 'Provinsi'}, inplace=True)
        
        if 'Tahunan' in df.columns:
            df = df.drop(columns=['Tahunan'])
            
        df = df.dropna(subset=['Provinsi'])
        df = df[~df['Provinsi'].astype(str).str.match(r'^\d+$')] 

        daily_data = []

        year = 2025
        months = {
            'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6,
            'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
        }

        for index, row in df.iterrows():
            provinsi = row['Provinsi']
            
            if str(provinsi).lower().strip() == 'indonesia':
                continue

            for month_name, month_num in months.items():
                if month_name not in df.columns:
                    continue
                    
                try:
                    val_str = str(row[month_name]).replace(',', '').strip()
                    if val_str == '-' or val_str == '':
                        monthly_total = 0.0
                    else:
                        monthly_total = float(val_str)
                except ValueError:
                    monthly_total = 0.0
                
                _, num_days = calendar.monthrange(year, month_num)
                
                if monthly_total <= 0:
                    daily_values = np.zeros(num_days)
                else:
                    noise = np.random.normal(loc=1.0, scale=0.1, size=num_days)
                    
                    noise = np.maximum(noise, 0)
                    
                    base_daily = monthly_total / num_days
                    
                    daily_values = base_daily * noise
                    
                    current_sum = np.sum(daily_values)
                    if current_sum > 0:
                        daily_values = daily_values * (monthly_total / current_sum)
                    else:
                        daily_values = np.full(num_days, base_daily)
                
                for day, value in enumerate(daily_values, start=1):
                    date_str = f"{year}-{month_num:02d}-{day:02d}"
                    daily_data.append({
                        'Date': date_str,
                        'Provinsi': provinsi,
                        'Crop': crop_name,
                        'Production_Ton': round(value, 2)
                    })

        os.makedirs(output_path.parent, exist_ok=True)

        if daily_data:
            final_df = pd.DataFrame(daily_data)
            final_df.to_csv(output_path, index=False)
            print(f"Success! Saved {len(final_df)} rows to '{output_path}'")
        else:
            print("No data processed.")

    except Exception as e:
        print(f"An error occurred while processing {crop_name}: {e}")

if __name__ == "__main__":
    print("Starting conversion process...")
    
    convert_monthly_to_daily(FILE_PADI, OUT_PADI, 'Padi')
    
    convert_monthly_to_daily(FILE_JAGUNG, OUT_JAGUNG, 'Jagung')
    
    print("\nAll tasks completed.")