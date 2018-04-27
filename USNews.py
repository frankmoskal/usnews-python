from bs4 import BeautifulSoup, SoupStrainer
import csv
import lxml
import re
import requests


#########################
## START OF USER INPUT ##
#########################

# Username and password for USNews Premium Account
USERNAME = ""
PASSWORD = ""

# Category URL is the url when you look at all of the colleges in the tables
# Make sure it's put in the form of "url/page+"
# EX: CATEGORY_URL = "https://premium.usnews.com/best-graduate-schools/top-business-schools/part-time-rankings/page+"
CATEGORY_URL = ""


# Number of pages is the number of pages of colleges
# EX: NUMBER_OF_PAGES = 12
NUMBER_OF_PAGES = 0

# Just take the first part after https://premium.usnews.com
# EX: LINK_SELECTOR = "/best-graduate-schools/"
LINK_SELECTOR = ""


# On the Unit_ID href, take this bit (if not graduate, not sure how you get it)
# Put "N/A" if you don't want to find it
# EX: UNIT_ID_SELECTOR = "/best-graduate-schools/top-graduate-schools/"
UNIT_ID_SELECTOR = "N/A"

# SUB_PAGES is the pages you want, e.g. admissions, rankings, etc.
# EX: SUB_PAGES = [ "admissions" ]
SUB_PAGES = [ "" ]

# Tables is the tables you want, e.g. part time enrollment, full time, etc.
# Put [ "N/A" ] if doesn't matter what table (e.g. there are no duplicate attributes)
# MAKE SURE TO USE THE CSS CLASS FOR THE TABLE
# EX: TABLES = ["fall_admissions_enrollment_pt"]
TABLES = ["fall_admissions_enrollment_pt"]

# Attributes is the data you want, just use the english description
# to set it up, make each set of data you want from a page a list and then put those in a big list
# EX:  [ ["page one stuff", "other page one stuff"] , [ "page 2 stuff", "other page 2 stuff" ] ]
ATTRIBUTES = [ [ "" ] ]

#########################################
## END OF USER INPUT, START OF PROGRAM ##
#########################################


# sets initial urls
LOGIN_URL = "https://secure.usnews.com/member/login"
BASE_URL = "https://premium.usnews.com"
PAGE_URL = ""

# create a new session and login
session = requests.Session()
PAYLOAD = {
'username': USERNAME ,
'password': PASSWORD
}
login = session.post(LOGIN_URL, data=PAYLOAD)

# finds the link and name for each college in the category rankings, and stores them to a list
print("obtaining list of colleges...")
COLLEGE_URLS = []
NAMES = []
link_re = re.compile(LINK_SELECTOR)
for x in range(1, NUMBER_OF_PAGES + 1):
    html = BeautifulSoup(session.get(CATEGORY_URL + str(x)).content, 'lxml', parse_only=SoupStrainer('tbody'))
    for url in html.find_all("a", href=link_re):
        if (url.text[0].isalpha()):
            COLLEGE_URLS.append(url.get("href"))
            NAMES.append(url.text)
print("found " + str(len(NAMES)) + " colleges...")

# open CSV file for writing
f = open('output.csv','w')
csv_writer = csv.writer(f, dialect='excel')
csv_row = ["University Name", "Unit ID"]
csv_row.extend([attrib for list in ATTRIBUTES for attrib in list])
csv_writer.writerow(csv_row)

# parses each link for the correct attributes & unitid
unit_re = re.compile(UNIT_ID_SELECTOR)
numeric = re.compile('[^0-9]')
for i, college in enumerate(COLLEGE_URLS):
    print("scraping data for " + NAMES[i] + "...")
    csv_row = [NAMES[i]]
    if (UNIT_ID_SELECTOR != "N/A"):
        PAGE_URL = BASE_URL + college + "/ranking"
        html = BeautifulSoup(session.get(PAGE_URL).content, 'lxml')
        for url in html.find_all("a", href=unit_re):
            csv_row.append(numeric.sub('', url['href']))
            break
    for j, page in enumerate(SUB_PAGES):
        table_list = []
        PAGE_URL = BASE_URL + college + "/" + page
        html = BeautifulSoup(session.get(PAGE_URL).content, 'lxml')
        if TABLES[0] == "NULL":
            table_list = html.find_all("table")
        else:
            for item in TABLES:
                table_list.append(html.find("table", class_=item))
        data = []
        for t in table_list:
            rows = t.find_all("tr")
            for r in rows:
                columns = r.find_all("td")
                data.append([(" ".join(c.text.split())) for c in columns])
        for attrib in ATTRIBUTES[j]:
            for dict in data:
                if attrib in dict[0]:
                    csv_row.append(dict[1])
    csv_writer.writerow(csv_row)
f.close()
exit()
