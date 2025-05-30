import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import time
import tableauserverclient as TSC
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *

# -----------------------------------Enter variables

# --------------------------------- end variables

ds_dest_file = os.path.join(file_loc, log_file_loc, "Update Data Source Log.xlsx")

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

# ---------------------------------- Begin Script
start_time = time.time()

# create dataframe to store errors and activity
log_df = pd.DataFrame(
    columns=["Time Log", "Object Name", "Script Name", "Project", "Result", "Error"]
)
log_df["Script Name"] = "UpdateDataSource.py"

# read data source import source file and data source connection import file

# data source
ds_csv_df = pd.read_csv(ds_source_file)
ds_csv_df.dropna(axis=0, how="all", inplace=True)

# get count of data sources expected to publish
count_ds_source = len(ds_csv_df.index)

# check if csv file has required headers, if not exit
req_header = ["Data Source Name", "Project ID", "Owner Email"]
req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(ds_csv_df.columns)
check_header = [header.upper() for header in check_header]

x = 0

for req in req_header:
    if search(check_header, req):
        x = x + 1

if x != check_sum:
    sys.exit(f"File must contain required column headers: {req_header}")

# begin logging
f = open(log_file, "a")
f.write(time_log + "******* Begin Update Data Source ********" + "\n")
f.close()

count_ds = 0

for k in ds_csv_df.index:
    with server.auth.sign_in(tableau_auth):
        try:
            ds_csv_name = ds_csv_df["Data Source Name"][k]
            ds_destination_project = ds_csv_df["Project ID"][k]
            ds_owner_id = ds_csv_df["Owner Email"][k]

            # get id of newly published data source

            req_options = TSC.RequestOptions(pagesize=1000)
            all_projects = list(TSC.Pager(server.projects, req_options))

            req_options.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    ds_csv_name,
                )
            )
            filter_datasource = list(TSC.Pager(server.datasources, req_options))

            if not filter_datasource:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": ds_csv_name,
                    "Script Name": "UpdateDataSource.py",
                    "Project": str(ds_destination_project),
                    "Result": "Failed",
                    "Error": "datasource does not exist",
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
                continue

            for proj in all_projects:
                if proj.id == ds_destination_project:
                    ds_destination_proj_name = proj.name
                    break

            if not ds_destination_proj_name:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": ds_csv_name,
                    "Script Name": "UpdateDataSource.py",
                    "Project": str(ds_destination_project),
                    "Result": "Failed",
                    "Error": "Project does not exist",
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
                continue

            # get datasource id to update
            for fw in filter_datasource:
                if fw.project_id == ds_destination_project:
                    published_datasource_id = fw.id
                    break

            if not published_datasource_id:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": ds_csv_name,
                    "Script Name": "UpdateDataSource.py",
                    "Project": str(ds_destination_project)
                    + " "
                    + ds_destination_proj_name,
                    "Result": "Failed",
                    "Error": "Cannot find the datasource in the project",
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
                continue

            # get user id based on email
            req_options = TSC.RequestOptions(pagesize=1000)
            req_options.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    ds_owner_id,
                )
            )
            filter_users = list(TSC.Pager(server.users, req_options))

            for fu in filter_users:
                filter_users_id = fu.id

            if not filter_users_id:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": ds_csv_name,
                    "Script Name": "UpdateDataSource.py",
                    "Project": str(ds_destination_project),
                    "Result": "Warning",
                    "Error": str(ds_owner_id)
                    + " Owner does not exist, default owner is assigned",
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

            update_datasource = server.datasources.get_by_id(published_datasource_id)
            update_datasource.owner_id = filter_users_id
            server.datasources.update(update_datasource)

            count_ds = count_ds + 1

            new_row = {
                "Time Log": time_log,
                "Object Name": ds_csv_name,
                "Script Name": "UpdateDataSource.py",
                "Project": str(ds_destination_project),
                "Result": "Success",
                "Error": str(ds_owner_id) + " was updated as the datasource owner",
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            new_row = {
                "Time Log": time_log,
                "Object Name": ds_csv_name,
                "Script Name": "UpdateDataSource.py",
                "Project": str(ds_destination_project),
                "Result": "Failed",
                "Error": str(err),
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

with pd.ExcelWriter(ds_dest_file) as writer:
    log_df.to_excel(writer, sheet_name="UpdateDataSource", index=False)

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

f = open(log_file, "a")
f.write(
    "Number of data sources to update: "
    + str(count_ds_source)
    + "\n"
    + "Number of data sources updated: "
    + str(count_ds)
    + "\n"
)
if count_ds != count_ds_source:
    log_error(ds_source_file, 3)
f.write("Check detailed logs in " + ds_dest_file + "\n")
f.write(time_log + "******* End Update Data Source ********" + "\n")
f.close()

print(
    f"Completed {script_name} in {duration}. Please check your log files for any errors."
)
