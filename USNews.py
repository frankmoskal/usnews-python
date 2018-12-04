import math
import csv
import re
import time
from selenium import webdriver

###
#    USER INPUT
###

# Username and password for USNews Premium
USERNAME = ""
PASSWORD = ""

# Category URL is the url when you look at all of the colleges in the tables
# EX: CATEGORY_URL = "https://premium.usnews.com/best-colleges/rankings"
CATEGORY_URL = "https://premium.usnews.com/best-colleges/rankings"


# Number of pages is the number of pages of colleges
# EX: NUMBER_OF_PAGES = 12
NUMBER_OF_PAGES = 0

# the first part after https://premium.usnews.com
# EX: LINK_SELECTOR = "/best-graduate-schools/"
LINK_SELECTOR = "/best-colleges/"

# SUB_PAGES is the list of sub-pages you want to visit. This INCLUDES the base page
# EX: SUB_PAGES = [ "", "admissions" ]
SUB_PAGES = ["", "rankings"]

# Column headings is the list of headings for your csv columns
COLUMN_HEADINGS = []

# Attributes is the data you want per-page, using a CSS selector
#       (firefox can get you this by inspect element, copy as CSS selector)
# to set it up, make each set of data you want from a page a list and then put those in a big list
# EX:  [ ["page one stuff", "other page one stuff"] , [ "page 2 stuff", "other page 2 stuff" ] ]
# NOTE: THIS SHOULD NOT INCLUDE NAME, LOCATION, or XWALK ID, THAT WILL AUTOMATICALLY BE GATHERED
ATTRIBUTES = [[], []]

# This is where you put the xpath for the meta tag containing name, location, and xwalk-id
# EX: <meta data-school-name="Princeton University"
# data-school-xwalk-id="186131" data-school-location="Princeton, NJ">
META = "/html/head/meta[11]"


###
#    START OF PROGRAM
###
def main():

    # create a new webdriver
    print("creating webdriver...")
    browser = webdriver.Firefox()

    # login to usnews premium
    print("logging into USNews...")
    browser.get("https://secure.usnews.com/member/login")
    browser.find_element_by_name("username").send_keys(USERNAME)
    browser.find_element_by_name("password").send_keys(PASSWORD)
    browser.find_element_by_xpath('.//input[@type="submit"]').click()

    # wait for page to be loaded
    time.sleep(2)

    # get list later
    college_urls = []

    # open CSV file for writing
    print("creating csv file...")
    csv_file = open("output.csv", "w")
    csv_writer = csv.writer(csv_file, dialect="excel")
    csv_row = COLUMN_HEADINGS
    csv_writer.writerow(csv_row)

    # parses each link for the correct attributes & unitid
    for college in college_urls:
        browser.get("https://premium.usnews.com" + college)
        time.sleep(2)
        meta_data = browser.find_element_by_css_selector(
            "meta[data-school-xwalk-id]"
        )
        print(
            "scraping data for "
            + str(meta_data.get_attribute("data-school-name"))
            + "..."
        )
        csv_row = [
            meta_data.get_attribute("data-school-name"),
            meta_data.get_attribute("data-school-xwalk-id"),
            meta_data.get_attribute("data-school-location"),
        ]
        for attrib in ATTRIBUTES[0]:
            try:
                csv_row.append(
                    browser.find_element_by_css_selector(attrib).text
                )
            except:
                csv_row.append("N/A")
        browser.get("https://premium.usnews.com" + college + "/" + "rankings")
        time.sleep(6)
        for attrib in ATTRIBUTES[1]:
            try:
                csv_row.append(
                    str(
                        browser.find_element_by_css_selector(
                            attrib
                        ).get_attribute("innerHTML")
                    ).strip()
                )
            except:
                csv_row.append("N/A")
        csv_writer.writerow(csv_row)
    csv_file.close()
    exit()


if __name__ == "__main__":
    main()
