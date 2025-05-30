# GetCustomViews.py connects to Tableau Server/Cloud and the Tableau REST API,
# gets a list of Custom Views, then prints the list of Custom Views in csv/Excel
# the output files contain the necessary information to import Custom Views using the Tableau REST API

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time
import pandas as pd
import tableauserverclient as TSC

# -----------------------------------Enter variables
# cv_dest_file = os.path.join(file_loc, "CustomViewList.xlsx")

create_file_locations()

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = (
    "This script gets information about user Custom Views on your site."
)

# Prompt the user with the script name and description
logging.info(f"You are running the {script_name} script. {script_description}")

# call the perform_action function with dynamic environment names
logging.info(f"Begin {script_name}. This might take several minutes.")

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

start_time = time.time()

# Empty arrays to populate responses from GET List Custom Views API call
# and users with a Custom View set as their default view
cv_list = []
cv_users = []

with server.auth.sign_in(tableau_auth):

    request_opts = TSC.RequestOptions(pagesize=1000)

    # pull necessary API authentication values from TSC Authentication
    auth_token = server._auth_token
    api_version = server.server_info.get().rest_api_version
    site_luid = server.site_id

    logging.info("Getting Custom Views for site. Please wait.")
    all_views = list(TSC.Pager(server.custom_views, request_opts))

    # iterate through the list of Custom Views returned
    for view in all_views:
        cv_id = view.id
        cv_name = view.name
        shared = view.shared
        view_id = view.view.id
        workbook_id = view.workbook.id
        owner_id = view.owner.id

        # normalize values to be appended as new rows in the data list
        cv_data = [
            cv_id,
            cv_name,
            shared,
            view_id,
            workbook_id,
            owner_id,
        ]

        logging.info(f"Extracting data for Custom View [{cv_id}][{cv_name}]")

        # write Custom Views to the data list
        cv_list.append(cv_data)

        # Get users with Custom View as default
        logging.info(
            f"Extracting Users with Custom View [{cv_id}][{cv_name}] set as Default."
        )

        user_list = customViews.users.getDefault(
            portal_url, api_version, site_luid, auth_token, cv_id
        )

        # Set user_list to None if no results/users are returned
        if len(user_list) == 0:
            user_list = None

        # Normalize values to be appended as new rows in the cv_users list
        user_data = [
            cv_id,
            cv_name,
            user_list,
        ]

        # write users to the cv_users list
        cv_users.append(user_data)

# convert the data list to a dataframe
cv_df = pd.DataFrame(
    cv_list,
    columns=[
        "Custom View Id",
        "Custom View Name",
        "Shared",
        "View Id",
        "Workbook Id",
        "Owner Id",
    ],
)

# convert the cv_users list to a dataframe
cv_user_df = pd.DataFrame(
    cv_users,
    columns=[
        "Custom View Id",
        "Custom View Name",
        "Default Users",
    ],
)

# Write the dataframe to the CustomViewList.xlsx Excel file
with pd.ExcelWriter(cv_dest_file) as writer:
    cv_df.to_excel(writer, sheet_name="Custom View List", header=True, index=False)
    cv_user_df.to_excel(
        writer, sheet_name="Default User List", header=True, index=False
    )

end_time = time.time()
seconds = end_time - start_time

if seconds < 60:
    duration = f"{round(seconds,2)} second(s)"
elif seconds > 60 and seconds < 3600:
    duration_s = round(seconds % 60, 2)
    duration_m = round(seconds / 60)
    duration = f"{duration_m} minute(s) and {duration_s} second(s)"
elif seconds >= 3600:
    duration_m = round((seconds % 3600) / 60, 2)
    duration_h = round(seconds / 3600)
    duration = f"{duration_h} hour(s) and {duration_m} minute(s)"

# Print final script results
logging.info(
    f"""
Completed {script_name} in {duration}.
\tTotal Custom Views: {len(cv_df)}
\tTotal Users with Custom Views as Default: {len(cv_user_df)}
Please view file: {cv_dest_file}
"""
)
