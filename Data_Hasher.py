import hashlib
import pandas as pd

file = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/ElectionModelProjectAugust2024Onward/Biden_AND_Kamala_AND_General_Congression.csv"
file = pd.read_csv(file)

def hash_data(data):
    # ensures the data is in bytes. 
    if isinstance(data, str):
        data = data.encode('utf-8')
        #data = data.replace("\n", "")
        #print(data)
    # creates a SHA-256 hash object
    sha256_hash = hashlib.sha256(data)
    
    # updates the hash object with the data
    sha256_hash.update(data)
    
    # gets the hexadecimal representation of the hash
    hashed_data = sha256_hash.hexdigest()
    
    return hashed_data


hash_list = []

for index, row in file.iterrows():
    concatenated_string = ' '.join([str(value) for value in row])
    hashed = hash_data(concatenated_string)
    hash_list.append(str(hashed))
  
df_hash = pd.DataFrame(hash_list, columns=["Hashed"])

file_save = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/ElectionModelProjectAugust2024Onward/hashed_list_v1.csv"

df_hash.to_csv(file_save, index=True)
print("program is done")










