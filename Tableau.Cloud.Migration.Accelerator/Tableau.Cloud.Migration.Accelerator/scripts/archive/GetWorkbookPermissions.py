# GetWorkbookPermissions.py connects to Tableau Server/Cloud and the Tableau REST API,
# gets Workbook asset permissions, then prints the list of each capability by group/user in Excel
# in preparation to add each permission to Tableau Cloud

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time
import pandas as pd
import tableauserverclient as TSC

# -----------------------------------Enter variables

wb_src_file = os.path.join(file_loc, export_file_loc, "WorkbookList.xlsx")

create_file_locations()

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about user Favorites on your site."

# Prompt the user with the script name and description
print(f"You are running the {script_name} script. {script_description}")

# call the perform_action function with dynamic environment names

print(f"Begin {script_name}. This might take several minutes.")

# -----------------------------------Tableau REST API Authorization for fetching items by LUID


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

# -----------------------------------end Session Authentication

# -----------------------------------Get Users/Groups (Groups aren't needed, but the download into the same file)
# This section will:
# Read the user list exported from the GetUsersGroups.py script
# If you haven't run this script, you must create a user list with the following headers:
# User ID, User Name, User Email, Site Role, Password, Display Name, License Level, Admin Level, Publishing

# Read GroupUserList.xlsx and check if it has the correct headers:
# users = pd.read_excel(user_file)
# usergroups = pd.read_excel(usergroup_file)

# build a dataframe of projects to get parentProjectName for project Favorites
# project_list = get_projects(server, tableau_auth)

# empty array to populate favorites from GET Get Favorites API call
data = []

start_time = time.time()

with server.auth.sign_in(tableau_auth):
    # pull necessary API authentication values from TSC Authentication
    auth_token = server._auth_token
    api_version = server.server_info.get().rest_api_version
    site_luid = server.site_id

    req_options = TSC.RequestOptions(pagesize=1000)

    all_workbooks = list(TSC.Pager(server.workbooks, req_options))
    all_groups = list(TSC.Pager(server.groups, req_options))

    for wb in all_workbooks:
        wb_id = wb.id
        wb_name = wb.name

        print(f"Getting Workbook permissions for workbook {wb_name} [{wb_id}].")

        try:
            wb_permissions = workbooks.permissions.get(
                portal_url, site_luid, api_version, auth_token, wb_id
            )
            # returns wb_id, wb_name, wb_owner, grantee_type, grantee_name, grantee (id), capabilities

            for k in wb_permissions:
                data.append(k)

        except:
            continue

    df = pd.DataFrame(
        data,
        columns=[
            "Workbook ID",
            "Workbook Name",
            "Workbook Owner",
            "Grantee Type",
            "Grantee Name",
            "Grantee ID",
            "Capability",
        ],
    )

    # Populate Grantee Name field by searching for Group ID or User ID
    print("Populating permission grantee names. This will take a moment.")

    for index, row in df.iterrows():
        if row["Grantee Type"] == "Group":
            for grp in all_groups:
                if grp.id == row["Grantee ID"]:
                    grantee_name = grp.name
        if row["Grantee Type"] == "User":
            usr = server.users.get_by_id(row["Grantee ID"])
            if usr.email is None:
                usr_name = usr.name
            else:
                usr_name = usr.email
            grantee_name = usr_name

        row["Grantee Name"] = grantee_name

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

# write the dataframe to the FavoritesList.xlsx Excel file
with pd.ExcelWriter(wb_src_file, engine="openpyxl", mode="a") as writer:
    df.to_excel(
        writer, sheet_name="Workbook Permissions List", header=True, index=False
    )

print(f"Completed {script_name}. Please view {wb_src_file} for details.")
