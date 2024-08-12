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

        #dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
        #dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

        #rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
        #rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
        #rvalue_pattern3 = 

        dvalue_pattern = r'"candidate":\[\{.*?"name":"([^"]*)","affiliation":"Democrat","value":"([^"]*)".*?\}'
        rvalue_pattern = r'"candidate":\[\{.*?"name":"([^"]*)","affiliation":"Republican","value":"([^"]*)".*?\}'


        dvalue_data = re.findall(dvalue_pattern, x) #or #re.findall(dvalue_pattern2, x)
        rvalue_data = re.findall(rvalue_pattern, x) #or #re.findall(rvalue_pattern2, x)

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
                
    "Alabama": "https://www.realclearpolling.com/polls/governor/general/2014/alabama/bentley-vs-griffith#polls",
    "Alaska": "https://www.realclearpolling.com/polls/governor/general/2014/alaska/parnell-vs-walker#polls", #independent won
    "Arizona": "https://www.realclearpolling.com/polls/governor/general/2014/arizona/ducey-vs-duval#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/governor/general/2014/arkansas/hutchinson-vs-ross#polls",
    "California": "https://www.realclearpolling.com/polls/governor/general/2014/california/kashkari-vs-brown#polls",
    "Colorado": "https://www.realclearpolling.com/polls/governor/general/2014/colorado/beauprez-vs-hickenlooper#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/governor/general/2014/connecticut/foley-vs-malloy-vs-visconti#polls",
    #"Delaware": "https://www.realclearpolitics.com/epolls/2016/governor/de/delaware_governor_bonini_vs_carney-6096.html#polls", 
    "Florida": "https://www.realclearpolling.com/polls/governor/general/2014/florida/scott-vs-crist-vs-wyllie#polls",
    "Georgia": "https://www.realclearpolling.com/polls/governor/general/2014/georgia/deal-vs-carter-vs-hunt#polls",
    "Hawaii": "https://www.realclearpolling.com/polls/governor/general/2014/hawaii/aiona-vs-Ige-vs-hannemann#polls",
    "Idaho": "https://www.realclearpolling.com/polls/governor/general/2014/idaho/otter-vs-balukoff#polls",
    "Illinois": "https://www.realclearpolling.com/polls/governor/general/2014/illinois/grimm-vs-quinn#polls",
    #"Indiana": "https://www.realclearpolling.com/polls/governor/general/2016/indiana/holcomb-vs-gregg#polls",
    "Iowa": "https://www.realclearpolling.com/polls/governor/general/2014/iowa/branstad-vs-hatch#polls",
    "Kansas": "https://www.realclearpolling.com/polls/governor/general/2014/kansas/brownback-vs-davis#polls",
    #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
    #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
    "Maine": "https://www.realclearpolling.com/polls/governor/general/2014/maine/lepage-vs-michaud-vs-cutler#polls",
    "Maryland": "https://www.realclearpolling.com/polls/governor/general/2014/maryland/hogan-vs-brown#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2014/massachusetts/baker-vs-coakley#polls",
    "Michigan": "https://www.realclearpolling.com/polls/governor/general/2014/michigan/snyder-vs-schauer#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/governor/general/2014/minnesota/johnson-vs-dayton#polls",
    #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
    #"Missouri": "https://www.realclearpolling.com/polls/governor/general/2016/missouri/greitens-vs-koster#polls",
    #"Montana": "https://www.realclearpolling.com/polls/governor/general/2016/montana/gianforte-vs-bullock#polls",
    "Nebraksa": "https://www.realclearpolling.com/polls/governor/general/2014/nebraska/ricketts-vs-hassebrook#polls",
    "Nevada": "https://www.realclearpolling.com/polls/governor/general/2014/nevada/sandoval-vs-goodman#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2014/new-hampshire/havenstein-vs-hassan#polls",
    #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/governor/general/2014/new-mexico/martinez-vs-king#polls",
    "New York": "https://www.realclearpolling.com/polls/governor/general/2014/new-york/astorino-vs-cuomo#polls",
    #"North Carolina": "https://www.realclearpolling.com/polls/governor/general/2016/north-carolina/mccrory-vs-cooper#polls",
    #"North Dakota": "https://www.realclearpolitics.com/epolls/2016/governor/nd/north_dakota_governor_burgum_vs_nelson-6099.html#polls",
    "Ohio": "https://www.realclearpolling.com/polls/governor/general/2014/ohio/kasich-vs-fitzgerald#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2014/oklahoma/fallin-vs-dorman#polls",
    "Oregon": "https://www.realclearpolling.com/polls/governor/general/2014/oregon/richardson-vs-kitzhaber#polls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2014/pennsylvania/corbett-vs-wolf#polls",
    "Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2014/rhode-island/fung-vs-raimondo#polls",  
    "South Carolina":"https://www.realclearpolling.com/polls/governor/general/2014/south-carolina/haley-vs-sheheen#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/governor/general/2014/south-dakota/daugaard-vs-wismer#polls",
    "Tennessee": "https://www.realclearpolling.com/polls/governor/general/2014/tennessee/haslam-vs-brown#polls",
    "Texas": "https://www.realclearpolling.com/polls/governor/general/2014/texas/abbott-vs-davis#polls",
    #"Utah": "https://www.realclearpolling.com/polls/governor/general/2016/utah/herbert-vs-weinholtz#polls",
    "Vermont": "https://www.realclearpolling.com/polls/governor/general/2014/vermont/milne-vs-shumlin#polls",
    #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
    #"Washington": "https://www.realclearpolling.com/polls/governor/general/2016/washington/bryant-vs-inslee#polls",
    #"West Virginia": "https://www.realclearpolling.com/polls/governor/general/2016/west-virginia/cole-vs-justice#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2014/wisconsin/walker-vs-burke#polls",
    "Wyoming": "https://www.realclearpolling.com/polls/governor/general/2014/wyoming/mead-vs-gosar#polls"
       
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

print(all_state_df.to_string(index=True))
#print(all_state_df.shape)

