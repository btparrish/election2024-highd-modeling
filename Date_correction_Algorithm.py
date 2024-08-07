import requests
import re
from bs4 import BeautifulSoup 
import numpy as np
import pandas as pd
from itertools import zip_longest
from matplotlib import pyplot as plt

url = 'https://www.realclearpolling.com/polls/president/general/2020/trump-vs-biden'

def get_national2024_data(url):
    import json
    page = requests.get(url)

    #check and return code
    if page.status_code == 200:
        url_content = page.text
        print("Success")
    else:
        print("Failed to retrieve. Status Code was", page.status_code)
        exit()

    soup = BeautifulSoup(page.content, "html.parser") 

    script_tags = soup.find_all('script')


    for script in script_tags:
        if script.string and 'finalData' in script.string:
            
            str = script.string
            break

    str2 = str.split('self.__next_f.push(')
    str3 = str2[1][:-1]
    json = json.loads(str3)

    json_str = json[1] 

    #search pattern index
    pollster_pattern = r'"pollster":\s*"([^"]*)"'
    date_pattern = r'"date":\s*"([^"]*)"'
    sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
    margin_error_pattern = r'"marginError":\s*"([^"]*)"'
    link_pattern = r'"link":\s*"([^"]*)"'

    pollster_data = re.findall(pollster_pattern, json_str)
    date_data = re.findall(date_pattern, json_str)
    sample_size_data = re.findall(sample_size_pattern, json_str)
    margin_error_data = re.findall(margin_error_pattern, json_str)
    link_data = re.findall(link_pattern, json_str)

    dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
    dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

    rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
    rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'

    dvalue_data = re.findall(dvalue_pattern1, json_str) or re.findall(dvalue_pattern2, json_str)
    rvalue_data = re.findall(rvalue_pattern1, json_str) or re.findall(rvalue_pattern2, json_str)

    data_rows = []
    for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, link_data, fillvalue=None):
        data_rows.append({
            "pollster": row[0],
            "date": row[1],
            "sampleSize": row[2],
            "marginError": row[3],
            "dvalue": row[4],
            "rvalue": row[5],


        })

    df = pd.DataFrame(data_rows)

    df = df.drop_duplicates().dropna(subset=['pollster'])
    df.reset_index(inplace=True)
    #print(df.to_string(index=True))
    #print(len(df))
    return df
