# Prerequisites

Before using this script, ensure that you have the following prerequisites installed:

- Python 3.x
- Required Python packages (install with `pip install -r requirements.txt`)
- [Git Bash](https://git-scm.com/downloads)
- [Google Chrome](https://www.google.com/intl/en/chrome/?standalone=1&platform=win64) (version must match chrome-driver.exe -- currently `118.0.5993.71`)
- [Chromedriver](https://googlechromelabs.github.io/chrome-for-testing/#stable) (version must be for chrome version)

# PP Grabber Script

This python script grabs prop data from PP via selenium using the chrome-driver and saves the json to the `pp_data` directory.

## Usage

- `run_pp_grabber.bat` uses selenium and chrome driver to download prop json snapshot from pp.  Data is written to `pp_data` directory.
- `run_pp_grabber_3x_daily.bat` uses selenium and chrome driver to download prop json snapshot at the 3 different times every day.  Data is written to `pp_data` directory.

# NFL Data Analysis Script

This Python script is designed to automate the process of gathering and analyzing NFL data for a specific year and week. It runs a series of sub-scripts to perform tasks related to fantasy football and player prop betting.

## Usage

To run the script, use the following command-line arguments:

- `--game_day`: Day of the game data to generate report for.  Specify 'all' to generate results for all games that weekend. (default: "sunday")
- `--pp_day`: Day of the pp player prop data used in the driver (default: "saturday")
- `--year`: Year for NFL data (default: 2023)
- `--week`: NFL week (default: 6)

Example usage (see `run_pp_prop_report.bat`)

```bash
python driver.py --game_day sunday --pp_day saturday --year 2023 --week 6
```

