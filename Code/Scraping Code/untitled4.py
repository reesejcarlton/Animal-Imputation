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

    url = f"https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/{state_name}/st{fips_code}_2_019_019.pdf"

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
        # Extract broiler scaling factors
        # ---------------------
        
        row_number_state_broiler = [i for i, line in enumerate(lines) if "Broilersandothermeat-typechickenssold" in line][0]
        row_numbers_broiler_state_2022 = [i for i, line in enumerate(lines) if "number,2022" in line]
        corrected_row_broiler_numbers_state_2022 = [x for x in row_numbers_broiler_state_2022 if x > row_number_state_broiler][0]
        state_broiler_count = int(lines[corrected_row_broiler_numbers_state_2022].split()[1].replace(",", ""))/5.5

        broilerBinsNames = ["1to1,999", 
                           "2,000to59,999", 
                           "60,000to99,999", 
                           "100,000to199,999", 
                           "200,000to499,999", 
                           "500,000ormore"]

        broilerCafoWeights = [1/5.5,
                       2000/5.5,
                       60000/5.5,
                       100000/5.5,
                       200000/5.5,
                       500000/5.5]

        bin_row_indices = [
            [i for i, line in enumerate(lines) if label in line][0] for label in broilerBinsNames
        ]

        weighted_broiler_total = 0

        for row_idx, weight in zip(bin_row_indices, broilerCafoWeights):
            farms_in_bin = int(lines[row_idx].split()[1].replace(",", ""))
            weighted_broiler_total += farms_in_bin * weight
            
        broilerFactor = state_broiler_count/weighted_broiler_total
        
        # ---------------------
        # Extract layer scaling factors
        # ---------------------
        
        row_number_state_layer = [i for i, line in enumerate(lines) if "Layers..." in line][0]
        row_numbers_layer_state_2022 = [i for i, line in enumerate(lines) if "number,2022" in line]
        corrected_row_layer_numbers_state_2022 = [x for x in row_numbers_layer_state_2022 if x > row_number_state_layer][0]
        state_layer_count = int(lines[corrected_row_layer_numbers_state_2022].split()[1].replace(",", ""))

        layerBinsNames = ["1to49",
                          "50to99",
                          "100to399",
                          "400to3,199",
                          "3,200to9,999",
                          "10,000to19,999",
                          "20,000to49,999",
                          "50,000to99,999",
                          "100,000ormore"]
        layerCafoWeights = [1,
                       50,
                       100,
                       400,
                       3200,
                       10000,
                       20000,
                       50000,
                       100000]

        bin_row_indices = [
            [i for i, line in enumerate(lines) if label in line][0] for label in layerBinsNames
        ]

        weighted_layer_total = 0

        for row_idx, weight in zip(bin_row_indices, layerCafoWeights):
            farms_in_bin = int(lines[row_idx].split()[1].replace(",", ""))
            weighted_layer_total += farms_in_bin * weight
            
        layerFactor = state_layer_count/weighted_layer_total
        
        # ---------------------
        # Extract data rows
        # ---------------------
        
        row_numbers_100 = [i for i, line in enumerate(lines) if "100,000ormore" in line]
        row_numbers_500 = [i for i, line in enumerate(lines) if "500,000ormore" in line]

        layers_list = []
        broiler_list = []

        for i in range(len(item_indices)):
            # Layer
            tempLayerIndex = row_numbers_100[i]
            farms_layer = lines[tempLayerIndex].split()[1:]
            layers_list.append({'farms': farms_layer, 'numbers': [int(i) * 100000 * layerFactor if '-' not in i else i for i in farms_layer]})

            # Broiler
            tempBroilerIndex = row_numbers_500[i]
            farms_broiler = lines[tempBroilerIndex].split()[1:]
            broiler_list.append({'farms': farms_broiler, 'numbers': [int(i) * 500000 / 5.5 * broilerFactor if '-' not in i else i for i in farms_broiler]})


        # Flatten
        layer_farms = [x for block in layers_list for x in block['farms']]
        layer_numbers = [x for block in layers_list for x in block['numbers']]

        broiler_farms = [x for block in broiler_list for x in block['farms']]
        broiler_numbers = [x for block in broiler_list for x in block['numbers']]

        min_len = min(len(countyList), len(broiler_farms), len(broiler_numbers), len(layer_farms), len(layer_numbers))

        df = pd.DataFrame({
            "State": [state_name] * min_len,
            "County": countyList[:min_len],
            "LayerFarms": layer_farms[:min_len],
            "LayerNumber": layer_numbers[:min_len],
            "BroilerFarms": broiler_farms[:min_len],
            "BroilerNumber": broiler_numbers[:min_len]
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
finalChickenDf = pd.concat(all_dfs, ignore_index=True)

print("\nFINAL COMBINED DF:")
print(finalChickenDf.head())
print("\nRows:", len(finalChickenDf))
