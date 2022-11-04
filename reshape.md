[back to main](https://milleroztn.github.io/BACatMC/)

-   <a href="#introduction" id="toc-introduction">Introduction</a>
-   <a href="#import-modules" id="toc-import-modules">Import Modules</a>
-   <a href="#rosetta-stone" id="toc-rosetta-stone">"Rosetta Stone" matching document</a>
-   <a href="#variables-measured-at-sub-borough-level" id="toc-variables-measured-at-sub-borough-level">Sub-borough Variables</a>
-   <a href="#variables-measured-at-community-district-level" id="toc-variables-measured-at-community-district-level">Community District Variables</a>
-   <a href="#other-gid-variables" id="toc-other-gid-variables">Other GID Variables</a>

# Introduction 
This script is the first part of a two-stage data-cleaning process that consolidates raw data from multiple Excel files into a single panel dataset. The data contains housing data, demographic data, and covid data for geographic sub-regions of New York City.

This script reformats each of the variables in the raw data from its various formats into conventional region-year format.

The outputs of this script are:
- [stone.csv](https://github.com/milleroztn/BACatMC/blob/main/data/stone.csv), which matches each community district with the appropriate sub-borough and provides Geography IDs for each community district and sub-burough region.
- [SB_data.csv](https://github.com/milleroztn/BACatMC/blob/main/data/SB_data.csv), which contains all variables that are organized by sub-borough region and year.
- [CD_data.csv](https://github.com/milleroztn/BACatMC/blob/main/data/CD_data.csv), which contains all variables that are organized by community district region and year.
- [gid_data.csv](https://github.com/milleroztn/BACatMC/blob/main/data/gid_data.csv), which contains all variables that are organized by Geography ID, which are either by sub-borough or by community district.


## Import Modules


```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import Series, DataFrame
from numpy import nan as NA
```

This script does not use all of these modules, but these are the modules I routinely import at the start of all of my data scripts.

## "Rosetta Stone"
I noticed that the sheet for the 'Crowding' variable had measurements for each sub-borough and for each community district, as well as the Geography ID associated with each region. Additionally, the actual values are the same for every community district that is associated with the same sub-borough (perhaps all measurements are at the sub-borough level, even if listed as community district). I use this information to a) match each region with the appropriate ID, and b) match each sub-borough with the corresponding community districts.



```python
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=8)

stone = raw.loc[raw.GeoTypeName=='Neighborhood (Sub-borough/PUMA)', :]
stone = stone.iloc[:,:8]
stone = stone.merge(raw.iloc[:,[1,2,3,4,6,7]], on=[
    'Number','Percent of Households'], how='left')
stone.loc[:,'Sub-Borough Area'] = stone['Geography_x'].str.slice(start=16)
stone.rename(columns={'Geography ID_x':'sb', 'Geography ID_y':'gid'}, inplace=True)
stone.to_csv('data/stone.csv', index=False)
```

The sheet numbers and column locations are taken from observing the organization of the Excel spreadsheets. This script will only work on the unchanged/unsorted original raw data.

## Variables Measured at Sub-borough Level

### Import and reshape first sub-borough sheet/variable


```python
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=4)
sb_data = raw.melt(raw.columns[2], raw.columns[3:18], 'year', raw.short_name[0])
```

Each sheet in the housing data and the demographic data files represents a single variable. Individual observations are identified by 'Sub-Borough Area' (third column), and each year of data is unpivoted into a new 'year variable'. The result is one column identifying sub-borough, one identifying year, and one for the actual variable values (the short name is used as the variable name).

### Repeat process for every other Sub-borough sheet and join to existing data


```python
%%capture --no-display  
# to hide merge warning

sb = list(range(5,8))+list(range(9,13))
for i in sb:
    raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2], raw.columns[3:18], 'year', raw.short_name[0]).dropna()
    sb_data = sb_data.merge(sheet, how='outer')

raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=13)
sheet = raw.iloc[:,7:11].melt(
    raw.columns[9], raw.columns[10], 'year', raw.short_name[0]).dropna()
sb_data = sb_data.merge(sheet, how='outer')
```

Variable '% public housing' has some observations by sub-borough and others by community district. Here I isolate the sub-borough ones to add to the growing sb_data dataframe.


```python
for i in range(2):
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[1], raw.columns[2:16], 'year', raw.long_name[0]).dropna()
    sb_data = sb_data.merge(sheet, how='outer')
```

The first two demographic sheets don't have short names for some reason. I use the long name instead.


```python
for i in range(7,11):
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2], raw.columns[3:18], 'year', raw.short_name[0]).dropna()
    sb_data = sb_data.merge(sheet, how='outer')   
```

### Add IDs from "Rosetta Stone"


```python
sbids = stone.loc[:,['sb','Sub-Borough Area']].drop_duplicates()
sb_data = sb_data.merge(sbids, how='left')

sb_data.loc[sb_data.sb.isna(),'Sub-Borough Area'].unique()
```




    array(['Rego Park/Forest Hills', 'Ozone Park/Woodhaven',
           'South Ozone Park/Howard Beach', 'Queens Village', 'Mid-Island',
           'Morrisania/Belmont', 'East New York/Starrett City',
           'North Crown Heights/Prospect Heights'], dtype=object)



Generate a list of sub-boroughs that are missing IDs.


```python
sb_data.loc[sb_data['Sub-Borough Area']=='Rego Park/Forest Hills', 'sb'] = 44
sb_data.loc[sb_data['Sub-Borough Area']=='Ozone Park/Woodhaven', 'sb'] = 47
sb_data.loc[sb_data['Sub-Borough Area']=='South Ozone Park/Howard Beach', 'sb'] = 48
sb_data.loc[sb_data['Sub-Borough Area']=='Queens Village', 'sb'] = 51
sb_data.loc[sb_data['Sub-Borough Area']=='Mid-Island', 'sb'] = 54
sb_data.loc[sb_data['Sub-Borough Area']=='Morrisania/Belmont', 'sb'] = 2
sb_data.loc[sb_data['Sub-Borough Area']=='East New York/Starrett City', 'sb'] = 15
sb_data.loc[sb_data['Sub-Borough Area']=='North Crown Heights/Prospect Heights', 'sb'] = 18
```

Manual fix for all the missing IDs.

### Export


```python
sb_data.to_csv('data/sb_data.csv', index=False)
```

The 'sb_data' data frame has 880 rows (55 sub-boroughs by 16 years) and 18 variables.

## Variables Measured at Community District Level

### Import and reshape first community district sheet/variable


```python
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=0)
cd_data = raw.melt(raw.columns[2], raw.columns[3:22], 'year', raw.short_name[0]).dropna()
```

### Repeat process for every other community district sheet and join to existing data


```python
%%capture --no-display  
# to hide merge warning

for i in range(1,4):
    raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2], raw.columns[3:22], 'year', raw.short_name[0]).dropna()
    cd_data = cd_data.merge(sheet, how='outer')

raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=13)
sheet = raw.iloc[:,:4].melt(
    raw.columns[2], raw.columns[3], 'year', raw.short_name[0]).dropna()
cd_data = cd_data.merge(sheet, how='outer')
```

Here I isolate the observations of '% public housing' that organized by community district.


```python
%%capture --no-display  
# to hide merge warning

raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=2)
sheet = raw.melt(raw.columns[1], raw.columns[2:16], 'year', raw.long_name[0]).dropna()
cd_data = cd_data.merge(sheet, how='outer')
```

Again the first demographic variable doesn't have short name; long name used instead.
(Note: BK 08 - Crown Heights/Prospect Heights was in 'serious crime' twice. I removed the duplicate row out of the Excel file before starting this process.)


```python
for i in range(3,7):
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.melt(raw.columns[2], raw.columns[3:9], 'year', raw.short_name[0]).dropna()
    cd_data = cd_data.merge(sheet, how='outer')
```

### Repeat one-time-measured data for all years


```python
cd_data['prox_subway_pct'] = cd_data.groupby('Community District')['prox_subway_pct'].transform(
    lambda g: g.fillna(g.mean()))

cd_data['prox_park_pct'] = cd_data.groupby('Community District')['prox_park_pct'].transform(
    lambda g: g.fillna(g.mean()))
```

### Generate IDs to match with those in "Rosetta Stone"


```python
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

```

Borough is IDed by two letters; I needed to change those to the appropriate gid numbers.


```python
cd_data = cd_data.merge(stone.loc[:,['sb','gid']], how='left')
```

Each Community District gid is matched with the corresponding Sub-borough IDs using the Rosetta Stone file.

### Export


```python
cd_data.to_csv('data/cd_data.csv', index=False)
```

The 'cd_data' data frame has 1179 rows (59 districts for 20 years, and 58 districts for 19 years; only three variables are available in 2019 and there is no data for these for district 501- North Shore Staten Island) and 15 variables.

## Other GID Variables

These variables only have a single measurement (time-invariant), but each sheet has a different number of variables to extract.


```python
raw = pd.read_excel('rawdata/NYC-housing-data.xlsx', sheet_name=8)
gid_data = raw.loc[raw.GeoTypeName == 'Neighborhood (Sub-borough/PUMA)'].iloc[:,[4,6,7]]
gid_data.rename(
    columns = {'Number':'crowding_number', 'Percent of Households':'crowding_percent'}, inplace=True)
```

The first sheet is 'crowding'; the same as used to create the Rosetta Stone file.


```python
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=13)
sheet = raw.iloc[6:,[4,6]]
sheet.columns = pd.concat([
    Series(sheet.columns[0]), sheet.columns[[1]].to_series().apply(
        lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
gid_data = gid_data.merge(sheet, how='outer')
```

This sheet has a single variable, but I also need to remove city- and borough-level observations.


```python
for i in [12,14]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.iloc[:,[4,6]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')
```

These sheets each have a single variable; no removals needed


```python
for i in [11,15]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.loc[raw.GeoTypeName == 'Neighborhood (Sub-borough/PUMA)'].iloc[:,[4,6,7]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1,2]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')
```

These sheets each have two variables, only measured at sub-borough level.


```python
for i in [16,20,21,22]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.iloc[:,[4,6,7]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1,2]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')
```

More sheets with only two variables.


```python
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=23)
sheet = raw.iloc[:,[4,6,7,8]]
sheet.columns = pd.concat([
    Series(sheet.columns[0]), sheet.columns[[1,2,3]].to_series().apply(
        lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
gid_data = gid_data.merge(sheet, how='outer')
```

These sheets each have three variables.


```python
raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=18)
sheet = raw.iloc[6:,[4,6,7,8,9]]
sheet.columns = pd.concat([
    Series(sheet.columns[0]), sheet.columns[[1,2,3,4]].to_series().apply(
        lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
gid_data = gid_data.merge(sheet, how='outer')
```

Four variables; also need to remove city- and borough-level observations.


```python
for i in [17,19]:
    raw = pd.read_excel('rawdata/NYC-demographic-other-data.xlsx', sheet_name=i)
    sheet = raw.iloc[:,[4,6,7,8,9,10,11]]
    sheet.columns = pd.concat([
        Series(sheet.columns[0]), sheet.columns[[1,2,3,4,5,6]].to_series().apply(
            lambda col : raw['Indicator Name'][0]+'_'+col)], ignore_index=True)
    gid_data = gid_data.merge(sheet, how='outer')
```

Last two sheets have 6 variables each.
## Rename gid


```python
gid_data.rename(columns={'Geography ID':'gid'}, inplace=True)
```

## Export


```python
gid_data.to_csv('data/gid_data.csv', index=False)
```

The 'gid_data' data frame has 114 rows (55 sub-buroughs and 59 community districts) and 37 variables.
