# GetGroups.py connects to Tableau Server
# gets users and groups then prints the list of users and their groups in csv
# The file can be used as a source to create groups in Tableau
# the csv output must be formatted using the required format for CSV import to Tableau Online

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

# File location for Exporting Users, Groups,
group_dest_file = os.path.join(file_loc, export_file_loc, "GroupList.xlsx")

create_file_locations()

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about the groups on your site."

# Prompt the user with the script name and description
print(f"\nYou are running the {script_name} script. {script_description}")


# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

print(f"\nBegin {script_name}. This might take several minutes.")
# -----------------------------------Session Authentication to Tableau Server

server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()

#
# # -------------------------------end Session Authentication

# ------------------------------- Get Groups

# empty array to populate users from server.user.get
data = []
group_data = []
start_time = time.time()

with server.auth.sign_in(tableau_auth):
    all_groups, pagination_item = server.groups.get()
    for groups in all_groups:
        server.groups.populate_users(groups)
        group_values = [groups.name, groups.domain_name]
        group_data.append(group_values)
        print(f"Extracting group: {groups.name} [{groups.id}]")
        for user in groups.users:
            # include user.id if a script will be used to add user to a group
            values = [
                groups.name,
                groups.domain_name,
                user.id,
                user.name,
                user.email,
                user.site_role,
                "",
            ]
            data.append(values)

print("\nCreating data frames with Group and Group Membership details. Please wait.")

df = pd.DataFrame(
    data,
    columns=[
        "Group Name",
        "AD Domain",
        "User ID",
        "User Name",
        "User Email",
        "Site Role",
        "Migrate?",
    ],
)
group_df = pd.DataFrame(group_data, columns=["Group Name", "AD Domain"])
add_user_group_df = df[["Group Name", "User ID"]]

group_df.to_csv(
    os.path.join(file_loc, import_file_loc, "GroupList.csv"), header=True, index=False
)
add_user_group_df.to_csv(
    os.path.join(file_loc, import_file_loc, "AddUserToGroup.csv"),
    header=True,
    index=False,
)

with pd.ExcelWriter(group_dest_file) as writer:
    print(f"\nWriting results to {group_dest_file}. Please wait.")
    df.to_excel(writer, sheet_name="Group List", header=True, index=False)

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

print(f"\nCompleted {script_name} in {duration}. Please view file {group_dest_file}")
