import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import Series, DataFrame
from numpy import nan as NA

covid = pd.read_excel('rawdata/NYC-COVID-data.xlsx').iloc[:,:10]
## covid match document created manually to match neighborhood name to sb
covmatch = pd.read_excel('rawdata/covidmatch.xlsx').iloc[:,:2]
cd_data = pd.read_csv('data/cd_data.csv')
sb_data = pd.read_csv('data/sb_data.csv')
gid_data = pd.read_csv('data/gid_data.csv')


### prep COVID data to combine
## add gids to the covid data
covid = covid.merge(covmatch,on="NEIGHBORHOOD_NAME", how='left').iloc[:,3:]

### combine gid_data and covid data to cd_data
cd_data = cd_data.merge(gid_data, how='left', on='gid').dropna(axis=1, how='all')
cd_data = cd_data.merge(covid, how='left', on='gid').dropna(axis=1, how='all')

### get relative populations of cds to combine
cd_pops = cd_data.loc[cd_data.year == 2000,[
    'gid', 'Bicycle Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)',
    'Bicycle Injury Hospitalizations_Number',
    'Pedestrian Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)',
    'Pedestrian Injury Hospitalizations_Number',
    'Non-fatal Assault Hospitalizations_Age-Adjusted Rate (per 100,000 residents)',
    'Non-fatal Assault Hospitalizations_Number']].loc[
        cd_data.gid.isin([104,105,201,202,203,206]),:]

cd_pops['pop1'] = 100000*cd_pops['Bicycle Injury Hospitalizations_Number']/cd_pops['Bicycle Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)']
cd_pops['pop2'] = 100000*cd_pops['Pedestrian Injury Hospitalizations_Number']/cd_pops['Pedestrian Injury Hospitalizations_Age-Adjusted Rate (per 100,000 residents)']
cd_pops['pop3'] = 100000*cd_pops['Non-fatal Assault Hospitalizations_Number']/cd_pops['Non-fatal Assault Hospitalizations_Age-Adjusted Rate (per 100,000 residents)']
cd_pops['population'] = cd_pops.loc[:,['pop1','pop2','pop3']].mean(axis=1)

cd_pops = cd_pops.loc[:,['gid','population']]

### set weights for combining (based on estimated population)
cd_data = cd_data.merge(cd_pops, how='left', on='gid')
cd_data['weight'] = np.where(cd_data['population'].isna(), 1, cd_data['population'])
cd_data['weight'] = np.where(cd_data['POP_DENOMINATOR'].isna(), cd_data['weight'], cd_data['POP_DENOMINATOR'])
cd_data.sort_values(by=['sb','year'])

### combine cds into sb level
cdbysb = cd_data.loc[:,['sb','year']].drop_duplicates().sort_values(by=['sb','year'])


for v in cd_data.loc[:,~cd_data.columns.isin([
        'year', 'volume_1f', 'volume_cn', 'District Name', 'br', 'gid', 'sb', 
        'population', 'weight', 'Pedestrian Injury Hospitalizations_Number', 
        'Non-fatal Assault Hospitalizations_Number',
        'Chronic Obstructive Pulmonary Disease  Hospitalization_Number',
        'Bicycle Injury Hospitalizations_Number',
        'COVID_CASE_COUNT', 'COVID_DEATH_COUNT', 'TOTAL_COVID_TESTS', 'POP_DENOMINATOR'])]:
    cdbysb = cdbysb.merge(cd_data.groupby(['sb','year']).apply(lambda g: np.average(
    g[v], weights=g.weight)).rename(v).reset_index(), on=['sb','year'])
    
       
for v in ['volume_1f', 'volume_cn', 'COVID_CASE_COUNT', 'COVID_DEATH_COUNT', 'TOTAL_COVID_TESTS', 
          'POP_DENOMINATOR', 'Bicycle Injury Hospitalizations_Number',
          'Pedestrian Injury Hospitalizations_Number', 
          'Non-fatal Assault Hospitalizations_Number', 
          'Chronic Obstructive Pulmonary Disease  Hospitalization_Number']:
        cdbysb = cdbysb.merge(cd_data.groupby(['sb','year']).apply(lambda g: np.sum(
    g[v])).rename(v).reset_index(), on=['sb','year'])

       
cdbysb.rename(columns={'POP_DENOMINATOR':'pop_covid_region'}, inplace=True)

### combine gid_data and covid data to sb_data
for i in sb_data['sb'].drop_duplicates():
    missingyears = pd.DataFrame({'sb':[i,i,i,i],'year':[2001,2002,2003,2019]})
    sb_data = pd.concat([sb_data, missingyears], ignore_index=True)    


sb_data = sb_data.merge(gid_data, how='left', left_on='sb', right_on='gid').dropna(axis=1, how='all')
sb_data = sb_data.merge(covid, how='left', left_on='sb', right_on='gid').dropna(axis=1, how='all')

#### combine datasets ####

## combine sb-year level data first, then sb-level data will repeat for all years
## also combine rent_pct_nycha from 2017,2018 into a single variable
bac = sb_data.merge(cdbysb, on=['sb','year'], how='outer')

bac['rent_pct_nycha'] = np.where(bac['rent_pct_nycha_x'].isna(), bac['rent_pct_nycha_y'], bac['rent_pct_nycha_x'])
bac.drop(['rent_pct_nycha_x','rent_pct_nycha_y'], axis=1, inplace=True)

#### export
bac.to_csv('data/bac.csv', index=False)
