import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_governor2016_data(url, state):

    page = requests.get(url)

    if page.status_code == 200:
        url_content = page.text
        print("Success")
        
        soup = BeautifulSoup(page.content, "html.parser") 

        script_tags = soup.find_all('script')

        str = ""
        for script in script_tags:
            if script.string and 'finalData' in script.string:
                str += script.string

        x = str.replace("\\","")     

        #str2 = str.split('self.__next_f.push(')
        #str3 = str2[1][:-1]
        #jsonx = json.loads(str3)
        #json_str = jsonx[1] 
        #print(json_str)
        
        pollster_pattern = r'"pollster":\s*"([^"]*)"'
        date_pattern = r'"date":\s*"([^"]*)"'
        sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
        margin_error_pattern = r'"marginError":\s*"([^"]*)"'
        
        link_pattern = r'"link":\s*"([^"]*)"'

        dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
        dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

        rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
        rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'


        dvalue_data = re.findall(dvalue_pattern1, x) or re.findall(dvalue_pattern2, x)
        rvalue_data = re.findall(rvalue_pattern1, x) or re.findall(rvalue_pattern2, x)

        pollster_data = re.findall(pollster_pattern, x)
        date_data = re.findall(date_pattern, x)
        sample_size_data = re.findall(sample_size_pattern, x)
        margin_error_data = re.findall(margin_error_pattern, x)
        
        link_data = re.findall(link_pattern, x)

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
                
    #"Alabama": "https://www.realclearpolitics.com/epolls/2018/governor/al/alabama_governor_ivey_vs_maddox-6405.html#polls",
    #"Alaska": "https://www.realclearpolling.com/polls/governor/general/2018/alaska/dunleavy-vs-begich#polls",
    #"Arizona": "https://www.realclearpolling.com/polls/governor/general/2018/arizona/ducey-vs-garcia#polls",
    #"Arkansas": "https://www.realclearpolling.com/polls/governor/general/2018/arkansas/hutchinson-vs-henderson#polls",
    #"California": "https://www.realclearpolling.com/polls/governor/general/2018/california/cox-vs-newsom#polls",
    #"Colorado": "https://www.realclearpolling.com/polls/governor/general/2018/colorado/stapleton-vs-polis#polls",
    #"Connecticut": "https://www.realclearpolling.com/polls/governor/general/2018/connecticut/stefanowski-vs-lamont#polls",
    "Delaware": "https://www.realclearpolitics.com/epolls/2016/governor/de/delaware_governor_bonini_vs_carney-6096.html#polls", 
    #"Florida": "https://www.realclearpolling.com/polls/governor/general/2018/florida/desantis-vs-gillum#polls",
    #"Georgia": "https://www.realclearpolling.com/polls/governor/general/2018/georgia/kemp-vs-abrams#polls",
    #"Hawaii": "https://www.realclearpolling.com/polls/governor/general/2018/hawaii/tupola-vs-ige#polls",
    #"Idaho": "https://www.realclearpolitics.com/epolls/2018/governor/id/idaho_governor_little_vs_jordan-6413.html#polls",
    #"Illinois": "https://www.realclearpolling.com/polls/governor/general/2018/illinois/rauner-vs-pritzker#polls",
    "Indiana": "https://www.realclearpolling.com/polls/governor/general/2016/indiana/holcomb-vs-gregg#polls",
    #"Iowa": "https://www.realclearpolling.com/polls/governor/general/2018/iowa/reynolds-vs-hubbell#polls",
    #"Kansas": "https://www.realclearpolling.com/polls/governor/general/2018/kansas/kobach-vs-kelly-vs-orman#polls",
    #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
    #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
    #"Maine": "https://www.realclearpolling.com/polls/governor/general/2018/maine/moody-vs-mills#polls",
    #"Maryland": "https://www.realclearpolling.com/polls/governor/general/2018/maryland/hogan-vs-jealous#polls",
    #"Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2018/massachusetts/baker-vs-gonzalez#polls",
    #"Michigan": "https://www.realclearpolling.com/polls/governor/general/2018/michigan/schuette-vs-whitmer#polls",
    #"Minnesota": "https://www.realclearpolling.com/polls/governor/general/2018/minnesota/johnson-vs-walz#polls",
    #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
    "Missouri": "https://www.realclearpolling.com/polls/governor/general/2016/missouri/greitens-vs-koster#polls",
    "Montana": "https://www.realclearpolling.com/polls/governor/general/2016/montana/gianforte-vs-bullock#polls",
    #"Nebraksa": "https://www.realclearpolitics.com/epolls/2018/governor/ne/nebraska_governor_ricketts_vs_krist-6421.html#polls",
    #"Nevada": "https://www.realclearpolling.com/polls/governor/general/2018/nevada/laxalt-vs-sisolak#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2016/new-hampshire/sununu-vs-ostern#polls",
    #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
    #"New Mexico": "https://www.realclearpolling.com/polls/governor/general/2018/new-mexico/pearce-vs-grisham#polls",
    #"New York": "https://www.realclearpolling.com/polls/governor/general/2018/new-york/molinaro-vs-cuomo#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/governor/general/2016/north-carolina/mccrory-vs-cooper#polls",
    "North Dakota": "https://www.realclearpolitics.com/epolls/2016/governor/nd/north_dakota_governor_burgum_vs_nelson-6099.html#polls",
    #"Ohio": "https://www.realclearpolling.com/polls/governor/general/2018/ohio/dewine-vs-cordray#polls",
    #"Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2018/oklahoma/stitt-vs-edmondson#polls",
    "Oregon": "https://www.realclearpolling.com/polls/governor/general/2016/oregon/pierce-vs-brown#polls",
    #"Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2018/pennsylvania/wagner-vs-wolf#polls",
    #"Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2018/rhode-island/fung-vs-raimondo#polls",  
    #"South Carolina":"https://www.realclearpolling.com/polls/governor/general/2018/south-carolina/mcmaster-vs-smith#polls",
    #"South Dakota": "https://www.realclearpolling.com/polls/governor/general/2018/south-dakota/noem-vs-sutton#polls",
    #"Tennessee": "https://www.realclearpolling.com/polls/governor/general/2018/tennessee/lee-vs-dean#polls",
    #"Texas": "https://www.realclearpolling.com/polls/governor/general/2018/texas/abbott-vs-valdez#polls",
    "Utah": "https://www.realclearpolling.com/polls/governor/general/2016/utah/herbert-vs-weinholtz#polls",
    "Vermont": "https://www.realclearpolling.com/polls/governor/general/2016/vermont/scott-vs-minter#polls",
    #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
    "Washington": "https://www.realclearpolling.com/polls/governor/general/2016/washington/bryant-vs-inslee#polls",
    "West Virginia": "https://www.realclearpolling.com/polls/governor/general/2016/west-virginia/cole-vs-justice#polls",
    #"Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2018/wisconsin/walker-vs-evers-vs-anderson#polls",
    #"Wyoming": "https://www.realclearpolitics.com/epolls/2018/governor/wy/wyoming_governor_gordon_vs_throne-6666.html#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_governor2016_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

#print(all_state_df.to_string(index=True))
#print(all_state_df.shape)
