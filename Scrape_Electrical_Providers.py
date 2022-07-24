
# Python standard libs
import json
import sys, time
from time import sleep
from typing import Any, Dict, List, Set

# 3rd party libs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC

# local module
from Collect_State_Info import STATES

# Used by webdriver_manager if not supplying path to driver
# from webdriver_manager.firefox import GeckoDriverManager
# webdriver_manager info:
#
# https://github.com/SergeyPirogov/webdriver_manager#use-with-chrome
# This option can be used with minor adjustments to the get_driver() function
# 
#
# Or to download the browser driver:
#   https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
#
FIREFOX_PATH = "./geckodriver" # replace with path to driver for your OS

BASE_URL = "https://findenergy.com/"
OUTPUT_DIR = 'outputs'

CLICK_DELAY = 2


def button_click(driver: webdriver, section: Any) -> bool:
    '''Click a button on the page found by the XPATH in the formatString argument.'''
    
    try:
        # This try except block is need because the buttons used to traverse
        #   the paginated table appear/disappear from the DOM as you move 
        #   through the list. If an exception is raised, then we have reached the end
        buttonList = section.find_element(By.CSS_SELECTOR, "ul.pagination.svelte-x63klk")
        button = WDW(buttonList, 3).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "li.active + li"
            ))
        )
    except (NoSuchElementException, TimeoutException):
        # no more buttons
        return True
    
    driver.execute_script("arguments[0].scrollIntoView();", button)
    # adding a delay so the page fully loads before clicking
    time.sleep(CLICK_DELAY)

    button.click()
    # adding a delay so the page fully loads after clicking
    time.sleep(CLICK_DELAY)

    return False

def get_table_rows(section: Any) -> Any:
    '''Returns object containing list of tr elements from a table in the section.'''
    table = section.find_element(By.CSS_SELECTOR, ".table.sortable-table.svelte-x63klk")
    t_body = table.find_element(By.CSS_SELECTOR, "tbody")
    table_rows = t_body.find_elements(By.CSS_SELECTOR, "tr.svelte-x63klk")

    return table_rows

def scrape_table(driver: webdriver, section: Any, numItems: int, is_link: bool, key1: str, key2: str) -> List[Dict]:
    current_page = 1
    item_list = []
    
    while len(item_list) != numItems:
        repeat = False

        print("start page {}".format(current_page))

        tableRows = get_table_rows(section)

        # iterate over items in the table to get href tag for a elements
        for row in tableRows:
            columns = row.find_elements(By.CSS_SELECTOR, "td.svelte-x63klk")
            item = {}
            
            # print(providerElement.text)
            if is_link:
                link = columns[0].find_element(By.CSS_SELECTOR, "a")
                county = link.text
                # split url by '/' and get 3rd from last item which is the state abbreviation
                state = link.get_attribute("href").split('/')[-3].upper()
                item[key1] = "{}, {}".format(county, state)
            else:
                item[key1] = columns[0].text

            item[key2] = int("".join(columns[1].text.split(',')))

            if item in item_list:
                repeat = True
                print("Repeat item. Trying again.")
                break
            print(item)
            item_list.append(item)
        
        if not repeat:
            print("done page {}".format(current_page))
            current_page += 1

        if button_click(driver, section):
            break

    return item_list

