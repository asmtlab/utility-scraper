import json
import os


from Collect_State_Info import *
from Scrape_Electrical_Providers import OUTPUT_DIR

OUTPUT_DIR = "outputs"

out_filename = "all-states-utility-info.json"

states_dict = {}

with open(OUTPUT_FILE, 'r') as rf:
    all_states_info = json.load(rf)

with os.scandir(OUTPUT_DIR) as outputs:
    for file in outputs:
        if not file.name.startswith('.'):
            state_abrv = file.name.split('-')[0]
            if state_abrv in all_states_info.keys():
                with open("{}/{}".format(OUTPUT_DIR, file.name), 'r') as rf:
                    state_info = json.load(rf)
                all_states_info[state_abrv]['electrical-providers'] = state_info['electrical-providers']


with open(out_filename, 'w') as wf:
    json.dump(all_states_info, wf, indent=1)