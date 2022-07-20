# STATE, COUNTY, AND CITY POPULATION DATASETS

# CITY POPULATIONS
# -------------------------------------------------
#  datasets can be found here: 
#   https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/cities/totals/
#  specific dataset used:
#   https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/cities/totals/sub-est2021_all.csv
#
# This city dataset also includes population info for counties and the entire state 

# STATEWIDE ELECTRICITY PRODUCTION DATASETS
# -------------------------------------------------
#  datasets can be found here: 
#     https://www.eia.gov/electricity/data/state/
#  specific dataset used found here: 
#       https://www.eia.gov/electricity/data/state/annual_generation_state.xls

# DATASET HEADER KEY
# -------------------------------
# https://www.census.gov/data/developers/data-sets/popest-popproj/popest/popest-vars.html

import json
import sys
from typing import Dict, List

from pandas import read_excel
from pandas import read_csv
from pandas import DataFrame

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

#### FILE INFO ####
DATASETS_DIRECTORY_PATH = "datasets" # path to dataset directory 
ENERGY_PRODUCTION_BY_STATE_FILE = "annual_generation_state.xls"
US_POPULATION_BY_CITY_FILE = "sub-est2021_all.csv"

#### CSV/XLS HEADER NAMES ####
# These strings are from the files shown above and are consistent
#   between the census.gov datasets. 
# The year should be adjusted as needed
COL_HEADER_1 = 'POPESTIMATE2020'
COL_HEADER_2 = 'POPESTIMATE2021'

# These specify the dictionary key for annual population
#   Adjust accordingly
POP_KEY_1 = 'estimate-2020'
POP_KEY_2 = 'estimate-2021'

### Used when parsing info from ENERGY_PRODUCTION_PATH
YEAR_MIN = 1990
YEAR_MAX = 2020

def write_json(filename: str, content: Dict) -> None:
    '''Writes content to a json file.'''
    with open(filename, 'w') as wf:
        json.dump(content, wf, indent=1)

def get_excel_df(filepath: str) -> DataFrame:
    '''Read xls file into a pandas data-frame.'''
    excel_data_df = None
    try:
        excel_data_df = read_excel(filepath, header=[1], skiprows=0)
        # header=[1] specifies the index of the header row in the xls file
        #   adjust accordingly to ignore rows at the top of the xls file
    except Exception as err:
        print(err, file=sys.stderr)
        
    return excel_data_df

def get_csv_df(filepath: str) -> DataFrame:
    '''Read CSV file into a pandas data-frame'''
    csv_data_df = None

    try:
        csv_data_df = read_csv(filepath, encoding="ISO-8859-1")
    except Exception as err:
        print(err, file=sys.stderr)

    return csv_data_df

def get_state_energy_production(df: DataFrame, state: str) -> Dict:
    '''Get energy production by source and MWhs generated for a particular state.'''
    state_info = {}

    for year in range(YEAR_MIN, YEAR_MAX+1):
        # Filter dataframe by state and year
        state_df = df.query(
            "(`STATE` == '{}') and (`TYPE OF PRODUCER` == 'Total Electric Power Industry')\
                and (`YEAR` == {})".format(state, year)
        )
        
        yearly_production = {}
        for item in state_df.itertuples():
            yearly_production[item._4] = item._5
            # {
            #     'source': item._4,
            #     'generation-MWhs': item._5
            # })
        
        state_info[year] = yearly_production

    return state_info

def get_state_population(df: DataFrame, state: str) -> Dict:
    '''Get state population data for a specific state from dataframe.'''
    states_pop = {}

    states_df = df.query(
            "(`NAME` == '{}') and (`SUMLEV` == 40)".format(state)
        )
    # SUMLEV 40 is State and/or Statistical Equivalent

    for state, pop1, pop2 in zip(states_df['NAME'], 
        states_df[COL_HEADER_1], states_df[COL_HEADER_2]):
        states_pop[POP_KEY_1] = pop1
        states_pop[POP_KEY_2] = pop2

    return states_pop

def get_county_populations(df: DataFrame, state: str) -> List[Dict]:
    '''Get county population data for a specific state from dataframe.'''
    counties = []

    state_df = df.query(
        "(`STNAME` == '{}') and (`SUMLEV` == 50)".format(state) 
    )
    # SUMLEV 50 is County and/or Statistical Equivalent

    for county, pop1, pop2 in zip(state_df['NAME'], 
        state_df[COL_HEADER_1], state_df[COL_HEADER_2]):

        counties.append({
            'county': county,
            POP_KEY_1: pop1,
            POP_KEY_2: pop2
        })

    # sort the list by population of the most recent year
    return sorted(counties, reverse=True, key=lambda county: county[POP_KEY_2])

def get_city_populations(df, state) -> List[Dict]:
    '''Get city population data for a specific state from dataframe.'''
    cities = []

    state_df = df.query(
        "(`STNAME` == '{}') and (`SUMLEV` == 162)".format(state) 
    )
    # SUMLEV 162 is Incorporated Place

    for city, pop1, pop2 in zip(state_df['NAME'], 
        state_df[COL_HEADER_1], state_df[COL_HEADER_2]):

        cities.append({
            'name': city,
            POP_KEY_1: pop1,
            POP_KEY_2: pop2
        })

    # sort the list by population of the most recent year
    return sorted(cities, reverse=True, key=lambda city: city[POP_KEY_2])

def get_states_info(energy_production_file: str, population_file: str) -> Dict:
    '''Collects population and energy production data for all states.'''
    states_dict = {}
    # read energy production xlsx
    energy_production_df = get_excel_df(energy_production_file)
    if energy_production_df is None: return None

    statewide_pop_df = get_csv_df(population_file)
    if statewide_pop_df is None: return None

    for state_name, state_abrev in STATES.items():
        states_dict[state_abrev] = {}
        states_dict[state_abrev]['population'] = {}
        states_dict[state_abrev]['energy-production'] = {}

        # get state population
        states_dict[state_abrev]['population']['total'] = get_state_population(statewide_pop_df, state_name)
        # get population of counties
        states_dict[state_abrev]['population']['counties'] = get_county_populations(statewide_pop_df, state_name)
        # get population of cities
        states_dict[state_abrev]['population']['cities'] = get_city_populations(statewide_pop_df, state_name)
        # get energy production
        states_dict[state_abrev]['energy-production']['annual'] = get_state_energy_production(energy_production_df, state_abrev)
    
    return states_dict

def main():
    energy_production_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, ENERGY_PRODUCTION_BY_STATE_FILE
    )

    population_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_POPULATION_BY_CITY_FILE
    )

    states_dict = get_states_info(
        energy_production_file, 
        population_file
    )

    if states_dict is None:
        return 1

    # write info to json file
    write_json('energy-production-all-states.json', states_dict)

    return 0

if __name__ == "__main__":
    sys.exit(main())