import requests
import re
from bs4 import BeautifulSoup #data scraper package
import numpy
import pandas as pd
from itertools import zip_longest
#url loading and get
url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-biden'

def get_national2024_data(url):
    import json
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


    for script in script_tags:
        if script.string and 'finalData' in script.string:
            
            str = script.string
            break

    str2 = str.split('self.__next_f.push(')
    str3 = str2[1][:-1]
    json = json.loads(str3)

    json_str = json[1] 
    print(json_str)

    #search pattern index
    pollster_pattern = r'"pollster":\s*"([^"]*)"'
    date_pattern = r'"date":\s*"([^"]*)"'
    sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
    margin_error_pattern = r'"marginError":\s*"([^"]*)"'
    dvalue_pattern = r'"candidate":\[{"name":"Biden","affiliation":"Democrat","value":"([^"]*)"'
    rvalue_pattern = r'"candidate":\[{[^}]*},{"name":"Trump","affiliation":"Republican","value":"([^"]*)"'
    link_pattern = r'"link":\s*"([^"]*)"'





    pollster_data = re.findall(pollster_pattern, json_str)
    date_data = re.findall(date_pattern, json_str)
    sample_size_data = re.findall(sample_size_pattern, json_str)
    margin_error_data = re.findall(margin_error_pattern, json_str)

    link_data = re.findall(link_pattern, json_str)

    dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
    dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

    rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
    rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'

    dvalue_data = re.findall(dvalue_pattern1, json_str) or re.findall(dvalue_pattern2, json_str)
    rvalue_data = re.findall(rvalue_pattern1, json_str) or re.findall(rvalue_pattern2, json_str)

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

    return df_revised2

df_national = get_national2024_data(url)
    
print(df_national.to_string(index=False))

csv_file_path = r'2024_RCP_National.csv'
df_national.to_csv(csv_file_path, index=False)
