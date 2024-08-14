import requests
import re
from bs4 import BeautifulSoup 
import numpy as np
import pandas as pd
from itertools import zip_longest
from matplotlib import pyplot as plt

z = "2018"

master_generalcongression = {
    "2014":"https://www.realclearpolitics.com/epolls/other/generic_congressional_vote-2170.html#polls",
    "2016":"https://www.realclearpolitics.com/epolls/other/2016_generic_congressional_vote-5279.html",
    "2018":"https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html",
    "2020":"https://www.realclearpolitics.com/epolls/other/2020_generic_congressional_vote-6722.html",
    "2022":"https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html",
}

#url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-harris'
#url = "https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html"

file = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/ElectionModelProjectAugust2024Onward/Congressional Data.xlsx"
file = pd.read_excel(file)
#print(file)

fourteen = file[file["year"] == 2014].reset_index(drop=True)
sixteen = file[file["year"] == 2016].reset_index(drop=True)
eighteen = file[file["year"] == 2018].reset_index(drop=True)
twenty = file[file["year"] == 2020].reset_index(drop=True)
twentytwo  = file[file["year"] == 2022].reset_index(drop=True)



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
    #df = df.drop(df[df['pollster'] == 'rcp_average'].index)
    #df.reset_index(inplace=True)
    #df = df.drop(df[df['pollster'] == 'rcp_average'].index)
    df.reset_index(inplace=True)

    #print(df.to_string(index=True))
    #print(len(df))
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
            #clockstart = 0  #maybe index a year onto it...
            a = 0
            b = 0 #writing block
            c = 0 #flip block corrector
            
            leadingdate = df['date'][0]
            leading_pattern = r"(\d{1,2})/(\d{1,2}) - (\d{1,2})/(\d{1,2})"
            match0 = re.match(leading_pattern, leadingdate)
            leadingdate = int(match0.group(1))
            print(leadingdate)

            if year == "2024" and leadingdate > 8: #current month (writing as of august)
                year_flip = int(year) - 1 
            else:
                year_flip = int(year)

            #year_flip = int(year)
            print(year_flip)
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
                    #if year_flip == "2024" and (month1 > 8 or month2 > 8) and fuck == 0:
                        #year_flip -= 1
                        #fuck += 1
                except:
                    continue
            
                if a == 0 and b == 0:  #Clock intitialization...write a into memory
                    if month1 < month2:
                        month = month2
                        #clockstart += month
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
                        #clockstart += month
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
                if a > 0 and b == 0: #2nd and memory initialization
                    if month1 < month2:
                        month = month2
                        b = a #1st iteration b is written into memory
                        b_day += a_day
                        a = month #2nd iteration is written down
                        a_day = int(match.group(4))
                        #year_str = str(int(year) - year_flip)
                        new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                        new_dates.append(new_date)
                        #amount -= 1
                        continue    
                    else:
                        month = month2
                        b = a #1st iteration
                        b_day += a_day
                        a = month #2nd iteration
                        a_day = int(match.group(4))
                        #year_str = str(int(year) - year_flip)
                        new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                        new_dates.append(new_date)
                        #amount -= 1
                        continue
                if  a > 0 and b > 0: #WORK HERE....
                    if month1 < month2: #GET LOWEST MONTH   
                        month = month2  #assign to month assign to lowest?
                        if month < a: #check for year error or regular appending
                            if month2 == a: #try month2 because see if there is error...
                                month = month2
                                b = a 
                                b_day = a_day
                                a = month 
                                a_day = int(match.group(4))
                                #year_str = str(int(year) - year_flip)
                                new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                                new_dates.append(new_date)
                                #amount -= 1 
                                continue
                            else: #regular appending as month is decreasing
                                b = a 
                                b_day = a_day
                                a = month
                                a_day = int(match.group(4))  
                                #year_str = str(int(year) - year_flip) 
                                new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                                new_dates.append(new_date)
                                #amount -= 1 
                                continue    
                        if month > a and (month - a) > 3: #year flip!!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                            new_dates.append(new_date)
                            year_flip -= 1
                            #amount -= 1 
                            print("a=", a, "b=",b, "month=",month, year_flip)
                            continue
                        if month > a and (month - a) <= 3: #error!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                            new_dates.append(new_date)
                            #year_flip += 1
                            #amount -= 1 
                            continue
                        if month == a: #regular appending when year month is equal...
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
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
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                            new_dates.append(new_date)
                            #amount -= 1 
                            continue        
                        if month > a and (month - a) > 3: #year flip!!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                            new_dates.append(new_date)
                            year_flip -= 1
                            #amount -= 1 
                            print("a=", a, "b=",b, "month=",month, year_flip)
                            continue
                        if month > a and (month - a) <= 3: #error!
                            b = a
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                            new_dates.append(new_date)
                            #year_flip += 1
                            #amount -= 1 
                            continue
                        if month == a: #regular appending!!
                            b = a 
                            b_day = a_day
                            a = month
                            a_day = int(match.group(4))  
                            #year_str = str(int(year) - year_flip) 
                            new_date = str(b) + '/' + str(b_day) + '/' + str(year_flip)
                            new_dates.append(new_date)
                            #amount -= 1 
                            continue 
                #if clockstart >0 and a > 0 and b > 0 and year_flip != 0:
            #year_str = str(int(year) - year_flip) 
            new_date = str(a) + '/' + str(a_day) + '/' + str(year_flip)
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
            #try:
            #    df['marginError'] = df['marginError'].apply(margin_to_float)
            #except:
                
            df['Type'] = type
            
            

            return df


fourteen = clean_data(fourteen, "congressional", "2014") 
sixteen = clean_data(sixteen, "congressional", "2016")
eighteen = clean_data(eighteen, "congressional", "2018")
twenty = clean_data(twenty, "congressional", "2020")
twentytwo = clean_data(twentytwo, "congressional", "2022")


master_list = []
master_list.append(fourteen)
master_list.append(sixteen)
master_list.append(eighteen)
master_list.append(twenty)
master_list.append(twentytwo)


all_general = pd.concat(master_list, ignore_index=True)
file_save = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/ElectionModelProjectAugust2024Onward/Congressional_Data_Algo_2014.2022CSVversion.CSV"

all_general.to_csv(file_save, index=False)

print(all_general.to_string())

print(len(all_general))







#df = get_national2024_data(url)
#df = clean_data(df, "national", z)

#df = clean_data(file, "congressional", )



#print(file.head())

#print(df.to_string(index=False))
#filename = "C:/Users/lukem/Documents/C files/RCP SCRAPERS/Generalcongression2014.2022ThruAlgo.csv"
#df.to_csv(filename, index=False)

