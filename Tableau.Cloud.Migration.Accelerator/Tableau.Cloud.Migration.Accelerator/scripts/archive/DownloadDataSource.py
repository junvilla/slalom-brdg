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

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download data sources from your site."

# Prompt the user with the script name and description
print(f"\nYou are running {script_name} script. {script_description}")

"""
generally False if you don't want to download the data within the extract and only metadata
True means downloading the actual data within an extract, could be BIG!
noting that by not including extract, some data sources will not be downloaded as they require the extract and
therefore won't be published either
"""

# Prompt user whether or not to include data source extracts
ext_response = input("Do you want to download data extracts? (y/n)")
if ext_response.lower() == "y":
    inc_extracts = True
    print(
        "You have chosen to include data extracts.  These files make take a significant amount of time to download."
    )
else:
    inc_extract = False
    print(
        "You have chosen not to include data extracts. These will not be migrated to the destination environment."
    )

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
# This section will:
# download data source in a specified folder location

print("Begin downloading data sources. This might take several minutes.")

ds_data = []

create_file_locations()

start_time = time.time()

# check if directory to download data sources exists, if not create it
if not os.path.exists(ds_file_loc):
    os.makedirs(ds_file_loc)

# see Shared TSC GlobalVariables.py for source file format
csv_df = pd.read_csv(ds_download_file)

count_ds_source = len(csv_df.index)

# check if csv file has required headers, if not exit
req_header = ["Datasource ID"]

req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(list(csv_df.columns))
check_header = [header.upper() for header in check_header]

x = 0
for req in req_header:
    if search(check_header, req):
        x = x + 1


if x != check_sum:
    sys.exit(f"\nFile must contain required column headers: {req_header}")

print(
    f"\nBegin downloading data sources. Number of data sources to download: {count_ds_source}. \nThis might take several minutes."
)

with server.auth.sign_in(tableau_auth):
    count_ds = 0

    # start logging
    f = open(log_file, "a")
    f.write(time_log + "***** Begin Downloading Data Sources ******" + "\n")
    f.close()

    # Iterate through the data source list and begin downloading
    for index, row in csv_df.iterrows():
        f_ds = row["Datasource ID"]
        f_path = row["Path"]

        try:
            ds_to_download = server.datasources.get_by_id(f_ds)
            if not ds_to_download:
                log_error(ds_to_download.name, 7)
                continue
            ds_name = ds_to_download.name
            ds_owner = server.users.get_by_id(ds_to_download.owner_id)
            ds_owner_email = ds_owner.email
            ds_owner_name = ds_owner.name

            # Download data sources to folder.  change include_extract = True for extracts
            print(
                f"Downloading datasource [{ds_name}] from project [{ds_to_download.project_name}] owned by [{ds_owner_email}]. Filename: {ds_to_download.id}"
            )
            file_path = server.datasources.download(
                ds_to_download.id, filepath=ds_file_loc, include_extract=inc_extracts
            )

            # Pause for 5 seconds - the pace of the downloads was causing issues with the filenames reporting correctly in get_latest_file()
            time.sleep(5)

            # Split the file name and extension, and rename the file to LUID.ext
            _, filename = os.path.split(file_path)
            f_name, f_ext = os.path.splitext(filename)

            updated_ds_name = f"{ds_to_download.id}{f_ext}"
            os.rename(f"{file_path}", f"{ds_file_loc}\\{updated_ds_name}")

            count_ds += 1

            # get project name
            ds_projects, pagination_item = server.projects.get()

            for ds_proj in ds_projects:
                if ds_proj.id != ds_to_download.project_id:
                    continue
                ds_project_name = ds_proj.name

            # Write the results to a data frame results/log files
            values = [
                ds_to_download.id,
                ds_to_download.name,
                updated_ds_name,
                ds_to_download.project_id,
                ds_project_name,
                ds_owner_email,
                f_path,
            ]
            ds_data.append(values)

            # Write results to the log file
            f = open(log_file, "a")
            f.write(
                time_log
                + " Download successful: "
                + ds_to_download.name
                + " File: "
                + updated_ds_name
                + " in Project: "
                + ds_project_name
                + "\n"
            )
            f.close()

            time.sleep(5)

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            f = open(log_file, "a")
            f.write(error + "\n")
            f.close()
            print(err)

f = open(log_file, "a")
f.write(time_log + "***** End Downloading Datasources ******" + "\n")
f.close()

ds_df = pd.DataFrame(
    ds_data,
    columns=[
        "Data Source ID",
        "Data Source Name",
        "File Name",
        "Project ID",
        "Project Name",
        "Owner Email",
        "Path",
    ],
)

ds_df.to_csv(ds_source_file, header=True, index=False)

with pd.ExcelWriter(ds_dest_file) as writer:
    ds_df.to_excel(writer, sheet_name="DataSource List", index=False)

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
    f"Completed {script_name} in {duration}. \nDownloaded {str(count_ds)} datasources. \nPlease check the log files for errors."
)
