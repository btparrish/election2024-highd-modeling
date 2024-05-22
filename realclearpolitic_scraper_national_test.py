import requests
import json
import re
from bs4 import BeautifulSoup #data scraper package
import numpy
import pandas as pd
from itertools import zip_longest
#url loading and get
url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-biden#polls'
page = requests.get(url)

#check and return code
if page.status_code == 200:
    url_content = page.text
    print("Success")
else:
    print("Failed to retrieve. Status Code was", page.status_code)
    exit()

soup = BeautifulSoup(page.content, "html.parser") #EVERYTHING

script_tags = soup.find_all('script')

counter = 0 #this checks the line with the JS that has ALL THE DATA in it
for script in script_tags:
    if script.string and 'finalData' in script.string:
        counter += 1
        #print(script.string)
        str = script.string
        break
#shaving the values into readable json for json.loads
str2 = str.split('self.__next_f.push(')
str3 = str2[1][:-1]
json = json.loads(str3)
#print(json[1]) #so now its in a big LIST
json_str = json[1] #chooses the 2nd item in the list indexed as 1
print(json_str)

#search pattern index
pollster_pattern = r'"pollster":\s*"([^"]*)"'
date_pattern = r'"date":\s*"([^"]*)"'
sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
margin_error_pattern = r'"marginError":\s*"([^"]*)"'
dvalue_pattern = r'"candidate":\[{"name":"Biden","affiliation":"Democrat","value":"([^"]*)"'
rvalue_pattern = r'"candidate":\[{[^}]*},{"name":"Trump","affiliation":"Republican","value":"([^"]*)"'
link_pattern = r'"link":\s*"([^"]*)"'


#puts the data into a list
pollster_data = re.findall(pollster_pattern, json_str)
date_data = re.findall(date_pattern, json_str)
sample_size_data = re.findall(sample_size_pattern, json_str)
margin_error_data = re.findall(margin_error_pattern, json_str)
dvalue_data = re.findall(dvalue_pattern, json_str)
rvalue_data = re.findall(rvalue_pattern, json_str)
link_data = re.findall(link_pattern, json_str)



#data_dict = {
    #"pollster": pollster_data,
    #"date":date_data,
    #"sample_size":sample_size_data,
    #"margin_error": margin_error_data,
    #"dvalue": dvalue_data,
    #"rvalue": rvalue_data,
    #"link": link_data,
#}

#data_dict = {
#    key: list(value) for key, value in zip_longest(
#        ["pollster", "date", "sampleSize", "marginError", "dvalue", "rvalue", "link"],
#        [pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, link_data],
#        fillvalue="None"
#    )
#}


data_rows = []
for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, link_data, fillvalue=None):
    data_rows.append({
        "pollster": row[0],
        "date": row[1],
        "sampleSize": row[2],
        "marginError": row[3],
        "dvalue": row[4],
        "rvalue": row[5],


    })

df = pd.DataFrame(data_rows)

df_revised = df.drop_duplicates()

df_revised2 = df_revised.dropna(subset=['pollster'])

#print(df_revised2)

print(df_revised2.to_string(index=False))

#print(df_revised2.shape)
#x = print(df_revised2.reset_index())
#print(x.shape)

df_final = df_revised2.to_csv('out.csv', index=False)


























#print(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, link_data)



#maryland_frame = pd.DataFrame({"pollster":pollster_data,
                              # "date":date_data,
                              # "sample_size":sample_size_data,
                              # "margin_error":margin_error_data,
                              # "dvalue":dvalue_data,
                              # "rvalue":rvalue_data})

#print(maryland_frame)

#keys = ["pollster", "data", "samplesize", "moe", "dvalue", "rvalue", "link"]



#print(len(pollster_data)) #this might be the solution for specifying the amount
#maybe i have to make a dictionary for each row
    



#pollster_dict = dict(zip(keys,pollster_data ))
#date_dict = dict(zip(keys, date_data))
#sample_size_dict = dict(zip(keys, sample_size_data ))
#margin_error_dict = dict(zip(keys, margin_error_data))
#dvalue_dict = dict(zip(keys, dvalue_data))
#rvalue_dict = dict(zip(keys, rvalue_data))
#link_dict = dict(zip(keys, link_data))


#print(pollster_dict)

#print (pollster_data)
#print (date_data)
#print (sample_size_data)
#print (margin_error_data)
#print (dvalue_data)
#print (rvalue_data)
#print (link_data)



#"pollster":" "
#"date":" "
#"sampleSize":" "
#"marginError":" "
#"candidate":[
#{"name":"Biden","affiliation":"Democrat","value":" "
#{"name":"Trump","affiliation":"Republican","value":" "
#"link":" "




#for value in values:
    #print(value)




#pollster_element = json.find("")


#pollster_element = script.string.find("value", )

#for poll_element in script.string:
    #pollster_element = 
    #date_element =   
    #sample_element = 
    #moe_element = 
    #biden_percentage_element = 
    #trump_percentage_element = 




    
   
#use find/find_all to isolate data strings
#because of websites architecture,
#copy both tables down and then cancel out
#the values that are similar based on indexing







