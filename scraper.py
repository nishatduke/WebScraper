from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import numpy as np
import time
import json
from downloading_new import extract_text_and_save
import logging,os
import pymssql
import configparser
import pypyodbc as obdc
from testing_models import run_main_model
from dotenv import load_dotenv

load_dotenv()
driver = os.getenv("DRIVER_ENV")
server = os.getenv("SERVER_ENV")
user = os.getenv("USERNAME_ENV")
password = os.getenv("PASSWORD_ENV")
db = os.getenv("DATABASE_ENV")
print(driver)
print(server) 
print(user)
print(password) 
print(db)

appState = {
    "recentDestinations": [
        {
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }
    ],
    "selectedDestinationId": "Save as PDF",
    "version": 2
}


cnxn = obdc.connect(f'DRIVER={{{driver}}};SERVER={server};DATABASE={db};Trust_Connection=yes;UID={user};PWD={password}')
cursor = cnxn.cursor()
cursor.execute("SELECT symbol FROM scraping_schema.company_data")
tickers = cursor.fetchall()
print(tickers)
for ticker in tickers[0:10]: 
     print(ticker[0])

cursor.execute("TRUNCATE TABLE scraping_schema.url_table")
cnxn.commit()


profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState),
           'savefile.default_directory': 'path/to/dir/'}


chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option('prefs', profile)
chrome_options.add_argument('--kiosk-printing')
driver = webdriver.Chrome(options=chrome_options)
urls = []
stock_company_data = pd.read_csv("constituents.csv")
tickers = np.asarray(stock_company_data["Symbol"])
print(tickers[:10])
wait = WebDriverWait(driver, 10,poll_frequency=1) 



filing_data_list =[]

form_types = ["10-Q","10-K"]

form_type_string =''

for form_type in form_types: 
    form_type_string+=form_type+'%252C'

form_type_string=form_type_string[:-5]


dont_run_driver = False 
if(not dont_run_driver):
    for ticker in tickers[:3]:
        try:
            main_url = 'https://www.sec.gov/edgar/search/#/dateRange=all&category=custom&entityName='+ticker+'&forms='+form_type_string
            print(main_url)
            driver.get(main_url)
            time.sleep(2)
            
            rows = wait.until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'preview-file')))
            date_rows = wait.until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'filed')))
            date_rows = date_rows[1:]
            for i in range(0,5):
                row = rows[i]
                date_filed = date_rows[i] 
                if row.is_displayed():
                    row = wait.until(EC.element_to_be_clickable(row))
                    current_filing_data = {} 
                    current_filing_data["ticker"] = ticker
                    current_filing_data["form_type"] = row.text
                    current_filing_data["date_filed"] = date_filed.text
                    row.click() 
                    button = wait.until(EC.visibility_of_element_located((By.ID, 'open-file')))
                    button.click()
                    currentTabs = driver.window_handles
                    driver.switch_to.window(currentTabs[1])
                    current_url = driver.current_url
                    urls.append(current_url)
                    current_filing_data["url"] = current_url
                    driver.close()
                    driver.switch_to.window(currentTabs[0])
                    close_button = wait.until(EC.visibility_of_element_located((By.ID, 'close-modal')))
                    close_button.click()
                    filing_data_list.append(current_filing_data)
            print("FINISHED A FULL TICKER AND MADE IT HERE")
        except:
            logging.warning('It errored out here')  
            
    print("Im Done with the TICKER LOOOP!")
    extract_text_and_save(urls)
    for entry in filing_data_list: 
            print(entry)
            entry_url = entry["url"]
            entry_ticker = entry["ticker"]
            entry_form_type = entry["form_type"]
            entry_date_filed = entry["date_filed"]
            cursor.execute("INSERT INTO scraping_schema.url_table (url, ticker, form_type, date_filed) VALUES (?, ?, ?, ?)",
            [entry_url, entry_ticker, entry_form_type, entry_date_filed])
            cnxn.commit()
    driver.quit()
print("FULLY DONE WITH EVERYTHING")

