from Scrape_Electrical_Providers import *
from Collect_State_Info import *

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

DATASETS_DIRECTORY_PATH = "datasets" # path to dataset directory 
ENERGY_PRODUCTION_BY_STATE_FILE = "annual_generation_state.xls"
US_POPULATION_BY_CITY_FILE = "sub-est2021_all.csv"
OUTPUT_FILE = "all-states-info.json"

STATES = {
    'Alaska': 'AK',
    'Alabama': 'AL',
    'Arkansas': 'AR',
    'Arizona': 'AZ',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Iowa': 'IA',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Massachusetts': 'MA',
    'Maryland': 'MD',
    'Maine': 'ME',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Missouri': 'MO',
    'Mississippi': 'MS',
    'Montana': 'MT',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Nebraska': 'NE',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'Nevada': 'NV',
    'New York': 'NY',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Virginia': 'VA',
    'Vermont': 'VT',
    'Washington': 'WA',
    'Wisconsin': 'WI',
    'West Virginia': 'WV',
    'Wyoming': 'WY'
}

def main():
    # get state population and overall electrical production data
    energy_production_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, ENERGY_PRODUCTION_BY_STATE_FILE
    )
    # read xls file into pandas dataframe
    energy_production_df = get_excel_df(energy_production_file)
    if energy_production_df is None: return None


    population_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_POPULATION_BY_CITY_FILE
    )
    # read csv file into pandas dataframe
    statewide_pop_df = get_csv_df(population_file)
    if statewide_pop_df is None: return None


    states_dict = {}
    for state_name, state_abrev in STATES.items():
        states_dict[state_abrev] = get_state_info(
            state_name, state_abrev,
            energy_production_df, statewide_pop_df
        )

    # write info to json file
    write_json(OUTPUT_FILE, states_dict)

    # collect state electrical provider data
    driver = get_driver('Firefox', ['--headless', '--no-sandbox' ], FIREFOX_PATH)
    if driver is None:
        print("Not able to create webdriver object")
        return 1

    info = {}
    for name, abrv in STATES.items():
        urlQueryString = "{}{}".format(BASE_URL, abrv)
        info[abrv] = scrape_state(driver, urlQueryString, abrv)

        with open('{}/{}-energy-utility-info.json'.format(OUTPUT_DIR, abrv), 'w') as wf:
            json.dump(info[abrv], wf)
    
    driver.close()


    # collect water providers



    # combine json files

    return 0
    

if __name__ == "__main__":
    sys.exit(main())