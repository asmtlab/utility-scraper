import json

from Collect_State_Info import STATES, OUTPUT_FILE

JSON_DIR = "outputs"

REGION_5_ABRV = [ 'IL', 'IN', 'MI', 'MN', 'OH', 'WI' ]
REGION_5 = {
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Ohio': 'OH',
    'Wisconsin': 'WI'
}

in_filename = OUTPUT_FILE
water_info_file = "region-5-water.json"

out_filename = "region-5-utility-info.json"

region_5_states = {}

with open(in_filename, 'r') as rf:
    all_states = json.load(rf)

for key in all_states.keys():
    if key in REGION_5_ABRV:
        region_5_states[key] = all_states[key]
        region_5_states[key]['water-providers'] = []
        region_5_states[key]['electrical-providers'] = []

all_water_info = []

with open(water_info_file, 'r') as rf:
    all_water_info = json.load(rf)

for water_provider in all_water_info:
    r5_state = water_provider['State']
    
    if r5_state in REGION_5.keys():
        region_5_states[REGION_5[r5_state]]['water-providers'].append(water_provider)

for state in region_5_states.keys():
    water_providers = region_5_states[state]['water-providers']
    region_5_states[state]['water-providers'] = sorted(
        water_providers, reverse=True, key=lambda provider: provider['Population-served']
    )

for state in region_5_states.keys():
    state_info = region_5_states[state]

    if state in REGION_5_ABRV:
        with open("{}/{}-energy-utility-info.json".format(JSON_DIR, state), 'r') as rf:
            s = json.load(rf)
            state_info['electrical-providers'] = s['electrical-providers']
        
        region_5_states[state] = state_info

with open(out_filename, 'w') as wf:
    json.dump(region_5_states, wf, indent=1)