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

time_range = 365
start_date = str(td - timedelta(days=time_range))
print(start_date)

# Create start_date, end_date
end_date = str(td)
print(end_date)

import datetime

def get_month_pairs(start_date, end_date):
    start_month = datetime.datetime.strptime(start_date, "%Y-%m-%d").date().replace(day=1)
    end_month = datetime.datetime.strptime(end_date, "%Y-%m-%d").date().replace(day=1)
    month_pairs = []

    while start_month <= end_month:
        year = start_month.year + (start_month.month // 12)
        month = (start_month.month % 12) + 1

        next_month = start_month.replace(year=year, month=month, day=1)
        end_of_month = next_month - datetime.timedelta(days=1)
        month_pairs.append((start_month, end_of_month))
        start_month = next_month

    return month_pairs



pairs = get_month_pairs(start_date, end_date)

for start_month, end_month in pairs:
    print(start_month, end_month)

output = pd.DataFrame()

#Open Website
current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, 'chromedriver_linux64/chromedriver')
service = Service(path)
driver = webdriver.Chrome(service=service)

driver.get('https://core.aiesec.org.eg/analytics/1626/MC22/')
wait = WebDriverWait(driver, 30)

for start_month, end_month in pairs:
    print(start_month, end_month)
    # #enter start_date & end_date to field
    start_date_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="start-date"]')))
    start_date_field.clear()
    start_date_field.send_keys(start_month.strftime("%m/%d/%Y"))

    end_date_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="end-date"]')))
    end_date_field.clear()
    end_date_field.send_keys(end_month.strftime("%m/%d/%Y"))

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

    # print(df.shape)

    # print(df.head())

    # Define the desired columns
    desired_columns = ['SIGN UPs', 'APPLICANTS','ACCEPTED APPLICANTS', 'APPROVED', 'REALIZED', 'FINISHED', 'COMPLETED']

    # Define the product list
    product_list = ["iGV", "iGTa", "iGTe", "oGV", "oGTa", "oGTe"]


    # Reset index to move the multi-level columns to rows
    df_copy = df.copy()
    entity_column = ('Entity', 'Entity')
    df.set_index(entity_column, inplace=True)

    print(df.columns)
    # df_reset = df.stack(level=0).reset_index()
    # print(df.head())

    df_new = pd.DataFrame(columns=['Entity', 'Product'] + desired_columns)
    if entity_column in df_copy.columns:    
        unique_entities = df_copy[entity_column].unique()
        unique_entities_str = ', '.join(unique_entities)
        # print(f"Unique entities: {unique_entities_str}")
            
        for entity in unique_entities:
            print(entity)
            entity_data = df_copy.loc[df_copy[entity_column] == entity]
            # print(entity_data.head())

            for product in product_list:
                entity_dict = {'Entity': entity, 'Product': product, 'Date': end_month}
                for desired_column in desired_columns:
                    if (desired_column, product) in entity_data.columns:
                        exchange_value = entity_data.loc[:, (desired_column, product)]
                        entity_dict[str(desired_column)] = exchange_value
                    else:
                        entity_dict[str(desired_column)] = None

                df_entity = pd.DataFrame(entity_dict)
                df_new = pd.concat([df_new, df_entity], ignore_index=True)
                
        
        df_new[['Entity', 'Product']] = df_new[['Entity', 'Product']].astype(str)
    else:
        print(f"Entity column {entity_column} does not exist in the DataFrame.")
    df_new[['Entity', 'Product']] = df_new[['Entity', 'Product']].astype(str)
    output = pd.concat([output,df_new], ignore_index=True)
    # print(output.head())
    
# Set the appropriate data types
output[['Entity', 'Product']] = output[['Entity', 'Product']].astype(str)

# Set the index to 'Entity' and 'Product'
# df_new.set_index(['Entity', 'Product'], inplace=True)

# Fill missing values with NaN
output = output.replace('', pd.NA)

current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, 'ELDs_result.xlsx')
output.to_excel(path)

# Print the new DataFrame
print(output.head())

time.sleep(15)

driver.quit()