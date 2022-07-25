import os

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
DRIVER_PATH = "./geckodriver" # replace with path to driver for your OS

BASE_URL = "https://findenergy.com/"

# Dataset files
DATASETS_DIRECTORY_PATH            = "datasets" 
US_ENERGY_PRODUCTION_BY_STATE_FILE = "annual_generation_state.xls"
US_POPULATION_BY_CITY_FILE         = "sub-est2021_all.csv"
US_WATER_PROVIDERS_BY_STATE_FILE   = "Water System Detail.csv"

# Outputs
OUTPUT_DIR  = 'outputs'
OUTPUT_FILE = "all-states-info.json"


def main():

    # State energy production
    energy_production_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_ENERGY_PRODUCTION_BY_STATE_FILE
    )

    energy_production_df = get_excel_df(energy_production_file, header=1, skiprows=0)
    if energy_production_df is None: return 1

    # State water providers
    water_provider_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_WATER_PROVIDERS_BY_STATE_FILE
    )

    water_provider_df = get_csv_df(water_provider_file)
    if water_provider_df is None: return 1

    # State populations
    population_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_POPULATION_BY_CITY_FILE
    )

    statewide_pop_df = get_csv_df(population_file)
    if statewide_pop_df is None: return None

    # combine energy, water, and population info
    states_dict = {}
    for state_name, state_abrev in STATES.items():
        states_dict[state_abrev] = get_state_info(
            state_name, state_abrev,
            energy_production_df, water_provider_df, statewide_pop_df
        )

    # collect state electrical provider data
    driver = get_driver('Firefox', DRIVER_PATH, ['--headless', '--no-sandbox' ])
    if driver is None:
        print("Not able to create webdriver object")
        return 1

    # create directory for outputs if not already there
    if not os.path.exists(OUTPUT_DIR) or not os.path.isdir(OUTPUT_FILE):
        os.makedirs(OUTPUT_DIR)
    
    info = {}
    for name, abrv in STATES.items():
        urlQueryString = "{}{}".format(BASE_URL, abrv)
        info[abrv] = scrape_state(driver, urlQueryString, abrv)

        states_dict[abrv]['electrical-providers'] = info[abrv]

        with open('{}/{}-energy-utility-info.json'.format(OUTPUT_DIR, abrv), 'w') as wf:
            json.dump(info[abrv], wf)

    driver.close()

    write_json(OUTPUT_FILE, states_dict)

    return 0

if __name__ == "__main__":
    sys.exit(main())