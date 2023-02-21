import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

dypro_values_df = pd.read_csv(
        '/Users/nick/sleepertoolsversion2/values/dypro_values.csv')
ktc_values_df = pd.read_csv(
        '/Users/nick/sleepertoolsversion2/values/ktc_values.csv')

etr_values_df = pd.read_csv(
        '/Users/nick/sleepertoolsversion2/values/etr_ranks.csv')

merged_df = ktc_values_df.merge(etr_values_df, on='merge_name', how='left')
values_df = merged_df.merge(dypro_values_df, on='merge_name', how='left')

values_df['HIM VALUE'] = round(values_df[['KTC Value', 'ETR Value', 'DyPro Value']].mean(axis=1),0)
values_df['Uncertainty'] = round(values_df[['KTC Value', 'ETR Value', 'DyPro Value']].std(axis=1),0)
values_df['High Rank'] = values_df[['KTC Rank', 'ETR Rank', 'DyPro Rank']].min(axis=1)
values_df['Low Rank'] = values_df[['KTC Rank', 'ETR Rank', 'DyPro Rank']].max(axis=1)
values_df['High Source'] = values_df[['KTC Rank', 'ETR Rank', 'DyPro Rank']].apply(lambda x: x.idxmin(), axis=1)
values_df['Low Source'] = values_df[['KTC Rank', 'ETR Rank', 'DyPro Rank']].apply(lambda x: x.idxmax(), axis=1)


values_df['HIM RANK'] = values_df['HIM VALUE'].rank(ascending=False, method='dense')
values_df.rename(columns={'dypro_age':'Age'}, inplace=True)
missing_cols = ['KTC Value', 'DyPro Value', 'ETR Value']
values_df = values_df[(values_df['HIM VALUE'].notna())]

# missing_values_slice = missing_values_slice[(missing_values_slice['team'].notna())]
#
# missing_values_slice = missing_values_slice.loc[missing_values_slice[missing_cols].isna().any(axis=1), :]
# print(missing_values_slice[['full_name','merge_name','position','team','etr_name','ktc_name','dypro_name']])
values_df = values_df[['merge_name', 'HIM RANK', 'Age', 'HIM VALUE','Uncertainty','High Rank','Low Rank','High Source','Low Source']]
values_df.to_csv('/Users/nick/sleepertoolsversion2/values/values.csv', index=False)