def get_provider_info(driver: webdriver, url: str) -> Dict:
    provider_info = {}

    # fetch page
    driver.get(url)

    # Scrape Company Name
    company_name = driver.find_element(By.CSS_SELECTOR, 
        ".overview__title.svelte-1f6rrn3").text

    print("Scraping {}".format(company_name))
    provider_info['company'] = company_name

    company_overview_sections = driver.find_elements(By.CSS_SELECTOR,
        "section#overview .col-lg-5"
    )

    company_type = company_overview_sections[0].find_elements(By.CSS_SELECTOR,
        "li.svelte-1f6rrn3 span.svelte-1f6rrn3")[1].text

    # print("\ttype: {}".format(company_type))
    provider_info['company-type'] = company_type
    
    try:
        company_website = company_overview_sections[0].find_elements(By.CSS_SELECTOR,
            "ul.list-unstyled.company-info__list.svelte-1f6rrn3")[1].find_element(By.CSS_SELECTOR,
                "li.svelte-1f6rrn3 a"
            ).get_attribute("href")
    except:
        company_website = ''
    finally:
        # print("\twebsite: {}".format(company_website))
        provider_info['website'] = company_website

    # get provider types (residential, commercial, industrial)
    service_type_elements = driver.find_element(By.CSS_SELECTOR, 
        ".tab-nav.tab-nav--underlined.svelte-9ar7ba").find_elements(
            By.CSS_SELECTOR, ".tab-nav__link"
        )
    
    service_types = []
    for item in service_type_elements:
        service_types.append(item.text)
    
    provider_info['service-types'] = service_types
    # print("\tservice types:", service_types)

    # collect customers by type
    stats_sections = driver.find_element(By.CSS_SELECTOR,
        ".sidebar-widget").find_elements(By.CSS_SELECTOR,
            ".facts-item.svelte-3uw1eb")

    section_title = stats_sections[0].find_element(By.CSS_SELECTOR, 
        "h3.facts-item__title.svelte-3uw1eb").text

    if section_title == "SALES & CUSTOMERS":
        customers_section = stats_sections[0].find_elements(By.CSS_SELECTOR,
            ".facts-item__li.svelte-3uw1eb")

        total_customers = 0
        for section in customers_section:
            # Replace spaces with '-' for key
            text = section.find_element(By.CSS_SELECTOR,
                "h4.facts-item__label.svelte-3uw1eb").text.replace(' ', '-')
            
            stat = section.find_element(By.CSS_SELECTOR,
                "p.facts-item__data.svelte-3uw1eb strong").text.strip('$')

            amount = float("".join(stat.split(',')))

            if "Customers" in text:
                total_customers += amount
            else:
                text = "{}-($)".format(text)

            provider_info[text] = amount
            # print(text, amount)
        
        provider_info['Total-Customers'] = total_customers
        print("Total customers: ", total_customers)

    # collect energy production
    section_title = stats_sections[1].find_element(By.CSS_SELECTOR, 
        "h3.facts-item__title.svelte-3uw1eb").text

    if section_title == "ENERGY PRODUCTION":
        production_stats = stats_sections[1].find_elements(By.CSS_SELECTOR,
            ".facts-item__li.svelte-3uw1eb")
        
        for section in production_stats:
            text = section.find_element(By.CSS_SELECTOR, 
                ".facts-item__label.svelte-3uw1eb").text.replace(' ', '-')
            stat = section.find_element(By.CSS_SELECTOR,
                ".facts-item__data.svelte-3uw1eb strong").text
            units = section.find_element(By.CSS_SELECTOR,
                ".text-muted").text.strip()
            text = "{}-{}".format(text, units)
            
            provider_info[text] = float("".join(stat.split(',')))
            # print(text, provider_info[text])

    #### COLLECT CITIES SERVED ####
    print("Scraping cities")

    provider_info["cities-served"] = []
    city_elements = None
    try:
        # try to grab city-coverage section from bottom of page
        city_section = driver.find_element(By.CSS_SELECTOR,
            "#city-coverage")
        city_elements = city_section.find_elements(By.CSS_SELECTOR,
            "li.svelte-1f6rrn3")
    except:
        # if NoSuchElement Exception is thrown, then grab cities from top of page
        city_section = company_overview_sections[1].find_element(By.CSS_SELECTOR,
            "ul.list-unstyled.company-info__list.svelte-1f6rrn3:nth-child(3) > li:nth-child(3)")
        city_elements = city_section.find_elements(By.CSS_SELECTOR, "ul.list-unstyled li")
        
    for city in city_elements:
        try:
            provider_info["cities-served"].append(city.get_element(
                By.CSS_SELECTOR, "a").text)
        except:
            provider_info["cities-served"].append(city.text)
    #### END CITIES SERVED ####

    #### Collect counties served ####
    
    # grab section for County table and use as starting node
    try:
        county_section = driver.find_element(By.CSS_SELECTOR,
            "#county-coverage")

        num_counties = int(county_section.find_element(By.CSS_SELECTOR,
            ".table-footer__data.svelte-x63klk").text.split(' ')[0])
        print("Scraping {} counties".format(num_counties))
        counties = scrape_table(driver, county_section, num_counties, 
                        is_link=True, key1="county", key2="population")

        provider_info['counties-served'] = sorted(counties, reverse=True, key= lambda county: county['population'])
    except:
        pass
    #### End counties ####

    #### Collect states served ####
    states_section = driver.find_element(By.CSS_SELECTOR,
        "#state-coverage")
    
    numStates = int(states_section.find_element(By.CSS_SELECTOR,
        ".table-footer__data.svelte-x63klk").text.split(' ')[0])
    print("Scraping {} states".format(numStates))

    states = scrape_table(driver, states_section, numStates,
                    is_link=False, key1="state", key2="customers")
    
    provider_info["states-served"] = sorted(states, reverse=True, key= lambda state: state['customers'])
    #### End states ####

    return provider_info

