import requests
import pdfplumber
import pandas as pd
from io import BytesIO

# -----------------------------
# State FIPS codes & names
# -----------------------------
state_map = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut",
    "10": "Delaware", "11": "District_of_Columbia", "12": "Florida",
    "13": "Georgia", "16": "Idaho", "17": "Illinois", "18": "Indiana",
    "19": "Iowa", "20": "Kansas", "21": "Kentucky", "22": "Louisiana",
    "23": "Maine", "24": "Maryland", "25": "Massachusetts",
    "26": "Michigan", "27": "Minnesota", "28": "Mississippi",
    "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New_Hampshire", "34": "New_Jersey",
    "35": "New_Mexico", "36": "New_York", "37": "North_Carolina",
    "38": "North_Dakota", "39": "Ohio", "40": "Oklahoma",
    "41": "Oregon", "42": "Pennsylvania", "44": "Rhode_Island",
    "45": "South_Carolina", "46": "South_Dakota", "47": "Tennessee",
    "48": "Texas", "49": "Utah", "50": "Vermont", "51": "Virginia",
    "53": "Washington", "54": "West_Virginia", "55": "Wisconsin",
    "56": "Wyoming"
}

# Remove AK/HI/DC if needed
del state_map["02"]
del state_map["11"]

# -----------------------------
# Helper function to parse one PDF
# -----------------------------
def extract_state_data(state_name, fips_code):

    url = f"https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/{state_name}/st{fips_code}_2_011_011.pdf"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Skipping {state_name}: PDF not found")
            return None

        pdf_file = BytesIO(response.content)

        # Read all text
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        lines = text.split("\n")

        # ---------------------
        # Extract counties
        # ---------------------
        first_item_index = next(i for i, line in enumerate(lines) if "Item" in line)
        first_item_row = lines[first_item_index]

        item_indices = []
        for i in range(first_item_index, len(lines)):
            if lines[i] == first_item_row and i != first_item_index:
                break
            if "Item" in lines[i]:
                item_indices.append(i)

        countyList = []
        for i in item_indices:
            countyLine = lines[i]
            counties = countyLine.split()[1:]
            countyList.extend(counties)

        # ---------------------
        # Extract data rows
        # ---------------------
        row_numbers_500 = [i for i, line in enumerate(lines) if "500or" in line]
        row_numbers_beef = [i for i, line in enumerate(lines) if "Cattleandcalves-Con." in line]
        row_numbers_dry = [i for i, line in enumerate(lines) if "Milkcows" in line]

        beef_list = []
        dry_list = []

        for i in range(len(item_indices)):
            # Beef
            tempBeefIndex = row_numbers_beef[i]
            tempBeef500Index = [x for x in row_numbers_500 if x > tempBeefIndex][0]

            farms_beef = lines[tempBeef500Index].split()[1:]
            numbers_beef = lines[tempBeef500Index + 1].split()[1:]
            beef_list.append({'farms': farms_beef, 'numbers': numbers_beef})

            # Dry
            tempDryIndex = row_numbers_dry[i]
            tempDry500Index = [x for x in row_numbers_500 if x > tempDryIndex][0]

            farms_dry = lines[tempDry500Index].split()[1:]
            numbers_dry = lines[tempDry500Index + 1].split()[1:]
            dry_list.append({'farms': farms_dry, 'numbers': numbers_dry})


        # Flatten
        beef_farms = [x for block in beef_list for x in block['farms']]
        beef_numbers = [x for block in beef_list for x in block['numbers']]

        dry_farms = [x for block in dry_list for x in block['farms']]
        dry_numbers = [x for block in dry_list for x in block['numbers']]

        min_len = min(len(countyList), len(beef_farms), len(beef_numbers), len(dry_farms), len(dry_numbers))

        df = pd.DataFrame({
            "State": [state_name] * min_len,
            "County": countyList[:min_len],
            "DryFarms": dry_farms[:min_len],
            "DryNumber": dry_numbers[:min_len],
            "BeefFarms": beef_farms[:min_len],
            "BeefNumber": beef_numbers[:min_len]
        })

        print(f"Finished {state_name}")
        return df

    except Exception as e:
        print(f"Error processing {state_name}: {e}")
        return None

# -----------------------------
# Loop through all states
# -----------------------------
all_dfs = []

for fips, name in state_map.items():
    df_state = extract_state_data(name, fips)
    if df_state is not None:
        all_dfs.append(df_state)

# Combine everything
finalCattleDf = pd.concat(all_dfs, ignore_index=True)

print("\nFINAL COMBINED DF:")
print(finalCattleDf.head())
print("\nRows:", len(finalCattleDf))
