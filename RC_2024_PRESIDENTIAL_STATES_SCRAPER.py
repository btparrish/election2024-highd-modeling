import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_state_data(url, state):

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
                "state": state
                #"race": race_value
                
            })
        
        return data_rows
        
    else:
        print("Failed to retrieve. Status Code was", page.status_code)
        return[]
        

state_urls = {
                
    "Alabama": "https://www.realclearpolling.com/polls/president/general/2024/alabama/trump-vs-biden#polls",
    "Alaska": "https://www.realclearpolling.com/polls/president/general/2024/alaska/trump-vs-biden#polls",
    "Arizona": "https://www.realclearpolling.com/polls/president/general/2024/arizona/trump-vs-biden#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/president/general/2024/arkansas/trump-vs-biden#polls",
    "California": "https://www.realclearpolling.com/polls/president/general/2024/california/trump-vs-biden#polls",
    "Colorado": "https://www.realclearpolling.com/polls/president/general/2024/colorado/trump-vs-biden#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/president/general/2024/connecticut/trump-vs-biden#polls",
    "Delaware": "https://www.realclearpolitics.com/epolls/2024/president/de/delaware_trump_vs_biden-8423.html", 
    "Florida": "https://www.realclearpolling.com/polls/president/general/2024/florida/trump-vs-biden#polls",
    "Georgia": "https://www.realclearpolling.com/polls/president/general/2024/georgia/trump-vs-biden#polls",
    "Hawaii": "https://www.realclearpolitics.com/epolls/2024/president/hi/hawaii_trump_vs_biden-8427.html#polls",
    "Idaho": "https://www.realclearpolling.com/polls/president/general/2024/idaho/trump-vs-biden#polls",
    "Illinois": "https://www.realclearpolling.com/polls/president/general/2024/illinois/trump-vs-biden#polls",
    "Indiana": "https://www.realclearpolling.com/polls/president/general/2024/indiana/trump-vs-biden#polls",
    "Iowa": "https://www.realclearpolling.com/polls/president/general/2024/iowa/trump-vs-biden#polls",
    "Kansas": "https://www.realclearpolling.com/polls/president/general/2024/kansas/trump-vs-biden#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/president/general/2024/kentucky/trump-vs-biden#polls",
    "Louisiana": "https://www.realclearpolling.com/polls/president/general/2024/louisiana/trump-vs-biden#polls",
    "Maine": "https://www.realclearpolling.com/polls/president/general/2024/maine/biden-vs-trump#polls",
    "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
    "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
    "Maryland": "https://www.realclearpolling.com/polls/president/general/2024/maryland/trump-vs-biden#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2024/massachusetts/trump-vs-biden#polls",
    "Michigan": "https://www.realclearpolling.com/polls/president/general/2024/michigan/trump-vs-biden#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/president/general/2024/minnesota/trump-vs-biden#polls",
    "Mississippi": "https://www.realclearpolling.com/polls/president/general/2024/mississippi/trump-vs-biden#polls",
    "Missouri": "https://www.realclearpolling.com/polls/president/general/2024/missouri/trump-vs-biden#polls",
    "Montana": "https://www.realclearpolling.com/polls/president/general/2024/montana/trump-vs-biden#polls",
    "Nebraksa": "https://www.realclearpolling.com/polls/president/general/2024/nebraska/trump-vs-biden#polls",
    "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
    "Nevada": "https://www.realclearpolling.com/polls/president/general/2024/nevada/trump-vs-biden#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2024/new-hampshire/trump-vs-biden#polls",
    "New Jersey": "https://www.realclearpolling.com/polls/president/general/2024/new-jersey/trump-vs-biden#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/president/general/2024/new-mexico/trump-vs-biden#polls",
    "New York": "https://www.realclearpolling.com/polls/president/general/2024/new-york/trump-vs-biden#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/president/general/2024/north-carolina/trump-vs-biden#polls",
    "North Dakota": "https://www.realclearpolling.com/polls/president/general/2024/north-dakota/trump-vs-biden#polls",
    "Ohio": "https://www.realclearpolling.com/polls/president/general/2024/ohio/trump-vs-biden#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2024/oklahoma/trump-vs-biden#polls",
    "Oregon": "https://www.realclearpolling.com/polls/president/general/2024/oregon/trump-vs-biden#polls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2024/pennsylvania/trump-vs-biden#polls",
    "Rhode Island": "https://www.realclearpolling.com/polls/president/general/2024/rhode-island/trump-vs-biden",  
    "South Carolina": "https://www.realclearpolling.com/polls/president/general/2024/south-carolina/trump-vs-biden#polls",
    "South Dakota": "https://www.realclearpolitics.com/epolls/2024/president/sd/south_dakota_trump_vs_biden_vs_kennedy-8477.html#polls",
    "Tennessee": "https://www.realclearpolling.com/polls/president/general/2024/tennessee/trump-vs-biden#polls",
    "Texas": "https://www.realclearpolling.com/polls/president/general/2024/texas/trump-vs-biden#polls",
    "Utah": "https://www.realclearpolling.com/polls/president/general/2024/utah/trump-vs-biden#polls",
    "Vermont": "https://www.realclearpolling.com/polls/president/general/2024/vermont/trump-vs-biden#polls",
    "Virginia": "https://www.realclearpolling.com/polls/president/general/2024/virginia/trump-vs-biden#polls",
    "Washington": "https://www.realclearpolling.com/polls/president/general/2024/washington/trump-vs-biden#polls",
    "West Virginia": "https://www.realclearpolling.com/polls/president/general/2024/west-virginia/trump-vs-biden#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2024/wisconsin/trump-vs-biden#polls",
    "Wyoming": "https://www.realclearpolling.com/polls/president/general/2024/wyoming/trump-vs-biden#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_state_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)


print(all_state_df.info())