def get_electrical_providers(driver: webdriver) -> Set[Dict]:
    '''Traverses table of providers on a state's homepage 
        (e.g. https://findenergy.com/ak).'''
    providers = set()   # set of links to provider pages
    current_page = 1    # current page from Electricity providers table

    num_providers = driver.find_element(By.CSS_SELECTOR, 
        ".table-footer__data.svelte-x63klk.svelte-x63klk").text.split(' ')[0]

    print("Number of providers: {}".format(str(num_providers)))
    
    while len(providers) != int(num_providers):
        repeat = False
        print("start providers page {}".format(current_page))
        # grab table of Electrical Providers and use as starting node
        provider_section = driver.find_element(By.CSS_SELECTOR, "#electricity-providers")

        table = provider_section.find_element(By.CSS_SELECTOR, ".table.sortable-table.svelte-x63klk tbody")
        table_rows = table.find_elements(By.CSS_SELECTOR, "tr.svelte-x63klk")

        # iterate over items in the table to get href tag for a elements

        for row in table_rows:
            provider_element = row.find_element(By.CSS_SELECTOR, "td.svelte-x63klk a")
            link = provider_element.get_attribute("href")
            if link in providers:
                repeat = True
                print("Repeat item. Trying again")
                break
            print(provider_element.text)
            providers.add(link)

        if not repeat:
            print("done providers page {}".format(current_page))

            current_page += 1

        if button_click(driver, provider_section):
            break

    return providers


def scrape_state(driver: webdriver, url: str, state: str) -> Dict:
    driver.get(url)
    driver.maximize_window()
    print("Scraping {}".format(state))
    state_info = {}

    provider_urls = get_electrical_providers(driver)

    providers_info = []
    for providerURL in provider_urls:
        providers_info.append(get_provider_info(driver, providerURL))

    # sort providers by total customers served
    state_info["electrical-providers"] = sorted(providers_info, 
        key=lambda provider: provider["Total-Customers"], reverse=True)
    
    return state_info

def get_driver(browser: str, driver_path: str, options_list: List[str], ) -> webdriver:
    '''Create webdriver object using path to driver and list of options.'''
    driver = None

    if browser.lower() == 'firefox':
        options = webdriver.FirefoxOptions()

        for option in options_list:
            options.add_argument(option)

        try:
            driver = webdriver.Firefox(service=FirefoxService(executable_path=driver_path), 
                options=options)
        except Exception as er:
            print(er, file=sys.stderr)
    elif browser.lower() in ['chrome', 'chromium']:
        # not always as reliable as Firefox, and testing was mostly done with Firefox
        options = webdriver.ChromeOptions()

        for option in options_list:
            options.add_argument(option)        

        try:
            driver = webdriver.Chrome(service=ChromeService(executable_path=driver_path), 
                options=options)
        except Exception as er:
            print(er, file=sys.stderr)

    return driver

def main():
    # info = get_provider_info(driver, 'https://findenergy.com/providers/reliant-energy/')

    driver = get_driver('Firefox', FIREFOX_PATH, ['--headless', '--no-sandbox' ])
    if driver is None:
        print("Not able to create webdriver object")
        return 1

    info = {}
    for state, state_abrv in STATES.items():
        url_query = "{}{}".format(BASE_URL, state_abrv)
        info[state_abrv] = scrape_state(driver, url_query, state_abrv)

        with open('{}/{}-energy-utility-info.json'.format(OUTPUT_DIR, state_abrv), 'w') as wf:
            json.dump(info[state_abrv], wf, indent=1)

    driver.close()
    
    return 0
    

if __name__ == "__main__":
    sys.exit(main())