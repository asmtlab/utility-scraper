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

# Water Provider Data
# -------------------------------------------------
# https://ordspub.epa.gov/ords/sfdw/sfdw/r/sdwis_fed_reports_public/wsdetail?clear=RP,RIR

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

REGION_1 = [ 'CT', 'ME', 'MA', 'NH', 'RI', 'VT' ]
REGION_2 = [ 'NJ', 'NY', ]
REGION_3 = [ 'DE', 'MD', 'PA', 'VA', 'WV' ]
REGION_4 = [ 'AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'SC', 'TN' ]
REGION_5 = [ 'IL', 'IN', 'MI', 'MN', 'OH', 'WI' ]
REGION_6 = [ 'TX', 'AR', 'LA', 'NM', 'OK' ]
REGION_7 = [ 'IA', 'KS', 'MO', 'NE' ]
REGION_8 = [ 'CO', 'MT', 'ND', 'SD', 'UT', 'WY' ]
REGION_9 = [ 'AZ', 'CA', 'HI', 'NV' ]
REGION_10 = [ 'AK', 'ID', 'OR', 'WA' ]

REGIONS = {
     "1": REGION_1,
     "2": REGION_2,
     "3": REGION_3,
     "4": REGION_4,
     "5": REGION_5,
     "6": REGION_6,
     "7": REGION_7,
     "8": REGION_8,
     "9": REGION_9,
    "10": REGION_10
}

#### FILE INFO ####
DATASETS_DIRECTORY_PATH             = "datasets" 
US_ENERGY_PRODUCTION_BY_STATE_FILE  = "annual_generation_state.xls"
US_POPULATION_BY_CITY_FILE          = "sub-est2021_all.csv"
US_WATER_PROVIDERS_BY_STATE_FILE    = "Water System Detail.csv"

OUTPUT_FILE = "all-states-water-population-info.json"

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

def capitalize(string: str) -> str:
    '''Capitalize the first letter in a string.'''
    return " ".join([ word.capitalize() for word in string.split() ])

def write_json(filename: str, content: Dict) -> None:
    '''Writes content to a json file.'''
    with open(filename, 'w') as wf:
        json.dump(content, wf, indent=1)

def get_excel_df(filepath: str, header: int, skiprows: int) -> DataFrame:
    '''Read xls file into a pandas data-frame.'''
    excel_data_df = None
    try:
        excel_data_df = read_excel(filepath, header=[header], skiprows=0)
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
        
        state_info[year] = yearly_production

    return state_info

def get_state_water_providers(df: DataFrame, state: str) -> List[Dict]:
    state_providers = []

    # Filter dataframe by state
    state_df = df.query(
        "`Primacy Agency` == '{}'".format(state)
    )

    for pws_id, pws_name, pws_type, owner_type, source, pop_served in \
        zip(
            state_df['PWS ID'], state_df['PWS Name'], state_df['PWS Type'], 
            state_df['Owner Type'], state_df['Primary Source'], 
            state_df['Population Served Count']
        ):
        # print(pop_served)
        state_providers.append({
            'PWS-ID': pws_id,
            'PWS-Name': capitalize(pws_name),
            'PWS-Type': capitalize(pws_type),
            'Owner-Type': capitalize(owner_type),
            'Primary-Source': capitalize(source),
            'Population-Served': int("".join(pop_served.split(',')))
        })

    # Sort list of providers by population served (descending) and return
    return sorted(state_providers, reverse=True, key=lambda provider: provider['Population-Served'])

def get_state_info(state_name: str, state_abrev: str, 
        energy_production_df: DataFrame, water_provider_df: DataFrame,
        statewide_pop_df: DataFrame) -> Dict:
    '''Collects population and energy production data for all states.'''
    state_dict = {}
    # read energy production xlsx

    state_dict['population'] = {}
    state_dict['energy-production'] = {}

    # get state population
    state_dict['population']['total'] = get_state_population(statewide_pop_df, state_name)
    # get population of counties
    state_dict['population']['counties'] = get_county_populations(statewide_pop_df, state_name)
    # get population of cities
    state_dict['population']['cities'] = get_city_populations(statewide_pop_df, state_name)
    # get energy production
    state_dict['energy-production']['annual'] = get_state_energy_production(energy_production_df, state_abrev)
    # get water providers
    state_dict['water-providers'] = get_state_water_providers(water_provider_df, state_name)

    return state_dict

def main():
    energy_production_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_ENERGY_PRODUCTION_BY_STATE_FILE
    )
    # read xls file into pandas dataframe
    energy_production_df = get_excel_df(energy_production_file, header=1, skiprows=0)
    if energy_production_df is None: return 1

    water_provider_file = "{}/{}".format(
        DATASETS_DIRECTORY_PATH, US_WATER_PROVIDERS_BY_STATE_FILE
    )

    water_provider_df = get_csv_df(water_provider_file)
    if water_provider_df is None: return 1

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
            energy_production_df, water_provider_df, statewide_pop_df
        )

    # write info to json file
    write_json(OUTPUT_FILE, states_dict)

    return 0

if __name__ == "__main__":
    sys.exit(main())