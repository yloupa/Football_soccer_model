import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import ast
from statsmodels.stats.outliers_influence import variance_inflation_factor

df = pd.read_csv('matches_expanded.csv')

print(df.head())

duplicate_count = df.duplicated().sum()
print(f"Number of duplicate rows: {duplicate_count}")

# if you need to check the duplicates
# duplicate_rows = df[df.duplicated(keep=False)]
# duplicate_rows.to_csv('dup_test.csv', index=False)

df['Diff_act_xG']= df['xG'] - df['scored'] #create difference between xG and scored for the team in title
df['Diff_act_xGA'] = df['xGA'] - df['missed'] #create difference between xG and scored for the opposition

#fixing PPDA - the dict converted to strings by saving to csv
df['ppda'] = df['ppda'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df['ppda_allowed'] = df['ppda_allowed'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df['ppda_att'] = df.ppda.apply(lambda x: x['att'])
df['ppda_def'] = df.ppda.apply(lambda x: x['def'])
df['ppda_att_ad'] = df.ppda_allowed.apply(lambda x: x['att'])
df['ppda_def_ad'] = df.ppda_allowed.apply(lambda x: x['def'])
df['ppda_cal'] = (df['ppda_att'] /
                           df['ppda_def'].replace(0, np.nan)).fillna(0)

df['ppda_cal_ad'] = (df['ppda_att_ad'] /
                           df['ppda_def_ad'].replace(0, np.nan)).fillna(0)

df['date_datetime'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

print(df.head())
print(df.columns)

df_sorted = df.sort_values(by=['title', 'date_datetime']).reset_index(drop=True) #reset the index post sorting

# Define the number of lagged games to look back
lag_features = ['xG', 'xGA', 'scored', 'missed', 'ppda_cal']
lag_window = 5  # Look back up to 5 games

# Create lagged features for each team
for feature in lag_features:
    for lag in range(1, lag_window + 1):
        df_sorted[f'{feature}_lag{lag}'] = df_sorted.groupby('title')[feature].shift(lag)

# Create rolling average features
rolling_window = 5  # Rolling window of last 3 games
for feature in lag_features:
    df_sorted[f'{feature}_rolling_mean'] = df_sorted.groupby('title')[feature].transform(
        lambda x: x.shift(1).rolling(window=rolling_window, min_periods=1).mean()
    )

# Create rolling sum features for goals scored
for feature in ['scored', 'missed']:
    df_sorted[f'{feature}_rolling_sum'] = df_sorted.groupby('title')[feature].transform(
        lambda x: x.shift(1).rolling(window=rolling_window, min_periods=1).sum()
    )


# Create separate rolling averages for home and away games
df_sorted['xG_home_rolling_mean'] = df_sorted[df_sorted['h_a'] == 'h'].groupby('title')['xG'].transform(
    lambda x: x.shift(1).rolling(window=rolling_window, min_periods=1).mean()
)

df_sorted['xG_away_rolling_mean'] = df_sorted[df_sorted['h_a'] == 'a'].groupby('title')['xG'].transform(
    lambda x: x.shift(1).rolling(window=rolling_window, min_periods=1).mean()
)

# You can also create interaction features like combining home/away and lagged features
df_sorted['xG_home_lag1'] = df_sorted.apply(lambda row: row['xG_lag1'] if row['h_a'] == 'h' else None, axis=1)
df_sorted['xG_away_lag1'] = df_sorted.apply(lambda row: row['xG_lag1'] if row['h_a'] == 'a' else None, axis=1)

df_sorted['days_since_last_match'] = df_sorted.groupby('title')['date_datetime'].diff().dt.days

# Define the smoothing factor alpha (e.g., 0.1 for moderate weighting to recent games)
alpha = 0.4

# Calculate the Exponential Moving Average (EMA) for 'xG' with a span equivalent to the smoothing factor
df_sorted['xG_ema'] = df_sorted['xG'].ewm(alpha=alpha, adjust=False).mean()


# Extract month from the date and create a month feature
df_sorted['month'] = df_sorted['date_datetime'].dt.month

print(df_sorted.isna().sum()[df_sorted.isna().sum() > 0])



# Convert 'season' to a categorical variable if it isn't already
# df_sorted['season'] = df_sorted['season'].astype('category')
# df_sorted['month'] = df_sorted['month'].astype('category')

# Display the first few rows to check the new features
print(df_sorted.head())

df_sorted.fillna(0, inplace=True)

df_sorted.to_csv('df_sorted.csv', index=False)


#lets try with arsenal
arsenal_data = df_sorted[df_sorted['title'] == 'Arsenal']

ars_data_u = arsenal_data[['title','h_a','season','date_datetime','xG','deep','scored','Diff_act_xG','ppda_att','ppda_def','ppda_cal','xG_lag1','xG_lag2','xG_lag3','xG_lag4',
                           'xG_lag5','xG_home_rolling_mean','xG_away_rolling_mean','days_since_last_match','xG_ema']]

print(df.isnull().sum())
print(arsenal_data.columns)
print(arsenal_data.dtypes)

numeric_df = ars_data_u.select_dtypes(include=['float64', 'int64'])

X = ars_data_u.select_dtypes(include=[float, int]).drop(columns=['scored'])  # Drop target
vif_data = pd.DataFrame()
vif_data['feature'] = X.columns
vif_data['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print(vif_data)


sns.set(font_scale=0.5)
plt.figure(figsize=(12,8))
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
plt.show()

# arsenal_data.to_csv('arsenal_model_test.csv',index=False)

