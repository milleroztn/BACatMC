import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import Series, DataFrame
from numpy import nan as NA


### Rosetta Stone- match Geography IDs for Sub-boroughs and Community Districts
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=8)

stone = raw.loc[raw.GeoTypeName == 'Neighborhood (Sub-borough/PUMA)',:]
stone = stone.iloc[:,:8]
stone = stone.merge(raw.iloc[:,[1,2,3,4,6,7]], on=['Number','Percent of Households'], how='left')
stone.loc[:,'Sub-Borough Area'] = stone['Geography_x'].str.slice(start=16)
stone.rename(columns={'Geography ID_x':'sb', 'Geography ID_y':'gid'}, inplace=True)
stone.to_csv('data/stone.csv', index=False)

## gids for each sub-borough
sbids = stone.loc[:,['sb','Sub-Borough Area']].drop_duplicates()

### Sub-borough Variables

# Import and reshape first Sub-borough sheet
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=4)
sb_data = raw.melt(raw.columns[2],raw.columns[3:18],'year',raw.short_name[0])

# repeat process for every other Sub-borough sheet and join to existing data
sb = list(range(5,8))+list(range(9,13))
for i in sb:
    raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2],raw.columns[3:18],'year',raw.short_name[0]).dropna()
    sb_data = sb_data.merge(sheet, how='outer')

# % public housing has some Community Districts and some Sub-boroughs
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=13)
sheet = raw.iloc[:,7:11].melt(raw.columns[9],raw.columns[10],'year',raw.short_name[0]).dropna()
sb_data = sb_data.merge(sheet, how='outer')

# same process for demographic data
## first two don't have short names for some reason
for i in range(2):
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[1],raw.columns[2:16],'year',raw.long_name[0]).dropna()
    sb_data = sb_data.merge(sheet, how='outer')
    
for i in range(7,11):
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2],raw.columns[3:18],'year',raw.short_name[0]).dropna()
    sb_data = sb_data.merge(sheet, how='outer')
    
### Add IDs
sb_data = sb_data.merge(sbids,how='left')

# check for missing ids
sb_data.loc[sb_data.sb.isna(),'Sub-Borough Area'].unique()

# manual fix
sb_data.loc[sb_data['Sub-Borough Area']=='Rego Park/Forest Hills', 'sb'] = 44
sb_data.loc[sb_data['Sub-Borough Area']=='Ozone Park/Woodhaven', 'sb'] = 47
sb_data.loc[sb_data['Sub-Borough Area']=='South Ozone Park/Howard Beach', 'sb'] = 48
sb_data.loc[sb_data['Sub-Borough Area']=='Queens Village', 'sb'] = 51
sb_data.loc[sb_data['Sub-Borough Area']=='Mid-Island', 'sb'] = 54
sb_data.loc[sb_data['Sub-Borough Area']=='Morrisania/Belmont', 'sb'] = 2
sb_data.loc[sb_data['Sub-Borough Area']=='East New York/Starrett City', 'sb'] = 15
sb_data.loc[sb_data['Sub-Borough Area']=='North Crown Heights/Prospect Heights', 'sb'] = 18

# export
sb_data.to_csv('data/sb_data.csv', index=False)

### Community District Variables

# import and reshape first Community-district sheet
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=0)
cd_data = raw.melt(raw.columns[2],raw.columns[3:22],'year',raw.short_name[0]).dropna()

# repeat process for every other Community-district sheet and join to existing data
for i in range(1,4):
    raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2],raw.columns[3:22],'year',raw.short_name[0]).dropna()
    cd_data = cd_data.merge(sheet, how='outer')

# % public housing has some Community Districts and some Sub-boroughs
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=13)
sheet = raw.iloc[:,:4].melt(raw.columns[2],raw.columns[3],'year',raw.short_name[0]).dropna()
cd_data = cd_data.merge(sheet, how='outer')

# same process for demographic data
## first one doesn't have short name for some reason
## BK 08 - Crown Heights/Prospect Heights was in 'serious crime' twice and
## duplicate row has been previously removed
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=2)
sheet = raw.melt(raw.columns[1],raw.columns[2:16],'year',raw.long_name[0]).dropna()
cd_data = cd_data.merge(sheet, how='outer')
    
for i in range(3,7):
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2],raw.columns[3:9],'year',raw.short_name[0]).dropna()
    cd_data = cd_data.merge(sheet, how='outer')

## repeat one-time (no year) data for all years
cd_data['prox_subway_pct'] = cd_data.groupby('Community District')['prox_subway_pct'].transform(
    lambda g: g.fillna(g.mean()))

cd_data['prox_park_pct'] = cd_data.groupby('Community District')['prox_park_pct'].transform(
    lambda g: g.fillna(g.mean()))

### Add IDs
# borough is IDed by two letter; change them to the appropriate gid numbers
cd_data[['bid','District Name']] = cd_data['Community District'].str.split(' - ', expand=True)
cd_data[['br','id']] = cd_data['bid'].str.split(' ', expand=True)
cdidkey = pd.DataFrame({
    'br': ["BX", "BK", "QN", "SI", "MN"],
    'b': [2,3,4,5,1]
    })
cd_data = cd_data.merge(cdidkey, how='outer')
cd_data['gid'] = cd_data['b'].astype(str) + cd_data['id']
cd_data['gid'] = cd_data.gid.astype(int)
cd_data.drop(columns=['Community District', 'bid', 'b', 'id'], inplace=True)

# match each Community District gid with the corresponding Sub-borough ID
cd_data = cd_data.merge(stone.loc[:,['sb','gid']], how='left')

## export
cd_data.to_csv('data/cd_data.csv', index=False)

### GID variables- already wide; sheets have different numbers of variables

## begin with crowding, same as from Rosetta stone
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=8)
gid_data = raw.loc[raw.GeoTypeName == 'Neighborhood (Sub-borough/PUMA)'].iloc[:,[4,6,7]]
gid_data.rename(columns = {'Number':'crowding_number', 'Percent of Households':'crowding_percent'}, inplace=True)

#single variable, remove city- and borough-level observations
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=13)
sheet = raw.iloc[6:,[4,6]]
sheet.columns = pd.concat([
    Series(sheet.columns[0]), sheet.columns[[1]].to_series().apply(
        lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
gid_data = gid_data.merge(sheet, how='outer')

#single variable, no removals
for i in [12,14]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.iloc[:,[4,6]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')

#2 vars
for i in [11,15]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.loc[raw.GeoTypeName == 'Neighborhood (Sub-borough/PUMA)'].iloc[:,[4,6,7]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1,2]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')
    
for i in [16,20,21,22]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.iloc[:,[4,6,7]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1,2]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')

#3 vars
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=23)
sheet = raw.iloc[:,[4,6,7,8]]
sheet.columns = pd.concat([
    Series(sheet.columns[0]), sheet.columns[[1,2,3]].to_series().apply(
        lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
gid_data = gid_data.merge(sheet, how='outer')

#4 vars, remove city- and borough-level observations
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=18)
sheet = raw.iloc[6:,[4,6,7,8,9]]
sheet.columns = pd.concat([
    Series(sheet.columns[0]), sheet.columns[[1,2,3,4]].to_series().apply(
        lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
gid_data = gid_data.merge(sheet, how='outer')

#6 vars
for i in [17,19]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.iloc[:,[4,6,7,8,9,10,11]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1,2,3,4,5,6]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')

#rename gid
gid_data.rename(columns={'Geography ID':'gid'}, inplace=True)

## export
gid_data.to_csv('data/gid_data.csv', index=False)