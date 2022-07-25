# utility-scraper :zap: :droplet:

## Requirements ##

### Dependencies ###

`pip install selenium`

Download the necessary browser driver (Firefox preferred) from [here](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) and update the filepath to this driver.

```Py
DRIVER_PATH = "./geckodriver" # replace with path to driver for your OS
```

## Datasets ##

The datasets used to collect necessary information are included in the repo under the `datasets` directory. To include a newer version of a specific dataset it should be included in the `datasets` directory and then update the corresponding variable in `utility-scraper.py` with the appropriate filename.

``` Py
    # Dataset files
    DATASETS_DIRECTORY_PATH            = "datasets" 
    US_ENERGY_PRODUCTION_BY_STATE_FILE = "annual_generation_state.xls"
    US_POPULATION_BY_CITY_FILE         = "sub-est2021_all.csv"
    US_WATER_PROVIDERS_BY_STATE_FILE   = "Water System Detail.csv"
```

### Population ###

<https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/cities/totals/>

[File used](https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/cities/totals/sub-est2021_all.csv)

### State Specific Electrical Production ###

<https://www.eia.gov/electricity/data/state/>

[File used](https://www.eia.gov/electricity/data/state/annual_generation_state.xls)

### Water Providers ###

<https://ordspub.epa.gov/ords/sfdw/sfdw/r/sdwis_fed_reports_public/1>

Under '*Select a Report*' in the **Report Options** section, select '*Water System Detail*'. Select the appropriate Submission year and quarter (e.g. 2022 Quarter 2) and then select *View Reports*.

### State Specific Electrical Providers ###

Site scraped: [findenergy.com](https://findenergy.com/)

This site aggregates information found from several government agency reports (mostly EIA) found [here](https://findenergy.com/data/)

## Usage ##

Data for all 50 states can be collected out of the box by running the `utility-scraper.py` file.

```
python3 utility-scraper.py
```