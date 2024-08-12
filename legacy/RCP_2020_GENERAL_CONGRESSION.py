import requests
import re
from bs4 import BeautifulSoup 
import numpy
import pandas as pd
from itertools import zip_longest
url = 'https://www.realclearpolitics.com/epolls/other/2020_generic_congressional_vote-6722.html'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.google.com',
    'Accept-Language': 'en-US,en;q=0.9'
}   
page = requests.get(url, headers=headers)
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
df = pd.DataFrame(data_rows, columns =['Pollster', 'Date', 'Samples', 'dvalue', 'rvalue'])

df = df.drop_duplicates().sort_values('Pollster')
print(df.to_string(index=False))
print(df.shape)
