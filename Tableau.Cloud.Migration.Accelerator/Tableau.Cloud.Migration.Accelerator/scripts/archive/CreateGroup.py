# CreateGroup.py connects to Tableau Server
# reads a csv file, creates a group from the column Group Name
# The csv file must contain a header as the first row
# group_source_file: to import groups
#        The csv file must contain the group name, user id and AD domain (if using Active Directory)
#        The column with the group information must have a column name 'Group Name'. Group Names are case-sensitive
#        If adding users to a group, the file must contain user id (not user name) with column name 'User ID'
#        If creating Active Directory group, the file must also contain the domain name, with column name 'AD Domain'

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import itertools
import time
import pandas as pd
import tableauserverclient as TSC

# -----------------------------------enter session variables here

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will create groups on your site."

# Prompt the user with the script name and description
print(f"\nYou are running {script_name} script. {script_description}")

# Create local or AD group?
# Prompt user for value: 1 (to Create Local Group) or 2 (to Create Active Directory Group)
print("\nWhat type of group(s) are you migrating? \n\t1: Local \n\t2: Active Directory")
group_type = input("\nEnter your choice (1-2): ")

try:
    if group_type == "1" or group_type == "2":
        print(f"\nYou entered {group_type}")
    else:
        print("\nInvalid input. Please enter either 1 or 2.")
except ValueError:
    print("\nInvalid input. Please enter a valid number.")

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


# ------------------------------- CreateGroup
# This section will:
# Read the source csv file, check for column headers
# create the groups


# read csv file
start_time = time.time()
df = pd.read_csv(group_source_file)

# check if csv file has required headers, if not exit. uses group_type to determine if local group or AD group
if group_type == "1":
    req_header = ["Group Name"]
else:
    req_header = ["Group Name", "AD Domain"]

req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(list(df.columns))
check_header = [header.upper() for header in check_header]

x = 0
for req in req_header:
    if search(check_header, req):
        x = x + 1

if x != check_sum:
    sys.exit("\nFile must contain required column headers")

existing_group = []
new_data = []
data = []
ad_data = []

# get only the unique values of the list in csv file
data = list(df["Group Name"].unique())

# if creating AD groups, get unique values in csv file
if group_type == "2":
    ad_data = df[["Group Name", "AD Domain"]].values.tolist()
    # remove duplicates, convert back to a list
    ad_data = list(map(list, list(set(map(tuple, map(list, ad_data))))))

# --------------------------------------------- Create Groups

with server.auth.sign_in(tableau_auth):
    # get list of existing groups
    all_groups, pagination_item = server.groups.get()
    # check whether creating local groups or AD groups. 1 = local group 2 = AD group

    if group_type == "1":
        # create local groups
        for groups in all_groups:
            values = [groups.name]
            existing_group.append(values)
        # results return lists of lists, flatten list
        flat_existing_group = list(itertools.chain(*existing_group))
        # compare existing group with new group list, remove duplicates to avoid error
        temp_data = set(flat_existing_group).symmetric_difference(set(data))
        new_data = list(temp_data)
        if len(new_data) == 0:
            sys.exit("\nAll groups in the file are already in Tableau")
        for k in new_data:
            new_group = TSC.GroupItem(k)
            # optional: set the minimum site role
            new_group.minimum_site_role = TSC.UserItem.Roles.Viewer
            try:
                new_group = server.groups.create(new_group)
                print(f"Creating Local group [{new_group.name}]")
            except Exception as argument:
                f = open(log_file, "a")
                f.write(str(argument))
                f.close()
                continue
    elif group_type == "2":
        # create AD groups
        for groups in all_groups:
            values = [groups.name, groups.domain_name]
            existing_group.append(values)
        # compare existing groups with new group list, remove duplicates to avoid error
        new_data = [x for x in existing_group if x not in ad_data] + [
            x for x in ad_data if x not in existing_group
        ]
        for k in new_data:
            new_group = TSC.GroupItem(k[0], k[1])
            # set the minimum site role
            new_group.minimum_site_role = TSC.UserItem.Roles.Unlicensed
            new_group.license_mode = TSC.GroupItem.LicenseMode.onSync
            try:
                new_group.server.groups.create_AD_group(new_group)
                print(
                    f"Creating AD group [{new_group.name}] from domain [{new_group.domain_name}]"
                )
            except Exception as argument:
                f = open(log_file, "a")
                f.write(str(argument))
                f.close()
                continue

    else:
        sys.exit("\nYou must select a group type: \n\t1: Local \n\t2: Active Directory")

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
