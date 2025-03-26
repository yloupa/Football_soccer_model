import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import ast

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




df_home = df[df['h_a']=='h'] #gets home games
df_away = df[df['h_a']=='a'] #gets away games


#merge home games, with away games but only taking needed details to make the match.

df_compressed = pd.merge(df_home,df_away[['id','title','date','xGA']],how='left',left_on=['date','xG'],right_on=['date','xGA'],suffixes=('', '_away'))

print(df.shape)
print(df_home.shape)
print(df_away.shape)
print(df_compressed.shape)

print(df_compressed.columns)
print(df_compressed.dtypes)


#fixing datetime
df_compressed['date_datetime'] = pd.to_datetime(df_compressed['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
print('Number of NA datetimes:')
print(df_compressed['date_datetime'].isna().sum())
print(df_compressed[['date', 'date_datetime']].head())

print(df_compressed.dtypes)


print('PPDA checking:')
print(df_compressed['ppda'].head())
print(df_compressed['ppda'].dtype)
# print(df_compressed[~df_compressed['ppda'].apply(lambda x: isinstance(x, dict))])



#generate a unique match id
df_compressed['match_id'] =  df_compressed['id'].astype(str) + df_compressed['id_away'].astype(str) + df_compressed['season'].str[2:4] + df_compressed['season'].str[7:9]




#dropping un-needed columns
df_compressed =


#final dataframe (sorted)
df_f_sort = df_compressed.sort_values(by='date_datetime')








#test Arsenal
#df_ars = df_compressed[df_compressed['title']=='Arsenal']
# df_ars.to_csv('av_ars.csv', index=False)

# print(df_compressed[df_compressed['date'] =='2025-03-16 13:30:00'])#this looks different in excel, need to use this type of string
# print(df_compressed[df_compressed['title']=='Arsenal'])
# print(df_compressed[df_compressed['date_datetime'] =='2025-03-16 13:30:00'])

# print(df_compressed['date'].iloc[-5:])  # Print first few values



