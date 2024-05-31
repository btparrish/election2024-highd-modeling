import requests
import json
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest

def get_senate2020_data(url, state):

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
                
    "Alabama": "https://www.realclearpolling.com/polls/senate/general/2020/alabama/tuberville-vs-jones#polls",
    "Alaska": "https://www.realclearpolling.com/polls/senate/general/2020/alaska/sullivan-vs-gross#polls",
    "Arizona": "https://www.realclearpolling.com/polls/senate/general/2020/arizona/kelly-vs-mcsally#polls",
    "Arkansas": "https://www.realclearpolling.com/polls/senate/general/2020/arkansas/cotton-vs-harrington#polls",
    #"California": "https://www.realclearpolling.com/polls/senate/general/2022/california/meuser-vs-padilla#polls",
    "Colorado": "https://www.realclearpolling.com/polls/senate/general/2020/colorado/gardner-vs-hickenlooper#polls",
    #"Connecticut": "https://www.realclearpolling.com/polls/senate/general/2022/connecticut/levy-vs-blumenthal#polls",
    "Delaware": "https://www.realclearpolling.com/polls/senate/general/2020/delaware/witzke-vs-coons", 
    #"Florida": "https://www.realclearpolling.com/polls/senate/general/2022/florida/rubio-vs-demings#polls",
    "Georgia": "https://www.realclearpolling.com/polls/senate/general/2020/georgia/perdue-vs-ossoff#polls",
    #"Hawaii": "https://www.realclearpolitics.com/epolls/2022/senate/hi/hawaii_senate_mcdermott_vs_schatz-7929.html#polls",
    "Idaho": "https://www.realclearpolitics.com/epolls/2020/senate/id/idaho_senate_risch_vs_jordan-7070.html#polls",
    "Illinois": "https://www.realclearpolitics.com/epolls/2020/senate/il/illinois_senate_curran_vs_durbin-7071.html#polls",
    #"Indiana": "https://www.realclearpolitics.com/epolls/2022/senate/in/indiana_senate_young_vs_mcdermott-7746.html#polls",
    "Iowa": "https://www.realclearpolling.com/polls/senate/general/2020/iowa/ernst-vs-greenfield#polls",
    "Kansas": "https://www.realclearpolling.com/polls/senate/general/2020/kansas/marshall-vs-bollier#polls",
    "Kentucky": "https://www.realclearpolling.com/polls/senate/general/2020/kentucky/mcconnell-vs-mcgrath#polls",
    "Louisiana": "https://www.realclearpolitics.com/epolls/2020/senate/la/louisiana_senate_open_primary-7074.html#polls",
    "Maine": "https://www.realclearpolling.com/polls/senate/general/2020/maine/collins-vs-gideon#polls",
    #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
    #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
    #"Maryland": "https://www.realclearpolling.com/polls/senate/general/2022/maryland/vanhollen-vs-chaffee#polls",
    "Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2020/massachusetts/markey-vs-oconnor#polls",
    "Michigan": "https://www.realclearpolling.com/polls/senate/general/2020/michigan/james-vs-peters#polls",
    "Minnesota": "https://www.realclearpolling.com/polls/senate/general/2020/minnesota/lewis-vs-smith#polls",
    "Mississippi": "https://www.realclearpolling.com/polls/senate/general/2020/mississippi/hyde-smith-vs-espy#polls",
    #"Missouri": "https://www.realclearpolling.com/polls/senate/general/2022/missouri/schmitt-vs-valentine#polls",
    "Montana": "https://www.realclearpolling.com/polls/senate/general/2020/montana/daines-vs-bullock#polls",
    "Nebraksa": "https://www.realclearpolitics.com/epolls/2020/senate/ne/nebraska_senate_sasse_vs_democrat-7076.html#polls",
    #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
    #"Nevada": "https://www.realclearpolling.com/polls/senate/general/2022/nevada/laxalt-vs-cortezmasto#polls",
    "New Hampshire": "https://www.realclearpolling.com/polls/senate/general/2020/new-hampshire/messner-vs-shaheen#polls",
    "New Jersey": "https://www.realclearpolling.com/polls/senate/general/2020/new-jersey/mehta-vs-booker#polls",
    "New Mexico": "https://www.realclearpolling.com/polls/senate/general/2020/new-mexico/ronchetti-vs-lujan#polls",
    #"New York": "https://www.realclearpolling.com/polls/senate/general/2022/new-york/schumer-vs-pinion#polls",
    "North Carolina": "https://www.realclearpolling.com/polls/senate/general/2020/north-carolina/tillis-vs-cunningham#polls",
    #"North Dakota": "https://www.realclearpolitics.com/epolls/2022/senate/nd/north_dakota_senate_hoeven_vs_christiansen-7527.html#polls",
    #"Ohio": "https://www.realclearpolling.com/polls/senate/general/2022/ohio/vance-vs-ryan#polls",
    "Oklahoma": "https://www.realclearpolling.com/polls/senate/general/2020/oklahoma/inhofe-vs-broyles#polls",
    "Oregon": "https://www.realclearpolitics.com/epolls/2020/senate/or/oregon_senate_perkins_vs_merkley-7081.html#polls",
    #"Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2022/pennsylvania/oz-vs-fetterman#polls",
    "Rhode Island": "https://www.realclearpolitics.com/epolls/2020/senate/ri/rhode_island_senate_waters_vs_reed-7082.html#polls",  
    "South Carolina":"https://www.realclearpolling.com/polls/senate/general/2020/south-carolina/graham-vs-harrison#polls",
    "South Dakota": "https://www.realclearpolling.com/polls/senate/general/2020/south-dakota/rounds-vs-ahlers#polls",
    "Tennessee": "https://www.realclearpolitics.com/epolls/2020/senate/tn/tennessee_senate_hagerty_vs_bradshaw-7239.html#polls",
    "Texas": "https://www.realclearpolling.com/polls/senate/general/2020/texas/cornyn-vs-hegar#polls",
    #"Utah": "https://www.realclearpolling.com/polls/senate/general/2022/utah/lee-vs-mcmullin#polls",
    #"Vermont": "https://www.realclearpolling.com/polls/senate/general/2022/vermont/malloy-vs-welch#polls",
    "Virginia": "https://www.realclearpolling.com/polls/senate/general/2020/virginia/gade-vs-warner#polls",
    #"Washington": "https://www.realclearpolling.com/polls/senate/general/2022/washington/smiley-vs-murray#polls",
    "West Virginia": "https://www.realclearpolitics.com/epolls/2020/senate/wv/west_virginia_senate_moore_capito_vs_swearengin-7087.html#polls",
    #"Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2022/wisconsin/johnson-vs-barnes#polls",
    "Wyoming": "https://www.realclearpolling.com/polls/senate/general/2020/wyoming/lummis-vs-ben-david#polls"
       
}


all_state_dataframe = []

for state, url in state_urls.items():
    state_df = get_senate2020_data(url, state)
    df = pd.DataFrame(state_df)
    if len(df)>0:
        df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
        all_state_dataframe.append(df)
    else:
        continue
    
all_state_df = pd.concat(all_state_dataframe, ignore_index=True)

print(all_state_df.to_string(index=True))
print(all_state_df.shape)
