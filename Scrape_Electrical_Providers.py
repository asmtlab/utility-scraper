
# Python standard libs
import json
import sys, time
from time import sleep

# 3rd party libs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC

# Used by webdriver_manager if not supplying path to driver
# from webdriver_manager.firefox import GeckoDriverManager
# webdriver_manager info:
#
# https://github.com/SergeyPirogov/webdriver_manager#use-with-chrome
# 
#
# Or to download the browser driver:
#   https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
#
FIREFOX_PATH = "./geckodriver" # replace with path to driver for your OS

BASE_URL = "https://findenergy.com/"
OUTPUT_DIR = 'outputs'


# STATES = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
#            'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
#            'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
#            'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
#            'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
REGION_1 = [ 'CT', 'ME', 'MA', 'NH', 'RI', 'VT' ]
REGION_2 = [ 'NJ', 'NY', ]
REGION_3 = [ 'DE', 'MD', 'PA', 'VA', 'WV' ]
REGION_4 = [ 'AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'SC', 'TN' ]
REGION_5 = [ 'IL', 'IN', 'MI', 'MN', 'OH', 'WI' ]
REGION_6 = [ 'IL' ]


CLICK_DELAY = 6


def buttonClick(driver, section):
    '''Click a button on the page found by the XPATH in the formatString argument.'''


    # This try except block is need because the buttons used to traverse
    #   the paginated table appear/disappear from the DOM as you move 
    #   through the list. If an exception is raised, then we have reached the end
    try:
        buttonList = section.find_element(By.CSS_SELECTOR, "ul.pagination.svelte-x63klk")
        button = WDW(buttonList, 3).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "li.active + li"
            ))
        )
    except (NoSuchElementException, TimeoutException):
        # no more pages
        return True
    
    driver.execute_script("arguments[0].scrollIntoView();", button)
    # adding a delay so the page fully loads before clicking
    time.sleep(CLICK_DELAY)

    button.click()
    # adding a delay so the page fully loads after clicking
    time.sleep(CLICK_DELAY)

    return False

def getTableRows(section):
    '''Returns object containing list of tr elements from a table in the section.'''
    table = section.find_element(By.CSS_SELECTOR, ".table.sortable-table.svelte-x63klk")
    tBody = table.find_element(By.CSS_SELECTOR, "tbody")
    tableRows = tBody.find_elements(By.CSS_SELECTOR, "tr.svelte-x63klk")

    return tableRows

def scrapeTable(driver, section, numItems, firstItemLink, key1="", key2=""):
    currentPage = 1
    itemList = []
    
    while len(itemList) != numItems:

        print("start page {}".format(currentPage))

        tableRows = getTableRows(section)

        # iterate over items in the table to get href tag for a elements
        for row in tableRows:
            columns = row.find_elements(By.CSS_SELECTOR, "td.svelte-x63klk")
            item = {}
            
            # print(providerElement.text)
            if firstItemLink:
                link = columns[0].find_element(By.CSS_SELECTOR, "a")
                county = link.text
                # split url by '/' and get 3rd from last item which is the state abbreviation
                state = link.get_attribute("href").split('/')[-3].upper()
                item[key1] = "{}, {}".format(county, state)
            else:
                item[key1] = columns[0].text

            item[key2] = int("".join(columns[1].text.split(',')))

            print(item)
            itemList.append(item)
        
        print("done page {}".format(currentPage))
        
        currentPage += 1

        if buttonClick(driver, section):
            break

    return itemList

