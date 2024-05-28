from selenium import webdriver
from selenium.webdriver.firefox.service import Service  
import pandas as pd
from selenium.webdriver.common.by import By
from itertools import zip_longest
import numpy as np
import re
import webcolors



#options = webdriver.FirefoxOptions()

def get_538_data
driver=webdriver.Firefox()
#driver.get('https://projects.fivethirtyeight.com/polls/president-general/')
#driver.get('https://projects.fivethirtyeight.com/polls/governor/2022/maryland/')
driver.get('https://projects.fivethirtyeight.com/polls/senate/2024/maryland/')
#decides when button is stopped


while True:
    try:
        load_more_button = driver.find_element(By.CLASS_NAME, "show-more-wrap")
        load_more_button.click()
    except:
        break

dates = [element.text for element in driver.find_elements(By.CLASS_NAME, 'date-wrapper')]
samples = [element.text for element in driver.find_elements(By.CLASS_NAME, 'sample')]
sample_type = [element.text for element in driver.find_elements(By.CLASS_NAME, 'sample-type')]
pollsters = [element.text for element in driver.find_elements(By.CLASS_NAME, "pollster-name")]

dvalue = [element.text for element in driver.find_elements(By.XPATH, './/td[contains(@class, "value hide-mobile")][2]//div[@class="heat-map"]')]
dname = [element.text for element in driver.find_elements(By.CLASS_NAME, "answer.first.hide-mobile")]

rname = [element.text for element in driver.find_elements(By.XPATH, './/td[contains(@class, "answer hide-mobile")][1]')]
rvalue = [element.text for element in driver.find_elements(By.XPATH, './/td[contains(@class, "value hide-mobile")][3]//div[@class="heat-map"]')]


samples = [re.sub(r"SAMPLEi", "", sample) for sample in samples]

#samples_cleaned = []
#for sample in samples:
    #if "\n" in samples:
        #samples_cleaned.extend(sample.split("\n"))
   # else:
        #samples_cleaned.append(sample)


driver.quit()    


data_rows = list(zip_longest(pollsters, dates, samples, sample_type, dname, dvalue, rname, rvalue, fillvalue=None))
df = pd.DataFrame(data_rows, columns=['Pollster', 'Date', 'Sample', 'Type', 'Cand1','C1Val', 'Cand2', 'C2Val'])

#pollsters_interleaved = []
#for pollster in df['Pollster']:
    #pollsters_interleaved.append(pollster)
    #pollsters_interleaved.append('')

#data_rows_interleaved = list(zip_longest(pollsters_interleaved, dates, samples, fillvalue=""))
#df_interleaved = pd.DataFrame(data_rows_interleaved, columns=['Pollster', 'Date', 'Sample'])

#df['Sample'] = df['Sample'].shift(-1)

#for sample in df['Sample']:
#    if "" in df['Sample']:
#        df['Sample'].replace("", np.nan, inplace=True)

def clean_and_shift_up(df):
    df.replace("", np.nan, inplace=True)
    
    for col in df.columns:
        df[col] = df[col].dropna().reset_index(drop=True)
    
    df.dropna(how='all', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df


clean_df = clean_and_shift_up(df)

#df['Pollster'] = df['Pollster']


#print(clean_df.to_string(index=False))


#csv_file_path = r'C:\Users\lukem\Documents\C files\yourfile4.csv'
#clean_df.to_csv(csv_file_path, index=False)











