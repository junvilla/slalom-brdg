# AddUsersToGroup
# reads a csv file, adds users to group using User ID
# The csv file must contain the group name and user id (not user name) from Tableau Server
# The first row should be the column header with column name "Group Name" & "User ID"
# The groups & users must already be added in Tableau Server. Use CreateGroup.py to create the groups
# Existing group information can be extracted to a csv using GetGroups.py

"""
Add User to Group

For each group add all users that are associated to it from source
Requires users and groups already migrated.

Will iterate through current source captured data:
    User Groups - contains the users for each group (the source basis for the migration)
    Source users - contains the User ID that matches the User ID of the User Groups
                    But also contains the User Name
    Migrated users - contains the migrated User ID and User Name
                    we use the User Name to match to the Source Users to get the User ID
    Once we have the migrated User ID, we create various dataframes and combine them togeher
    Once combined we can then iterate through current migrated groups against the combined dataframe
    so that for each group we add the migrated User ID to match the server.
"""
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

# Get the name of the current script
script_name = os.path.basename(__file__)
# Define a description of the script
script_description = "This script will add each user to their respective group."

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

# -------------------------------variables
start_time = time.time()
log_df = pd.DataFrame(
    columns=["Time Log", "Object Name", "Script Name", "Result", "Error"]
)
log_df["Script Name"] = script_name

# ------------------------------- Begin
# This section will:
# Read the source csv file, check for required column headers
# check if group exists in Tableau Server, if so add user to the group


# read csv file
df = pd.read_csv(source_usergroups)

# by ben N 26-10-2023:
# api call relies on User ID which is an md5 hash encryption
# any users that are created at destination will have a different generated md5 than of the source
# so this script will need to assume the groups and user objects are already created at destination
# and this will need to fetch the users created as destination for the new User IDs into the dataframe before adding
# users to groups
# groups are by name (string)
# users are by ID (md5)

# check if csv file has required headers, if not exit
req_header = ["Group Name", "User ID"]
check_sum = len(req_header)
check_header = list(df.columns)

x = 0
# compare headers in csv file to req_header list
for req in req_header:
    if search(check_header, req):
        x = x + 1

if x != check_sum:
    sys.exit(f"\nFile must contain required column headers: {req_header}")

# --------------------------------------------- Add User To Groups

with server.auth.sign_in(tableau_auth):

    try:

        req_options = TSC.RequestOptions(pagesize=1000)

        # create usergroups dataframe from source extraction
        usergroups_df = []
        usergroups = pd.read_csv(source_usergroups)
        usergroups = usergroups[usergroups["Group Name"] != "All Users"]
        usergroups_df = pd.DataFrame(usergroups, columns=["Group Name", "User ID"])

        # create users dataframe from source extraction
        source_users_df = []
        source_users_obj = pd.read_excel(source_users)
        source_users_df = pd.DataFrame(
            source_users_obj, columns=["User ID", "User Name"]
        )

        # create users dataframe from migrated users (on destination instance)
        dest_users_df = []
        migrated_users_obj = list(TSC.Pager(server.users, req_options))
        for duser in migrated_users_obj:
            values = [duser.id, duser.name]
            dest_users_df.append(values)
        dest_users_df = pd.DataFrame(dest_users_df, columns=["User ID", "User Name"])

        # merge usergroups and source users joined by User ID
        merge_df = pd.merge(usergroups_df, source_users_df, on=["User ID"])

        # rename User ID to old User ID before we add destination User ID
        merge_df = merge_df.rename(columns={"User ID": "Old User ID"})

        # merge previously merged dataframe and migrated users joined by User Name
        merge_df = pd.merge(merge_df, dest_users_df, on=["User Name"])

        # create log file
        addusertogrouplogfile = os.path.join(
            file_loc, log_file_loc, "AddUserToGroup-Log.xlsx"
        )

        # create output file of final merged dataframe
        outputfile = os.path.join(
            file_loc, export_file_loc, "AddUserToGroup-output.xlsx"
        )
        with pd.ExcelWriter(outputfile) as writer:
            merge_df.to_excel(writer, sheet_name="AddUserToGroup", index=False)

        # load in recently created output file
        input_file = pd.read_excel(outputfile)
        # get migrated groups
        groups_obj = list(TSC.Pager(server.groups, req_options))
        # iterate through output file
        for i in input_file.index:
            group = input_file["Group Name"][i]  # group name
            uid = input_file["User ID"][i]  # user ID
            user = input_file["User Name"][i]  # user name

            # iterate through migrated groups
            for groups in groups_obj:
                if groups.name == group:  # check if migrated group is in output file
                    server.groups.add_user(
                        groups, uid
                    )  # create server object passing groupitem and user ID
            print(f"User {user} added to Group {group}")  # print to console

    except TSC.ServerResponseError as err:
        error = time_log + str(err)
        new_row = {
            "Time Log": time_log,
            "Object Name": usergroups[usergroups["Group Name"]],
            "Script Name": "AddUserToGroup.py",
            "Result": "Failed",
            "Error": str(err),
        }
        log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

with pd.ExcelWriter(addusertogrouplogfile) as writer:
    print(f"\nWriting results to {addusertogrouplogfile}. Please wait.")
    log_df.to_excel(writer, sheet_name="AddUserToGroup", index=False)

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
