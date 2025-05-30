# Download data source
# This script will download data sources from Tableau Server or Tableau Cloud
# into a specified file location
# and create export files of data source and connection information which can be used to import into Tableau Cloud

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time
import tableauserverclient as TSC

# -----------------------------------Enter variables

# file location. this is where tableau object information and workbooks/data sources will be downloaded
# ds_folder = location of downloaded data sources. uses file_loc variable in global variable for file path
# specify the folder name to store the downloaded files.
# these folder must already exist
ds_folder = "DS"
ds_file_loc = file_loc + ds_folder

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download data sources from your site."

# Prompt the user with the script name and description
print(f"\nYou are running {script_name} script. {script_description}")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

# -----------------------------------Session Authentication to Tableau Server
server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()

# ------------------------------- Download Data Source
start_time = time.time()

# This section will:
# download data source in a specified folder location
data = []
conn_data = []

# check if directory to download workbooks exist, if not create
if not os.path.exists(ds_file_loc):
    os.makedirs(ds_file_loc)

print("\nBegin downloading data sources. This might take several minutes.")

with server.auth.sign_in(tableau_auth):
    all_datasource, pagination_item = server.datasources.get()

    for ds in all_datasource:

        # check if duplicate data source names exist, if so do not download as it will overwrite the previous data
        # source file

        req_options = TSC.RequestOptions()
        req_options.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.Name,
                TSC.RequestOptions.Operator.Equals,
                ds.name,
            )
        )

        datasource = list(TSC.Pager(server.datasources, req_options))

        if len(datasource) > 1:
            log_error(ds.name, 5)

        if any(char in invalid_char for char in ds.name):
            log_error(ds.name, 6)

        # if duplicate data source name exists, do not download
        if len(datasource) > 1:
            continue

        # Check for special characters in name. if name has special characters, flag and do not download
        if not any(char in invalid_char for char in ds.name):
            # Download data sources to folder.  change include_extract = True for extracts
            server.datasources.download(
                ds.id, filepath=ds_file_loc, include_extract=True
            )
        else:
            continue

end_time = time.time()
seconds = end_time - start_time

if seconds < 60:
    duration = f"{round(seconds,2)} second(s)"
elif seconds > 60 and seconds < 3600:
    duration_s = round(seconds % 60, 2)
    duration_m = round(seconds / 60)
    duration = f"{duration_m} minute(s) and {duration_s} second(s)"
elif seconds >= 3600:
    duration_m = round(seconds % 3600, 2)
    duration_h = round(seconds / 3600)
    duration = f"{duration_h} hour(s) and {duration_m} minute(s)"

print(
    f"\nCompleted {script_name} in {duration}. Please check your log files for any errors."
)
