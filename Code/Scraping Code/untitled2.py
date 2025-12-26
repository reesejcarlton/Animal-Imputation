import requests 
import pdfplumber 
import re 
import pandas as pd 
from io import BytesIO 
url = "https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/California/st06_2_019_019.pdf" # ----------------------------- # 1. Read PDF as text # ----------------------------- 
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
row_numbers_1000 = [i for i, line in enumerate(lines) if "100,000ormore" in line]
row_numbers_layer = [i for i, line in enumerate(lines) if "2022farmsbyinventory:" in line]
row_numbers_broiler = [i for i, line in enumerate(lines) if "2022farmsbynumbersold:" in line]

hogs_list = []

for i in range(len(item_indices)):
    #Hog data
    tempHogsIndex = row_numbers_hogs[i]
    tempHog1000Index = [x for x in row_numbers_1000 if x > tempHogsIndex][0]
    farms_hogs = lines[tempHog1000Index].split()[1:]        # drop first element
    hogs_list.append({'farms': farms_hogs})
    
# Now you have two sepa|rate lists
print("Hogs:", hogs_list[:1])


    
#%%

# Flatten hogs lists
hogs_farms_flat = [farm for block in hogs_list for farm in block['farms']]
hogs_numbers_flat = [num for block in hogs_list for num in block['numbers']]

# Trim to shortest list length to avoid misalignment
min_len = min(len(countyList), len(hogs_farms_flat), len(hogs_numbers_flat))

counties_trim = countyList[:min_len]
hogs_farms_trim = hogs_farms_flat[:min_len]
hogs_numbers_trim = hogs_numbers_flat[:min_len]

# Create DataFrame
hogsDf = pd.DataFrame({
    'County': counties_trim,
    'HogsFarms': hogs_farms_trim,
    'HogsNumber': hogs_numbers_trim
})

print(hogsDf.head())