def getProviderInfo(driver, url):
    providerInfo = {}

    # fetch page
    driver.get(url)

    # Scrape Company Name
    companyName = driver.find_element(By.CSS_SELECTOR, 
        ".overview__title.svelte-1f6rrn3").text

    print("Scraping {}".format(companyName))
    providerInfo['company'] = companyName

    companyOverviewSections = driver.find_elements(By.CSS_SELECTOR,
        "section#overview .col-lg-5"
    )

    companyType = companyOverviewSections[0].find_elements(By.CSS_SELECTOR,
        "li.svelte-1f6rrn3 span.svelte-1f6rrn3")[1].text

    # print("\ttype: {}".format(companyType))
    providerInfo['company-type'] = companyType
    
    try:
        companyWebsite = companyOverviewSections[0].find_elements(By.CSS_SELECTOR,
            "ul.list-unstyled.company-info__list.svelte-1f6rrn3")[1].find_element(By.CSS_SELECTOR,
                "li.svelte-1f6rrn3 a"
            ).get_attribute("href")
    except:
        pass
    else:
        # print("\twebsite: {}".format(companyWebsite))
        providerInfo['website'] = companyWebsite

    # get provider types (residential, commercial, industrial)
    serviceTypesElements = driver.find_element(By.CSS_SELECTOR, 
        ".tab-nav.tab-nav--underlined.svelte-9ar7ba").find_elements(
            By.CSS_SELECTOR, 
            ".tab-nav__link"
        )
    
    serviceTypes = []
    for item in serviceTypesElements:
        serviceTypes.append(item.text)
    
    providerInfo['service-types'] = serviceTypes
    # print("\tservice types:", serviceTypes)

    # collect customers by type
    statsSections = driver.find_element(By.CSS_SELECTOR,
        ".sidebar-widget").find_elements(By.CSS_SELECTOR,
            ".facts-item.svelte-3uw1eb")

    sectionTitle = statsSections[0].find_element(By.CSS_SELECTOR, 
        "h3.facts-item__title.svelte-3uw1eb").text

    if sectionTitle == "SALES & CUSTOMERS":
        customerSections = statsSections[0].find_elements(By.CSS_SELECTOR,
            ".facts-item__li.svelte-3uw1eb")

        totalCustomers = 0
        for section in customerSections:
            # Replace spaces with '-' for key
            text = section.find_element(By.CSS_SELECTOR,
                "h4.facts-item__label.svelte-3uw1eb").text.replace(' ', '-')
            
            stat = section.find_element(By.CSS_SELECTOR,
                "p.facts-item__data.svelte-3uw1eb strong").text.strip('$')

            amount = float("".join(stat.split(',')))

            if "Customers" in text:
                totalCustomers += amount
            else:
                text = "{}-($)".format(text)

            providerInfo[text] = amount
            # print(text, amount)
        
        providerInfo['Total-Customers'] = totalCustomers
        print(totalCustomers)

    # collect energy production
    sectionTitle = statsSections[1].find_element(By.CSS_SELECTOR, 
        "h3.facts-item__title.svelte-3uw1eb").text

    if sectionTitle == "ENERGY PRODUCTION":
        productionStats = statsSections[1].find_elements(By.CSS_SELECTOR,
            ".facts-item__li.svelte-3uw1eb")
        
        for section in productionStats:
            text = section.find_element(By.CSS_SELECTOR, 
                ".facts-item__label.svelte-3uw1eb").text.replace(' ', '-')
            stat = section.find_element(By.CSS_SELECTOR,
                ".facts-item__data.svelte-3uw1eb strong").text
            units = section.find_element(By.CSS_SELECTOR,
                ".text-muted").text.strip()
            text = "{}-{}".format(text, units)
            
            providerInfo[text] = float("".join(stat.split(',')))
            # print(text, providerInfo[text])

    #### COLLECT CITIES SERVED ####
    print("Scraping cities")

    providerInfo["cities-served"] = []
    cityElements = None
    try:
        citySection = driver.find_element(By.CSS_SELECTOR,
            "#city-coverage")
        cityElements = citySection.find_elements(By.CSS_SELECTOR,
            "li.svelte-1f6rrn3")
    except:
        citySection = companyOverviewSections[1].find_element(By.CSS_SELECTOR,
            "ul.list-unstyled.company-info__list.svelte-1f6rrn3:nth-child(3) > li:nth-child(3)")
        cityElements = citySection.find_elements(By.CSS_SELECTOR, "ul.list-unstyled li")
        
    for city in cityElements:
        try:
            providerInfo["cities-served"].append(city.get_element(
                By.CSS_SELECTOR, "a").text)
        except:
            providerInfo["cities-served"].append(city.text)
    #### END CITIES SERVED ####

    #### Collect counties served ####
    
    # grab section for County table and use as starting node
    try:
        countySection = driver.find_element(By.CSS_SELECTOR,
            "#county-coverage")

        numCounties = int(countySection.find_element(By.CSS_SELECTOR,
            ".table-footer__data.svelte-x63klk").text.split(' ')[0])
        print("Scraping {} counties".format(numCounties))
        counties = scrapeTable(driver, countySection, numCounties, 
                        firstItemLink=True, key1="county", key2="population")

        providerInfo['counties-served'] = sorted(counties, key= lambda county: county['population'])
    except:
        pass
    #### End counties ####

    #### Collect states served ####
    statesSection = driver.find_element(By.CSS_SELECTOR,
        "#state-coverage")
    
    numStates = int(statesSection.find_element(By.CSS_SELECTOR,
        ".table-footer__data.svelte-x63klk").text.split(' ')[0])
    print("Scraping {} states".format(numStates))

    states = scrapeTable(driver, statesSection, numStates,
                    firstItemLink=False, key1="state", key2="customers")
    
    providerInfo["states-served"] = sorted(states, key= lambda state: state['customers'])
    #### End states ####

    return providerInfo


