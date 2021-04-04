
##########################################################################################################################
#  Created Date: 05/06/2020
#  Author : Arvind Gautam
#  Purpose of this Script: The main objective of this POC is to extract the product related information for JNJ products on
#                              various e-commerce websites like Amazon, Walmart  using Python web scraping.
#                          Inputs in the form of URL will be used in the POC and CSV file with the listed details
#                              should be generated. POC should be able to handle large number of URLs.
#                          Product details includes information such as Title, Categories, price, ratings, features,
#                              availability, product description, product details and customer_reviews.

#  Execution Instruction: This scripts requires chromedriver.exe matching the chrome version
##########################################################################################################################


# importing required libraries

import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import logging
from datetime import datetime

#assigning variables
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DRIVER_PATH = os.path.join(CURRENT_DIR, r'..\..\drivers\chromedriver.exe')
INPUT_AMAZON = os.path.join(CURRENT_DIR, r'..\..\input\amazon_url.csv')
OUTPUT_AMAZON = os.path.join(CURRENT_DIR, r'..\..\output\amazon_output_' + time_stamp + '.csv')
print(DRIVER_PATH)
print(INPUT_AMAZON)

#Generating logs
date = datetime.now()
time_stamp = date.strftime("%d_%m_%Y_%H_%M_%S")

LOG_PATH = os.path.join(CURRENT_DIR, r'..\..\log\scraping_log_file_' + time_stamp + '.log')
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=LOG_PATH, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)
print(LOG_PATH)

# Initiating the chrome session
option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=option)
logger.info("Browser initiated")

def amazon():
    """ This functions extracts the data from amazon.com and saves the output as amazon_output.csv"""
    indicator = "yes"
    counter = 0

    # taking urls from the csv file
    df_input = pd.read_csv(INPUT_AMAZON, header=None)
    url_list = df_input[0]
    logger.info("Inputs recieved")
    
    for url in url_list[:4]:

        try:
            driver.get(url)
            content = driver.page_source
            soup = BeautifulSoup(content, 'lxml')

            title = soup.select("#productTitle")[0].get_text().strip()
            logger.info("Title done %s", title)

            try:
                categories = []
                for li in soup.select("#wayfinding-breadcrumbs_container ul.a-unordered-list")[0].findAll("li"):
                    categories.append(li.get_text().strip())
                cat = [i for i in categories if len(i) > 2]
                categories = ", ".join(cat)
                logger.info("categories done %s", categories)
            except:
                categories = "Not available"
                logger.info("categories not found for %s", url)

            try:
                List_price = soup.find('span', {'class': 'priceBlockStrikePriceString a-text-strike'}).text.strip()
                logger.info("list price done %s", List_price)
            except:
                List_price = "Not available"
                logger.info("price not found ")

            try:
                price = soup.select("#priceblock_ourprice")[0].get_text()
                logger.info("price done %s", price)
            except:
                price = "Not available"
                logger.info("price not found ")

            try:
                rating = soup.find('span', {'class': 'a-icon-alt'}).text.strip()
                logger.info("rating done %s", rating)
            except:
                rating = "Ratings not available"
                logger.info("ratings not found for %s", url)

            try:
                availability = soup.select("#availability")[0].get_text().strip()
                if availability == 'Available from these sellers.':
                    availability = 'In Stock.'
                elif len(availability) > 20:
                    availability = 'Out of Stock.'
                logger.info("availability done %s", availability)
            except:
                availability = 'No Info'
                logger.info("availability not found for %s", url)
                
            try:
                features = []
                for li in soup.select("#feature-bullets ul.a-unordered-list")[0].findAll('li'):
                    features.append(li.get_text().strip())
                feature = ", ".join(features)
                logger.info("features done")
            except:
                feature = "No Features"
                logger.info("features not found for %s", url)
                
            try:
                product_description = soup.select("#productDescription")[0].get_text().strip()
                logger.info("description done ")
            except:
                product_description = "No Description"
                logger.info("description not found for %s", url)
            
            try:
                product_details = driver.find_element_by_xpath("(//*[@class='content'])[2]").text
                logger.info("details done ")
            except:
                product_details = driver.find_element_by_xpath("(//*[@class='content'])").text
                logger.info("details done ")

            try:
                review = []
                for re in soup.findAll("span", {'data-hook': "review-body"}):
                    review.append(re.get_text())
                new_review = []
                for i in review[:5]:
                    ind = i.find("Read more")
                    new_review.append(i[:ind])
                top_review = "\n".join(new_review).replace("\n", "    ")
                logger.info("review done ")
            except:
                top_review = "No Review"
                logger.info("No review ")
                

            # Creating the pandas dataframe of extracted details
            if indicator == 'yes':
                row = [[title, categories, List_price, price, rating, availability, feature, product_description,
                        product_details, top_review]]
                df_amazon_out = pd.DataFrame(row, columns=["Title", "categories", "List_price", "price", "rating",
                                                           "Availability", "Features", "product_description",
                                                           "product_details", "Top_Reviews"])
                indicator = 'no'
                counter = counter + 1
            else:
                row = [title, categories, List_price, price, rating, availability, feature, product_description,
                       product_details, top_review]
                df_amazon_out.loc[counter] = row
                counter = counter + 1
            logger.info('%s completed', url)
            logger.info('%s number of urls printed', counter)

        except:
            logger.info("%s URL NOT PROCESSED - BAD URL", url)
            continue
    # Printing output to csv file
    df_amazon_out.to_csv(OUTPUT_AMAZON, index=False)
    logger.info("Printing into csv done")


if __name__ == "__main__":
    amazon()
    fhandler.close()
    
    driver.quit()