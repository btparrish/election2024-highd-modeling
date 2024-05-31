import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_senate2022_data(url, state):

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
                
    "Alabama": "https://www.realclearpolling.com/polls/senate/general/2022/alabama/britt-vs-boyd#polls",
    "Alaska": "https://www.realclearpolling.com/polls/senate/general/2022/alaska/murkowski-vs-tshibaka-final-round#polls",
    "Arizona": "https://www.realclearpolling.com/polls/senate/general/2022/arizona/masters-vs-kelly#polls",
    "Arkansas": "https://www.realclearpolitics.com/epolls/2022/senate/ar/arkansas_senate_-7512.html#polls",
    "California": "https://www.realclearpolling.com/polls/senate/general/2022/california/meuser-vs-padilla#polls",
    "Colorado": "https://www.realclearpolling.com/polls/senate/general/2022/colorado/bennet-vs-o'dea#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/senate/general/2022/connecticut/levy-vs-blumenthal#polls",
    #"Delaware": "https://www.realclearpolling.com/polls/senate/general/2024/delaware/carper-vs-republican", 
    "Florida": "https://www.realclearpolling.com/polls/senate/general/2022/florida/rubio-vs-demings#polls",
    "Georgia": "https://www.realclearpolling.com/polls/senate/general/2022/georgia/walker-vs-warnock#polls",
    "Hawaii": "https://www.realclearpolitics.com/epolls/2022/senate/hi/hawaii_senate_mcdermott_vs_schatz-7929.html#polls",
    "Idaho": "https://www.realclearpolitics.com/epolls/2022/senate/id/idaho_senate_crapo_vs_roth-7742.html#polls",
    "Illinois": "https://www.realclearpolling.com/polls/senate/general/2022/illinois/salvi-vs-duckworth#polls",
    "Indiana": "https://www.realclearpolitics.com/epolls/2022/senate/in/indiana_senate_young_vs_mcdermott-7746.html#polls",
    "Iowa": "https://www.realclearpolling.com/polls/senate/general/2022/iowa/grassley-vs-franken#polls",
    "Kansas": "https://www.realclearpolling.com/polls/senate/general/2022/kansas/moran-vs-holland#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/senate/general/2022/kentucky/paul-vs-booker#polls",
    "Louisiana": "https://www.realclearpolling.com/polls/senate/open-primary/2022/louisiana#polls",
    #"Maine": "https://www.realclearpolling.com/polls/senate/general/2024/maine/king-vs-republican-vs-democrat#polls",
    #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
    #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
    "Maryland": "https://www.realclearpolling.com/polls/senate/general/2022/maryland/vanhollen-vs-chaffee#polls",
    #"Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2024/massachusetts/warren-vs-republican#polls",
    #"Michigan": "https://www.realclearpolling.com/elections/senate/2024/michigan#polls",
    #"Minnesota": "https://www.realclearpolling.com/polls/senate/general/2024/minnesota/fraser-vs-klobuchar#polls",
    #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2024/mississippi/wicker-vs-democrat#polls",
    "Missouri": "https://www.realclearpolling.com/polls/senate/general/2022/missouri/schmitt-vs-valentine#polls",
    #"Montana": "https://www.realclearpolling.com/polls/senate/general/2024/montana/sheehy-vs-tester#polls",
    #"Nebraksa": "https://www.realclearpolling.com/polls/senate/general/2024/nebraska/fischer-vs-democrat#polls",
    #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
    "Nevada": "https://www.realclearpolling.com/polls/senate/general/2022/nevada/laxalt-vs-cortezmasto#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/senate/general/2022/new-hampshire/hassan-vs-bolduc#polls",
    #"New Jersey": "https://www.realclearpolling.com/elections/senate/2024/new-jersey#polls",
    #"New Mexico": "https://www.realclearpolling.com/polls/senate/general/2024/new-mexico/heinrich-vs-republican#polls",
    "New York": "https://www.realclearpolling.com/polls/senate/general/2022/new-york/schumer-vs-pinion#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/senate/general/2022/north-carolina/budd-vs-beasley#polls",
    "North Dakota": "https://www.realclearpolitics.com/epolls/2022/senate/nd/north_dakota_senate_hoeven_vs_christiansen-7527.html#polls",
    "Ohio": "https://www.realclearpolling.com/polls/senate/general/2022/ohio/vance-vs-ryan#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/senate/general/2022/oklahoma/lankford-vs-horn#polls",
    "Oregon": "https://www.realclearpolling.com/polls/senate/general/2022/oregon/perkins-vs-wydenpolls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2022/pennsylvania/oz-vs-fetterman#polls",
    "Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2024/rhode-island/whitehouse-vs-republican#polls",  
    "South Carolina": "https://www.realclearpolitics.com/epolls/2022/senate/sc/south_carolina_senate_scott_vs_matthews-7530.html#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/senate/general/2022/south-dakota/thune-vs-bengs#polls",
    #"Tennessee": "https://www.realclearpolling.com/polls/senate/general/2024/tennessee/blackburn-vs-johnson#polls",
    #"Texas": "https://www.realclearpolling.com/polls/senate/general/2024/texas/cruz-vs-allred#polls",
    "Utah": "https://www.realclearpolling.com/polls/senate/general/2022/utah/lee-vs-mcmullin#polls",
    "Vermont": "https://www.realclearpolling.com/polls/senate/general/2022/vermont/malloy-vs-welch#polls",
    #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2024/virginia/kaine-vs-republican#polls",
    "Washington": "https://www.realclearpolling.com/polls/senate/general/2022/washington/smiley-vs-murray#polls",
    "West Virginia": "https://www.realclearpolling.com/polls/senate/open-seat/2024/west-virginia#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2022/wisconsin/johnson-vs-barnes#polls",
    #"Wyoming": "https://www.realclearpolling.com/polls/senate/general/2024/wyoming/barrasso-vs-democrat#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_senate2022_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

print(all_state_df.to_string(index=True))
print(all_state_df.shape)
