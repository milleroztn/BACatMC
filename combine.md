[back to main](https://milleroztn.github.io/BACatMC-2021/)

-   <a href="#introduction" id="toc-introduction">Introduction</a>
-   <a href="#import-modules" id="toc-import-modules">Import Modules</a>
-   <a href="#import-reformatted-data-files" id="toc-import-reformatted-data-files">Import Reformatted Data Files</a>
-   <a href="#prepare-community-district-data" id="toc-prepare-community-district-data">Prepare Community District Data</a>
-   <a href="#merge-with-sub-borough-data" id="toc-merge-with-sub-borough-data">Merge With Sub-borough Data</a>
-   <a href="#export" id="toc-export">Export</a>

# Introduction
This script is the second part of a two-stage data-cleaning process that consolidates raw data from multiple Excel files into a single panel dataset. The data contains housing data, demographic data, and covid data for geographic sub-regions of New York City.

This script combines data that has already been reshaped by the script [reshape.py](https://milleroztn.github.io/BACatMC-2021/reshape). Community districts must be combined/aggregated into the corresponding sub-borough.

The output of this script is a single time-series data frame organized by sub-borough, and exported as [bac.csv](https://github.com/milleroztn/BACatMC-2021/blob/main/data/bac.csv).

# Import Modules


```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import Series, DataFrame
from numpy import nan as NA
```

# Import Reformatted Data Files


```python
covid = pd.read_excel('rawdata/NYC-COVID-data.xlsx').iloc[:,:10]
covmatch = pd.read_excel('rawdata/covidmatch.xlsx').iloc[:,:2]
cd_data = pd.read_csv('data/cd_data.csv')
sb_data = pd.read_csv('data/sb_data.csv')
gid_data = pd.read_csv('data/gid_data.csv')
```

'covmatch' is a matching document created manually to match neighborhood name to sub-borough ID.
# Prepare Community District Data
## Add COVID and GID data to Community District Data


```python
covid = covid.merge(covmatch,on="NEIGHBORHOOD_NAME", how='left').iloc[:,3:]
cd_data = cd_data.merge(gid_data, how='left', on='gid').dropna(axis=1, how='all')
cd_data = cd_data.merge(covid, how='left', on='gid').dropna(axis=1, how='all')
```

I first have to add gids to the covid data from the covmatch file. Then I combine COVID data and other GID data to the appropriate community district. These time-invariant variables are all repeated for each year.

Some sub-boroughs contain multiple community districts. In order to combine community district variables that are measured as averages or percents into sub-borough level, I create weights based on estimated population. Variables measured as counts will just need to be summed across combined districts.
## Set Weights


```python
cd_pops = cd_data.loc[cd_data.year == 2000,[
    'gid', 'Bicycle Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)',
    'Bicycle Injury Hospitalizations_Number',
    'Pedestrian Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)',
    'Pedestrian Injury Hospitalizations_Number',
    'Non-fatal Assault Hospitalizations_Age-Adjusted Rate (per 100,000 residents)',
    'Non-fatal Assault Hospitalizations_Number']].loc[
        cd_data.gid.isin([104,105,201,202,203,206]),:]
```

Relative population estimates are generated from each of the available per-capita variables.


```python
cd_pops['pop1'] = 100000*cd_pops['Bicycle Injury Hospitalizations_Number']/cd_pops[
    'Bicycle Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)']
cd_pops['pop2'] = 100000*cd_pops['Pedestrian Injury Hospitalizations_Number']/cd_pops[
    'Pedestrian Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)']
cd_pops['pop3'] = 100000*cd_pops['Non-fatal Assault Hospitalizations_Number']/cd_pops[
    'Non-fatal Assault Hospitalizations_Age-Adjusted Rate (per 100,000 residents)']
cd_pops['population'] = cd_pops.loc[:,['pop1','pop2','pop3']].mean(axis=1)

cd_pops = cd_pops.loc[:,['gid','population']]
```

The result is three different population estimates (which are all fairly similar). The final estimate of population within each district is the avarege of these three estimates.


```python
cd_data = cd_data.merge(cd_pops, how='left', on='gid')
cd_data['weight'] = np.where(cd_data['population'].isna(), 1, cd_data['population'])
cd_data['weight'] = np.where(cd_data['POP_DENOMINATOR'].isna(), cd_data[
    'weight'], cd_data['POP_DENOMINATOR'])
```

Weights are set based on population estimate.
## Combine Community Districts into Sub-boroughs


```python
cdbysb = cd_data.loc[:,['sb','year']].drop_duplicates().sort_values(by=['sb','year'])
```

I start by creating a new data frame with the right shape. The data frame 'cdbysb' has one row for each sub-borough in each year that we have measurements.


```python
for v in cd_data.loc[:,~cd_data.columns.isin([
        'year', 'volume_1f', 'volume_cn', 'District Name', 'br', 'gid', 'sb', 
        'population', 'weight', 'Pedestrian Injury Hospitalizations_Number', 
        'Non-fatal Assault Hospitalizations_Number',
        'Chronic Obstructive Pulmonary Disease  Hospitalization_Number',
        'Bicycle Injury Hospitalizations_Number',
        'COVID_CASE_COUNT', 'COVID_DEATH_COUNT', 'TOTAL_COVID_TESTS', 'POP_DENOMINATOR'])]:
    cdbysb = cdbysb.merge(cd_data.groupby(['sb','year']).apply(lambda g: np.average(
    g[v], weights=g.weight)).rename(v).reset_index(), on=['sb','year'])
```

I first combine the variables of cd_data that are averages or percents to the sub-borough level with a weighted average function of any districts that need to be combined.


```python
for v in ['volume_1f', 'volume_cn', 'COVID_CASE_COUNT', 'COVID_DEATH_COUNT', 'TOTAL_COVID_TESTS', 
          'POP_DENOMINATOR', 'Bicycle Injury Hospitalizations_Number',
          'Pedestrian Injury Hospitalizations_Number', 
          'Non-fatal Assault Hospitalizations_Number', 
          'Chronic Obstructive Pulmonary Disease  Hospitalization_Number']:
        cdbysb = cdbysb.merge(cd_data.groupby(['sb','year']).apply(lambda g: np.sum(
    g[v])).rename(v).reset_index(), on=['sb','year'])
cdbysb.rename(columns={'POP_DENOMINATOR':'pop_covid_region'}, inplace=True)
```

All the count variables are summed when multiple districts are combined into a single sub-borough.
# Merge With Sub-borough Data


```python
for i in sb_data['sb'].drop_duplicates():
    missingyears = pd.DataFrame({'sb':[i,i,i,i],'year':[2001,2002,2003,2019]})
    sb_data = pd.concat([sb_data, missingyears], ignore_index=True)    
```

Original sub-borough variables don't have any data for years 2001, 2002, 2003, or 2019. I add empty rows that the other data frames can attach to.


```python
bac = sb_data.merge(gid_data, how='left', left_on='sb', right_on='gid').dropna(axis=1, how='all')
bac = bac.merge(covid, how='left', left_on='sb', right_on='gid').dropna(axis=1, how='all')
bac = bac.merge(cdbysb, on=['sb','year'], how='outer')

bac['rent_pct_nycha'] = np.where(bac['rent_pct_nycha_x'].isna(), bac[
    'rent_pct_nycha_y'], bac['rent_pct_nycha_x'])
bac.drop(['rent_pct_nycha_x','rent_pct_nycha_y'], axis=1, inplace=True)
```

I also combine rent_pct_nycha from 2017, 2018 into a single variable
# Export


```python
bac.to_csv('data/bac.csv', index=False)
```

The final 'bac' data frame has 1100 rows (55 sub-boroughs and 20 years) and 71 variables.
