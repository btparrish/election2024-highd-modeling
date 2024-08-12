import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_senate2016_data(url, state):

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
                
    "Alabama": "https://www.realclearpolitics.com/epolls/2016/senate/al/alabama_senate_shelby_vs_crumpton-5989.html#polls",
    "Alaska": "https://www.realclearpolling.com/polls/senate/general/2016/alaska/murkowski-vs-metcalfe-vs-miller-vs-stock#polls",
    "Arizona": "https://www.realclearpolling.com/polls/senate/general/2016/arizona/mccain-vs-kirkpatrick#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/senate/general/2016/arkansas/boozman-vs-eldridge#polls",
    "California": "https://www.realclearpolling.com/polls/senate/general/2016/california/harris-vs-sanchez#polls",
    "Colorado": "https://www.realclearpolling.com/polls/senate/general/2016/colorado/glenn-vs-bennet#polls",
    "Connecticut": "https://www.realclearpolling.com/polls/senate/general/2016/connecticut/carter-vs-blumenthal#polls",
    #"Delaware": "https://www.realclearpolling.com/polls/senate/general/2018/delaware/arlett-vs-carper#polls", 
    "Florida": "https://www.realclearpolling.com/polls/senate/general/2016/florida/rubio-vs-murphy#polls",
    "Georgia": "https://www.realclearpolling.com/polls/senate/general/2016/georgia/isakson-vs-barksdale#polls",
    "Hawaii": "https://www.realclearpolitics.com/epolls/2016/senate/hi/hawaii_senate_carroll_vs_schatz-5992.html#polls",
    "Idaho": "https://www.realclearpolling.com/polls/senate/general/2016/idaho/crapo-vs-sturgill#polls",
    "Illinois": "https://www.realclearpolling.com/polls/senate/general/2016/illinois/kirk-vs-duckworth#polls",
    "Indiana": "https://www.realclearpolling.com/polls/senate/general/2016/indiana/young-vs-bayh#polls",
    "Iowa": "https://www.realclearpolling.com/polls/senate/general/2016/iowa/grassley-vs-judge#polls",
    "Kansas": "https://www.realclearpolling.com/polls/senate/general/2016/kansas/moran-vs-wiesner#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/senate/general/2016/kentucky/paul-vs-gray#polls",
    "Louisiana": "https://www.realclearpolling.com/polls/senate/open-primary/2016/louisiana#polls",
    #"Maine": "https://www.realclearpolling.com/polls/senate/general/2018/maine/brakey-vs-king#polls",
    #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
    #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
    "Maryland": "https://www.realclearpolling.com/polls/senate/general/2016/maryland/vanhollen-vs-szeliga#polls",
    #"Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2018/massachusetts/diehl-vs-warren#polls",
    #"Michigan": "https://www.realclearpolling.com/polls/senate/general/2018/michigan/james-vs-stabenow#polls",
    #"Minnesota": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/newberger-vs-klobuchar#polls",
    #"Minnesota_SPECIAL": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/housley-vs-smith",
    #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2018/mississippi/wicker-vs-baria#polls",
    #"Mississippi_RUNOFF":"https://www.realclearpolling.com/polls/senate/general/2018/mississippi-runoff-election",
    "Missouri": "https://www.realclearpolling.com/polls/senate/general/2016/missouri/blunt-vs-kander#polls",
    #"Montana": "https://www.realclearpolling.com/polls/senate/general/2018/montana/rosendale-vs-tester#polls",
    #"Nebraksa": "https://www.realclearpolitics.com/epolls/2018/senate/ne/nebraska_senate_fischer_vs_raybould_-6315.html#polls",
    #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
    "Nevada": "https://www.realclearpolling.com/polls/senate/general/2016/nevada/cortezmasto-vs-heck#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/senate/general/2016/new-hampshire/ayotte-vs-hassan#polls",
    #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2018/new-jersey/hugin-vs-menendez#polls",
    #"New Mexico": "https://www.realclearpolling.com/polls/senate/general/2018/new-mexico/rich-vs-heinrich-vs-johnson#polls",
    "New York": "https://www.realclearpolling.com/polls/senate/general/2016/new-york/long-vs-schumer#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/senate/general/2016/north-carolina/burr-vs-ross#polls",
    "North Dakota": "https://www.realclearpolitics.com/epolls/2016/senate/nd/north_dakota_senate_hoeven_vs_glassheim-5996.html#polls",
    "Ohio": "https://www.realclearpolling.com/polls/senate/general/2016/ohio/portman-vs-strickland#polls",
    "Oklahoma": "https://www.realclearpolitics.com/epolls/2016/senate/ok/oklahoma_senate_lankford_vs_workman-5997.html#polls",
    "Oregon": "https://www.realclearpolling.com/polls/senate/general/2016/oregon/wyden-vs-callahan#polls",
    "Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2016/pennsylvania/toomey-vs-mcginty#polls",
    #"Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2018/rhode-island/flanders-vs-whitehouse#polls",  
    "South Carolina":"https://www.realclearpolling.com/polls/senate/general/2016/south-carolina/scott-vs-dixon#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/senate/general/2016/south-dakota/thune-vs-williams#polls",
    #"Tennessee": "https://www.realclearpolling.com/polls/senate/general/2018/tennessee/blackburn-vs-bredesen#polls",
    #"Texas": "https://www.realclearpolling.com/polls/senate/general/2018/texas/cruz-vs-o'rourke#polls",
    "Utah": "https://www.realclearpolling.com/polls/senate/general/2016/utah/lee-vs-snow#polls",
    "Vermont": "https://www.realclearpolling.com/polls/senate/general/2016/vermont/milne-vs-leahy#polls",
    #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2018/virginia/stewart-vs-kaine#polls",
    "Washington": "https://www.realclearpolling.com/polls/senate/general/2016/washington/vance-vs-murray#polls",
    #"West Virginia": "https://www.realclearpolling.com/polls/senate/general/2018/west-virginia/morrisey-vs-manchin#polls",
    "Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2016/wisconsin/johnson-vs-feingold#polls",
    #"Wyoming": "https://www.realclearpolitics.com/epolls/2018/senate/wy/wyoming_senate_barrasso_vs_trauner-6320.html#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_senate2016_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

#print(all_state_df.to_string(index=True))
#print(all_state_df.shape)
