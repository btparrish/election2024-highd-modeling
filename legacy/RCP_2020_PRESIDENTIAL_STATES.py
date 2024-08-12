import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_2020state_data(url, state):

    page = requests.get(url)

    if page.status_code == 200:
        url_content = page.text
        print("Success")
        
        soup = BeautifulSoup(page.content, "html.parser") 

        script_tags = soup.find_all('script')

        for script in script_tags:
            if script.string and 'finalData' in script.string:
                str = script.string
                break

        str2 = str.split('self.__next_f.push(')
        str3 = str2[1][:-1]
        jsonx = json.loads(str3)
        json_str = jsonx[1] 

        pollster_pattern = r'"pollster":\s*"([^"]*)"'
        date_pattern = r'"date":\s*"([^"]*)"'
        sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
        margin_error_pattern = r'"marginError":\s*"([^"]*)"'
        
        link_pattern = r'"link":\s*"([^"]*)"'

        dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
        dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

        rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
        rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'

        dvalue_data = re.findall(dvalue_pattern1, json_str) or re.findall(dvalue_pattern2, json_str)
        rvalue_data = re.findall(rvalue_pattern1, json_str) or re.findall(rvalue_pattern2, json_str)

        pollster_data = re.findall(pollster_pattern, json_str)
        date_data = re.findall(date_pattern, json_str)
        sample_size_data = re.findall(sample_size_pattern, json_str)
        margin_error_data = re.findall(margin_error_pattern, json_str)
        
        link_data = re.findall(link_pattern, json_str)

        data_rows = []
        for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, link_data, fillvalue=None):
            data_rows.append({
                
                "pollster": row[0],
                "date": row[1],
                "sampleSize": row[2],
                "marginError": row[3],
                "dvalue": row[4],
                "rvalue": row[5],
                "state": state,
                
            })
        
        return data_rows
    else:
        print("Failed to retrieve. Status Code was", page.status_code)
        return[]


state_urls = {
    
    "Alabama": "https://www.realclearpolling.com/polls/president/general/2020/alabama/trump-vs-biden#polls",
    "Alaska": "https://www.realclearpolling.com/polls/president/general/2020/alaska/trump-vs-biden#polls",
    "Arizona": "https://www.realclearpolling.com/polls/president/general/2020/arizona/trump-vs-biden#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/president/general/2020/arkansas/trump-vs-biden#polls",
    "California": "https://www.realclearpolling.com/polls/president/general/2020/california/trump-vs-biden#polls",
    "Colorado": "https://www.realclearpolling.com/polls/president/general/2020/colorado/trump-vs-biden#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/president/general/2020/connecticut/trump-vs-biden#polls",
    "Delaware": "https://www.realclearpolling.com/polls/president/general/2020/delaware/trump-vs-biden#polls",
    "Florida": "https://www.realclearpolling.com/polls/president/general/2020/florida/trump-vs-biden#polls",
    "Georgia": "https://www.realclearpolling.com/polls/president/general/2020/georgia/trump-vs-biden#polls",
    "Hawaii": "https://www.realclearpolling.com/polls/president/general/2020/hawaii/trump-vs-biden#polls",
    #"Idaho": "",  # Missing URL
    #"Illinois": "", #Missing URL
    "Indiana": "https://www.realclearpolling.com/polls/president/general/2020/indiana/trump-vs-biden#polls",
    "Iowa": "https://www.realclearpolling.com/polls/president/general/2020/iowa/trump-vs-biden#polls",
    "Kansas": "https://www.realclearpolling.com/polls/president/general/2020/kansas/trump-vs-biden#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/president/general/2020/kentucky/trump-vs-biden#polls",
    "Louisiana": "https://www.realclearpolling.com/polls/president/general/2020/louisiana/trump-vs-biden#polls",
    "Maine": "https://www.realclearpolling.com/polls/president/general/maine/2020/trump-vs-biden#polls",
    "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2020/maine-cd1/trump-vs-biden#polls",
    "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2020/maine/cd2-trump-vs-biden#polls",
    "Maryland": "https://www.realclearpolling.com/polls/president/general/2020/maryland/trump-vs-biden#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2020/massachusetts/trump-vs-biden#polls",
    "Michigan": "https://www.realclearpolling.com/polls/president/general/2020/michigan/trump-vs-biden#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/president/general/2020/minnesota/trump-vs-biden#polls",
    "Mississippi": "https://www.realclearpolling.com/polls/president/general/2020/mississippi/trump-vs-biden#polls",
    "Missouri": "https://www.realclearpolling.com/polls/president/general/2020/missouri/trump-vs-biden#polls",
    "Montana": "https://www.realclearpolling.com/polls/president/general/2020/montana/trump-vs-biden#polls",
    "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2020/nebraska-cd2/trump-vs-biden#polls",
    "Nevada": "https://www.realclearpolling.com/polls/president/general/2020/nevada/trump-vs-biden#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2020/new-hampshire/trump-vs-biden#polls",
    "New Jersey": "https://www.realclearpolling.com/polls/president/general/2020/new-jersey/trump-vs-biden#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/president/general/2020/new-mexico/trump-vs-biden#polls",
    "New York": "https://www.realclearpolling.com/polls/president/general/2020/new-york/trump-vs-biden#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/president/general/2020/north-carolina/trump-vs-biden#polls",
    #"North Dakota": "",  # Missing URL
    "Ohio": "https://www.realclearpolling.com/polls/president/general/2020/ohio/trump-vs-biden#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2020/oklahoma/trump-vs-biden#polls",
    "Oregon": "https://www.realclearpolling.com/polls/president/general/2020/oregon/trump-vs-biden#polls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2020/pennsylvania/trump-vs-biden#polls",
    #"Rhode Island": "",  # Missing URL
    "South Carolina": "https://www.realclearpolling.com/polls/president/general/2020/south-carolina/trump-vs-biden#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/president/general/2020/south-dakota/trump-vs-biden#polls",
    "Tennessee": "https://www.realclearpolling.com/polls/president/general/2020/tennessee/trump-vs-biden#polls",
    "Texas": "https://www.realclearpolling.com/polls/president/general/2020/texas/trump-vs-biden#polls",
    "Utah": "https://www.realclearpolling.com/polls/president/general/2020/utah/trump-vs-biden#polls",
    "Vermont": "https://www.realclearpolling.com/polls/president/general/2020/vermont/trump-vs-biden#polls",
    "Virginia": "https://www.realclearpolling.com/polls/president/general/2020/virginia/trump-vs-biden#polls",
    "Washington": "https://www.realclearpolling.com/polls/president/general/2020/washington/trump-vs-biden#polls",
    "West Virginia": "https://www.realclearpolling.com/polls/president/general/2020/west-virginia/trump-vs-biden#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2020/wisconsin/trump-vs-biden#polls",
    "Wyoming": "https://www.realclearpolling.com/polls/president/general/2020/wyoming/trump-vs-biden#polls",
                 
}

all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_2020state_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

#print(all_state_df.to_string(index=False))



