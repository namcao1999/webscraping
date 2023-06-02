import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

import pandas as pd
from datetime import date, timedelta

td = date.today()
print(td)

start_date = td - timedelta(days=365)
print(start_date)


# Create start_date, end_date
end_date = td


#Open Website
current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, 'chromedriver_linux64/chromedriver')
service = Service(path)
driver = webdriver.Chrome(service=service)

driver.get('https://core.aiesec.org.eg/analytics/1626/MC22/')
wait = WebDriverWait(driver, 30)


# #enter start_date & end_date to field
start_date_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="start-date"]')))
start_date_field.clear()
start_date_field.send_keys(start_date.strftime("%m/%d/%Y"))

end_date_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="end-date"]')))
end_date_field.clear()
end_date_field.send_keys(end_date.strftime("%m/%d/%Y"))

# #Enter to website to filter data based on fields
end_date_field.send_keys(Keys.ENTER)


dfs = []

# Find the table element
table = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="signups-table"]')))

page_number = 1
total_pages = 6

while page_number <= total_pages:
    # Scrape the current page of the table
    table_html = table.get_attribute('outerHTML')
    page_df = pd.read_html(table_html)[0]

    # Append the current page's data to the list of dataframes
    dfs.append(page_df)

    # Check if there is a "Next" button and update the total pages
    next_button = driver.find_element(By.XPATH, '//*[@id="signups-table_next"]/a')
    if 'disabled' in next_button.get_attribute('class'):
        # If the "Next" button is disabled, all rows have been scraped
        break
    else:
        # Click the "Next" button to load the next page
        next_button.click()
        page_number += 1
        
        time.sleep(2)
        table = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="signups-table"]')))        
        
# Concatenate all the dataframes into a single dataframe
df = pd.concat(dfs, ignore_index=True)

print(df.shape)

print(df.head())

# Print the scraped data
df.to_csv(os.path.join(current_dir, "ELDs_result.csv"), index=True)




time.sleep(15)

driver.quit()