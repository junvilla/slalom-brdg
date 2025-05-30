# Tableau Cloud Migration Accelerator - Tableau Migration SDK

## Getting Started

### Note: This SDK has only been tested on Windows using Visual Studio Code

* Make sure the "Python" workload is installed for Visual Studio;
* Install `Python 3.8+` (and pip3) (make sure it's on PATH) and restart Visual Studio;
  * It MUST be python3. To verify, start `python` and check the version (`python --version`). Python2 is very different.
* Update PIP and SetupTools to the latest version by executing:
  * `python -m pip install --upgrade pip setuptools` (Windows)
  * `python3 -m pip install --upgrade pip setuptools` (Linux/Unix/MacOS)
* Create the python virtual environment
  * (From tableau-cloud-migration-accelerator\Tableau.Migration.SDK):
  * `python -m venv venv` (Windows)
  * `python3 -m venv venv` (Linux/Unix/MacOS)
* Activate the virtual environment:
  * Windows:
    * `.\venv\Scripts\Activate.ps1`
      * OR
    * In VSCode, open `\venv\Scripts\Activate.ps1` and click `Run (Ctrl+F5)`
  * Linux/Unix/MacOS:
    * `/venv/bin/activate`
* Execute the setup file:
  * `python .\setup.py` (Windows)
  * `python3 ./setup.py` (Linux/Unix/MacOS)
* Add or update any filters, hooks, or mappings:
  * Create new filters
    * Add/edit functions in `migration_filters.py`
  * Add filters to the migration plan
    * Edit the `CoreMigration.py` file
    * Import the filter functions
      * `from migration_filters import {filter_function}`
  * Add the function to the migration plan
    * In the `migrate()` function, find `# Add filters here.`
    * Add the filter:
      * `plan_builder.filters.add(filter_function)`
* Repeat this process for hooks and mappings by editing:
  * `migration_hooks.py`
  * `migration_mappings.py`
  * Import the functions and add them to `CoreMigration.py` under the `migrate()` function
* By default, the plan is set to filter out all content:
  * Users
  * Groups
  * Projects
  * Data Sources
  * Workbooks
  * Extract Refresh Tasks
* In the VSCode terminal, enter the following:
  * `code .` (This will launch the virtual environment in a new window using the venv interpreter)
* Execute the main migration application:
  * `python .\main.py` (Windows)
  * `python3 ./main.py` (Linux/Unix/MacOS)
* Run the SDK application:
  * Select option `2: Migrate Content` from the main menu.
