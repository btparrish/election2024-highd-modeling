import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_senate2014_data(url, state):

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
                
    #"Alabama": no data
    "Alaska": "https://www.realclearpolling.com/polls/senate/general/2014/alaska/sullivan-vs-begich#polls",
    #"Arizona": "https://www.realclearpolling.com/polls/senate/general/2016/arizona/mccain-vs-kirkpatrick#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/senate/general/2014/arkansas/cotton-vs-pryor#polls",
    #"California": "https://www.realclearpolling.com/polls/senate/general/2016/california/harris-vs-sanchez#polls",
    "Colorado": "https://www.realclearpolling.com/polls/senate/general/2014/colorado/gardner-vs-udall#polls",
    #"Connecticut": "https://www.realclearpolling.com/polls/senate/general/2016/connecticut/carter-vs-blumenthal#polls",
    "Delaware": "https://www.realclearpolling.com/polls/senate/general/2014/delaware/wade-vs-coons#polls", 
    #"Florida": "https://www.realclearpolling.com/polls/senate/general/2016/florida/rubio-vs-murphy#polls",
    "Georgia": "https://www.realclearpolling.com/polls/senate/general/2014/georgia/perdue-vs-nunn-vs-swafford#polls",
    "Hawaii": "https://www.realclearpolling.com/polls/senate/general/2014/hawaii/cavasso-vs-schatz#polls",
    "Idaho": "https://www.realclearpolling.com/polls/senate/general/2014/idaho/risch-vs-mitchell#polls",
    "Illinois": "https://www.realclearpolling.com/polls/senate/general/2014/illinois/oberweis-vs-durbin#polls",
    #"Indiana": "https://www.realclearpolling.com/polls/senate/general/2016/indiana/young-vs-bayh#polls",
    "Iowa": "https://www.realclearpolling.com/polls/senate/general/2014/iowa/ernst-vs-braley#polls",
    "Kansas": "https://www.realclearpolling.com/polls/senate/general/2014/kansas/roberts-vs-orman#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
    "Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
    "Maine": "https://www.realclearpolling.com/polls/senate/general/2014/maine/collins-vs-bellows#polls",
    #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
    #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
    #"Maryland": "https://www.realclearpolling.com/polls/senate/general/2016/maryland/vanhollen-vs-szeliga#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2014/massachusetts/herr-vs-markey#polls",
    "Michigan": "https://www.realclearpolling.com/polls/senate/general/2014/michigan/land-vs-peters#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/senate/general/2014/minnesota/mcfadden-vs-franken#polls",
    #"Minnesota_SPECIAL": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/housley-vs-smith",
    "Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
    #"Mississippi_RUNOFF":"https://www.realclearpolling.com/polls/senate/general/2018/mississippi-runoff-election",
    #"Missouri": "https://www.realclearpolling.com/polls/senate/general/2016/missouri/blunt-vs-kander#polls",
    "Montana": "https://www.realclearpolling.com/polls/senate/general/2014/montana/daines-vs-curtis#polls",
    #"Nebraksa": "https://www.realclearpolitics.com/epolls/2018/senate/ne/nebraska_senate_fischer_vs_raybould_-6315.html#polls",
    #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
    #"Nevada": "https://www.realclearpolling.com/polls/senate/general/2016/nevada/cortezmasto-vs-heck#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/senate/general/2014/new-hampshire/brown-vs-shaheen#polls",
    "New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/senate/general/2014/new-mexico/weh-vs-udall#polls",
    #"New York": "https://www.realclearpolling.com/polls/senate/general/2016/new-york/long-vs-schumer#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/senate/general/2014/north-carolina/tillis-vs-hagan#polls",
    #"North Dakota": "https://www.realclearpolitics.com/epolls/2016/senate/nd/north_dakota_senate_hoeven_vs_glassheim-5996.html#polls",
    #"Ohio": "https://www.realclearpolling.com/polls/senate/general/2016/ohio/portman-vs-strickland#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/senate/general/2014/oklahoma/lankford-vs-johnson#polls",
    "Oregon": "https://www.realclearpolling.com/polls/senate/general/2014/oregon/wehby-vs-merkley#polls",
    #"Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2016/pennsylvania/toomey-vs-mcginty#polls",
    "Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2014/rhode-island/zaccaria-vs-reed#polls",  
    "South Carolina":"https://www.realclearpolling.com/polls/senate/general/2014/south-carolina/graham-vs-hutto-vs-ravenel#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/senate/general/2014/south-dakota/rounds-vs-weiland-vs-pressler#polls",
    "Tennessee": "https://www.realclearpolling.com/polls/senate/general/2014/tennessee/alexander-vs-ball#polls",
    "Texas": "https://www.realclearpolling.com/polls/senate/general/2014/texas/cornyn-vs-alameel#polls",
    #"Utah": "https://www.realclearpolling.com/polls/senate/general/2016/utah/lee-vs-snow#polls",
    #"Vermont": "https://www.realclearpolling.com/polls/senate/general/2016/vermont/milne-vs-leahy#polls",
    "Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
    #"Washington": "https://www.realclearpolling.com/polls/senate/general/2016/washington/vance-vs-murray#polls",
    "West Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/west-virginia/capito-vs-tennant#polls",
    #"Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2016/wisconsin/johnson-vs-feingold#polls",
    "Wyoming": "https://www.realclearpolling.com/polls/senate/general/2014/wyoming/enzi-vs-hardy#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_senate2014_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

print(all_state_df.to_string(index=True))
print(all_state_df.shape)
