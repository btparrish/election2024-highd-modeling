import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_states2016_data(url, state):

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
                
    "Alabama": "https://www.realclearpolitics.com/epolls/2016/president/al/alabama_trump_vs_clinton-5898.html",
    "Alaska": "https://www.realclearpolling.com/polls/president/general/2016/alaska/trump-vs-clinton#polls",
    "Arizona": "https://www.realclearpolling.com/polls/president/general/2016/arizona/trump-vs-clinton#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/president/general/2016/arkansas/trump-vs-clinton#polls",
    "California": "https://www.realclearpolling.com/polls/president/general/2016/california/trump-vs-clinton#polls",
    "Colorado": "https://www.realclearpolling.com/polls/president/general/2016/colorado/trump-vs-clinton#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/president/general/2016/connecticut/trump-vs-clinton#polls",
    "Delaware": "https://www.realclearpolling.com/polls/president/general/2016/delaware/trump-vs-clinton#polls", 
    "Florida": "https://www.realclearpolling.com/polls/president/general/2016/florida/trump-vs-clinton#polls",
    "Georgia": "https://www.realclearpolling.com/polls/president/general/2016/georgia/trump-vs-clinton#polls",
    "Hawaii": "https://www.realclearpolitics.com/epolls/2016/president/hi/hawaii_trump_vs_clinton-5902.html#polls",
    "Idaho": "https://www.realclearpolling.com/polls/president/general/2016/idaho/trump-vs-clinton#polls",
    "Illinois": "https://www.realclearpolling.com/polls/president/general/2016/illinois/trump-vs-clinton#polls",
    "Indiana": "https://www.realclearpolling.com/polls/president/general/2016/indiana/trump-vs-clinton#polls",
    "Iowa": "https://www.realclearpolling.com/polls/president/general/2016/iowa/trump-vs-clinton#polls",
    "Kansas": "https://www.realclearpolling.com/polls/president/general/2016/kansas/trump-vs-clinton#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/president/general/2016/kentucky/trump-vs-clinton#polls",
    "Louisiana": "https://www.realclearpolling.com/polls/president/general/2016/louisiana/trump-vs-clinton#polls",
    #"Maine": "", no data
    "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2016/maine/cd1-trump-vs-clinton#polls",
    "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2016/maine/cd2-trump-vs-clinton#polls",
    "Maryland": "https://www.realclearpolling.com/polls/president/general/2016/maryland/trump-vs-clinton#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2016/massachusetts/trump-vs-clinton#polls",
    "Michigan": "https://www.realclearpolling.com/polls/president/general/2016/michigan/trump-vs-clinton#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/president/general/2016/minnesota/trump-vs-clinton#polls",
    "Mississippi": "https://www.realclearpolling.com/polls/president/general/2016/mississippi/trump-vs-clinton#polls",
    "Missouri": "https://www.realclearpolling.com/polls/president/general/2016/missouri/trump-vs-clinton#polls",
    "Montana": "https://www.realclearpolling.com/polls/president/general/2016/montana/trump-vs-clinton#polls",
    "Nebraksa": "https://www.realclearpolling.com/polls/president/general/2016/nebraska/trump-vs-clinton#polls",
    "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2016/nebraska/cd2-trump-vs-clinton#polls",
    "Nevada": "https://www.realclearpolling.com/polls/president/general/2016/nevada/trump-vs-clinton-vs-johnson#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2016/new-hampshire/trump-vs-clinton#polls",
    "New Jersey": "https://www.realclearpolling.com/polls/president/general/2016/new-jersey/trump-vs-clinton#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/president/general/2016/new-mexico/trump-vs-clinton#polls",
    "New York": "https://www.realclearpolling.com/polls/president/general/2016/new-york/trump-vs-clinton#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/president/general/2016/north-carolina/trump-vs-clinton#polls",
    "North Dakota": "https://www.realclearpolitics.com/epolls/2016/president/nd/north_dakota_trump_vs_clinton-5907.html#polls",
    "Ohio": "https://www.realclearpolling.com/polls/president/general/2016/ohio/trump-vs-clinton#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2016/oklahoma/trump-vs-clinton#polls",
    "Oregon": "https://www.realclearpolling.com/polls/president/general/2016/oregon/trump-vs-clinton#polls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2016/pennsylvania/trump-vs-clinton#polls",
    "Rhode Island": "https://www.realclearpolling.com/polls/president/general/2016/rhode-island/trump-vs-clinton#polls",  
    "South Carolina": "https://www.realclearpolling.com/polls/president/general/2016/south-carolina/trump-vs-clinton#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/president/general/2016/south-dakota/trump-vs-clinton#polls",
    "Tennessee": "https://www.realclearpolling.com/polls/president/general/2016/tennessee/trump-vs-clinton#polls",
    "Texas": "https://www.realclearpolling.com/polls/president/general/2016/texas/trump-vs-clinton#polls",
    "Utah": "https://www.realclearpolling.com/polls/president/general/2016/utah/trump-vs-clinton#polls",
    "Vermont": "https://www.realclearpolling.com/polls/president/general/2016/vermont/trump-vs-clinton#polls",
    "Virginia": "https://www.realclearpolling.com/polls/president/general/2016/virginia/trump-vs-clinton#polls",
    "Washington": "https://www.realclearpolling.com/polls/president/general/2016/washington/trump-vs-clinton#polls",
    "West Virginia": "https://www.realclearpolling.com/polls/president/general/2016/west-virginia/trump-vs-clinton#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2016/wisconsin/trump-vs-clinton#polls",
    "Wyoming": "https://www.realclearpolitics.com/epolls/2016/president/wy/wyoming_trump_vs_clinton-5913.html#polls"
       
}

all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_states2016_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

print(all_state_df.to_string(index=False))
#print(all_state_df.shape())
