import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_governor2022_data(url, state):

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
                
    "Alabama": "https://www.realclearpolling.com/polls/governor/general/2022/alabama/ivey-vs-flowers#polls",
    "Alaska": "https://www.realclearpolling.com/polls/governor/general/2022/alaska/dunleavy-vs-gara-final-round#polls",
    "Arizona": "https://www.realclearpolling.com/polls/governor/general/2022/arizona/lake-vs-hobbs#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/governor/general/2022/arkansas/huckabeesanders-vs-jones#polls",
    "California": "https://www.realclearpolling.com/polls/governor/general/2022/california/dahle-vs-newsom#polls",
    "Colorado": "https://www.realclearpolling.com/polls/governor/general/2022/colorado/ganahl-vs-polis#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/governor/general/2022/connecticut/stefanowski-vs-lamont#polls",
    #"Delaware": "https://www.realclearpolling.com/polls/senate/general/2014/delaware/wade-vs-coons#polls", 
    "Florida": "https://www.realclearpolling.com/polls/governor/general/2022/florida/desantis-vs-crist#polls",
    "Georgia": "https://www.realclearpolling.com/polls/governor/general/2022/georgia/kemp-vs-abrams#polls",
    "Hawaii": "https://www.realclearpolitics.com/epolls/2022/governor/hi/hawaii_governor_aiona_vs_green-7928.html#polls",
    "Idaho": "https://www.realclearpolitics.com/epolls/2022/governor/id/idaho_governor_little_vs_heidt-7743.html#polls",
    "Illinois": "https://www.realclearpolling.com/polls/governor/general/2022/illinois/bailey-vs-pritzker#polls",
    #"Indiana": "https://www.realclearpolling.com/polls/senate/general/2016/indiana/young-vs-bayh#polls",
    "Iowa": "https://www.realclearpolling.com/polls/governor/general/2022/iowa/reynolds-vs-dejear#polls",
    "Kansas": "https://www.realclearpolling.com/polls/governor/general/2022/kansas/kelly-vs-schmidt#polls",
    #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
    #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
    "Maine": "https://www.realclearpolling.com/polls/governor/general/2022/maine/lepage-vs-mills#polls",
    "Maryland": "https://www.realclearpolling.com/polls/governor/general/2022/massachusetts/diehl-vs-healey#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2022/massachusetts/diehl-vs-healey#polls",
    "Michigan": "https://www.realclearpolling.com/polls/governor/general/2022/michigan/dixon-vs-whitmer#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/governor/general/2022/minnesota/jensen-vs-walz#polls",
    #"Minnesota_SPECIAL": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/housley-vs-smith",
    #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
    #"Mississippi_RUNOFF":"https://www.realclearpolling.com/polls/senate/general/2018/mississippi-runoff-election",
    #"Missouri": "https://www.realclearpolling.com/polls/governor/general/2024/missouri/ashcroft-vs-quade#polls",
    #"Montana": "https://www.realclearpolling.com/polls/senate/general/2014/montana/daines-vs-curtis#polls",
    "Nebraksa": "https://www.realclearpolitics.com/epolls/2022/governor/ne/nebraska_governor_pillen_vs_blood-7897.html#polls",
    #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
    "Nevada": "https://www.realclearpolling.com/polls/governor/general/2022/nevada/lombardo-vs-sisolak#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2022/new-hampshire/sununu-vs-sherman#polls",
    #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/governor/general/2022/new-mexico/ronchetti-vs-grisham#polls",
    "New York": "https://www.realclearpolling.com/polls/governor/general/2022/new-york/zeldin-vs-hochul#polls",
    #"North Carolina": "https://www.realclearpolling.com/polls/governor/general/2024/north-carolina/robinson-vs-stein#polls",
    #"North Dakota": "https://www.realclearpolitics.com/epolls/2016/senate/nd/north_dakota_senate_hoeven_vs_glassheim-5996.html#polls",
    "Ohio": "https://www.realclearpolling.com/polls/governor/general/2022/ohio/dewine-vs-whaley#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2022/oklahoma/stitt-vs-hofmeister#polls",
    "Oregon": "https://www.realclearpolling.com/polls/governor/general/2022/oregon/drazan-vs-kotek-vs-johnson#polls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2022/pennsylvania/mastriano-vs-shapiro#polls",
    "Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2022/rhode-island/kalus-vs-mckee#polls",  
    "South Carolina":"https://www.realclearpolling.com/polls/governor/general/2022/south-carolina/mcmaster-vs-cunningham#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/governor/general/2022/south-dakota/noem-vs-smith#polls",
    "Tennessee": "https://www.realclearpolitics.com/epolls/2022/governor/tn/tennessee_governor_lee_vs_martin-7925.html#polls",
    "Texas": "https://www.realclearpolling.com/polls/governor/general/2022/texas/abbott-vs-o'rourke#polls",
    #"Utah": "https://www.realclearpolling.com/polls/senate/general/2016/utah/lee-vs-snow#polls",
    "Vermont": "https://www.realclearpolling.com/polls/governor/general/2022/vermont/scott-vs-siegel#polls",
    #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
    #"Washington": "https://www.realclearpolling.com/polls/senate/general/2016/washington/vance-vs-murray#polls",
    #"West Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/west-virginia/capito-vs-tennant#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2022/wisconsin/michels-vs-evers#polls",
    "Wyoming": "https://www.realclearpolitics.com/epolls/2022/governor/wy/wyoming_governor_gordon_vs_livingston-7904.html#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_governor2022_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

#print(all_state_df.to_string(index=True))
#print(all_state_df.shape)
