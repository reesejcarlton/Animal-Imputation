import pandas as pd
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_dir)

# -----------------------------
# Join all usda dataset
# -----------------------------

chicken_cafo_2022 = pd.read_csv("../../Data/Scraped Data/2022_cafo/2022_chicken_cafo.csv")
cattle_cafo_2022 = pd.read_csv("../../Data/Scraped Data/2022_cafo/2022_cattle_cafo.csv")
hog_cafo_2022 = pd.read_csv("../../Data/Scraped Data/2022_cafo/2022_hog_cafo.csv")

usda_cafo_2022 = pd.merge(left = chicken_cafo_2022, right = cattle_cafo_2022, left_index=True, right_index = True, how = 'inner', copy = False).drop_duplicates()
usda_cafo_2022 = pd.merge(left = usda_cafo_2022, right = hog_cafo_2022, how = 'inner', left_index=True, right_index = True, copy = False).drop_duplicates()

# -----------------------------
# Clean usda dataset
# -----------------------------

usda_cafo_2022_cleaned = usda_cafo_2022.drop(['STATE', 'COUNTY', 'STATE_y', 'COUNTY_y'], axis =1)
usda_cafo_2022_cleaned = usda_cafo_2022_cleaned.rename(columns = ({'STATE_x':'STATE', 'COUNTY_x':'COUNTY'}))

usda_cafo_2022_cleaned.iloc[:, 2:] = usda_cafo_2022_cleaned.iloc[:, 2:].replace('(D)', -47)
usda_cafo_2022_cleaned.iloc[:, 2:] = usda_cafo_2022_cleaned.iloc[:, 2:].replace('-', 'NA')

usda_cafo_2022_cleaned.to_csv("../../Data/Scraped Data/2022_cafo/usda_cafo_2022_cleaned.csv", index=False)