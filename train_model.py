import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import time

# 1. Load Data
print("Loading data...")
df = pd.read_csv('final_training_data.csv')
original_len = len(df)

# 2. Advanced Preprocessing (The Game Changer)

# A. Remove Outliers (Crucial for R2)
# We remove the top 1% and bottom 1% of yields per Crop to eliminate bad data.
print("Cleaning outliers...")
cleaned_dfs = []
for crop in df['Crop'].unique():
    crop_df = df[df['Crop'] == crop]
    # Calculate quantiles
    low = crop_df['Target_Yield'].quantile(0.01)
    high = crop_df['Target_Yield'].quantile(0.99)
    # Filter
    mask = (crop_df['Target_Yield'] >= low) & (crop_df['Target_Yield'] <= high)
    cleaned_dfs.append(crop_df[mask])
    
df = pd.concat(cleaned_dfs)
print(f"Removed {original_len - len(df)} outlier rows.")

# B. Feature Engineering
print("Engineering biological features...")
df['Planting_Date'] = pd.to_datetime(df['Planting_Date'])
df['Harvest_Date'] = pd.to_datetime(df['Harvest_Date'])

# Feature 1: Seasonality (Month)
# Crops behave differently in January vs July, even if temp is similar.
df['Planting_Month'] = df['Planting_Date'].dt.month

# Feature 2: Duration & Intensity
df['Duration_Days'] = (df['Harvest_Date'] - df['Planting_Date']).dt.days
df['Rain_Intensity'] = df['Total_Rainfall'] / df['Duration_Days'] # Rain per day
df['Heat_Sum'] = df['Avg_Temp'] * df['Duration_Days'] # Growing Degree Days proxy

# C. Log Transform Target
print("Applying Log-Transformation...")
y_log = np.log1p(df['Target_Yield'])

# Drop non-numeric cols
X = df.drop(columns=['Planting_Date', 'Harvest_Date', 'Target_Yield'])

# D. One-Hot Encoding
print("Encoding features...")
X = pd.get_dummies(X, columns=['Crop', 'Province'])

# Save columns
joblib.dump(list(X.columns), 'model_columns.joblib')

# 3. Split
X_train, X_test, y_train_log, y_test_log = train_test_split(X, y_log, test_size=0.15, random_state=42)

# 4. Configure XGBoost (Ultra Mode)
print("Configuring XGBoost (Deep Learning Mode)...")

model = XGBRegressor(
    n_estimators=15000,       # Massive number of trees
    learning_rate=0.01,       # Very slow learning for maximum precision
    max_depth=14,             # Very deep trees to capture complex biology
    min_child_weight=5,       # Protects against overfitting
    subsample=0.9,            # Use 90% of data per tree
    colsample_bytree=0.9,     # Use 90% of features per tree
    gamma=0.2,                # Minimum loss reduction to make a split
    reg_alpha=0.1,            # L1 Regularization
    reg_lambda=1.0,           # L2 Regularization
    
    # GPU Settings
    tree_method='gpu_hist',
    gpu_id=0,
    predictor='gpu_predictor',
    
    n_jobs=-1,
    random_state=42
)

# 5. Train
print("Training Model on GPU (This will be intense)...")
start_time = time.time()

eval_set = [(X_test, y_test_log)]
model.fit(
    X_train, 
    y_train_log, 
    eval_set=eval_set,
    verbose=200,              # Print every 200 rounds
    early_stopping_rounds=150 
)

end_time = time.time()
print(f"Training finished in {end_time - start_time:.2f} seconds.")

# 6. Evaluate
print("Evaluating model...")
y_pred_log = model.predict(X_test)

# Reverse Log
y_pred_real = np.expm1(y_pred_log)
y_test_real = np.expm1(y_test_log)

mae = mean_absolute_error(y_test_real, y_pred_real)
r2 = r2_score(y_test_real, y_pred_real)

print(f"--- ULTRA RESULTS ---")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"R2 Score: {r2:.2f}")

joblib.dump(model, 'crop_yield_model.joblib')