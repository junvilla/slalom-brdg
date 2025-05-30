# GetUsers.py connects to Tableau Server
# gets users then prints the list of users in csv
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
# use for Importing Users, Groups, Projects
user_dest_file = os.path.join(file_loc, export_file_loc, "UserList.xlsx")

create_file_locations()

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about the users on your site."

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

# -------------------------------end Session Authentication

# ------------------------------- Get Users
# This section will:
# TSC User method to query Tableau and get a list of users.
# Save the list of users in a dataframe
# write to csv file

# empty array to populate users from server.user.get
data = []

# for csv file to import users
password = ""
display_name = ""
license_level = "Viewer"
admin_level = "None"
publishing = 0

start_time = time.time()

with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)
    all_users = list(TSC.Pager(server.users, req_options))
    for user in all_users:
        values = [user.id, user.name, user.email, user.site_role, ""]
        data.append(values)
        print("\n")
        print(f"Extracting user: {user.name} on ID: {user.id}")

df = pd.DataFrame(
    data, columns=["User ID", "User Name", "User Email", "Site Role", "Migrate?"]
)
# save to csv

(
    df["Password"],
    df["Display Name"],
    df["License Level"],
    df["Admin Level"],
    df["Publishing"],
) = [password, display_name, license_level, admin_level, publishing]

df.to_csv(
    file_loc + "UserList.csv",
    columns=[
        "User ID",
        "User Name",
        "Password",
        "Display Name",
        "License Level",
        "Admin Level",
        "Publishing",
    ],
    header=False,
    index=False,
)

with pd.ExcelWriter(user_dest_file) as writer:
    print(f"\nWriting results to {user_dest_file}. Please wait.")
    df.to_excel(writer, sheet_name="User List", header=True, index=False)

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

print(f"\nCompleted {script_name} in {duration}. Please view file {user_dest_file}.")
