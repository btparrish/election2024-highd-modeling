#def clean_data(dataframe,year, type):

import requests
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest
import numpy as np
import random

def clean_data(dataframe,year, type):

    def clean_r_and_dvalue(x):
        var = re.sub(r'[^\d.]', '', str(x))
        try:
            return float(var)
        except:
            return np.nan

    dataframe['dvalue'] = dataframe['dvalue'].apply(clean_r_and_dvalue)
    dataframe['rvalue'] = dataframe['rvalue'].apply(clean_r_and_dvalue)

    def clean_sample_size(x):
        if 'LV' in x:
            var = x.replace('LV', '').strip()
            try:
                var = float(var)
            except:
                var = np.nan
            return var
        else:
            return np.nan
        
    dataframe['sampleSize'] = dataframe['sampleSize'].apply(clean_sample_size)

    dataframe['Year'] = year

    dataframe['date'] = dataframe['date'].astype(str).str.replace(r'^.*-\s*','', regex=True)+'/' + str(year)
    dataframe['date'] = pd.to_datetime(dataframe['date'], errors='coerce')

    def margin_to_float(x):
        try:
            return float(x)
        except:
            return np.nan
        
    try:
        dataframe['marginError'] = dataframe['marginError'].apply(margin_to_float)
    except:
        pass
    
    dataframe['Type'] = type

    return dataframe

# 2014 General Congressional
url = 'https://www.realclearpolitics.com/epolls/other/generic_congressional_vote-2170.html#polls'
# List of User-Agent headers to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
]

#proxies

proxies_list = [
    'http://104.200.30.129:3128',
    # Add more proxies if necessary
]

proxy = random.choice(proxies_list)
proxies = {
        'http': proxy,
        'https': proxy,
    }

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'en-US,en;q=0.9'
}   
page = requests.get(url,headers=headers,proxies=proxies)
print(proxies)
if page.status_code == 200:
    url_content = page.text
    print("Success")
else:
    print("Failed to retrieve. Status Code was", page.status_code)
    exit()
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="container")


#rcpAvg = results.find("tr", class_="rcpAvg2")
#print(rcpAvg.text.strip())

pollster_data = []
date_data =[]
sample_data =[]
dvalue_data =[]
rvalue_data  = []

isinrcpavg = results.find_all("tr", class_="isInRcpAvg")
for poll in isinrcpavg:
    pollster = poll.find('a', class_='normal_pollster_name').text.strip()
    date = poll.find_all('td')[1].text.strip()
    sample = poll.find("td", class_="sample").text.strip()
    td_elements = poll.find_all('td')
    dvalue = td_elements[3].text.strip()
    rvalue = td_elements[4].text.strip()
    
    pollster_data.append(pollster)
    date_data.append(date)
    sample_data.append(sample)
    dvalue_data.append(dvalue)
    rvalue_data.append(rvalue)

alt = results.find_all("tr", class_="alt")
for poll in alt:
    pollster = poll.find('a', class_='normal_pollster_name').text.strip()
    date = poll.find_all('td')[1].text.strip()
    sample = poll.find("td", class_="sample").text.strip()
    td_elements = poll.find_all('td')
    dvalue = td_elements[3].text.strip()
    rvalue = td_elements[4].text.strip()
    
    pollster_data.append(pollster)
    date_data.append(date)
    sample_data.append(sample)
    dvalue_data.append(dvalue)
    rvalue_data.append(rvalue)

blank = results.select("tr[class='']")
for poll in blank:
    pollster = poll.find('a', class_='normal_pollster_name').text.strip()
    date = poll.find_all('td')[1].text.strip()
    sample = poll.find("td", class_="sample").text.strip()
    td_elements = poll.find_all('td')
    dvalue = td_elements[3].text.strip()
    rvalue = td_elements[4].text.strip()
    
    pollster_data.append(pollster)
    date_data.append(date)
    sample_data.append(sample)
    dvalue_data.append(dvalue)
    rvalue_data.append(rvalue)


data_rows = list(zip_longest(pollster_data, date_data, sample_data, dvalue_data, rvalue_data, fillvalue=None))
df = pd.DataFrame(data_rows, columns =['pollster', 'date', 'sampleSize', 'dvalue', 'rvalue'])

df = df.drop_duplicates().sort_values('pollster')
general_congressional_2014_df = df

general_congressional_2014 = clean_data(general_congressional_2014_df, 2014, 'General Congressional')
