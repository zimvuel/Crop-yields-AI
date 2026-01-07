import pandas as pd
import numpy as np
import joblib
import datetime

class CropPredictor:
    def __init__(self):
        print("Loading knowledge from final training data...")
        self.df = pd.read_csv('final_training_data.csv')
        self.model = joblib.load('crop_yield_model.joblib')
        self.model_columns = joblib.load('model_columns.joblib')

        # 1. Parse Dates Correctly
        self.df['Planting_Date'] = pd.to_datetime(self.df['Planting_Date'])
        self.df['Harvest_Date'] = pd.to_datetime(self.df['Harvest_Date'])
        self.df['Month'] = self.df['Planting_Date'].dt.month
        
        # Calculate Duration
        self.df['Duration_Days'] = (self.df['Harvest_Date'] - self.df['Planting_Date']).dt.days

        # 2. Build Soil Lookup (Static per Province)
        print("Learning soil profiles...")
        self.soil_lookup = self.df.groupby('Province')[
            ['Soil_pH', 'Clay_Ratio', 'Sand_Ratio']
        ].mean().to_dict('index')

        # 3. Build Weather Lookup (Base Monthly Averages)
        # We still calculate monthly baselines, but we will INTERPOLATE between them later.
        print("Learning weather patterns...")
        self.weather_lookup = self.df.groupby(['Province', 'Month'])[
            ['Avg_Temp', 'Total_Rainfall', 'Avg_Humidity', 'Avg_Soil_Moisture']
        ].mean().to_dict('index')

        # 4. Duration Lookup
        self.duration_lookup = self.df.groupby('Crop')['Duration_Days'].mean().to_dict()
        
        # 5. Baseline Yields (For comparison)
        self.baseline_yields = self.df.groupby(['Crop', 'Province'])['Target_Yield'].mean().to_dict()

        print("Engine Ready!")

    def normalize_province(self, prov):
        if pd.isna(prov): return ""
        return str(prov).lower().strip()

    def get_baseline_yield(self, crop, province):
        prov_norm = self.normalize_province(province)
        key = (crop, prov_norm)
        if key in self.baseline_yields:
            return float(self.baseline_yields[key])
        return 4.0

    def get_interpolated_weather(self, province, date):
        """
        Smart Weather: Calculates weather for a SPECIFIC DAY by blending 
        the current month's average with the next/prev month.
        This prevents the 'Staircase Effect' where values stay flat for 30 days.
        """
        prov_norm = self.normalize_province(province)
        month = date.month
        day = date.day
        
        # Current Month Stats
        current_stats = self.weather_lookup.get((prov_norm, month), 
                        self.weather_lookup.get((prov_norm, 1), # Fallback to Jan
                        {'Avg_Temp': 28.0, 'Total_Rainfall': 1000.0, 'Avg_Humidity': 80.0, 'Avg_Soil_Moisture': 30.0}))

        # Determine target for interpolation (Next month if > 15th, Prev month if < 15th)
        # We assume the "Average" represents the 15th of the month.
        if day > 15:
            # Interpolate towards Next Month
            next_month = month + 1 if month < 12 else 1
            target_stats = self.weather_lookup.get((prov_norm, next_month), current_stats)
            weight = (day - 15) / 30.0 # e.g. Day 20 is 16% towards next month
        else:
            # Interpolate towards Prev Month
            prev_month = month - 1 if month > 1 else 12
            target_stats = self.weather_lookup.get((prov_norm, prev_month), current_stats)
            weight = (15 - day) / 30.0 # e.g. Day 5 is 33% towards prev month
            
        # Perform Linear Interpolation
        blended_stats = {}
        for key in ['Avg_Temp', 'Total_Rainfall', 'Avg_Humidity', 'Avg_Soil_Moisture']:
            val_curr = current_stats.get(key, 0.0)
            val_target = target_stats.get(key, 0.0)
            
            # Blend: Current * (1-w) + Target * w
            blended_stats[key] = (val_curr * (1 - weight)) + (val_target * weight)
            
        return blended_stats

    def predict_yield_internal(self, crop, province, planting_date):
        prov_norm = self.normalize_province(province)
        month = planting_date.month
        
        # Get Soil (Static)
        soil_stats = self.soil_lookup.get(prov_norm, {'Soil_pH': 6.0, 'Clay_Ratio': 30.0, 'Sand_Ratio': 30.0})

        # Get Weather (DYNAMIC / INTERPOLATED)
        weather_stats = self.get_interpolated_weather(province, planting_date)

        duration = self.duration_lookup.get(crop, 90.0)

        input_data = {
            'Avg_Temp': weather_stats['Avg_Temp'],
            'Total_Rainfall': weather_stats['Total_Rainfall'],
            'Avg_Humidity': weather_stats['Avg_Humidity'],
            'Avg_Soil_Moisture': weather_stats['Avg_Soil_Moisture'],
            'Soil_pH': soil_stats['Soil_pH'],
            'Clay_Ratio': soil_stats['Clay_Ratio'],
            'Sand_Ratio': soil_stats['Sand_Ratio'],
            'Planting_Month': month,
            'Duration_Days': duration,
            'Rain_Intensity': weather_stats['Total_Rainfall'] / duration,
            'Heat_Sum': weather_stats['Avg_Temp'] * duration
        }
        
        data_dict = {col: 0.0 for col in self.model_columns}
        for col, val in input_data.items():
            if col in data_dict: data_dict[col] = float(val)
        
        if f"Crop_{crop}" in data_dict: data_dict[f"Crop_{crop}"] = 1.0
        if f"Province_{prov_norm}" in data_dict: data_dict[f"Province_{prov_norm}"] = 1.0
            
        model_df = pd.DataFrame([data_dict]).astype(float)
        log_pred = self.model.predict(model_df)[0]
        return float(max(0, np.expm1(log_pred)))

    def predict_yield(self, crop, province, planting_date_str):
        try:
            date = pd.to_datetime(planting_date_str)
        except:
            date = pd.Timestamp.now()
        return self.predict_yield_internal(crop, province, date)

    def find_best_planting_time(self, crop, province):
        """
        BRUTE FORCE OPTIMIZATION (365 DAYS)
        Now with interpolation, so Jan 5 will yield differently than Jan 6.
        """
        start_date = pd.Timestamp.now()
        best_date = None
        best_yield = -1.0
        
        # Loop 365 days
        for day_offset in range(365):
            check_date = start_date + datetime.timedelta(days=day_offset)
            
            yield_val = self.predict_yield_internal(crop, province, check_date)
            
            if yield_val > best_yield:
                best_yield = yield_val
                best_date = check_date

        return best_date.strftime('%Y-%m-%d'), best_yield