def clean_data(df, type, year):
            df['dvalue'] = df['dvalue'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', np.nan).astype(float)
            df['rvalue'] = df['rvalue'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', np.nan).astype(float)
            def clean_sample_size(x):
                if 'LV' in x:
                    var = x.replace('LV', '').strip()
                    try:
                        var = float(var)
                    except:
                        var = np.nan
                    return var
                elif 'RV' in x:
                    var = x.replace('RV', '').strip()
                    try:
                        var = float(var)
                    except:
                        var = np.nan
                    return var
                elif 'A' in x:
                    var = x.replace('A', '').strip()
                    try:
                        var = float(var)
                    except:
                        var = np.nan
                    return var
                else:
                    return np.nan
                
            df['sampleSize'] = df['sampleSize'].apply(clean_sample_size)
            df['year'] = year
            #df['date'] = df['date'].astype(str).str.replace(r'^.*-\s*','', regex=True)+'/' #+ str(year)
            
            
            new_dates = []
            pattern = r"(\d{1,2})/(\d{1,2}) - (\d{1,2})/(\d{1,2})"
            clockstart = 0  #maybe index a year onto it...
            a = 0
            b = 0 #writing block

            year_flip = 0
            
            a_day = 0
            b_day = 0
            
            for date in df['date']:
                match = re.match(pattern, date)
                month1 = int(match.group(1))
                month2 = int(match.group(3))
                if clockstart == 0 and a == 0 and b == 0:  #Clock intitialization...write a into memory
                    if month1 < month2:
                        month = month1
                        clockstart += month
                        a += month
                        a_day += int(match.group(2))
                        #amount -= 1
                        #print(a)
                        #print(b)
                        continue
                    else:
                        month = month2
                        #new_dates.append(str(month) + '/' + str(match.group(4)) + '/' + year)
                        clockstart += month
                        a += month
                        a_day += int(match.group(4))
                        #amount -= 1
                        continue
                if clockstart > 0 and a > 0 and b == 0: #2nd and memory initialization
                    if month1 < month2:
                        month = month1
                        b = a #1st iteration b is written into memory
                        b_day += a_day
                        a = month #2nd iteration is written down
                        a_day = int(match.group(2))
                        year_str = str(int(year) - year_flip)
                        new_date = str(b) + '/' + str(b_day) + '/' + year_str
                        new_dates.append(new_date)
                        #amount -= 1
                        continue    
                    else:
                        month = month2
                        b = a #1st iteration
                        b_day += a_day
                        a = month #2nd iteration
                        a_day = int(match.group(2))
                        year_str = str(int(year) - year_flip)
                        new_date = str(b) + '/' + str(b_day) + '/' + year_str
                        new_dates.append(new_date)
                        #amount -= 1
                        continue
                if clockstart > 0 and a > 0 and b > 0: #WORK HERE....
                    if month1 < month2: #GET LOWEST MONTH   
                        month = month1  #assign to month assign to lowest?
                        if month < a: #check for year error or regular appending
                            if month2 == a: #try month2 because see if there is error...
                                month = month2
                                b = a 
                                b_day = a_day
                                a = month 
                                a_day = int(match.group(4))
                                year_str = str(int(year) - year_flip)
                                new_date = str(b) + '/' + str(b_day) + '/' + year_str
                                new_dates.append(new_date)
                                #amount -= 1 
                                continue
                            else: #regular appending as month is decreasing
                                b = a 
                                b_day = a_day
                                a = month
                                a_day = int(match.group(2))  
                                year_str = str(int(year) - year_flip) 
                                new_date = str(b) + '/' + str(b_day) + '/' + year_str
                                new_dates.append(new_date)
                                #amount -= 1 
                                continue    
                        if month > a: #year flip!!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(2))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            year_flip += 1
                            #amount -= 1 
                            continue
                        if month == a: #regular appending when year month is equal...
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(2))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #amount -= 1 
                            continue    
                        
                    else: #therefore month2 and month1 are equal...
                        month = month2
                        if month < a: #regular appending... 
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #amount -= 1 
                            continue        
                        if month > a: #year flip!!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            year_flip += 1
                            #amount -= 1 
                            continue
                        if month == a: #regular appending!!
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(2))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #amount -= 1 
                            continue 
            #else:
            year_str = str(int(year) - year_flip) 
            new_date = str(a) + '/' + str(a_day) + '/' + year_str
            new_dates.append(new_date)
            
            #for item in new_dates:
                #print(item)
            #print(df['date'])
            #print(len(df['date']))
            #print(new_dates)
            #print()
            #print(len(new_dates))
            #print()
            
            df['date'] = pd.DataFrame(new_dates)
            #print(df['date'].to_string(index=False))


            #print(df['date'])
            def margin_to_float(x):
                try:
                    return float(x)
                except:
                    return np.nan
            df['marginError'] = df['marginError'].apply(margin_to_float)
            df['Type'] = type
            
            return df
    

df = get_national2024_data(url)


#print(len(df['date']))
df = clean_data(df, "national", "2020")


#print(df.to_string(index=True))
print(df.to_string(index=False))
#print(df['date'])
#plt.plot(df['date'], df['rvalue'])
#plt.plot(df['date'], df['dvalue'])
#plt.show()

#print(len(df))

    #found my problem....the reason that the next 14 get removed because maybe some function is confused.
    #also discovered that df['date'] has 307 elements with a removed 14...
