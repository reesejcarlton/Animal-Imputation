# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 22:28:37 2024

@author: reese
"""


import os
import requests
import numpy as np
from io import StringIO
import pandas as pd

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_dir)

# NOAA data

# from https://www.ncei.noaa.gov/pub/data/cirs/climdiv/
# README file: https://www.ncei.noaa.gov/pub/data/cirs/climdiv/county-readme.txt
# in this file CA state code is 04 (not 06)
noaa_pcp_url = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-pcpncy-v1.0.0-20240706.txt"
noaa_tmax_url = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-tmaxcy-v1.0.0-20240706.txt"
noaa_tmin_url = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-tmincy-v1.0.0-20240706.txt"
noaa_tavg_url = 'https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-tmpccy-v1.0.0-20240706.txt'
noaa_ccd_url = 'https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-cddccy-v1.0.0-20240706.txt'
noaa_hhd_url = 'https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-hddccy-v1.0.0-20240706.txt'


def get_noaa_data_df(target_url):
    noaa_data = requests.get(target_url)    
    noaa_month_colnames= ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    noaa_df = pd.read_csv(StringIO(noaa_data.text), lineterminator="\n", sep=r"\s+", header=None, names=["ID", *noaa_month_colnames], index_col=False, dtype="string")
    return noaa_df

pcp_data_df = get_noaa_data_df(noaa_pcp_url)
tmax_data_df = get_noaa_data_df(noaa_tmax_url)
tmin_data_df = get_noaa_data_df(noaa_tmin_url)
tavg_data_df = get_noaa_data_df(noaa_tavg_url)
ccd_data_df = get_noaa_data_df(noaa_ccd_url)
hhd_data_df = get_noaa_data_df(noaa_hhd_url)

# Concatenate NOAA dfs together
noaa_full_df = pd.concat([pcp_data_df, tmax_data_df, tmin_data_df, tavg_data_df, ccd_data_df, hhd_data_df], axis=0)
#%%
# Extract NOAA ID
def extract_noaa_id(df):
    df["STATE_CODE"] = df["ID"].str[:2]
    df["FIPS_CODE"] = df["ID"].str[2:5]
    df["ELEMENT_CODE"] = df["ID"].str[5:7]
    df["YEAR"] = df["ID"].str[7:]
    return df

extract_noaa_id(noaa_full_df)
# Map element codes to descriptive abbreviation

element_code_map = {
# element codes from docs
    "01": "pcp", # Precipitation
    "02": "tavg", # Average Temperature
    "25": "Heating Degree Days",
    "26": "Cooling Degree Days",
    "27": "tmax", # Maximum Temperature
    "28": "tmin" # Minimum Temperature
}

noaa_full_df["NOAA_ELEMENT"] = noaa_full_df["ELEMENT_CODE"].map(element_code_map).fillna(noaa_full_df["ELEMENT_CODE"])

years = [str(x) for x in np.arange(2013, 2024)]
noaa_shortened_df = noaa_full_df[noaa_full_df['YEAR'].isin(years)]
# FIPS Codes
#%%
# List of filenames
filenames = [
    "st01_al_cou2020.txt", "st02_ak_cou2020.txt", "st04_az_cou2020.txt", "st05_ar_cou2020.txt", 
    "st06_ca_cou2020.txt", "st08_co_cou2020.txt", "st09_ct_cou2020.txt", "st10_de_cou2020.txt", 
    "st11_dc_cou2020.txt", "st12_fl_cou2020.txt", "st13_ga_cou2020.txt", "st15_hi_cou2020.txt", 
    "st16_id_cou2020.txt", "st17_il_cou2020.txt", "st18_in_cou2020.txt", "st19_ia_cou2020.txt", 
    "st20_ks_cou2020.txt", "st21_ky_cou2020.txt", "st22_la_cou2020.txt", "st23_me_cou2020.txt", 
    "st24_md_cou2020.txt", "st25_ma_cou2020.txt", "st26_mi_cou2020.txt", "st27_mn_cou2020.txt", 
    "st28_ms_cou2020.txt", "st29_mo_cou2020.txt", "st30_mt_cou2020.txt", "st31_ne_cou2020.txt", 
    "st32_nv_cou2020.txt", "st33_nh_cou2020.txt", "st34_nj_cou2020.txt", "st35_nm_cou2020.txt", 
    "st36_ny_cou2020.txt", "st37_nc_cou2020.txt", "st38_nd_cou2020.txt", "st39_oh_cou2020.txt", 
    "st40_ok_cou2020.txt", "st41_or_cou2020.txt", "st42_pa_cou2020.txt", "st44_ri_cou2020.txt", 
    "st45_sc_cou2020.txt", "st46_sd_cou2020.txt", "st47_tn_cou2020.txt", "st48_tx_cou2020.txt", 
    "st49_ut_cou2020.txt", "st50_vt_cou2020.txt", "st51_va_cou2020.txt", "st53_wa_cou2020.txt", 
    "st54_wv_cou2020.txt", "st55_wi_cou2020.txt", "st56_wy_cou2020.txt"
]

# from https://www.census.gov/library/reference/code-lists/ansi.html#cou
fips_url = "https://www2.census.gov/geo/docs/reference/codes2020/cou/"

# List to store dataframes
dataframes = []

# Fetch data and append to the list
for filename in filenames:
    fips_data = requests.get(fips_url + filename)
    fips_df = pd.read_csv(StringIO(fips_data.text), lineterminator="\n", sep="|", dtype="string")
    dataframes.append(fips_df)

# Concatenate all dataframes
all_fips_df = pd.concat(dataframes, ignore_index=True)
all_fips_df["FULLFP"] = all_fips_df["STATEFP"] + all_fips_df["COUNTYFP"]

state_code_to_name = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

mapping_dict = {
    "01": "01",  # Alabama
    "02": "04",  # Arizona
    "03": "05",  # Arkansas
    "04": "06",  # California
    "05": "08",  # Colorado
    "06": "09",  # Connecticut
    "07": "10",  # Delaware
    "08": "12",  # Florida
    "09": "13",  # Georgia
    "10": "16",  # Idaho
    "11": "17",  # Illinois
    "12": "18",  # Indiana
    "13": "19",  # Iowa
    "14": "20",  # Kansas
    "15": "21",  # Kentucky
    "16": "22",  # Louisiana
    "17": "23",  # Maine
    "18": "24",  # Maryland
    "19": "25",  # Massachusetts
    "20": "26",  # Michigan
    "21": "27",  # Minnesota
    "22": "28",  # Mississippi
    "23": "29",  # Missouri
    "24": "30",  # Montana
    "25": "31",  # Nebraska
    "26": "32",  # Nevada
    "27": "33",  # New Hampshire
    "28": "34",  # New Jersey
    "29": "35",  # New Mexico
    "30": "36",  # New York
    "31": "37",  # North Carolina
    "32": "38",  # North Dakota
    "33": "39",  # Ohio
    "34": "40",  # Oklahoma
    "35": "41",  # Oregon
    "36": "42",  # Pennsylvania
    "37": "44",  # Rhode Island
    "38": "45",  # South Carolina
    "39": "46",  # South Dakota
    "40": "47",  # Tennessee
    "41": "48",  # Texas
    "42": "49",  # Utah
    "43": "50",  # Vermont
    "44": "51",  # Virginia
    "45": "53",  # Washington
    "46": "54",  # West Virginia
    "47": "55",  # Wisconsin
    "48": "56",  # Wyoming
    "50": "02"   # Alaska
}

all_fips_df['STATE'] = all_fips_df['STATE'].map(state_code_to_name)
noaa_shortened_df['STATE_CODE'] = noaa_shortened_df['STATE_CODE'].map(mapping_dict)
noaa_shortened_df["FULLFP"] = noaa_shortened_df["STATE_CODE"] + noaa_shortened_df["FIPS_CODE"]

#%%
# Join to FIPS df
noaa_counties_df = pd.merge(all_fips_df[["FULLFP", "COUNTYNAME", 'STATE']], noaa_shortened_df, left_on="FULLFP", right_on="FULLFP")
#%%
noaa_counties_df = noaa_counties_df.drop(["ID","STATE_CODE", "ELEMENT_CODE", 'YEAR', "FIPS_CODE"], axis = 1)
noaa_counties_df["COUNTYNAME"] = noaa_counties_df["COUNTYNAME"].str.split().apply(lambda row: ' '.join(row[:-1]))
new_order = ['FULLFP', 'STATE', 'COUNTYNAME', 'NOAA_ELEMENT', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL','AUG', 'SEP', 'OCT', 'NOV', 'DEC']
noaa_counties_df = noaa_counties_df[new_order]
noaa_counties_df.iloc[:, 4:] = noaa_counties_df.iloc[:, 4:].astype(float)
noaa_counties_average_df = noaa_counties_df.groupby(by=["FULLFP", 'STATE', "COUNTYNAME", "NOAA_ELEMENT"]).mean().reset_index()
noaa_counties_average_df['STATE'] = noaa_counties_average_df['STATE'].str.lower()
noaa_counties_average_df['COUNTYNAME'] = noaa_counties_average_df['COUNTYNAME'].str.lower()
noaa_counties_average_df['COUNTYNAME'] = noaa_counties_average_df['COUNTYNAME'].str.replace(' ', '')
noaa_counties_average_df['COUNTYNAME'] = noaa_counties_average_df['COUNTYNAME'].str.replace('.', '')
noaa_counties_average_df['COUNTYNAME'] = noaa_counties_average_df['COUNTYNAME'].str.replace("'", '')
noaa_counties_average_df['COUNTYNAME'] = noaa_counties_average_df['COUNTYNAME'].str.replace("doã±aana", 'donaana')
noaa_counties_average_df.loc[
    (noaa_counties_average_df['STATE'] == 'nevada') & 
    (noaa_counties_average_df['COUNTYNAME'] == 'carson'), 
    'COUNTYNAME'
] = 'carsoncity'

# Pivot the table
df_pivot = noaa_counties_average_df.pivot_table(index=['FULLFP', 'STATE','COUNTYNAME'], columns='NOAA_ELEMENT', aggfunc='first')

# Flatten the MultiIndex in columns
df_pivot.columns = [f'{col[1]}_{col[0]}' for col in df_pivot.columns]

# Reset the index to turn the MultiIndex into columns
df_pivot = df_pivot.reset_index()
#%%
df_pivot.to_csv("../Data/NOAA County Temperature Data 2013-2023.csv", index=False)