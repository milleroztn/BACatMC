# Introduction
This project takes several raw datasets on different geographic regions within New York City and combines them into a single panel dataset organized by sub-borough and year. The raw datasets were collected and provided by Manhattan College to participants in the Business Analytics Competition at Manhattan College in 2021. I created these scripts to support students participating in that competition.

The original data is organized in three excel files: 

- [NYC-housing-data.xlsx](https://github.com/milleroztn/BACatMC-2021/blob/main/rawdata/NYC-housing-data.xlsx)
- [NYC-demographic-other-data.xlsx](https://github.com/milleroztn/BACatMC-2021/blob/main/rawdata/NYC-demographic-other-data.xlsx)
- [NYC-COVID-data.xlsx](https://github.com/milleroztn/BACatMC-2021/blob/main/rawdata/NYC-COVID-data.xlsx)

and contains variables collected from the NYU Furman Center's [coredata.nyc](https://coredata.nyc/), from [NYC.gov](https://a816-dohbesp.nyc.gov/IndicatorPublic/beta/)'s Environment and Health Data, and from the NYC Department of Health and Mental Hygiene's Coronavirus Disease 2019 (COVID-19) in New York City (NYC) data stored at [github.com/nychealth](https://github.com/nychealth).

Some variables are measured by sub-borough and others are measured by community district. Additionally, some variables are measured over time for several years and others are measured only at one point in time. The [variables_summary.xlsx](https://github.com/milleroztn/BACatMC-2021/blob/main/rawdata/variables_summary.xlsx) file lists all the variables in the three raw files, whether they are measured by sub-borough or community district, whether they have a geography ID (a number that uniquely identifies each sub-borough or community district), and in which years each variable is measured. For those variables that have only a single value over time, I have also indicated which years are reflected by that value (e.g., over which years was a single average calculated). An image of this file is presented here:

![variables_summary.png](/BACatMC-2021/rawdata/variables_summary.png)

The data-cleaning process is broken up into two steps:

1. Reformat the original data into conventional region-year format. This is done separately for variables that are organized by sub-burough, community district, or generic Geography ID.

2. Combine the datasets for each region into a single dataset. This requires matching up which community districts are in each sub-borough and in some cases combinind data from multiple community districts into a single sub-borough.

# Reshape Raw Data
[BACatMC- Reshape Raw Data](https://milleroztn.github.io/BACatMC-2021/reshape)
# Combine Reshaped Data
[BACatMC- Combine Reshaped Data](https://milleroztn.github.io/BACatMC-2021/combine)