def getElectricalProviders(driver):
    '''Traverses table of providers on a state's homepage 
        (e.g. https://findenergy.com/ak).'''
    providers = []      # list of links to provider pages
    currentPage = 1     # current page from Electricity providers table

    numProviders = driver.find_element(By.CSS_SELECTOR, 
        ".table-footer__data.svelte-x63klk.svelte-x63klk").text.split(' ')[0]
    print("Number of providers: {}".format(str(numProviders)))

    while len(providers) != int(numProviders):
        print("start providers page {}".format(currentPage))
        # grab table of Electrical Providers and use as starting node
        providerSection = driver.find_element(By.CSS_SELECTOR, "#electricity-providers")
        table = providerSection.find_element(By.CSS_SELECTOR, ".table.sortable-table.svelte-x63klk tbody")
        tableRows = table.find_elements(By.CSS_SELECTOR, "tr.svelte-x63klk")

        # iterate over items in the table to get href tag for a elements
        for row in tableRows:
            providerElement = row.find_element(By.CSS_SELECTOR, "td.svelte-x63klk a")
            link = providerElement.get_attribute("href")
            print(providerElement.text)
            providers.append(link)

        print("done providers page {}".format(currentPage))

        currentPage += 1
        
        if buttonClick(driver, providerSection):
            break

    return providers


def scrapeState(driver, url, state):
    driver.get(url)
    driver.maximize_window()
    print("Scraping {}".format(state))
    stateInfo = {}

    electricalProviderURLS = getElectricalProviders(driver)
    
    electricalProvidersInfo = []
    for providerURL in electricalProviderURLS:
        electricalProvidersInfo.append(getProviderInfo(driver, providerURL))

    # sort providers by total customers served
    stateInfo["electrical-providers"] = sorted(electricalProvidersInfo, 
        key=lambda provider: provider["Total-Customers"], reverse=True)
    
    return stateInfo

def get_driver(browser, options, driver_path):
    pass

def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-sh-usage')
    driver = webdriver.Firefox(service=FirefoxService(executable_path=FIREFOX_PATH), options=options)

    # info = getProviderInfo(driver, 'https://findenergy.com/providers/reliant-energy/')

    info = {}
    for state in REGION_4:
        urlQueryString = "{}{}".format(BASE_URL, state)
        info[state] = scrapeState(driver, urlQueryString, state)

        with open('{}/{}-energy-utility-info.json'.format(OUTPUT_DIR, state), 'w') as wf:
            json.dump(info[state], wf)
    
    driver.close()
    
    return 0
    

if __name__ == "__main__":
    sys.exit(main())