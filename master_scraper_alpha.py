import requests
import re
from bs4 import BeautifulSoup 
import numpy as np
import pandas as pd
from itertools import zip_longest
import json
import csv
import random
import time

x = time.time() 
missing_data_url = []
missing_data_state = []
missing_data_year = []
missing_data_type = []
def collection(url, state, type, year):

    url = url
    state = state
    type = type
    year = year



    def x(url, state, type, year):
        page = requests.get(url)
        z = pd.DataFrame()
        if page.status_code == 200:
            url_content = page.text
            #print("Success")
            
            soup = BeautifulSoup(page.content, "html.parser") 

            script_tags = soup.find_all('script')

            str = ""
            for script in script_tags:
                if script.string and 'finalData' in script.string:
                        str += script.string

            x = str.replace("\\","")     

           
            
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

            
            final_dvalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Democrat","color":"[^"]*","rank":\d+,"value":"([^"]*?)"'
            final_dvalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Democrat","color":"[^"]*","rank":\d+,"value":"([^"]*?)"'#works

            final_rvalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Republican","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #works
            final_rvalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Republican","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #WORKS

            final_ivalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Independent","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #works
            final_ivalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Independent","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #WORKS
            
            final_dvalue_data = re.findall(final_dvalue_pattern1, x) or re.findall(final_dvalue_pattern2, x)
            final_rvalue_data = re.findall(final_rvalue_pattern1, x) or re.findall(final_rvalue_pattern2, x)
            final_ivalue_data = re.findall(final_ivalue_pattern1, x) or re.findall(final_ivalue_pattern2, x)
        

            try:
                if final_dvalue_data[0] > final_rvalue_data[0]:
                    winner = "D"
                elif final_rvalue_data[0] > final_dvalue_data[0]:
                    winner = "R"
            except:
                winner = "NA or ongoing"
         


            pollster_data = re.findall(pollster_pattern, x)
            date_data = re.findall(date_pattern, x)
            sample_size_data = re.findall(sample_size_pattern, x)
            margin_error_data = re.findall(margin_error_pattern, x)
            
            #link_data = re.findall(link_pattern, x) #we might need this 6.10.24

            data_rows = []
            for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, final_dvalue_data, final_rvalue_data, fillvalue=None):
                data_rows.append({
                    
                    "pollster": row[0],
                    "date": row[1],
                    "sampleSize": row[2],
                    "marginError": row[3],
                    "dvalue": row[4],
                    "rvalue": row[5],
                    "finalD": row[6],
                    "finalR": row[7],
                    "state": state,
                    "type": type,
                    "year": year,
                    "winner": winner

                    #"race": race_value
                    
                })
            
            df = pd.DataFrame(data_rows)
            
            if len(df) > 0:
                df = df.drop_duplicates().dropna(subset=['pollster'])
            else:
                return z    
            #df = df.drop(df[df['pollster'] == 'rcp_average'].index)              
            ##df = df[df.winner != 'NA or ongoing']
            #df.reset_index(inplace=True)
            return df
        else:
            print("403")
            return z
            

    def json_str(url, state, type, year):
        import json
        page = requests.get(url)
        z = pd.DataFrame()
        #check and return code
        if page.status_code == 200:
            url_content = page.text
            #print("Success")
        else:
            print("Failed to retrieve. Status Code was", page.status_code)
            return z

        soup = BeautifulSoup(page.content, "html.parser") 

        script_tags = soup.find_all('script')

        for script in script_tags:
            if script.string and 'finalData' in script.string:
                
                str = script.string
                break
        try:
            str2 = str.split('self.__next_f.push(')
            str3 = str2[1][:-1]
            json = json.loads(str3)
        except:
            return z 

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

        final_dvalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Democrat","color":"[^"]*","rank":\d+,"value":"([^"]*?)"'
        final_dvalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Democrat","color":"[^"]*","rank":\d+,"value":"([^"]*?)"'#works
        final_rvalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Republican","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #works
        final_rvalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Republican","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #WORKS
        final_ivalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Independent","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #works
        final_ivalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Independent","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #WORKS
        
        #final_dvalue_data = re.findall(final_dvalue_pattern1, x) or re.findall(final_dvalue_pattern2, x)
        #final_rvalue_data = re.findall(final_rvalue_pattern1, x) or re.findall(final_rvalue_pattern2, x)
        final_ivalue_data = re.findall(final_ivalue_pattern1, json_str) or re.findall(final_ivalue_pattern2, json_str)
        

        try:
            final_dvalue_data = re.findall(final_dvalue_pattern1, json_str) or re.findall(final_dvalue_pattern2, json_str)
            final_rvalue_data = re.findall(final_rvalue_pattern1, json_str) or re.findall(final_rvalue_pattern2, json_str)
            if final_dvalue_data[0] > final_rvalue_data[0]:
                winner = "D"
            elif final_rvalue_data[0] > final_dvalue_data[0]:
                winner = "R"
            else:
                winner = "NA or Ongoing"
        except:
            winner = "NA or ongoing"


        data_rows = []
        for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, final_dvalue_data, final_rvalue_data, fillvalue=None):
            data_rows.append({
                "pollster": row[0],
                "date": row[1],
                "sampleSize": row[2],
                "marginError": row[3],
                "dvalue": row[4],
                "rvalue": row[5],
                "finalD":row[6],
                "finalR":row[7],
                "state": state,
                "type": type,
                "year": year,
                "winner": winner
            })

        df = pd.DataFrame(data_rows)

        df = df.drop_duplicates().dropna(subset=['pollster'])
        df = df.drop(df[df['pollster'] == 'rcp_average'].index)              
        ##df = df[df.winner != 'NA or ongoing']
        df.reset_index(inplace=True)

        return df

    def alt_json_str(url, state, type, year):
        import json
        page = requests.get(url)
        z = pd.DataFrame()
        #check and return code
        if page.status_code == 200:
            url_content = page.text
            #print("Success")
        

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
            #print(json_str)

            #search pattern index
            pollster_pattern = r'"pollster":\s*"([^"]*)"'
            date_pattern = r'"date":\s*"([^"]*)"'
            sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
            margin_error_pattern = r'"marginError":\s*"([^"]*)"'
            dvalue_pattern = r'"candidate":\[{"name":"Biden","affiliation":"Democrat","value":"([^"]*)"'
            rvalue_pattern = r'"candidate":\[{[^}]*},{"name":"Trump","affiliation":"Republican","value":"([^"]*)"'
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

            final_dvalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Democrat","color":"[^"]*","rank":\d+,"value":"([^"]*?)"'
            final_dvalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Democrat","color":"[^"]*","rank":\d+,"value":"([^"]*?)"'#works
            final_rvalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Republican","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #works
            final_rvalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Republican","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #WORKS
            final_ivalue_pattern1 = r'"candidates":\[{"id":"[^"]*","name":"[^"]*?","affiliation":"Independent","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #works
            final_ivalue_pattern2 = r'"candidates":\[{[^}]*},{"id":"[^"]*","name":"[^"]*?","affiliation":"Independent","color":"[^"]*","rank":\d+,"value":"([^"]*?)"' #WORKS

            final_dvalue_data = re.findall(final_dvalue_pattern1, json_str) or re.findall(final_dvalue_pattern2, json_str)
            final_rvalue_data = re.findall(final_rvalue_pattern1, json_str) or re.findall(final_rvalue_pattern2, json_str)
            final_ivalue_data = re.findall(final_ivalue_pattern1, json_str) or re.findall(final_ivalue_pattern2, json_str)
            try:
                if final_dvalue_data[0] > final_rvalue_data[0]:
                    winner = "D"
                elif final_rvalue_data[0] > final_dvalue_data[0]:
                    winner = "R"
            except:
                winner = "I RACE"


            data_rows = []
            for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, final_dvalue_data, final_rvalue_data, fillvalue=None):
                data_rows.append({
                    "pollster": row[0],
                    "date": row[1],
                    "sampleSize": row[2],
                    "marginError": row[3],
                    "dvalue": row[4],
                    "rvalue": row[5],
                    "finalD":row[6],
                    "finalR":row[7],
                    "state": state,
                    "type": type,
                    "year": year,
                    "winner": winner



                })

            df = pd.DataFrame(data_rows)
            df = df.drop_duplicates().dropna(subset=['pollster'])
            return df
        else:
            print("Failed to retrieve. Status Code was", page.status_code)
            return z
    def headers(url, state, type, year):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        session = requests.Session()
        def get_soup(url):
            time.sleep(random.uniform(1, 3))  # Random delay between requests
            response = session.get(url, headers=headers)
            response.raise_for_status()  # This will raise an exception for 4XX and 5XX status codes
            return BeautifulSoup(response.text, 'html.parser')

        try:
            soup = get_soup(url)
            # Your scraping logic here
        except requests.exceptions.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                z = pd.DataFrame()
                return z 
        except Exception as e:
                print(f"An error occurred: {e}")
                z = pd.DataFrame()
                return z 

        #page = requests.get(url, headers=random.choice(headers))
        z = pd.DataFrame()
    #if page.status_code == 200:
        #url_content = page.text
       # print("Success")
    
        #soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="container")


        pollster_data = []
        date_data =[]
        sample_data =[]
        dvalue_data =[]
        rvalue_data  = []
        MoE = []
        

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


        data_rows = list(zip_longest(pollster_data, date_data, sample_data, MoE, dvalue_data, rvalue_data, fillvalue=None))
        df = pd.DataFrame(data_rows, columns =['pollster', 'date', 'sampleSize', 'dvalue', 'rvalue', 'finalR', 'finalD', 'state', 'type', 'year', 'winner'])


        #"pollster": row[0],
        #        "date": row[1],
        #        "sampleSize": row[2],
        #        "marginError": row[3],
        #        "dvalue": row[4],
        #        "rvalue": row[5],
        #        "finalR":row[6],
        #        "finalD":row[7],
        #        "state": state,
        #        "type": type,
        #        "year": year,
        #        "winner": winner
        df = df.drop_duplicates().sort_values('Pollster') 
        return df
    #else:
        #print("Failed to retrieve. Status Code was", page.status_code)
        #return z

    def clean_data1(dataframe, type, year):
        dataframe['dvalue'] = dataframe['dvalue'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', np.nan).astype(float)
        dataframe['rvalue'] = dataframe['rvalue'].astype(str).str.replace(r'[^\d.]', '', regex=True).replace('', np.nan).astype(float)
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
            
        dataframe['sampleSize'] = dataframe['sampleSize'].apply(clean_sample_size)
        dataframe['year'] = year
        dataframe['date'] = dataframe['date'].astype(str).str.replace(r'^.*-\s*','', regex=True)+'/'    + str(year)
        dataframe['date'] = pd.to_datetime(dataframe['date'], errors='coerce')
        def margin_to_float(x):
            try:
                return float(x)
            except:
                return np.nan
        dataframe['marginError'] = dataframe['marginError'].apply(margin_to_float)
        dataframe['Type'] = type
        return dataframe
    
    def clean_data2(df, type, year):
            df = df.drop(df[df['pollster'] == 'rcp_average'].index)              
            df.reset_index(inplace=True)

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
            #clockstart = 0
            a_day = 0
            b_day = 0
            fuck = 0
            
            for date in df['date']:
                match = re.match(pattern, date)
                month1 = int(match.group(1))
                month2 = int(match.group(3))
                if year == 2024 and month1 > 8 and month2 > 8 and fuck == 0:
                            #year_flip += 1
                            #fuck += 1
                if clockstart == 0 and a == 0 and b == 0:  #Clock intitialization...write a into memory
                    if month1 < month2:
                        month = month1
                        clockstart += month
                        a += month
                        a_day += int(match.group(2))
                        if year == 2024 and a > 6:
                            year_flip += 1
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
                        if year == 2024 and a > 6:
                            year_flip += 1
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
                        if month > a and (month - a) > 3: #year flip!!
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
                        if month > a and (month - a) <= 3: #error!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(2))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #year_flip += 1
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
                        if month > a and (month - a) > 3: #year flip!!
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
                        if month > a and (month - a) <= 3: #error!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(2))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #year_flip += 1
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
            a = 0
            b = 0
            year_flip = 0
            clockstart = 0
            a_day = 0
            b_day = 0
            
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
  
    def clean_data(df, type, year):
            df = df.drop(df[df['pollster'] == 'rcp_average'].index)              
            df.reset_index(inplace=True)
            
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
            fuck = 0
            print(len(df['date']))
            #print(df)
            for date in df['date']:
                try:    
                    match = re.match(pattern, date)
                    month1 = int(match.group(1))
                    month2 = int(match.group(3))
                    if year == "2024" and (month1 > 7 or month2 > 7) and fuck == 0:
                        year_flip += 1
                        fuck += 1
                except:
                    continue
                #if year == 2024 and month1 > 6 or month2 > 6 and fuck == 0:
                            #year_flip += 1
                            #fuck += 1
                if clockstart == 0 and a == 0 and b == 0:  #Clock intitialization...write a into memory
                    if month1 < month2:
                        month = month2
                        clockstart += month
                        a += month
                        a_day += int(match.group(4))
                        print("bigfuckingtitties1")
                        #if year == 2024 and month > 6:
                            #year_flip += 1
                        #amount -= 1
                        #print(a)
                        #print(b)
                        #if year == 2024:
                            #year_flip += 1
                        if len(df['date']) == 1:
                            break
                        else:
                            continue
                    else:
                        month = month2
                        #new_dates.append(str(month) + '/' + str(match.group(4)) + '/' + year)
                        clockstart += month
                        a += month
                        a_day += int(match.group(4))
                        print("bigfuckingtitties)")
                        #if year == 2024:
                            #year_flip += 1
                        #amount -= 1
                        if len(df['date']) == 1:
                            break
                        else:
                            continue
                if clockstart > 0 and a > 0 and b == 0: #2nd and memory initialization
                    if month1 < month2:
                        month = month2
                        b = a #1st iteration b is written into memory
                        b_day += a_day
                        a = month #2nd iteration is written down
                        a_day = int(match.group(4))
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
                        a_day = int(match.group(4))
                        year_str = str(int(year) - year_flip)
                        new_date = str(b) + '/' + str(b_day) + '/' + year_str
                        new_dates.append(new_date)
                        #amount -= 1
                        continue
                if clockstart > 0 and a > 0 and b > 0: #WORK HERE....
                    if month1 < month2: #GET LOWEST MONTH   
                        month = month2  #assign to month assign to lowest?
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
                                a_day = int(match.group(4))  
                                year_str = str(int(year) - year_flip) 
                                new_date = str(b) + '/' + str(b_day) + '/' + year_str
                                new_dates.append(new_date)
                                #amount -= 1 
                                continue    
                        if month > a and (month - a) > 3: #year flip!!
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
                        if month > a and (month - a) <= 3: #error!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #year_flip += 1
                            #amount -= 1 
                            continue
                        if month == a: #regular appending when year month is equal...
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
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
                        if month > a and (month - a) > 3: #year flip!!
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
                        if month > a and (month - a) <= 3: #error!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #year_flip += 1
                            #amount -= 1 
                            continue
                        if month == a: #regular appending!!
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + year_str
                            new_dates.append(new_date)
                            #amount -= 1 
                            continue 
        
            year_str = str(int(year) - year_flip) 
            new_date = str(a) + '/' + str(a_day) + '/' + year_str
            new_dates.append(new_date)
            df['date'] = pd.DataFrame(new_dates)
            
            if year == "2024":
                df['finalR'] = "ongoing"
                df['finalD'] = "ongoing"
                df['winner'] = "ongoing"
        


            #print(df['date'])
            def margin_to_float(x):
                try:
                    return float(x)
                except:
                    return np.nan
            df['marginError'] = df['marginError'].apply(margin_to_float)
            df['Type'] = type
            
            

            return df
    #missing_data_url = []
    if type in ["senate", "governor"]:
        #print("x")
        #print()
        df = x(url, state, type, year)
    elif type in ["general"] and year in ["2024"]:
        #print("alt")
        #print()
        df = alt_json_str(url, state, type, year)
    elif type in ["national", "president"]:
        #print("json")
        #print()
        df = json_str(url, state, type, year)
    #elif type in ["general"] and year not in ["2024"]: #hashed because headers collected
        #print("headers")
        #print()
        #df = headers(url, state, type, year)
        #df = clean_data(df, type, year)
        #return df     
    else:
        df = pd.DataFrame()
        missing_data_url.append(url)
        missing_data_state.append(state)
        missing_data_year.append(year)
        missing_data_type.append(type)
        return df 
    if df.empty:
        df = pd.DataFrame()
        missing_data_url.append(url)
        missing_data_state.append(state)
        missing_data_year.append(year)
        missing_data_type.append(type)
        return df  
    else:
        #print(df)
        df = clean_data(df, type, year)

        return df
        
#def allfunctions():

    def RCP_2024_senate():
            
        def get_senate2024_data(url, state):

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
                            
                #"Alabama": "https://www.realclearpolling.com/polls/president/general/2024/alabama/trump-vs-biden#polls",
                #"Alaska": "https://www.realclearpolling.com/polls/president/general/2024/alaska/trump-vs-biden#polls",
                "Arizona": "https://www.realclearpolling.com/polls/senate/general/2024/arizona/lake-vs-gallego#polls",
                #"Arkansas": "https://www.realclearpolling.com/polls/president/general/2024/arkansas/trump-vs-biden#polls",
                "California": "https://www.realclearpolling.com/polls/senate/general/2024/california/garvey-vs-schiff#polls",
                #"Colorado": "https://www.realclearpolling.com/polls/president/general/2024/colorado/trump-vs-biden#polls",
                "Connecticut": "https://www.realclearpolling.com/polls/senate/general/2024/connecticut/murphy-vs-republican#polls",
                "Delaware": "https://www.realclearpolling.com/polls/senate/general/2024/delaware/carper-vs-republican", 
                "Florida": "https://www.realclearpolling.com/polls/senate/general/2024/florida/scott-vs-mucarsel-powell#polls",
                #"Georgia": "https://www.realclearpolling.com/polls/president/general/2024/georgia/trump-vs-biden#polls",
                "Hawaii": "https://www.realclearpolling.com/polls/senate/general/2024/hawaii/hirono-vs-republican#polls",
                #"Idaho": "https://www.realclearpolling.com/polls/president/general/2024/idaho/trump-vs-biden#polls",
                #"Illinois": "https://www.realclearpolling.com/polls/president/general/2024/illinois/trump-vs-biden#polls",
                "Indiana": "https://www.realclearpolling.com/polls/senate/open-seat/2024/indiana#polls",
                #"Iowa": "https://www.realclearpolling.com/polls/president/general/2024/iowa/trump-vs-biden#polls",
                #"Kansas": "https://www.realclearpolling.com/polls/president/general/2024/kansas/trump-vs-biden#polls",
                #"Kentucky": "https://www.realclearpolling.com/polls/president/general/2024/kentucky/trump-vs-biden#polls",
                #"Louisiana": "https://www.realclearpolling.com/polls/president/general/2024/louisiana/trump-vs-biden#polls",
                "Maine": "https://www.realclearpolling.com/polls/senate/general/2024/maine/king-vs-republican-vs-democrat#polls",
                #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
                #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
                "Maryland": "https://www.realclearpolling.com/polls/senate/general/2024/maryland#polls",
                "Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2024/massachusetts/warren-vs-republican#polls",
                "Michigan": "https://www.realclearpolling.com/elections/senate/2024/michigan#polls",
                "Minnesota": "https://www.realclearpolling.com/polls/senate/general/2024/minnesota/fraser-vs-klobuchar#polls",
                "Mississippi": "https://www.realclearpolling.com/polls/senate/general/2024/mississippi/wicker-vs-democrat#polls",
                "Missouri": "https://www.realclearpolling.com/polls/senate/general/2024/missouri/hawley-vs-kunce#polls",
                "Montana": "https://www.realclearpolling.com/polls/senate/general/2024/montana/sheehy-vs-tester#polls",
                "Nebraksa": "https://www.realclearpolling.com/polls/senate/general/2024/nebraska/fischer-vs-democrat#polls",
                #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
                "Nevada": "https://www.realclearpolling.com/elections/senate/2024/nevada#polls",
                #"New Hampshire": "https://www.realclearpolling.com/polls/president/general/2024/new-hampshire/trump-vs-biden#polls",
                "New Jersey": "https://www.realclearpolling.com/elections/senate/2024/new-jersey#polls",
                "New Mexico": "https://www.realclearpolling.com/polls/senate/general/2024/new-mexico/heinrich-vs-republican#polls",
                "New York": "https://www.realclearpolling.com/polls/senate/general/2024/new-york/gillibrand-vs-republican#polls",
                #"North Carolina": "https://www.realclearpolling.com/polls/president/general/2024/north-carolina/trump-vs-biden#polls",
                "North Dakota": "https://www.realclearpolling.com/polls/senate/general/2024/north-dakota/cramer-vs-democrat#polls",
                "Ohio": "https://www.realclearpolling.com/polls/senate/general/2024/ohio/brown-vs-moreno#polls",
                #"Oklahoma": "https://www.realclearpolling.com/polls/president/general/2024/oklahoma/trump-vs-biden#polls",
                #"Oregon": "https://www.realclearpolling.com/polls/president/general/2024/oregon/trump-vs-biden#polls",
                "Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2024/pennsylvania/mccormick-vs-casey#polls",
                "Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2024/rhode-island/whitehouse-vs-republican#polls",  
                #"South Carolina": "https://www.realclearpolling.com/polls/president/general/2024/south-carolina/trump-vs-biden#polls",
                #"South Dakota": "https://www.realclearpolitics.com/epolls/2024/president/sd/south_dakota_trump_vs_biden_vs_kennedy-8477.html#polls",
                "Tennessee": "https://www.realclearpolling.com/polls/senate/general/2024/tennessee/blackburn-vs-johnson#polls",
                "Texas": "https://www.realclearpolling.com/polls/senate/general/2024/texas/cruz-vs-allred#polls",
                "Utah": "https://www.realclearpolling.com/polls/senate/open-seat/2024/utah#polls",
                "Vermont": "https://www.realclearpolling.com/polls/senate/general/2024/vermont/sanders-vs-republican#polls",
                "Virginia": "https://www.realclearpolling.com/polls/senate/general/2024/virginia/kaine-vs-republican#polls",
                "Washington": "https://www.realclearpolling.com/polls/senate/general/2024/washington/garcia-vs-cantwell#polls",
                "West Virginia": "https://www.realclearpolling.com/polls/senate/open-seat/2024/west-virginia#polls",
                "Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2024/wisconsin/hovde-vs-baldwin#polls",
                "Wyoming": "https://www.realclearpolling.com/polls/senate/general/2024/wyoming/barrasso-vs-democrat#polls"
                
            }

        all_state_dataframe = []

        for state, url in state_urls.items():
            state_df = get_senate2024_data(url, state)
            df = pd.DataFrame(state_df)
            if len(df)>0:
                df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
                all_state_dataframe.append(df)
            else:
                continue
                
        all_state_df = pd.concat(all_state_dataframe, ignore_index=True)
        df_2024_senate = all_state_df
        return df_2024_senate


    def RCP_2022_senate():
        
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
        df_2022_senate = all_state_df
        return df_2022_senate
        

    def RCP_2020_senate():
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
        df_2020_senate = all_state_df
        return df_2020_senate
        

    def RCP_2018_senate():
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
                        
            #"Alabama": "https://www.realclearpolling.com/polls/senate/general/2020/alabama/tuberville-vs-jones#polls",
            #"Alaska": "https://www.realclearpolling.com/polls/senate/general/2020/alaska/sullivan-vs-gross#polls",
            "Arizona": "https://www.realclearpolling.com/polls/senate/general/2018/arizona/mcsally-vs-sinema#polls",
            #"Arkansas": "https://www.realclearpolling.com/polls/senate/general/2020/arkansas/cotton-vs-harrington#polls",
            "California": "https://www.realclearpolling.com/polls/senate/general/2018/california/feinstein-vs-leon#polls",
            #"Colorado": "https://www.realclearpolling.com/polls/senate/general/2020/colorado/gardner-vs-hickenlooper#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/senate/general/2018/connecticut/corey-vs-murphy#polls",
            "Delaware": "https://www.realclearpolling.com/polls/senate/general/2018/delaware/arlett-vs-carper#polls", 
            "Florida": "https://www.realclearpolling.com/polls/senate/general/2018/florida/scott-vs-nelson#polls",
            #"Georgia": "https://www.realclearpolling.com/polls/senate/general/2020/georgia/perdue-vs-ossoff#polls",
            "Hawaii": "https://www.realclearpolitics.com/epolls/2018/senate/hi/hawaii_senate_curtis_vs_hirono-6264.html#polls",
            #"Idaho": "https://www.realclearpolitics.com/epolls/2020/senate/id/idaho_senate_risch_vs_jordan-7070.html#polls",
            #"Illinois": "https://www.realclearpolitics.com/epolls/2020/senate/il/illinois_senate_curran_vs_durbin-7071.html#polls",
            "Indiana": "https://www.realclearpolling.com/polls/senate/general/2018/indiana/braun-vs-donnelly-vs-brenton#polls",
            #"Iowa": "https://www.realclearpolling.com/polls/senate/general/2020/iowa/ernst-vs-greenfield#polls",
            #"Kansas": "https://www.realclearpolling.com/polls/senate/general/2020/kansas/marshall-vs-bollier#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2020/kentucky/mcconnell-vs-mcgrath#polls",
            #"Louisiana": "https://www.realclearpolitics.com/epolls/2020/senate/la/louisiana_senate_open_primary-7074.html#polls",
            "Maine": "https://www.realclearpolling.com/polls/senate/general/2018/maine/brakey-vs-king#polls",
            #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
            #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
            "Maryland": "https://www.realclearpolling.com/polls/senate/general/2018/maryland/campbell-vs-cardin-vs-simon#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2018/massachusetts/diehl-vs-warren#polls",
            "Michigan": "https://www.realclearpolling.com/polls/senate/general/2018/michigan/james-vs-stabenow#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/newberger-vs-klobuchar#polls",
            "Minnesota_SPECIAL": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/housley-vs-smith",
            "Mississippi": "https://www.realclearpolling.com/polls/senate/general/2018/mississippi/wicker-vs-baria#polls",
            "Mississippi_RUNOFF":"https://www.realclearpolling.com/polls/senate/general/2018/mississippi-runoff-election",
            "Missouri": "https://www.realclearpolling.com/polls/senate/general/2018/missouri/hawley-vs-mccaskill#polls",
            "Montana": "https://www.realclearpolling.com/polls/senate/general/2018/montana/rosendale-vs-tester#polls",
            "Nebraksa": "https://www.realclearpolitics.com/epolls/2018/senate/ne/nebraska_senate_fischer_vs_raybould_-6315.html#polls",
            #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/polls/senate/general/2018/nevada/heller-vs-rosen#polls",
            #"New Hampshire": "https://www.realclearpolling.com/polls/senate/general/2020/new-hampshire/messner-vs-shaheen#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/senate/general/2018/new-jersey/hugin-vs-menendez#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/senate/general/2018/new-mexico/rich-vs-heinrich-vs-johnson#polls",
            "New York": "https://www.realclearpolling.com/polls/senate/general/2018/new-york/farley-vs-gillibrand#polls",
            #"North Carolina": "https://www.realclearpolling.com/polls/senate/general/2020/north-carolina/tillis-vs-cunningham#polls",
            "North Dakota": "https://www.realclearpolling.com/polls/senate/general/2018/north-dakota/cramer-vs-heitkamp#polls",
            "Ohio": "https://www.realclearpolling.com/polls/senate/general/2018/ohio/renacci-vs-brown#polls",
            #"Oklahoma": "https://www.realclearpolling.com/polls/senate/general/2020/oklahoma/inhofe-vs-broyles#polls",
            #"Oregon": "https://www.realclearpolitics.com/epolls/2020/senate/or/oregon_senate_perkins_vs_merkley-7081.html#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2018/pennsylvania/barletta-vs-casey#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2018/rhode-island/flanders-vs-whitehouse#polls",  
            #"South Carolina":"https://www.realclearpolling.com/polls/senate/general/2020/south-carolina/graham-vs-harrison#polls",
            #"South Dakota": "https://www.realclearpolling.com/polls/senate/general/2020/south-dakota/rounds-vs-ahlers#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/senate/general/2018/tennessee/blackburn-vs-bredesen#polls",
            "Texas": "https://www.realclearpolling.com/polls/senate/general/2018/texas/cruz-vs-o'rourke#polls",
            "Utah": "https://www.realclearpolling.com/polls/senate/general/2018/utah/romney-vs-wilson#polls",
            "Vermont": "https://www.realclearpolling.com/polls/senate/general/2018/vermont/zupan-vs-sanders#polls",
            "Virginia": "https://www.realclearpolling.com/polls/senate/general/2018/virginia/stewart-vs-kaine#polls",
            "Washington": "https://www.realclearpolling.com/polls/senate/general/2018/washington/hutchison-vs-cantwell#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/senate/general/2018/west-virginia/morrisey-vs-manchin#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2018/wisconsin/vukmir-vs-baldwin#polls",
            "Wyoming": "https://www.realclearpolitics.com/epolls/2018/senate/wy/wyoming_senate_barrasso_vs_trauner-6320.html#polls"
            
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
        df_2018_senate = all_state_df
        return df_2018_senate


    def RCP_2016_senate():
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

        df_2016_senate = all_state_df
        return df_2016_senate


    def RCP_2014_senate():
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

        df_2014_senate = all_state_df
        return df_2014_senate   


    #there is NO 2024 governor data

    def RCP_2022_governor():
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
        df_2022_governor = all_state_df
        return df_2022_governor   

    def RCP_2020_governor():
        def get_governor2020_data(url, state):

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
                        
        # "Alabama": "https://www.realclearpolling.com/polls/governor/general/2022/alabama/ivey-vs-flowers#polls",
            #"Alaska": "https://www.realclearpolling.com/polls/governor/general/2022/alaska/dunleavy-vs-gara-final-round#polls",
            #"Arizona": "https://www.realclearpolling.com/polls/governor/general/2022/arizona/lake-vs-hobbs#polls",
            #"Arkansas": "https://www.realclearpolling.com/polls/governor/general/2022/arkansas/huckabeesanders-vs-jones#polls",
            #"California": "https://www.realclearpolling.com/polls/governor/general/2022/california/dahle-vs-newsom#polls",
            #"Colorado": "https://www.realclearpolling.com/polls/governor/general/2022/colorado/ganahl-vs-polis#polls",
            #"Connecticut": "https://www.realclearpolling.com/polls/governor/general/2022/connecticut/stefanowski-vs-lamont#polls",
            "Delaware": "https://www.realclearpolling.com/polls/governor/general/2020/delaware/murray-vs-carney#polls", 
            #"Florida": "https://www.realclearpolling.com/polls/governor/general/2022/florida/desantis-vs-crist#polls",
            #"Georgia": "https://www.realclearpolling.com/polls/governor/general/2022/georgia/kemp-vs-abrams#polls",
            #"Hawaii": "https://www.realclearpolitics.com/epolls/2022/governor/hi/hawaii_governor_aiona_vs_green-7928.html#polls",
            #"Idaho": "https://www.realclearpolitics.com/epolls/2022/governor/id/idaho_governor_little_vs_heidt-7743.html#polls",
            #"Illinois": "https://www.realclearpolling.com/polls/governor/general/2022/illinois/bailey-vs-pritzker#polls",
            "Indiana": "https://www.realclearpolling.com/polls/governor/general/2020/indiana/holcomb-vs-myers-#polls",
            #"Iowa": "https://www.realclearpolling.com/polls/governor/general/2022/iowa/reynolds-vs-dejear#polls",
            #"Kansas": "https://www.realclearpolling.com/polls/governor/general/2022/kansas/kelly-vs-schmidt#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
            #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
            #"Maine": "https://www.realclearpolling.com/polls/governor/general/2022/maine/lepage-vs-mills#polls",
            #"Maryland": "https://www.realclearpolling.com/polls/governor/general/2022/massachusetts/diehl-vs-healey#polls",
            #"Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2022/massachusetts/diehl-vs-healey#polls",
            #"Michigan": "https://www.realclearpolling.com/polls/governor/general/2022/michigan/dixon-vs-whitmer#polls",
            #"Minnesota": "https://www.realclearpolling.com/polls/governor/general/2022/minnesota/jensen-vs-walz#polls",
            #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
            "Missouri": "https://www.realclearpolling.com/polls/governor/general/2020/missouri/parson-vs-galloway#polls",
            "Montana": "https://www.realclearpolling.com/polls/governor/general/2020/montana/gianforte-vs-cooney#polls",
            #"Nebraksa": "https://www.realclearpolitics.com/epolls/2022/governor/ne/nebraska_governor_pillen_vs_blood-7897.html#polls",
            #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            #"Nevada": "https://www.realclearpolling.com/polls/governor/general/2022/nevada/lombardo-vs-sisolak#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2020/new-hampshire/sununu-vs-feltes#polls",
            #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
            #"New Mexico": "https://www.realclearpolling.com/polls/governor/general/2022/new-mexico/ronchetti-vs-grisham#polls",
            #"New York": "https://www.realclearpolling.com/polls/governor/general/2022/new-york/zeldin-vs-hochul#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/governor/general/2020/north-carolina/forest-vs-cooper#polls",
            "North Dakota": "https://www.realclearpolitics.com/epolls/2020/governor/nd/north_dakota_governor_burgum_vs_lenz-7200.html#polls",
            #"Ohio": "https://www.realclearpolling.com/polls/governor/general/2022/ohio/dewine-vs-whaley#polls",
            #"Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2022/oklahoma/stitt-vs-hofmeister#polls",
            #"Oregon": "https://www.realclearpolling.com/polls/governor/general/2022/oregon/drazan-vs-kotek-vs-johnson#polls",
            #"Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2022/pennsylvania/mastriano-vs-shapiro#polls",
            #"Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2022/rhode-island/kalus-vs-mckee#polls",  
            #"South Carolina":"https://www.realclearpolling.com/polls/governor/general/2022/south-carolina/mcmaster-vs-cunningham#polls",
            #"South Dakota": "https://www.realclearpolling.com/polls/governor/general/2022/south-dakota/noem-vs-smith#polls",
            #"Tennessee": "https://www.realclearpolitics.com/epolls/2022/governor/tn/tennessee_governor_lee_vs_martin-7925.html#polls",
            #"Texas": "https://www.realclearpolling.com/polls/governor/general/2022/texas/abbott-vs-o'rourke#polls",
            "Utah": "https://www.realclearpolling.com/polls/governor/general/2020/utah/cox-vs-peterson#polls",
            "Vermont": "https://www.realclearpolling.com/polls/governor/general/2020/vermont/scott-vs-zuckerman#polls",
            #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
            "Washington": "https://www.realclearpolling.com/polls/governor/general/2020/washington/culp-vs-inslee#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/governor/general/2020/west-virginia/justice-vs-salango#polls",
            #"Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2022/wisconsin/michels-vs-evers#polls",
            #"Wyoming": "https://www.realclearpolitics.com/epolls/2022/governor/wy/wyoming_governor_gordon_vs_livingston-7904.html#polls"
            
        }


        all_state_dataframe = []

        for state, url in state_urls.items():
            state_df = get_governor2020_data(url, state)
            df = pd.DataFrame(state_df)
            if len(df)>0:
                df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
                all_state_dataframe.append(df)
            else:
                continue
            
        all_state_df = pd.concat(all_state_dataframe, ignore_index=True)
        df_2020_governor = all_state_df
        return df_2020_governor

    def RCP_2018_governor():
        def get_governor2018_data(url, state):

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
                        
            "Alabama": "https://www.realclearpolitics.com/epolls/2018/governor/al/alabama_governor_ivey_vs_maddox-6405.html#polls",
            "Alaska": "https://www.realclearpolling.com/polls/governor/general/2018/alaska/dunleavy-vs-begich#polls",
            "Arizona": "https://www.realclearpolling.com/polls/governor/general/2018/arizona/ducey-vs-garcia#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/governor/general/2018/arkansas/hutchinson-vs-henderson#polls",
            "California": "https://www.realclearpolling.com/polls/governor/general/2018/california/cox-vs-newsom#polls",
            "Colorado": "https://www.realclearpolling.com/polls/governor/general/2018/colorado/stapleton-vs-polis#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/governor/general/2018/connecticut/stefanowski-vs-lamont#polls",
            #"Delaware": "https://www.realclearpolling.com/polls/governor/general/2020/delaware/murray-vs-carney#polls", 
            "Florida": "https://www.realclearpolling.com/polls/governor/general/2018/florida/desantis-vs-gillum#polls",
            "Georgia": "https://www.realclearpolling.com/polls/governor/general/2018/georgia/kemp-vs-abrams#polls",
            "Hawaii": "https://www.realclearpolling.com/polls/governor/general/2018/hawaii/tupola-vs-ige#polls",
            "Idaho": "https://www.realclearpolitics.com/epolls/2018/governor/id/idaho_governor_little_vs_jordan-6413.html#polls",
            "Illinois": "https://www.realclearpolling.com/polls/governor/general/2018/illinois/rauner-vs-pritzker#polls",
            #"Indiana": "https://www.realclearpolling.com/polls/governor/general/2020/indiana/holcomb-vs-myers-#polls",
            "Iowa": "https://www.realclearpolling.com/polls/governor/general/2018/iowa/reynolds-vs-hubbell#polls",
            "Kansas": "https://www.realclearpolling.com/polls/governor/general/2018/kansas/kobach-vs-kelly-vs-orman#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
            #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
            "Maine": "https://www.realclearpolling.com/polls/governor/general/2018/maine/moody-vs-mills#polls",
            "Maryland": "https://www.realclearpolling.com/polls/governor/general/2018/maryland/hogan-vs-jealous#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2018/massachusetts/baker-vs-gonzalez#polls",
            "Michigan": "https://www.realclearpolling.com/polls/governor/general/2018/michigan/schuette-vs-whitmer#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/governor/general/2018/minnesota/johnson-vs-walz#polls",
            #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
            #"Missouri": "https://www.realclearpolling.com/polls/governor/general/2020/missouri/parson-vs-galloway#polls",
            #"Montana": "https://www.realclearpolling.com/polls/governor/general/2020/montana/gianforte-vs-cooney#polls",
            "Nebraksa": "https://www.realclearpolitics.com/epolls/2018/governor/ne/nebraska_governor_ricketts_vs_krist-6421.html#polls",
            "Nevada": "https://www.realclearpolling.com/polls/governor/general/2018/nevada/laxalt-vs-sisolak#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2018/new-hampshire/sununu-vs-kelly#polls",
            #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/governor/general/2018/new-mexico/pearce-vs-grisham#polls",
            "New York": "https://www.realclearpolling.com/polls/governor/general/2018/new-york/molinaro-vs-cuomo#polls",
            #"North Carolina": "https://www.realclearpolling.com/polls/governor/general/2020/north-carolina/forest-vs-cooper#polls",
            #"North Dakota": "https://www.realclearpolitics.com/epolls/2020/governor/nd/north_dakota_governor_burgum_vs_lenz-7200.html#polls",
            "Ohio": "https://www.realclearpolling.com/polls/governor/general/2018/ohio/dewine-vs-cordray#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2018/oklahoma/stitt-vs-edmondson#polls",
            "Oregon": "https://www.realclearpolling.com/polls/governor/general/2018/oregon/buehler-vs-brown#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2018/pennsylvania/wagner-vs-wolf#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2018/rhode-island/fung-vs-raimondo#polls",  
            "South Carolina":"https://www.realclearpolling.com/polls/governor/general/2018/south-carolina/mcmaster-vs-smith#polls",
            "South Dakota": "https://www.realclearpolling.com/polls/governor/general/2018/south-dakota/noem-vs-sutton#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/governor/general/2018/tennessee/lee-vs-dean#polls",
            "Texas": "https://www.realclearpolling.com/polls/governor/general/2018/texas/abbott-vs-valdez#polls",
            #"Utah": "https://www.realclearpolling.com/polls/governor/general/2020/utah/cox-vs-peterson#polls",
            "Vermont": "https://www.realclearpolling.com/polls/governor/general/2018/vermont/scott-vs-hallquist#polls",
            #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
            #"Washington": "https://www.realclearpolling.com/polls/governor/general/2020/washington/culp-vs-inslee#polls",
            #"West Virginia": "https://www.realclearpolling.com/polls/governor/general/2020/west-virginia/justice-vs-salango#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2018/wisconsin/walker-vs-evers-vs-anderson#polls",
            "Wyoming": "https://www.realclearpolitics.com/epolls/2018/governor/wy/wyoming_governor_gordon_vs_throne-6666.html#polls"
            
        }


        all_state_dataframe = []

        for state, url in state_urls.items():
            state_df = get_governor2018_data(url, state)
            df = pd.DataFrame(state_df)
            if len(df)>0:
                df = df.drop_duplicates().dropna(subset=['pollster']).dropna(subset=['dvalue'])
                all_state_dataframe.append(df)
            else:
                continue
            
        all_state_df = pd.concat(all_state_dataframe, ignore_index=True)
        df_2018_governor = all_state_df
        return df_2018_governor

    def RCP_2016_governor():
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
        df_2016_governor = all_state_df
        return df_2016_governor

    def RCP_2014_governor():
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
        df_2014_governor = all_state_df
        return df_2014_governor



    def RCP_2024_national():
        
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
            return df
        url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-biden'
        df_national = get_national2024_data(url)  
        df_2024_national = df_national
        return df_2024_national

    def RCP_2020_national():
        
        def get_national2020_data(url):
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

            return df
        url = 'https://www.realclearpolling.com/polls/president/general/2020/trump-vs-biden'
        df_national = get_national2020_data(url)  
        df_2020_national = df_national
        return df_2020_national

    def RCP_2016_national():
        def get_national2016_data(url):
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

            return df
        url = 'https://www.realclearpolling.com/polls/president/general/2016/trump-vs-clinton'
        df_national = get_national2016_data(url)   
        df_2016_national = df_national
        return df_2016_national




    def RCP_2024_president():
        def get_state_data(url, state):

            page = requests.get(url)

            if page.status_code == 200:
                url_content = page.text
                print("Success")
                
                soup = BeautifulSoup(page.content, "html.parser") 

                script_tags = soup.find_all('script')

                for script in script_tags:
                    if script.string and 'finalData' in script.string:
                        str = script.string
                        break

                str2 = str.split('self.__next_f.push(')
                str3 = str2[1][:-1]
                jsonx = json.loads(str3)
                json_str = jsonx[1] 
                
                pollster_pattern = r'"pollster":\s*"([^"]*)"'
                date_pattern = r'"date":\s*"([^"]*)"'
                sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
                margin_error_pattern = r'"marginError":\s*"([^"]*)"'
                
                link_pattern = r'"link":\s*"([^"]*)"'

                dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
                dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

                rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
                rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'


                dvalue_data = re.findall(dvalue_pattern1, json_str) or re.findall(dvalue_pattern2, json_str)
                rvalue_data = re.findall(rvalue_pattern1, json_str) or re.findall(rvalue_pattern2, json_str)

                pollster_data = re.findall(pollster_pattern, json_str)
                date_data = re.findall(date_pattern, json_str)
                sample_size_data = re.findall(sample_size_pattern, json_str)
                margin_error_data = re.findall(margin_error_pattern, json_str)
                
                link_data = re.findall(link_pattern, json_str)

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
                        
            "Alabama": "https://www.realclearpolling.com/polls/president/general/2024/alabama/trump-vs-biden#polls",
            "Alaska": "https://www.realclearpolling.com/polls/president/general/2024/alaska/trump-vs-biden#polls",
            "Arizona": "https://www.realclearpolling.com/polls/president/general/2024/arizona/trump-vs-biden#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/president/general/2024/arkansas/trump-vs-biden#polls",
            "California": "https://www.realclearpolling.com/polls/president/general/2024/california/trump-vs-biden#polls",
            "Colorado": "https://www.realclearpolling.com/polls/president/general/2024/colorado/trump-vs-biden#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/president/general/2024/connecticut/trump-vs-biden#polls",
            "Delaware": "https://www.realclearpolitics.com/epolls/2024/president/de/delaware_trump_vs_biden-8423.html", 
            "Florida": "https://www.realclearpolling.com/polls/president/general/2024/florida/trump-vs-biden#polls",
            "Georgia": "https://www.realclearpolling.com/polls/president/general/2024/georgia/trump-vs-biden#polls",
            "Hawaii": "https://www.realclearpolitics.com/epolls/2024/president/hi/hawaii_trump_vs_biden-8427.html#polls",
            "Idaho": "https://www.realclearpolling.com/polls/president/general/2024/idaho/trump-vs-biden#polls",
            "Illinois": "https://www.realclearpolling.com/polls/president/general/2024/illinois/trump-vs-biden#polls",
            "Indiana": "https://www.realclearpolling.com/polls/president/general/2024/indiana/trump-vs-biden#polls",
            "Iowa": "https://www.realclearpolling.com/polls/president/general/2024/iowa/trump-vs-biden#polls",
            "Kansas": "https://www.realclearpolling.com/polls/president/general/2024/kansas/trump-vs-biden#polls",
            "Kentucky": "https://www.realclearpolling.com/polls/president/general/2024/kentucky/trump-vs-biden#polls",
            "Louisiana": "https://www.realclearpolling.com/polls/president/general/2024/louisiana/trump-vs-biden#polls",
            "Maine": "https://www.realclearpolling.com/polls/president/general/2024/maine/biden-vs-trump#polls",
            "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
            "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
            "Maryland": "https://www.realclearpolling.com/polls/president/general/2024/maryland/trump-vs-biden#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2024/massachusetts/trump-vs-biden#polls",
            "Michigan": "https://www.realclearpolling.com/polls/president/general/2024/michigan/trump-vs-biden#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/president/general/2024/minnesota/trump-vs-biden#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/president/general/2024/mississippi/trump-vs-biden#polls",
            "Missouri": "https://www.realclearpolling.com/polls/president/general/2024/missouri/trump-vs-biden#polls",
            "Montana": "https://www.realclearpolling.com/polls/president/general/2024/montana/trump-vs-biden#polls",
            "Nebraksa": "https://www.realclearpolling.com/polls/president/general/2024/nebraska/trump-vs-biden#polls",
            "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/polls/president/general/2024/nevada/trump-vs-biden#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2024/new-hampshire/trump-vs-biden#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/president/general/2024/new-jersey/trump-vs-biden#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/president/general/2024/new-mexico/trump-vs-biden#polls",
            "New York": "https://www.realclearpolling.com/polls/president/general/2024/new-york/trump-vs-biden#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/president/general/2024/north-carolina/trump-vs-biden#polls",
            "North Dakota": "https://www.realclearpolling.com/polls/president/general/2024/north-dakota/trump-vs-biden#polls",
            "Ohio": "https://www.realclearpolling.com/polls/president/general/2024/ohio/trump-vs-biden#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2024/oklahoma/trump-vs-biden#polls",
            "Oregon": "https://www.realclearpolling.com/polls/president/general/2024/oregon/trump-vs-biden#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2024/pennsylvania/trump-vs-biden#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/president/general/2024/rhode-island/trump-vs-biden",  
            "South Carolina": "https://www.realclearpolling.com/polls/president/general/2024/south-carolina/trump-vs-biden#polls",
            "South Dakota": "https://www.realclearpolitics.com/epolls/2024/president/sd/south_dakota_trump_vs_biden_vs_kennedy-8477.html#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/president/general/2024/tennessee/trump-vs-biden#polls",
            "Texas": "https://www.realclearpolling.com/polls/president/general/2024/texas/trump-vs-biden#polls",
            "Utah": "https://www.realclearpolling.com/polls/president/general/2024/utah/trump-vs-biden#polls",
            "Vermont": "https://www.realclearpolling.com/polls/president/general/2024/vermont/trump-vs-biden#polls",
            "Virginia": "https://www.realclearpolling.com/polls/president/general/2024/virginia/trump-vs-biden#polls",
            "Washington": "https://www.realclearpolling.com/polls/president/general/2024/washington/trump-vs-biden#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/president/general/2024/west-virginia/trump-vs-biden#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2024/wisconsin/trump-vs-biden#polls",
            "Wyoming": "https://www.realclearpolling.com/polls/president/general/2024/wyoming/trump-vs-biden#polls"
            
        }


        all_state_dataframe = []

        for state, url in state_urls.items():
            state_df = get_state_data(url, state)
            df = pd.DataFrame(state_df)
            if len(df)>0:
                df = df.drop_duplicates().dropna(subset=['pollster'])
                all_state_dataframe.append(df)
            else:
                continue
            
        all_state_df = pd.concat(all_state_dataframe, ignore_index=True)
        df_2024_president = all_state_df
        return df_2024_president   

    def RCP_2020_president():
        def get_2020state_data(url, state):

            page = requests.get(url)

            if page.status_code == 200:
                url_content = page.text
                print("Success")
                
                soup = BeautifulSoup(page.content, "html.parser") 

                script_tags = soup.find_all('script')

                for script in script_tags:
                    if script.string and 'finalData' in script.string:
                        str = script.string
                        break

                str2 = str.split('self.__next_f.push(')
                str3 = str2[1][:-1]
                jsonx = json.loads(str3)
                json_str = jsonx[1] 

                pollster_pattern = r'"pollster":\s*"([^"]*)"'
                date_pattern = r'"date":\s*"([^"]*)"'
                sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
                margin_error_pattern = r'"marginError":\s*"([^"]*)"'
                
                link_pattern = r'"link":\s*"([^"]*)"'

                dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
                dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

                rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
                rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'

                dvalue_data = re.findall(dvalue_pattern1, json_str) or re.findall(dvalue_pattern2, json_str)
                rvalue_data = re.findall(rvalue_pattern1, json_str) or re.findall(rvalue_pattern2, json_str)

                pollster_data = re.findall(pollster_pattern, json_str)
                date_data = re.findall(date_pattern, json_str)
                sample_size_data = re.findall(sample_size_pattern, json_str)
                margin_error_data = re.findall(margin_error_pattern, json_str)
                
                link_data = re.findall(link_pattern, json_str)

                data_rows = []
                for row in zip_longest(pollster_data, date_data, sample_size_data, margin_error_data, dvalue_data, rvalue_data, link_data, fillvalue=None):
                    data_rows.append({
                        
                        "pollster": row[0],
                        "date": row[1],
                        "sampleSize": row[2],
                        "marginError": row[3],
                        "dvalue": row[4],
                        "rvalue": row[5],
                        "state": state,
                        
                    })
                
                return data_rows
            else:
                print("Failed to retrieve. Status Code was", page.status_code)
                return[]


        state_urls = {
            
            "Alabama": "https://www.realclearpolling.com/polls/president/general/2020/alabama/trump-vs-biden#polls",
            "Alaska": "https://www.realclearpolling.com/polls/president/general/2020/alaska/trump-vs-biden#polls",
            "Arizona": "https://www.realclearpolling.com/polls/president/general/2020/arizona/trump-vs-biden#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/president/general/2020/arkansas/trump-vs-biden#polls",
            "California": "https://www.realclearpolling.com/polls/president/general/2020/california/trump-vs-biden#polls",
            "Colorado": "https://www.realclearpolling.com/polls/president/general/2020/colorado/trump-vs-biden#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/president/general/2020/connecticut/trump-vs-biden#polls",
            "Delaware": "https://www.realclearpolling.com/polls/president/general/2020/delaware/trump-vs-biden#polls",
            "Florida": "https://www.realclearpolling.com/polls/president/general/2020/florida/trump-vs-biden#polls",
            "Georgia": "https://www.realclearpolling.com/polls/president/general/2020/georgia/trump-vs-biden#polls",
            "Hawaii": "https://www.realclearpolling.com/polls/president/general/2020/hawaii/trump-vs-biden#polls",
            #"Idaho": "",  # Missing URL
            #"Illinois": "", #Missing URL
            "Indiana": "https://www.realclearpolling.com/polls/president/general/2020/indiana/trump-vs-biden#polls",
            "Iowa": "https://www.realclearpolling.com/polls/president/general/2020/iowa/trump-vs-biden#polls",
            "Kansas": "https://www.realclearpolling.com/polls/president/general/2020/kansas/trump-vs-biden#polls",
            "Kentucky": "https://www.realclearpolling.com/polls/president/general/2020/kentucky/trump-vs-biden#polls",
            "Louisiana": "https://www.realclearpolling.com/polls/president/general/2020/louisiana/trump-vs-biden#polls",
            "Maine": "https://www.realclearpolling.com/polls/president/general/maine/2020/trump-vs-biden#polls",
            "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2020/maine-cd1/trump-vs-biden#polls",
            "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2020/maine/cd2-trump-vs-biden#polls",
            "Maryland": "https://www.realclearpolling.com/polls/president/general/2020/maryland/trump-vs-biden#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2020/massachusetts/trump-vs-biden#polls",
            "Michigan": "https://www.realclearpolling.com/polls/president/general/2020/michigan/trump-vs-biden#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/president/general/2020/minnesota/trump-vs-biden#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/president/general/2020/mississippi/trump-vs-biden#polls",
            "Missouri": "https://www.realclearpolling.com/polls/president/general/2020/missouri/trump-vs-biden#polls",
            "Montana": "https://www.realclearpolling.com/polls/president/general/2020/montana/trump-vs-biden#polls",
            "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2020/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/polls/president/general/2020/nevada/trump-vs-biden#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2020/new-hampshire/trump-vs-biden#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/president/general/2020/new-jersey/trump-vs-biden#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/president/general/2020/new-mexico/trump-vs-biden#polls",
            "New York": "https://www.realclearpolling.com/polls/president/general/2020/new-york/trump-vs-biden#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/president/general/2020/north-carolina/trump-vs-biden#polls",
            #"North Dakota": "",  # Missing URL
            "Ohio": "https://www.realclearpolling.com/polls/president/general/2020/ohio/trump-vs-biden#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2020/oklahoma/trump-vs-biden#polls",
            "Oregon": "https://www.realclearpolling.com/polls/president/general/2020/oregon/trump-vs-biden#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2020/pennsylvania/trump-vs-biden#polls",
            #"Rhode Island": "",  # Missing URL
            "South Carolina": "https://www.realclearpolling.com/polls/president/general/2020/south-carolina/trump-vs-biden#polls",
            "South Dakota": "https://www.realclearpolling.com/polls/president/general/2020/south-dakota/trump-vs-biden#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/president/general/2020/tennessee/trump-vs-biden#polls",
            "Texas": "https://www.realclearpolling.com/polls/president/general/2020/texas/trump-vs-biden#polls",
            "Utah": "https://www.realclearpolling.com/polls/president/general/2020/utah/trump-vs-biden#polls",
            "Vermont": "https://www.realclearpolling.com/polls/president/general/2020/vermont/trump-vs-biden#polls",
            "Virginia": "https://www.realclearpolling.com/polls/president/general/2020/virginia/trump-vs-biden#polls",
            "Washington": "https://www.realclearpolling.com/polls/president/general/2020/washington/trump-vs-biden#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/president/general/2020/west-virginia/trump-vs-biden#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2020/wisconsin/trump-vs-biden#polls",
            "Wyoming": "https://www.realclearpolling.com/polls/president/general/2020/wyoming/trump-vs-biden#polls",
                        
        }

        all_state_dataframe = []

        for state, url in state_urls.items():
            state_df = get_2020state_data(url, state)
            df = pd.DataFrame(state_df)
            if len(df)>0:
                df = df.drop_duplicates().dropna(subset=['pollster'])
                all_state_dataframe.append(df)
            else:
                continue
            
        all_state_df = pd.concat(all_state_dataframe, ignore_index=True)
        df_2020_president = all_state_df
        return df_2020_president   

    def RCP_2016_president():   
        def get_states2016_data(url, state):

            page = requests.get(url)

            if page.status_code == 200:
                url_content = page.text
                print("Success")
                
                soup = BeautifulSoup(page.content, "html.parser") 

                script_tags = soup.find_all('script')

                for script in script_tags:
                    if script.string and 'finalData' in script.string:
                        str = script.string
                        break

                str2 = str.split('self.__next_f.push(')
                str3 = str2[1][:-1]
                jsonx = json.loads(str3)
                json_str = jsonx[1] 
                
                pollster_pattern = r'"pollster":\s*"([^"]*)"'
                date_pattern = r'"date":\s*"([^"]*)"'
                sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
                margin_error_pattern = r'"marginError":\s*"([^"]*)"'
                
                link_pattern = r'"link":\s*"([^"]*)"'

                dvalue_pattern1 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'
                dvalue_pattern2 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Democrat","value":"([^"]*)"'

                rvalue_pattern1 = r'"candidate":\[{[^}]*},{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'
                rvalue_pattern2 = r'"candidate":\[{"name":"([^"]*?)","affiliation":"Republican","value":"([^"]*)"'


                dvalue_data = re.findall(dvalue_pattern1, json_str) or re.findall(dvalue_pattern2, json_str)
                rvalue_data = re.findall(rvalue_pattern1, json_str) or re.findall(rvalue_pattern2, json_str)

                pollster_data = re.findall(pollster_pattern, json_str)
                date_data = re.findall(date_pattern, json_str)
                sample_size_data = re.findall(sample_size_pattern, json_str)
                margin_error_data = re.findall(margin_error_pattern, json_str)
                
                link_data = re.findall(link_pattern, json_str)

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
                        
            "Alabama": "https://www.realclearpolitics.com/epolls/2016/president/al/alabama_trump_vs_clinton-5898.html",
            "Alaska": "https://www.realclearpolling.com/polls/president/general/2016/alaska/trump-vs-clinton#polls",
            "Arizona": "https://www.realclearpolling.com/polls/president/general/2016/arizona/trump-vs-clinton#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/president/general/2016/arkansas/trump-vs-clinton#polls",
            "California": "https://www.realclearpolling.com/polls/president/general/2016/california/trump-vs-clinton#polls",
            "Colorado": "https://www.realclearpolling.com/polls/president/general/2016/colorado/trump-vs-clinton#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/president/general/2016/connecticut/trump-vs-clinton#polls",
            "Delaware": "https://www.realclearpolling.com/polls/president/general/2016/delaware/trump-vs-clinton#polls", 
            "Florida": "https://www.realclearpolling.com/polls/president/general/2016/florida/trump-vs-clinton#polls",
            "Georgia": "https://www.realclearpolling.com/polls/president/general/2016/georgia/trump-vs-clinton#polls",
            "Hawaii": "https://www.realclearpolitics.com/epolls/2016/president/hi/hawaii_trump_vs_clinton-5902.html#polls",
            "Idaho": "https://www.realclearpolling.com/polls/president/general/2016/idaho/trump-vs-clinton#polls",
            "Illinois": "https://www.realclearpolling.com/polls/president/general/2016/illinois/trump-vs-clinton#polls",
            "Indiana": "https://www.realclearpolling.com/polls/president/general/2016/indiana/trump-vs-clinton#polls",
            "Iowa": "https://www.realclearpolling.com/polls/president/general/2016/iowa/trump-vs-clinton#polls",
            "Kansas": "https://www.realclearpolling.com/polls/president/general/2016/kansas/trump-vs-clinton#polls",
            "Kentucky": "https://www.realclearpolling.com/polls/president/general/2016/kentucky/trump-vs-clinton#polls",
            "Louisiana": "https://www.realclearpolling.com/polls/president/general/2016/louisiana/trump-vs-clinton#polls",
            #"Maine": "", no data
            "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2016/maine/cd1-trump-vs-clinton#polls",
            "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2016/maine/cd2-trump-vs-clinton#polls",
            "Maryland": "https://www.realclearpolling.com/polls/president/general/2016/maryland/trump-vs-clinton#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2016/massachusetts/trump-vs-clinton#polls",
            "Michigan": "https://www.realclearpolling.com/polls/president/general/2016/michigan/trump-vs-clinton#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/president/general/2016/minnesota/trump-vs-clinton#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/president/general/2016/mississippi/trump-vs-clinton#polls",
            "Missouri": "https://www.realclearpolling.com/polls/president/general/2016/missouri/trump-vs-clinton#polls",
            "Montana": "https://www.realclearpolling.com/polls/president/general/2016/montana/trump-vs-clinton#polls",
            "Nebraksa": "https://www.realclearpolling.com/polls/president/general/2016/nebraska/trump-vs-clinton#polls",
            "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2016/nebraska/cd2-trump-vs-clinton#polls",
            "Nevada": "https://www.realclearpolling.com/polls/president/general/2016/nevada/trump-vs-clinton-vs-johnson#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2016/new-hampshire/trump-vs-clinton#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/president/general/2016/new-jersey/trump-vs-clinton#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/president/general/2016/new-mexico/trump-vs-clinton#polls",
            "New York": "https://www.realclearpolling.com/polls/president/general/2016/new-york/trump-vs-clinton#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/president/general/2016/north-carolina/trump-vs-clinton#polls",
            "North Dakota": "https://www.realclearpolitics.com/epolls/2016/president/nd/north_dakota_trump_vs_clinton-5907.html#polls",
            "Ohio": "https://www.realclearpolling.com/polls/president/general/2016/ohio/trump-vs-clinton#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2016/oklahoma/trump-vs-clinton#polls",
            "Oregon": "https://www.realclearpolling.com/polls/president/general/2016/oregon/trump-vs-clinton#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2016/pennsylvania/trump-vs-clinton#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/president/general/2016/rhode-island/trump-vs-clinton#polls",  
            "South Carolina": "https://www.realclearpolling.com/polls/president/general/2016/south-carolina/trump-vs-clinton#polls",
            "South Dakota": "https://www.realclearpolling.com/polls/president/general/2016/south-dakota/trump-vs-clinton#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/president/general/2016/tennessee/trump-vs-clinton#polls",
            "Texas": "https://www.realclearpolling.com/polls/president/general/2016/texas/trump-vs-clinton#polls",
            "Utah": "https://www.realclearpolling.com/polls/president/general/2016/utah/trump-vs-clinton#polls",
            "Vermont": "https://www.realclearpolling.com/polls/president/general/2016/vermont/trump-vs-clinton#polls",
            "Virginia": "https://www.realclearpolling.com/polls/president/general/2016/virginia/trump-vs-clinton#polls",
            "Washington": "https://www.realclearpolling.com/polls/president/general/2016/washington/trump-vs-clinton#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/president/general/2016/west-virginia/trump-vs-clinton#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2016/wisconsin/trump-vs-clinton#polls",
            "Wyoming": "https://www.realclearpolitics.com/epolls/2016/president/wy/wyoming_trump_vs_clinton-5913.html#polls"
            
        }

        all_state_dataframe = []

        for state, url in state_urls.items():
            state_df = get_states2016_data(url, state)
            df = pd.DataFrame(state_df)
            if len(df)>0:
                df = df.drop_duplicates().dropna(subset=['pollster'])
                all_state_dataframe.append(df)
            else:
                continue
            
        all_state_df = pd.concat(all_state_dataframe, ignore_index=True)
        df_2016_president = all_state_df
        return df_2016_president   



    def RCP_2024_general():
        

        def get_generalongressional2024_data(url):
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
            print(json_str)

            #search pattern index
            pollster_pattern = r'"pollster":\s*"([^"]*)"'
            date_pattern = r'"date":\s*"([^"]*)"'
            sample_size_pattern = r'"sampleSize":\s*"([^"]*)"'
            margin_error_pattern = r'"marginError":\s*"([^"]*)"'
            dvalue_pattern = r'"candidate":\[{"name":"Biden","affiliation":"Democrat","value":"([^"]*)"'
            rvalue_pattern = r'"candidate":\[{[^}]*},{"name":"Trump","affiliation":"Republican","value":"([^"]*)"'
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
            return df
        url = 'https://www.realclearpolling.com/polls/state-of-the-union/2024/generic-congressional-vote'
        df_national = get_generalongressional2024_data(url)
        df_2024_general = df_national
        return df_2024_general    

    def RCP_2022_general():
        url = 'https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html'

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
        df_2022_general = df
        return df_2022_general

    def RCP_2020_general():
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
        df_2020_general = df
        return df_2020_general 

    def RCP_2018_general():
        url = 'https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html'

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
        df_2018_general = df
        return df_2018_general

    def RCP_2016_general():
        url = 'https://www.realclearpolitics.com/epolls/other/2016_generic_congressional_vote-5279.html'

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
        df_2016_general = df
        return df_2016_general

    def RCP_2014_general():
        url = 'https://www.realclearpolitics.com/epolls/other/generic_congressional_vote-2170.html#polls'

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
        df_2014_general = df
        return df_2014_general   

master_url = {
    "2024":{
        "senate":{
                            
            #"Alabama": "https://www.realclearpolling.com/polls/president/general/2024/alabama/trump-vs-biden#polls",
            #"Alaska": "https://www.realclearpolling.com/polls/president/general/2024/alaska/trump-vs-biden#polls",
            "Arizona": "https://www.realclearpolling.com/polls/senate/general/2024/arizona/lake-vs-gallego#polls",
            #"Arkansas": "https://www.realclearpolling.com/polls/president/general/2024/arkansas/trump-vs-biden#polls",
            "California": "https://www.realclearpolling.com/polls/senate/general/2024/california/garvey-vs-schiff#polls",
            #"Colorado": "https://www.realclearpolling.com/polls/president/general/2024/colorado/trump-vs-biden#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/senate/general/2024/connecticut/murphy-vs-republican#polls",
            "Delaware": "https://www.realclearpolling.com/polls/senate/general/2024/delaware/carper-vs-republican", 
            "Florida": "https://www.realclearpolling.com/polls/senate/general/2024/florida/scott-vs-mucarsel-powell#polls",
            #"Georgia": "https://www.realclearpolling.com/polls/president/general/2024/georgia/trump-vs-biden#polls",
            "Hawaii": "https://www.realclearpolling.com/polls/senate/general/2024/hawaii/hirono-vs-republican#polls",
            #"Idaho": "https://www.realclearpolling.com/polls/president/general/2024/idaho/trump-vs-biden#polls",
            #"Illinois": "https://www.realclearpolling.com/polls/president/general/2024/illinois/trump-vs-biden#polls",
            "Indiana": "https://www.realclearpolling.com/polls/senate/open-seat/2024/indiana#polls",
            #"Iowa": "https://www.realclearpolling.com/polls/president/general/2024/iowa/trump-vs-biden#polls",
            #"Kansas": "https://www.realclearpolling.com/polls/president/general/2024/kansas/trump-vs-biden#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/president/general/2024/kentucky/trump-vs-biden#polls",
            #"Louisiana": "https://www.realclearpolling.com/polls/president/general/2024/louisiana/trump-vs-biden#polls",
            "Maine": "https://www.realclearpolling.com/polls/senate/general/2024/maine/king-vs-republican-vs-democrat#polls",
            #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
            #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
            "Maryland": "https://www.realclearpolling.com/polls/senate/general/2024/maryland#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2024/massachusetts/warren-vs-republican#polls",
            "Michigan": "https://www.realclearpolling.com/elections/senate/2024/michigan#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/senate/general/2024/minnesota/fraser-vs-klobuchar#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/senate/general/2024/mississippi/wicker-vs-democrat#polls",
            "Missouri": "https://www.realclearpolling.com/polls/senate/general/2024/missouri/hawley-vs-kunce#polls",
            "Montana": "https://www.realclearpolling.com/polls/senate/general/2024/montana/sheehy-vs-tester#polls",
            "Nebraksa": "https://www.realclearpolling.com/polls/senate/general/2024/nebraska/fischer-vs-democrat#polls",
            #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/elections/senate/2024/nevada#polls",
            #"New Hampshire": "https://www.realclearpolling.com/polls/president/general/2024/new-hampshire/trump-vs-biden#polls",
            "New Jersey": "https://www.realclearpolling.com/elections/senate/2024/new-jersey#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/senate/general/2024/new-mexico/heinrich-vs-republican#polls",
            "New York": "https://www.realclearpolling.com/polls/senate/general/2024/new-york/gillibrand-vs-republican#polls",
            #"North Carolina": "https://www.realclearpolling.com/polls/president/general/2024/north-carolina/trump-vs-biden#polls",
            "North Dakota": "https://www.realclearpolling.com/polls/senate/general/2024/north-dakota/cramer-vs-democrat#polls",
            "Ohio": "https://www.realclearpolling.com/polls/senate/general/2024/ohio/brown-vs-moreno#polls",
            #"Oklahoma": "https://www.realclearpolling.com/polls/president/general/2024/oklahoma/trump-vs-biden#polls",
            #"Oregon": "https://www.realclearpolling.com/polls/president/general/2024/oregon/trump-vs-biden#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2024/pennsylvania/mccormick-vs-casey#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2024/rhode-island/whitehouse-vs-republican#polls",  
            #"South Carolina": "https://www.realclearpolling.com/polls/president/general/2024/south-carolina/trump-vs-biden#polls",
            #"South Dakota": "https://www.realclearpolitics.com/epolls/2024/president/sd/south_dakota_trump_vs_biden_vs_kennedy-8477.html#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/senate/general/2024/tennessee/blackburn-vs-johnson#polls",
            "Texas": "https://www.realclearpolling.com/polls/senate/general/2024/texas/cruz-vs-allred#polls",
            "Utah": "https://www.realclearpolling.com/polls/senate/open-seat/2024/utah#polls",
            "Vermont": "https://www.realclearpolling.com/polls/senate/general/2024/vermont/sanders-vs-republican#polls",
            "Virginia": "https://www.realclearpolling.com/polls/senate/general/2024/virginia/kaine-vs-republican#polls",
            "Washington": "https://www.realclearpolling.com/polls/senate/general/2024/washington/garcia-vs-cantwell#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/senate/open-seat/2024/west-virginia#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2024/wisconsin/hovde-vs-baldwin#polls",
            "Wyoming": "https://www.realclearpolling.com/polls/senate/general/2024/wyoming/barrasso-vs-democrat#polls"
                
            },
        "governor":{   #no governor
            #no data
        },
        "national":{
            "national":"https://www.realclearpolling.com/polls/president/general/2024/trump-vs-biden"
        },
        "president":{
            "Alabama": "https://www.realclearpolling.com/polls/president/general/2024/alabama/trump-vs-biden#polls",
            "Alaska": "https://www.realclearpolling.com/polls/president/general/2024/alaska/trump-vs-biden#polls",
            "Arizona": "https://www.realclearpolling.com/polls/president/general/2024/arizona/trump-vs-biden#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/president/general/2024/arkansas/trump-vs-biden#polls",
            "California": "https://www.realclearpolling.com/polls/president/general/2024/california/trump-vs-biden#polls",
            "Colorado": "https://www.realclearpolling.com/polls/president/general/2024/colorado/trump-vs-biden#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/president/general/2024/connecticut/trump-vs-biden#polls",
            "Delaware": "https://www.realclearpolitics.com/epolls/2024/president/de/delaware_trump_vs_biden-8423.html", 
            "Florida": "https://www.realclearpolling.com/polls/president/general/2024/florida/trump-vs-biden#polls",
            "Georgia": "https://www.realclearpolling.com/polls/president/general/2024/georgia/trump-vs-biden#polls",
            "Hawaii": "https://www.realclearpolitics.com/epolls/2024/president/hi/hawaii_trump_vs_biden-8427.html#polls",
            "Idaho": "https://www.realclearpolling.com/polls/president/general/2024/idaho/trump-vs-biden#polls",
            "Illinois": "https://www.realclearpolling.com/polls/president/general/2024/illinois/trump-vs-biden#polls",
            "Indiana": "https://www.realclearpolling.com/polls/president/general/2024/indiana/trump-vs-biden#polls",
            "Iowa": "https://www.realclearpolling.com/polls/president/general/2024/iowa/trump-vs-biden#polls",
            "Kansas": "https://www.realclearpolling.com/polls/president/general/2024/kansas/trump-vs-biden#polls",
            "Kentucky": "https://www.realclearpolling.com/polls/president/general/2024/kentucky/trump-vs-biden#polls",
            "Louisiana": "https://www.realclearpolling.com/polls/president/general/2024/louisiana/trump-vs-biden#polls",
            "Maine": "https://www.realclearpolling.com/polls/president/general/2024/maine/biden-vs-trump#polls",
            "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
            "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
            "Maryland": "https://www.realclearpolling.com/polls/president/general/2024/maryland/trump-vs-biden#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2024/massachusetts/trump-vs-biden#polls",
            "Michigan": "https://www.realclearpolling.com/polls/president/general/2024/michigan/trump-vs-biden#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/president/general/2024/minnesota/trump-vs-biden#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/president/general/2024/mississippi/trump-vs-biden#polls",
            "Missouri": "https://www.realclearpolling.com/polls/president/general/2024/missouri/trump-vs-biden#polls",
            "Montana": "https://www.realclearpolling.com/polls/president/general/2024/montana/trump-vs-biden#polls",
            "Nebraksa": "https://www.realclearpolling.com/polls/president/general/2024/nebraska/trump-vs-biden#polls",
            "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/polls/president/general/2024/nevada/trump-vs-biden#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2024/new-hampshire/trump-vs-biden#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/president/general/2024/new-jersey/trump-vs-biden#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/president/general/2024/new-mexico/trump-vs-biden#polls",
            "New York": "https://www.realclearpolling.com/polls/president/general/2024/new-york/trump-vs-biden#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/president/general/2024/north-carolina/trump-vs-biden#polls",
            "North Dakota": "https://www.realclearpolling.com/polls/president/general/2024/north-dakota/trump-vs-biden#polls",
            "Ohio": "https://www.realclearpolling.com/polls/president/general/2024/ohio/trump-vs-biden#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2024/oklahoma/trump-vs-biden#polls",
            "Oregon": "https://www.realclearpolling.com/polls/president/general/2024/oregon/trump-vs-biden#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2024/pennsylvania/trump-vs-biden#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/president/general/2024/rhode-island/trump-vs-biden",  
            "South Carolina": "https://www.realclearpolling.com/polls/president/general/2024/south-carolina/trump-vs-biden#polls",
            "South Dakota": "https://www.realclearpolitics.com/epolls/2024/president/sd/south_dakota_trump_vs_biden_vs_kennedy-8477.html#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/president/general/2024/tennessee/trump-vs-biden#polls",
            "Texas": "https://www.realclearpolling.com/polls/president/general/2024/texas/trump-vs-biden#polls",
            "Utah": "https://www.realclearpolling.com/polls/president/general/2024/utah/trump-vs-biden#polls",
            "Vermont": "https://www.realclearpolling.com/polls/president/general/2024/vermont/trump-vs-biden#polls",
            "Virginia": "https://www.realclearpolling.com/polls/president/general/2024/virginia/trump-vs-biden#polls",
            "Washington": "https://www.realclearpolling.com/polls/president/general/2024/washington/trump-vs-biden#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/president/general/2024/west-virginia/trump-vs-biden#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2024/wisconsin/trump-vs-biden#polls",
            "Wyoming": "https://www.realclearpolling.com/polls/president/general/2024/wyoming/trump-vs-biden#polls"
        },
        "general":{
            "general": "https://www.realclearpolling.com/polls/state-of-the-union/2024/generic-congressional-vote"
        }
    },
    "2022":{
        "senate":{
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
        },
        "governor":{
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
        },
        "national":{  # no data/not an P'election year
            #no data
        },
        "general":{
            #"general":"https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html"
        }
    },
    "2020":{
        "senate":{
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
        },
        "governor":{
            "Alabama": "https://www.realclearpolling.com/polls/governor/general/2022/alabama/ivey-vs-flowers#polls",
            #"Alaska": "https://www.realclearpolling.com/polls/governor/general/2022/alaska/dunleavy-vs-gara-final-round#polls",
            #"Arizona": "https://www.realclearpolling.com/polls/governor/general/2022/arizona/lake-vs-hobbs#polls",
            #"Arkansas": "https://www.realclearpolling.com/polls/governor/general/2022/arkansas/huckabeesanders-vs-jones#polls",
            #"California": "https://www.realclearpolling.com/polls/governor/general/2022/california/dahle-vs-newsom#polls",
            #"Colorado": "https://www.realclearpolling.com/polls/governor/general/2022/colorado/ganahl-vs-polis#polls",
            #"Connecticut": "https://www.realclearpolling.com/polls/governor/general/2022/connecticut/stefanowski-vs-lamont#polls",
            "Delaware": "https://www.realclearpolling.com/polls/governor/general/2020/delaware/murray-vs-carney#polls", 
            #"Florida": "https://www.realclearpolling.com/polls/governor/general/2022/florida/desantis-vs-crist#polls",
            #"Georgia": "https://www.realclearpolling.com/polls/governor/general/2022/georgia/kemp-vs-abrams#polls",
            #"Hawaii": "https://www.realclearpolitics.com/epolls/2022/governor/hi/hawaii_governor_aiona_vs_green-7928.html#polls",
            #"Idaho": "https://www.realclearpolitics.com/epolls/2022/governor/id/idaho_governor_little_vs_heidt-7743.html#polls",
            #"Illinois": "https://www.realclearpolling.com/polls/governor/general/2022/illinois/bailey-vs-pritzker#polls",
            "Indiana": "https://www.realclearpolling.com/polls/governor/general/2020/indiana/holcomb-vs-myers-#polls",
            #"Iowa": "https://www.realclearpolling.com/polls/governor/general/2022/iowa/reynolds-vs-dejear#polls",
            #"Kansas": "https://www.realclearpolling.com/polls/governor/general/2022/kansas/kelly-vs-schmidt#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
            #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
            #"Maine": "https://www.realclearpolling.com/polls/governor/general/2022/maine/lepage-vs-mills#polls",
            #"Maryland": "https://www.realclearpolling.com/polls/governor/general/2022/massachusetts/diehl-vs-healey#polls",
            #"Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2022/massachusetts/diehl-vs-healey#polls",
            #"Michigan": "https://www.realclearpolling.com/polls/governor/general/2022/michigan/dixon-vs-whitmer#polls",
            #"Minnesota": "https://www.realclearpolling.com/polls/governor/general/2022/minnesota/jensen-vs-walz#polls",
            #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
            "Missouri": "https://www.realclearpolling.com/polls/governor/general/2020/missouri/parson-vs-galloway#polls",
            "Montana": "https://www.realclearpolling.com/polls/governor/general/2020/montana/gianforte-vs-cooney#polls",
            #"Nebraksa": "https://www.realclearpolitics.com/epolls/2022/governor/ne/nebraska_governor_pillen_vs_blood-7897.html#polls",
            #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            #"Nevada": "https://www.realclearpolling.com/polls/governor/general/2022/nevada/lombardo-vs-sisolak#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2020/new-hampshire/sununu-vs-feltes#polls",
            #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
            #"New Mexico": "https://www.realclearpolling.com/polls/governor/general/2022/new-mexico/ronchetti-vs-grisham#polls",
            #"New York": "https://www.realclearpolling.com/polls/governor/general/2022/new-york/zeldin-vs-hochul#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/governor/general/2020/north-carolina/forest-vs-cooper#polls",
            "North Dakota": "https://www.realclearpolitics.com/epolls/2020/governor/nd/north_dakota_governor_burgum_vs_lenz-7200.html#polls",
            #"Ohio": "https://www.realclearpolling.com/polls/governor/general/2022/ohio/dewine-vs-whaley#polls",
            #"Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2022/oklahoma/stitt-vs-hofmeister#polls",
            #"Oregon": "https://www.realclearpolling.com/polls/governor/general/2022/oregon/drazan-vs-kotek-vs-johnson#polls",
            #"Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2022/pennsylvania/mastriano-vs-shapiro#polls",
            #"Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2022/rhode-island/kalus-vs-mckee#polls",  
            #"South Carolina":"https://www.realclearpolling.com/polls/governor/general/2022/south-carolina/mcmaster-vs-cunningham#polls",
            #"South Dakota": "https://www.realclearpolling.com/polls/governor/general/2022/south-dakota/noem-vs-smith#polls",
            #"Tennessee": "https://www.realclearpolitics.com/epolls/2022/governor/tn/tennessee_governor_lee_vs_martin-7925.html#polls",
            #"Texas": "https://www.realclearpolling.com/polls/governor/general/2022/texas/abbott-vs-o'rourke#polls",
            "Utah": "https://www.realclearpolling.com/polls/governor/general/2020/utah/cox-vs-peterson#polls",
            "Vermont": "https://www.realclearpolling.com/polls/governor/general/2020/vermont/scott-vs-zuckerman#polls",
            #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
            "Washington": "https://www.realclearpolling.com/polls/governor/general/2020/washington/culp-vs-inslee#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/governor/general/2020/west-virginia/justice-vs-salango#polls",
            #"Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2022/wisconsin/michels-vs-evers#polls",
            #"Wyoming": "https://www.realclearpolitics.com/epolls/2022/governor/wy/wyoming_governor_gordon_vs_livingston-7904.html#polls"
        },
        "national":{
            "national":"https://www.realclearpolling.com/polls/president/general/2020/trump-vs-biden"
        },
        "president":{
            "Alabama": "https://www.realclearpolling.com/polls/president/general/2020/alabama/trump-vs-biden#polls",
            "Alaska": "https://www.realclearpolling.com/polls/president/general/2020/alaska/trump-vs-biden#polls",
            "Arizona": "https://www.realclearpolling.com/polls/president/general/2020/arizona/trump-vs-biden#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/president/general/2020/arkansas/trump-vs-biden#polls",
            "California": "https://www.realclearpolling.com/polls/president/general/2020/california/trump-vs-biden#polls",
            "Colorado": "https://www.realclearpolling.com/polls/president/general/2020/colorado/trump-vs-biden#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/president/general/2020/connecticut/trump-vs-biden#polls",
            "Delaware": "https://www.realclearpolling.com/polls/president/general/2020/delaware/trump-vs-biden#polls",
            "Florida": "https://www.realclearpolling.com/polls/president/general/2020/florida/trump-vs-biden#polls",
            "Georgia": "https://www.realclearpolling.com/polls/president/general/2020/georgia/trump-vs-biden#polls",
            "Hawaii": "https://www.realclearpolling.com/polls/president/general/2020/hawaii/trump-vs-biden#polls",
            #"Idaho": "",  # Missing URL
            #"Illinois": "", #Missing URL
            "Indiana": "https://www.realclearpolling.com/polls/president/general/2020/indiana/trump-vs-biden#polls",
            "Iowa": "https://www.realclearpolling.com/polls/president/general/2020/iowa/trump-vs-biden#polls",
            "Kansas": "https://www.realclearpolling.com/polls/president/general/2020/kansas/trump-vs-biden#polls",
            "Kentucky": "https://www.realclearpolling.com/polls/president/general/2020/kentucky/trump-vs-biden#polls",
            "Louisiana": "https://www.realclearpolling.com/polls/president/general/2020/louisiana/trump-vs-biden#polls",
            "Maine": "https://www.realclearpolling.com/polls/president/general/maine/2020/trump-vs-biden#polls",
            "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2020/maine-cd1/trump-vs-biden#polls",
            "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2020/maine/cd2-trump-vs-biden#polls",
            "Maryland": "https://www.realclearpolling.com/polls/president/general/2020/maryland/trump-vs-biden#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2020/massachusetts/trump-vs-biden#polls",
            "Michigan": "https://www.realclearpolling.com/polls/president/general/2020/michigan/trump-vs-biden#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/president/general/2020/minnesota/trump-vs-biden#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/president/general/2020/mississippi/trump-vs-biden#polls",
            "Missouri": "https://www.realclearpolling.com/polls/president/general/2020/missouri/trump-vs-biden#polls",
            "Montana": "https://www.realclearpolling.com/polls/president/general/2020/montana/trump-vs-biden#polls",
            "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2020/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/polls/president/general/2020/nevada/trump-vs-biden#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2020/new-hampshire/trump-vs-biden#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/president/general/2020/new-jersey/trump-vs-biden#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/president/general/2020/new-mexico/trump-vs-biden#polls",
            "New York": "https://www.realclearpolling.com/polls/president/general/2020/new-york/trump-vs-biden#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/president/general/2020/north-carolina/trump-vs-biden#polls",
            #"North Dakota": "",  # Missing URL
            "Ohio": "https://www.realclearpolling.com/polls/president/general/2020/ohio/trump-vs-biden#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2020/oklahoma/trump-vs-biden#polls",
            "Oregon": "https://www.realclearpolling.com/polls/president/general/2020/oregon/trump-vs-biden#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2020/pennsylvania/trump-vs-biden#polls",
            #"Rhode Island": "",  # Missing URL
            "South Carolina": "https://www.realclearpolling.com/polls/president/general/2020/south-carolina/trump-vs-biden#polls",
            "South Dakota": "https://www.realclearpolling.com/polls/president/general/2020/south-dakota/trump-vs-biden#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/president/general/2020/tennessee/trump-vs-biden#polls",
            "Texas": "https://www.realclearpolling.com/polls/president/general/2020/texas/trump-vs-biden#polls",
            "Utah": "https://www.realclearpolling.com/polls/president/general/2020/utah/trump-vs-biden#polls",
            "Vermont": "https://www.realclearpolling.com/polls/president/general/2020/vermont/trump-vs-biden#polls",
            "Virginia": "https://www.realclearpolling.com/polls/president/general/2020/virginia/trump-vs-biden#polls",
            "Washington": "https://www.realclearpolling.com/polls/president/general/2020/washington/trump-vs-biden#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/president/general/2020/west-virginia/trump-vs-biden#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2020/wisconsin/trump-vs-biden#polls",
            "Wyoming": "https://www.realclearpolling.com/polls/president/general/2020/wyoming/trump-vs-biden#polls",
        },
        "general":{
            #"general":"https://www.realclearpolitics.com/epolls/other/2020_generic_congressional_vote-6722.html"
        },
    },
    "2018":{
        "senate":{
            #"Alabama": "https://www.realclearpolling.com/polls/senate/general/2020/alabama/tuberville-vs-jones#polls",
            #"Alaska": "https://www.realclearpolling.com/polls/senate/general/2020/alaska/sullivan-vs-gross#polls",
            "Arizona": "https://www.realclearpolling.com/polls/senate/general/2018/arizona/mcsally-vs-sinema#polls",
            #"Arkansas": "https://www.realclearpolling.com/polls/senate/general/2020/arkansas/cotton-vs-harrington#polls",
            "California": "https://www.realclearpolling.com/polls/senate/general/2018/california/feinstein-vs-leon#polls",
            #"Colorado": "https://www.realclearpolling.com/polls/senate/general/2020/colorado/gardner-vs-hickenlooper#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/senate/general/2018/connecticut/corey-vs-murphy#polls",
            "Delaware": "https://www.realclearpolling.com/polls/senate/general/2018/delaware/arlett-vs-carper#polls", 
            "Florida": "https://www.realclearpolling.com/polls/senate/general/2018/florida/scott-vs-nelson#polls",
            #"Georgia": "https://www.realclearpolling.com/polls/senate/general/2020/georgia/perdue-vs-ossoff#polls",
            "Hawaii": "https://www.realclearpolitics.com/epolls/2018/senate/hi/hawaii_senate_curtis_vs_hirono-6264.html#polls",
            #"Idaho": "https://www.realclearpolitics.com/epolls/2020/senate/id/idaho_senate_risch_vs_jordan-7070.html#polls",
            #"Illinois": "https://www.realclearpolitics.com/epolls/2020/senate/il/illinois_senate_curran_vs_durbin-7071.html#polls",
            "Indiana": "https://www.realclearpolling.com/polls/senate/general/2018/indiana/braun-vs-donnelly-vs-brenton#polls",
            #"Iowa": "https://www.realclearpolling.com/polls/senate/general/2020/iowa/ernst-vs-greenfield#polls",
            #"Kansas": "https://www.realclearpolling.com/polls/senate/general/2020/kansas/marshall-vs-bollier#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2020/kentucky/mcconnell-vs-mcgrath#polls",
            #"Louisiana": "https://www.realclearpolitics.com/epolls/2020/senate/la/louisiana_senate_open_primary-7074.html#polls",
            "Maine": "https://www.realclearpolling.com/polls/senate/general/2018/maine/brakey-vs-king#polls",
            #"Maine CD1": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd1#polls",
            #"Maine CD2": "https://www.realclearpolling.com/polls/president/general/2024/maine/trump-vs-biden-cd2#polls",
            "Maryland": "https://www.realclearpolling.com/polls/senate/general/2018/maryland/campbell-vs-cardin-vs-simon#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/senate/general/2018/massachusetts/diehl-vs-warren#polls",
            "Michigan": "https://www.realclearpolling.com/polls/senate/general/2018/michigan/james-vs-stabenow#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/newberger-vs-klobuchar#polls",
            "Minnesota_SPECIAL": "https://www.realclearpolling.com/polls/senate/general/2018/minnesota/housley-vs-smith",
            "Mississippi": "https://www.realclearpolling.com/polls/senate/general/2018/mississippi/wicker-vs-baria#polls",
            "Mississippi_RUNOFF":"https://www.realclearpolling.com/polls/senate/general/2018/mississippi-runoff-election",
            "Missouri": "https://www.realclearpolling.com/polls/senate/general/2018/missouri/hawley-vs-mccaskill#polls",
            "Montana": "https://www.realclearpolling.com/polls/senate/general/2018/montana/rosendale-vs-tester#polls",
            "Nebraksa": "https://www.realclearpolitics.com/epolls/2018/senate/ne/nebraska_senate_fischer_vs_raybould_-6315.html#polls",
            #"Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2024/nebraska-cd2/trump-vs-biden#polls",
            "Nevada": "https://www.realclearpolling.com/polls/senate/general/2018/nevada/heller-vs-rosen#polls",
            #"New Hampshire": "https://www.realclearpolling.com/polls/senate/general/2020/new-hampshire/messner-vs-shaheen#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/senate/general/2018/new-jersey/hugin-vs-menendez#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/senate/general/2018/new-mexico/rich-vs-heinrich-vs-johnson#polls",
            "New York": "https://www.realclearpolling.com/polls/senate/general/2018/new-york/farley-vs-gillibrand#polls",
            #"North Carolina": "https://www.realclearpolling.com/polls/senate/general/2020/north-carolina/tillis-vs-cunningham#polls",
            "North Dakota": "https://www.realclearpolling.com/polls/senate/general/2018/north-dakota/cramer-vs-heitkamp#polls",
            "Ohio": "https://www.realclearpolling.com/polls/senate/general/2018/ohio/renacci-vs-brown#polls",
            #"Oklahoma": "https://www.realclearpolling.com/polls/senate/general/2020/oklahoma/inhofe-vs-broyles#polls",
            #"Oregon": "https://www.realclearpolitics.com/epolls/2020/senate/or/oregon_senate_perkins_vs_merkley-7081.html#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/senate/general/2018/pennsylvania/barletta-vs-casey#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/senate/general/2018/rhode-island/flanders-vs-whitehouse#polls",  
            #"South Carolina":"https://www.realclearpolling.com/polls/senate/general/2020/south-carolina/graham-vs-harrison#polls",
            #"South Dakota": "https://www.realclearpolling.com/polls/senate/general/2020/south-dakota/rounds-vs-ahlers#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/senate/general/2018/tennessee/blackburn-vs-bredesen#polls",
            "Texas": "https://www.realclearpolling.com/polls/senate/general/2018/texas/cruz-vs-o'rourke#polls",
            "Utah": "https://www.realclearpolling.com/polls/senate/general/2018/utah/romney-vs-wilson#polls",
            "Vermont": "https://www.realclearpolling.com/polls/senate/general/2018/vermont/zupan-vs-sanders#polls",
            "Virginia": "https://www.realclearpolling.com/polls/senate/general/2018/virginia/stewart-vs-kaine#polls",
            "Washington": "https://www.realclearpolling.com/polls/senate/general/2018/washington/hutchison-vs-cantwell#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/senate/general/2018/west-virginia/morrisey-vs-manchin#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/senate/general/2018/wisconsin/vukmir-vs-baldwin#polls",
            "Wyoming": "https://www.realclearpolitics.com/epolls/2018/senate/wy/wyoming_senate_barrasso_vs_trauner-6320.html#polls"
        },
        "governor":{
            "Alabama": "https://www.realclearpolitics.com/epolls/2018/governor/al/alabama_governor_ivey_vs_maddox-6405.html#polls",
            "Alaska": "https://www.realclearpolling.com/polls/governor/general/2018/alaska/dunleavy-vs-begich#polls",
            "Arizona": "https://www.realclearpolling.com/polls/governor/general/2018/arizona/ducey-vs-garcia#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/governor/general/2018/arkansas/hutchinson-vs-henderson#polls",
            "California": "https://www.realclearpolling.com/polls/governor/general/2018/california/cox-vs-newsom#polls",
            "Colorado": "https://www.realclearpolling.com/polls/governor/general/2018/colorado/stapleton-vs-polis#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/governor/general/2018/connecticut/stefanowski-vs-lamont#polls",
            #"Delaware": "https://www.realclearpolling.com/polls/governor/general/2020/delaware/murray-vs-carney#polls", 
            "Florida": "https://www.realclearpolling.com/polls/governor/general/2018/florida/desantis-vs-gillum#polls",
            "Georgia": "https://www.realclearpolling.com/polls/governor/general/2018/georgia/kemp-vs-abrams#polls",
            "Hawaii": "https://www.realclearpolling.com/polls/governor/general/2018/hawaii/tupola-vs-ige#polls",
            "Idaho": "https://www.realclearpolitics.com/epolls/2018/governor/id/idaho_governor_little_vs_jordan-6413.html#polls",
            "Illinois": "https://www.realclearpolling.com/polls/governor/general/2018/illinois/rauner-vs-pritzker#polls",
            #"Indiana": "https://www.realclearpolling.com/polls/governor/general/2020/indiana/holcomb-vs-myers-#polls",
            "Iowa": "https://www.realclearpolling.com/polls/governor/general/2018/iowa/reynolds-vs-hubbell#polls",
            "Kansas": "https://www.realclearpolling.com/polls/governor/general/2018/kansas/kobach-vs-kelly-vs-orman#polls",
            #"Kentucky": "https://www.realclearpolling.com/polls/senate/general/2014/kentucky/mcconnell-vs-grimes#polls",
            #"Louisiana": "https://www.realclearpolitics.com/epolls/2014/senate/louisiana_senate_race.html#polls",
            "Maine": "https://www.realclearpolling.com/polls/governor/general/2018/maine/moody-vs-mills#polls",
            "Maryland": "https://www.realclearpolling.com/polls/governor/general/2018/maryland/hogan-vs-jealous#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/governor/general/2018/massachusetts/baker-vs-gonzalez#polls",
            "Michigan": "https://www.realclearpolling.com/polls/governor/general/2018/michigan/schuette-vs-whitmer#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/governor/general/2018/minnesota/johnson-vs-walz#polls",
            #"Mississippi": "https://www.realclearpolling.com/polls/senate/general/2014/mississippi/cochran-vs-childers#polls",
            #"Missouri": "https://www.realclearpolling.com/polls/governor/general/2020/missouri/parson-vs-galloway#polls",
            #"Montana": "https://www.realclearpolling.com/polls/governor/general/2020/montana/gianforte-vs-cooney#polls",
            "Nebraksa": "https://www.realclearpolitics.com/epolls/2018/governor/ne/nebraska_governor_ricketts_vs_krist-6421.html#polls",
            "Nevada": "https://www.realclearpolling.com/polls/governor/general/2018/nevada/laxalt-vs-sisolak#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/governor/general/2018/new-hampshire/sununu-vs-kelly#polls",
            #"New Jersey": "https://www.realclearpolling.com/polls/senate/general/2014/new-jersey/bell-vs-booker#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/governor/general/2018/new-mexico/pearce-vs-grisham#polls",
            "New York": "https://www.realclearpolling.com/polls/governor/general/2018/new-york/molinaro-vs-cuomo#polls",
            #"North Carolina": "https://www.realclearpolling.com/polls/governor/general/2020/north-carolina/forest-vs-cooper#polls",
            #"North Dakota": "https://www.realclearpolitics.com/epolls/2020/governor/nd/north_dakota_governor_burgum_vs_lenz-7200.html#polls",
            "Ohio": "https://www.realclearpolling.com/polls/governor/general/2018/ohio/dewine-vs-cordray#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/governor/general/2018/oklahoma/stitt-vs-edmondson#polls",
            "Oregon": "https://www.realclearpolling.com/polls/governor/general/2018/oregon/buehler-vs-brown#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/governor/general/2018/pennsylvania/wagner-vs-wolf#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/governor/general/2018/rhode-island/fung-vs-raimondo#polls",  
            "South Carolina":"https://www.realclearpolling.com/polls/governor/general/2018/south-carolina/mcmaster-vs-smith#polls",
            "South Dakota": "https://www.realclearpolling.com/polls/governor/general/2018/south-dakota/noem-vs-sutton#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/governor/general/2018/tennessee/lee-vs-dean#polls",
            "Texas": "https://www.realclearpolling.com/polls/governor/general/2018/texas/abbott-vs-valdez#polls",
            #"Utah": "https://www.realclearpolling.com/polls/governor/general/2020/utah/cox-vs-peterson#polls",
            "Vermont": "https://www.realclearpolling.com/polls/governor/general/2018/vermont/scott-vs-hallquist#polls",
            #"Virginia": "https://www.realclearpolling.com/polls/senate/general/2014/virginia/gillespie-vs-warner#polls",
            #"Washington": "https://www.realclearpolling.com/polls/governor/general/2020/washington/culp-vs-inslee#polls",
            #"West Virginia": "https://www.realclearpolling.com/polls/governor/general/2020/west-virginia/justice-vs-salango#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/governor/general/2018/wisconsin/walker-vs-evers-vs-anderson#polls",
            "Wyoming": "https://www.realclearpolitics.com/epolls/2018/governor/wy/wyoming_governor_gordon_vs_throne-6666.html#polls"
        },
        "national":{  # no data/not an P'election year
            #no data
        },    
        "general":{
           # "general":"https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html"
        }
    },
    "2016":{
        "senate":{
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
        },
        "governor":{
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
        },
        "national":{  
            "national":"https://www.realclearpolling.com/polls/president/general/2016/trump-vs-clinton"
        },
        "president":{
            "Alabama": "https://www.realclearpolitics.com/epolls/2016/president/al/alabama_trump_vs_clinton-5898.html",
            "Alaska": "https://www.realclearpolling.com/polls/president/general/2016/alaska/trump-vs-clinton#polls",
            "Arizona": "https://www.realclearpolling.com/polls/president/general/2016/arizona/trump-vs-clinton#polls",
            "Arkansas": "https://www.realclearpolling.com/polls/president/general/2016/arkansas/trump-vs-clinton#polls",
            "California": "https://www.realclearpolling.com/polls/president/general/2016/california/trump-vs-clinton#polls",
            "Colorado": "https://www.realclearpolling.com/polls/president/general/2016/colorado/trump-vs-clinton#polls",
            "Connecticut": "https://www.realclearpolling.com/polls/president/general/2016/connecticut/trump-vs-clinton#polls",
            "Delaware": "https://www.realclearpolling.com/polls/president/general/2016/delaware/trump-vs-clinton#polls", 
            "Florida": "https://www.realclearpolling.com/polls/president/general/2016/florida/trump-vs-clinton#polls",
            "Georgia": "https://www.realclearpolling.com/polls/president/general/2016/georgia/trump-vs-clinton#polls",
            "Hawaii": "https://www.realclearpolitics.com/epolls/2016/president/hi/hawaii_trump_vs_clinton-5902.html#polls",
            "Idaho": "https://www.realclearpolling.com/polls/president/general/2016/idaho/trump-vs-clinton#polls",
            "Illinois": "https://www.realclearpolling.com/polls/president/general/2016/illinois/trump-vs-clinton#polls",
            "Indiana": "https://www.realclearpolling.com/polls/president/general/2016/indiana/trump-vs-clinton#polls",
            "Iowa": "https://www.realclearpolling.com/polls/president/general/2016/iowa/trump-vs-clinton#polls",
            "Kansas": "https://www.realclearpolling.com/polls/president/general/2016/kansas/trump-vs-clinton#polls",
            "Kentucky": "https://www.realclearpolling.com/polls/president/general/2016/kentucky/trump-vs-clinton#polls",
            "Louisiana": "https://www.realclearpolling.com/polls/president/general/2016/louisiana/trump-vs-clinton#polls",
            #"Maine": "", no data
            "Maine CD1": "https://www.realclearpolling.com/polls/president/general/2016/maine/cd1-trump-vs-clinton#polls",
            "Maine CD2": "https://www.realclearpolling.com/polls/president/general/2016/maine/cd2-trump-vs-clinton#polls",
            "Maryland": "https://www.realclearpolling.com/polls/president/general/2016/maryland/trump-vs-clinton#polls",
            "Massachusetts": "https://www.realclearpolling.com/polls/president/general/2016/massachusetts/trump-vs-clinton#polls",
            "Michigan": "https://www.realclearpolling.com/polls/president/general/2016/michigan/trump-vs-clinton#polls",
            "Minnesota": "https://www.realclearpolling.com/polls/president/general/2016/minnesota/trump-vs-clinton#polls",
            "Mississippi": "https://www.realclearpolling.com/polls/president/general/2016/mississippi/trump-vs-clinton#polls",
            "Missouri": "https://www.realclearpolling.com/polls/president/general/2016/missouri/trump-vs-clinton#polls",
            "Montana": "https://www.realclearpolling.com/polls/president/general/2016/montana/trump-vs-clinton#polls",
            "Nebraksa": "https://www.realclearpolling.com/polls/president/general/2016/nebraska/trump-vs-clinton#polls",
            "Nebraska CD2": "https://www.realclearpolling.com/polls/president/general/2016/nebraska/cd2-trump-vs-clinton#polls",
            "Nevada": "https://www.realclearpolling.com/polls/president/general/2016/nevada/trump-vs-clinton-vs-johnson#polls",
            "New Hampshire": "https://www.realclearpolling.com/polls/president/general/2016/new-hampshire/trump-vs-clinton#polls",
            "New Jersey": "https://www.realclearpolling.com/polls/president/general/2016/new-jersey/trump-vs-clinton#polls",
            "New Mexico": "https://www.realclearpolling.com/polls/president/general/2016/new-mexico/trump-vs-clinton#polls",
            "New York": "https://www.realclearpolling.com/polls/president/general/2016/new-york/trump-vs-clinton#polls",
            "North Carolina": "https://www.realclearpolling.com/polls/president/general/2016/north-carolina/trump-vs-clinton#polls",
            "North Dakota": "https://www.realclearpolitics.com/epolls/2016/president/nd/north_dakota_trump_vs_clinton-5907.html#polls",
            "Ohio": "https://www.realclearpolling.com/polls/president/general/2016/ohio/trump-vs-clinton#polls",
            "Oklahoma": "https://www.realclearpolling.com/polls/president/general/2016/oklahoma/trump-vs-clinton#polls",
            "Oregon": "https://www.realclearpolling.com/polls/president/general/2016/oregon/trump-vs-clinton#polls",
            "Pennsylvania": "https://www.realclearpolling.com/polls/president/general/2016/pennsylvania/trump-vs-clinton#polls",
            "Rhode Island": "https://www.realclearpolling.com/polls/president/general/2016/rhode-island/trump-vs-clinton#polls",  
            "South Carolina": "https://www.realclearpolling.com/polls/president/general/2016/south-carolina/trump-vs-clinton#polls",
            "South Dakota": "https://www.realclearpolling.com/polls/president/general/2016/south-dakota/trump-vs-clinton#polls",
            "Tennessee": "https://www.realclearpolling.com/polls/president/general/2016/tennessee/trump-vs-clinton#polls",
            "Texas": "https://www.realclearpolling.com/polls/president/general/2016/texas/trump-vs-clinton#polls",
            "Utah": "https://www.realclearpolling.com/polls/president/general/2016/utah/trump-vs-clinton#polls",
            "Vermont": "https://www.realclearpolling.com/polls/president/general/2016/vermont/trump-vs-clinton#polls",
            "Virginia": "https://www.realclearpolling.com/polls/president/general/2016/virginia/trump-vs-clinton#polls",
            "Washington": "https://www.realclearpolling.com/polls/president/general/2016/washington/trump-vs-clinton#polls",
            "West Virginia": "https://www.realclearpolling.com/polls/president/general/2016/west-virginia/trump-vs-clinton#polls",
            "Wisconsin": "https://www.realclearpolling.com/polls/president/general/2016/wisconsin/trump-vs-clinton#polls",
            "Wyoming": "https://www.realclearpolitics.com/epolls/2016/president/wy/wyoming_trump_vs_clinton-5913.html#polls"
        },
        "general":{
            "general":"https://www.realclearpolitics.com/epolls/other/2016_generic_congressional_vote-5279.html"
        },
    },
    "2014":{
        "senate":{
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
        },
        "governor":{
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
        },
        "national":{  # no data/not an P'election year
            #no data
    },
        "general":{
           "general":"https://www.realclearpolitics.com/epolls/other/generic_congressional_vote-2170.html#polls"
        }
    },
}

all_df_list = []
import time 
for year, elections in master_url.items(): #year
        for election_type, states in elections.items(): #category
            for state, url in states.items(): #url and state
                
                df = collection(url, state, election_type, year)
                
                if len(df) > 0:
                    print(f"Year: {year}, Election Type: {election_type}, State: {state}, URL: {url}")
                    all_df_list.append(df)
                    print(df)
                else:
                    continue
                                                    
all_df = pd.concat(all_df_list, ignore_index=False)
#all_df.drop(df[])

z = random.randrange(6, 100)
filename = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/ToBen2.csv"
all_df.to_csv(filename, index=False)
missing = pd.DataFrame({
    'urls':missing_data_url,
    'state':missing_data_state,
    'year':missing_data_year,
    'type': missing_data_type
})

#filename1 = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/missing_urls_csv.csv"
#missing.to_csv(filename1, index=False)
#print(missing.to_string(index=False))
print("printed")
y = time.time()

seconds_elapsed = y - x 

print("This script took ", seconds_elapsed, "seconds to run")
