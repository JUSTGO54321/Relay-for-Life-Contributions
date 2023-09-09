from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# preventing chrome page from closing after completion
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# login id
username = USERNAME
password = PASSWORD

# initializing chrome webdriver for selenium to use
driver = webdriver.Chrome("chromedriver", chrome_options=chrome_options)

# login to event manager account
driver.get("https://support.cancer.ca/site/SPageServer/?NONCE_TOKEN=91BD7941219D90F6E06A5EF7FEBD0C98&pagename=RFLY_NW_Login")
driver.find_element("id", "USERNAME2").send_keys(username)
driver.find_element("id", "Password2").send_keys(password)
driver.find_element("id", "login").click()

# wait the ready state to be complete
WebDriverWait(driver=driver, timeout=10).until(
    lambda x: x.execute_script("return document.readyState === 'complete'")
)

# determine whether login succeded or failed
error_message = "The username or password is invalid."
errors = driver.find_elements("css selector", ".ErrorMessage")
for i in errors:
    print(i.text)
if any(error_message in e.text for e in errors):
    print("[!] Login failed")
else:
    print("[+] Login successful")

# wait for pages to redirect until "manage event" button appears
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.XPATH, "//*[@id='loginMessage']/p/a"))).click()
driver.find_element("id", "em_customer_service").click()
driver.find_element("id", "ProcessLink_teams_list").click()

# manually input team IDs
team_id = [503730,
           502404,
           501656,
           501413,
           501625,
           501881,
           501899,
           502399,
           503272, 
           502044, 
           501554, 
           503377, 
           502322, 
           501644, 
           503665, 
           501952, 
           503360, 
           501653,
           501514,
           501987,
           501619,
           501615,
           502516,
           503872,
           501610]

# scrape raw contribution details from all tables
contributions = []
for i in team_id:

    # go to all team pages
    driver.get(f"https://support.cancer.ca/site/TREM?tr.emgmt=em_team_summary&mfc_pref=T&team_id={i}&action=view_team_summary_gifts&fr_id=28802")
   
    # if there are no contributions
    try:
        driver.find_element("css selector", ".PaddedEntryC")
        continue
    except:
        pass

    # if there are contributions
    table = driver.find_element(By.CSS_SELECTOR, "table[summary='This table lists the data items and information about them in each row.']")
    
    for row in table.find_elements(By.CSS_SELECTOR, 'tr'):
        temp = []
        for cell in row.find_elements(By.CSS_SELECTOR, 'td'): 
            temp.append(cell.text)
        contributions.append(temp)

# remove all header rows (blank lists)
new_contributions = [data for data in contributions if data != []]

# add up all contributions and organize under participants' names
contributions_dict = defaultdict(int)
for i in new_contributions:
    del i[0:4]
    i[0] = i[0].replace("$", "")
    i[0] = float(i[0])
    contributions_dict[i[1]] += i[0]
    print(contributions_dict[i[1]])

# write contribution details to a .txt file to easily copy-paste into spreadsheet
with open("relayDonations.txt", 'w') as f:
    for i in contributions_dict.keys():
        f.write(i)
        f.write("\n")
    for i in contributions_dict.values():
        f.write(str(i))
        f.write("\n")