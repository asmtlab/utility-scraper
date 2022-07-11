import json
import sys
import pandas

def xlsx_json(xlsx_path):
    # Read excel document
    excel_data_df = pandas.read_excel(xlsx_path, sheet_name='Sheet1')
    # Convert excel to string
    # (define orientation of document in this case from up to down)
    thisisjson = excel_data_df.to_json(orient='records')
    # Print out the result
    # print('Excel Sheet to JSON:\n', thisisjson)
    # Make the string into a list to be able to input in to a JSON-file
    thisisjson_dict = json.loads(thisisjson)
    # Define file to write to and 'w' for write option -> json.dump()
    # defining the list to write from and file to write to
    with open('.\data-electric.json', 'w') as json_file:
        json_file.write(json.dumps(thisisjson_dict, indent=4))


if len(sys.argv) < 2:
    print("XLSX files required")
    print("Usage: python CSVScrape.py </path/to/xlsx file>")
elif len(sys.argv) == 2:
    xlsx_json(sys.argv[1])

