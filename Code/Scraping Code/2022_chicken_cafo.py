import requests 
import pdfplumber 
import re 
import pandas as pd 
from io import BytesIO 
url = "https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/Arizona/st04_2_019_019.pdf" # ----------------------------- # 1. Read PDF as text # ----------------------------- 
response = requests.get(url) 
pdf_file = BytesIO(response.content) 
text = "" 
with pdfplumber.open(pdf_file) as pdf: 
    for page in pdf.pages: 
        text += page.extract_text() + "\n" # Split the text into lines 
        
lines = text.split("\n") 

#%%

# Counties


# Split the text into lines
lines = text.split("\n")

# Find the first row containing "Item"
first_item_index = next(i for i, line in enumerate(lines) if "Item" in line)
first_item_row = lines[first_item_index]

# Initialize list of indices for rows containing "Item"
item_indices = []

# Loop from the first occurrence onward
for i in range(first_item_index, len(lines)):
    if lines[i] == first_item_row and i != first_item_index:
        # Stop at the second occurrence of the first Item row
        break
    if "Item" in lines[i]:
        item_indices.append(i)

# Extract counties
countyList = []
for i in item_indices:
    countyLine = lines[i]
    # Split the line by spaces and drop the first element ("Item")
    counties = countyLine.split()[1:]
    countyList.extend(counties)  # Use extend to flatten the list

print(countyList)

#%%

row_number_state_broiler = [i for i, line in enumerate(lines) if "Broilersandothermeat-typechickenssold" in line][0]
row_numbers_state_2022 = [i for i, line in enumerate(lines) if "number,2022" in line]
corrected_row_numbers_state_2022 = [x for x in row_numbers_state_2022 if x > row_number_state_broiler][0]
state_broiler_count = int(lines[corrected_row_numbers_state_2022].split()[1].replace(",", ""))/5.5

broilerBinsNames = ["1to1,999", 
                   "2,000to59,999", 
                   "60,000to99,999", 
                   "100,000to199,999", 
                   "200,000to499,999", 
                   "500,000ormore"]

cafoWeights = [1/5.5,
               2000/5.5,
               60000/5.5,
               100000/5.5,
               200000/5.5,
               500000/5.5]

bin_row_indices = [
    [i for i, line in enumerate(lines) if label in line][0] for label in broilerBinsNames
]

weighted_broiler_total = 0

for row_idx, weight in zip(bin_row_indices, cafoWeights):
    farms_in_bin = int(lines[row_idx].split()[1].replace(",", "").replace('-', '0'))
    weighted_broiler_total += farms_in_bin * weight
    
broilerFactor = state_broiler_count/weighted_broiler_total

# Now you have two sepa|rate lists
print("Factor:", broilerFactor)

#%%

row_number_state_layer = [i for i, line in enumerate(lines) if "Layers..." in line][0]
row_numbers_state_2022 = [i for i, line in enumerate(lines) if "number,2022" in line]
corrected_row_numbers_state_2022 = [x for x in row_numbers_state_2022 if x > row_number_state_layer][0]
state_layer_count = int(lines[corrected_row_numbers_state_2022].split()[1].replace(",", ""))

layerBinsNames = ["1to49",
                  "50to99",
                  "100to399",
                  "400to3,199",
                  "3,200to9,999",
                  "10,000to19,999",
                  "20,000to49,999",
                  "50,000to99,999",
                  "100,000ormore"]
cafoWeights = [1,
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

for row_idx, weight in zip(bin_row_indices, cafoWeights):
    farms_in_bin = int(lines[row_idx].split()[1].replace(",", ""))
    weighted_layer_total += farms_in_bin * weight
    
layerFactor = state_layer_count/weighted_layer_total
# Now you have two seprate lists
print("Factor:", layerFactor)

#%%
row_numbers_100 = [i for i, line in enumerate(lines) if "100,000ormore" in line]
row_numbers_500 = [i for i, line in enumerate(lines) if "500,000ormore" in line]

layers_list = []
broiler_list = []

for i in range(len(item_indices)):
    # Layer
    tempLayerIndex = row_numbers_100[i]
    farms_layer = lines[tempLayerIndex].split()[1:]
    layers_list.append({'farms': farms_layer, 'numbers': [int(i.replace(",", "")) * 100000 * layerFactor if '-' not in i else i for i in farms_layer]})

    # Broiler
    tempBroilerIndex = row_numbers_500[i]
    farms_broiler = lines[tempBroilerIndex].split()[1:]
    broiler_list.append({'farms': farms_broiler, 'numbers': [int(i.replace(",", "")) * 500000 / 5.5 * broilerFactor if '-' not in i else i for i in farms_broiler]})

    
# Now you have two separate lists
print("Layer:", layers_list[:1])
print("Broiler:", broiler_list[:1])


    
#%%

# Flatten
layer_farms = [x for block in layers_list for x in block['farms']]
layer_numbers = [x for block in layers_list for x in block['numbers']]

broiler_farms = [x for block in broiler_list for x in block['farms']]
broiler_numbers = [x for block in broiler_list for x in block['numbers']]

min_len = min(len(countyList), len(broiler_farms), len(broiler_numbers), len(layer_farms), len(layer_numbers))

df = pd.DataFrame({
    "State": 'California',
    "County": countyList[:min_len],
    "LayerFarms": layer_farms[:min_len],
    "LayerNumber": layer_numbers[:min_len],
    "BroilerFarms": broiler_farms[:min_len],
    "BroilerNumber": broiler_numbers[:min_len]
})
