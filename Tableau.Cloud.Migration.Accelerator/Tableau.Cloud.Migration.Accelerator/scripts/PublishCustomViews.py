# PublishCustomViews.py connects to Tableau Cloud using the Tableau REST API,
# and publishes Custom Views based on the Import/CustomView_Import.csv file.

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import ast
import time
import pandas as pd
import numpy as np
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables
cv_import = os.path.join(file_loc, "CustomViewList.xlsx")
log_file = os.path.join(log_file_loc, "Create Custom Views Log.xlsx")
manifest_file = os.path.join(manifest_loc, "manifest.xlsx")

# check if manifest file exists. If not, exit program.
if not os.path.exists(manifest_file):
    sys.exit(
        """ERROR: 'manifest.xlsx' not found.
        Please run script 'GetDestinationContent.py' before running this script."""
    )

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will create Custom Views for users on your site."

# Prompt the user with the script name and description
logging.info(f"You are running the {script_name} script. {script_description}")

# call the perform_action function with dynamic environment names
logging.info(f"Begin {script_name}. This might take several minutes.\n")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

# -----------------------------------Session Authentication using Tableau Server Client
server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()

# -----------------------------------end Session Authentication

# This section will:
# Read the Custom Views list exported from the GetCustomViews.py script
# If you haven't run this script, you do so before executing this script or it will fail.

# Read CustomView_Import.csv and check if it has the correct headers:
customview_df = pd.read_excel(cv_import, sheet_name="Custom View List")

# Read CustomView_Users_Import.csv and check if it has the correct headers:
cv_users = pd.read_excel(cv_import, sheet_name="Default User List")

# Merge the two data frames by Custom View Name and Workbook Name
customview_df = pd.merge(
    customview_df,
    cv_users[["Custom View Id", "Default Users"]],
    on="Custom View Id",
    how="left",
)

# Get a count of custom views to migrate from the source
count_cv_source = len(customview_df)
count_cv = 0

# Set the NaN values to None
customview_df = customview_df.replace(np.nan, None)

# Create DataFrames from manifest/ContentInventory
user_df = pd.read_excel(manifest_file, sheet_name="User List")
user_df = user_df.replace(np.nan, None)

workbook_df = pd.read_excel(manifest_file, sheet_name="Workbook List")
workbook_df = workbook_df.replace(np.nan, None)

start_time = time.time()

customview_data = []
success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):
    # pull necessary API authentication values from TSC Authentication
    auth_token = server._auth_token
    api_version = server.server_info.get().rest_api_version
    site_luid = server.site_id

    # Load site content necessary for publishing Custom Views
    all_users = Content.load(ContentItem.users, ContentLocation.destination)
    all_workbooks = Content.load(ContentItem.workbooks, ContentLocation.destination)
    all_views = Content.load(ContentItem.views, ContentLocation.destination)

    # -----------------------------------Get Custom Views List

    # iterate through Custom Views list and create a dataframe of details to import new Custom Views
    for index, row in customview_df.iterrows():
        owner_id = row["Owner Id"]
        cv_name = row["Custom View Name"]
        view_id = row["View Id"]
        workbook_id = row["Workbook Id"]
        shared = row["Shared"]
        cv_filename = row["File Name"]
        default_users = row["Default Users"]

        filtered_user = user_df[user_df["Source Id"] == owner_id]
        destination_owner_id = filtered_user.iloc[0]["Destination Id"]

        # If owner/user doesn't exist, continue with next custom view
        if not destination_owner_id:
            logging.error("Target Owner not found on destination site. Skipping...")
            continue

        else:
            # Get the Destination Id by matching Target Id to Source Id
            filtered_workbook = workbook_df[workbook_df["Source Id"] == workbook_id]
            destination_workbook_id = filtered_workbook.iloc[0]["Destination Id"]

            # If workbook doesn't exist, continue with next custom view
            if not destination_workbook_id:
                logging.error(
                    "Target Workbook not found on destination site. Skipping..."
                )
                continue

            else:
                logging.info(
                    f"Publishing Custom View [{cv_name}] for Owner [{destination_owner_id}]..."
                )

                for user in all_users:
                    if user.id == destination_owner_id:
                        owner_item = user

                for workbook in all_workbooks:
                    if workbook.id == destination_workbook_id:
                        workbook_item = workbook

                cv_item = TSC.CustomViewItem(name=cv_name)
                cv_item.shared = shared
                cv_item.owner = owner_item
                # cv_item.workbook = workbook_item
                cv_item._workbook = workbook_item

                cv_file = os.path.join(cv_file_loc, cv_filename)

                try:
                    destination_cv = server.custom_views.publish(cv_item, cv_file)

                    logging.info(f"Success. Custom View [{cv_name}] published.")
                    logging.info(f"Destination Custom View Id: {destination_cv.id}")

                    status = "SUCCESS"
                    count_cv += 1

                    ### Set Custom View as Default for Users
                    if default_users == None or len(default_users) == 0:
                        logging.info(
                            "No users have set this Custom View as Default. Continuing..."
                        )
                        continue

                    else:
                        logging.info(
                            "Setting Custom View as Default for users. Please wait."
                        )

                        # Convert the Default Users column to a list from a string
                        default_users = ast.literal_eval(default_users)

                        # Create a list for the destination User Ids
                        destination_user_ids = []

                        for user in default_users:
                            # Get the Destination User by matching User Id to Source Id
                            filtered_user = user_df[user_df["Source Id"] == user]
                            destination_user_id = filtered_user.iloc[0][
                                "Destination Id"
                            ]
                            destination_user_ids.append(destination_user_id)

                        # Send data to the function to process the API request
                        cvd_status, cvd_response = customViews.users.setDefault(
                            portal_url,
                            api_version,
                            site_luid,
                            auth_token,
                            destination_cv.id,
                            destination_user_ids,
                        )
                        logging.info(
                            f"Set as Default View for Users... Result: {cvd_response}"
                        )

                        time.sleep(1)

                except Exception as e:
                    status = "ERROR"
                    logging.error(f"Failed to publish Custom View. Error: {e}.")

                results = {
                    "Time Log": time_log,
                    "Script Name": script_name,
                    "Destination Owner Id": destination_owner_id,
                    "Custom View Name": cv_name,
                    "Status": status,
                }

        if status == "SUCCESS":
            logging.info(results)
            success_list.append(results)

        else:
            logging.error(results)
            error_list.append(results)

# Write results to file for review
success_df = pd.DataFrame(success_list)
error_df = pd.DataFrame(error_list)

logging.info(f"\nWriting results to file...")
with pd.ExcelWriter(log_file) as writer:
    success_df.to_excel(writer, sheet_name="CustomViews Published", index=False)
    error_df.to_excel(writer, sheet_name="CustomViews Errored", index=False)

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

logging.info(f"Completed {script_name} in {duration}. Please view file {log_file}.")

# Print final script results
logging.info(
    f"""Completed {script_name} in {duration}.
    Custom Views in import file: {count_cv_source}
    Custom Views published: {count_cv}
    Please check {log_file} for any errors."""
)
