# CreateFavorites.py connects to Tableau Server/Cloud and the Tableau REST API,
# and publishes User Favorites based on the Export/FavoritesList.xlsx file.
#
# The script will find assets by name/content URL and users by username (typically, an email address).
# Due to the nature of publishing favorites via the Tableau REST API, the script
# must execute each type of favorite using a unique API request body.


from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import pandas as pd
import numpy as np
import tableauserverclient as TSC
import openpyxl
import time
from logging_config import *

# -----------------------------------Enter variables

favorites_file = os.path.join(file_loc, "FavoritesList.xlsx")
fav_dest_file = os.path.join(log_file_loc, "Create Favorites Log.xlsx")
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
script_description = "This script will create favorites for users on your site."

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

# -----------------------------------Session Authentication using Tableau Server Client

server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()

# -----------------------------------end Session Authentication

# -----------------------------------Get Favorites List
# This section will:
# Read the Favorites list exported from the GetFavorites.py script
# If you haven't run this script, you do so before executing this script or it will fail.

# Read FavoritesList.xlsx and check if it has the correct headers:
favorites_df = pd.read_excel(favorites_file, sheet_name="Favorites List")
favorites_df = favorites_df.replace(np.nan, None)

# Create DataFrames from manifest.json/ContentInventory.xlsx
user_df = pd.read_excel(manifest_file, sheet_name="User List")
user_df = user_df.replace(np.nan, None)

project_df = pd.read_excel(manifest_file, sheet_name="Project List")
project_df = project_df.replace(np.nan, None)

datasource_df = pd.read_excel(manifest_file, sheet_name="Data Source List")
datasource_df = datasource_df.replace(np.nan, None)

workbook_df = pd.read_excel(manifest_file, sheet_name="Workbook List")
workbook_df = workbook_df.replace(np.nan, None)

view_df = pd.read_excel(manifest_file, sheet_name="View List")
view_df = view_df.replace(np.nan, None)

flow_df = pd.read_excel(manifest_file, sheet_name="Flow List")
flow_df = flow_df.replace(np.nan, None)

# Set up base variables
project = TSC.ProjectItem
datasource = TSC.DatasourceItem
workbook = TSC.WorkbookItem
view = TSC.ViewItem
flow = TSC.FlowItem

item_dict = {
    "projects": project,
    "datasources": datasource,
    "workbooks": workbook,
    "views": view,
    "flows": flow,
}

# check if log file already exists. If not, create it.
if not os.path.exists(fav_dest_file):
    importfile = openpyxl.Workbook()
    importfile.save(fav_dest_file)

# get count of tasks expected to publish
count_fav_source = len(favorites_df)

start_time = time.time()

count_fav = 0

success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):

    all_users = Content.load(ContentItem.users, ContentLocation.destination)

    # iterate through favorites list and create a dataframe of details to import new favorites
    for index, row in favorites_df.iterrows():
        try:
            user_id = row["User Id"]
            target_id = row["Target Id"]
            target_type = row["Target Type"]
            label = row["Label"]

            filtered_user = user_df[user_df["Source Id"] == user_id]
            destination_user_id = filtered_user.iloc[0]["Destination Id"]

            # If user doesn't exist, continue with next favorite
            if not destination_user_id:
                logging.error("Target User not found on destination site. Skipping...")
                continue

            # Get the Destination Id by matching Target Id to Source Id
            if target_type == "project":
                filtered_project = project_df[project_df["Source Id"] == target_id]
                destination_target_id = filtered_project.iloc[0]["Destination Id"]

            elif target_type == "workbook":
                filtered_workbook = workbook_df[workbook_df["Source Id"] == target_id]
                destination_target_id = filtered_workbook.iloc[0]["Destination Id"]

            elif target_type == "view":
                filtered_view = view_df[view_df["Source Id"] == target_id]
                destination_target_id = filtered_view.iloc[0]["Destination Id"]

            elif target_type == "datasource":
                filtered_datasource = datasource_df[
                    datasource_df["Source Id"] == target_id
                ]
                destination_target_id = filtered_datasource.iloc[0]["Destination Id"]

            elif target_type == "flow":
                filtered_flow = flow_df[flow_df["Source Id"] == target_id]
                destination_target_id = filtered_flow.iloc[0]["Destination Id"]

            # If user doesn't exist, continue with next favorite
            if not destination_target_id:
                logging.error(
                    "Target object not found on destination site. Skipping..."
                )
                continue

            else:
                logging.info(
                    f"Creating Favorite for User [{destination_user_id}] for {target_type} [{destination_target_id}]."
                )

                # Get the UserItem from all_users
                for user in all_users:
                    if user.id == destination_user_id:
                        user_item = user

                if user_item:

                    # Get the ContentItem object from content_list
                    content_list = Content.load(
                        f"{target_type}s", ContentLocation.destination
                    )

                    for item in content_list:
                        if item.id == destination_target_id:
                            content_item = item

                    try:
                        server.favorites.add_favorite(
                            user_item, target_type, content_item
                        )

                        status = "SUCCESS"

                        logging.info(
                            f"Success. Favorite for User [{user_item.id}] for {target_type} [{content_item.name}] created."
                        )

                        count_fav += 1

                        time.sleep(1)

                    except Exception as e:
                        status = "ERROR"
                        logging.error(f"\tFailed to create Favorite. Error: {e}")

                    time.sleep(0.5)

        except Exception as e:
            status = "ERROR"
            logging.error(e)

        # Logging Details
        results = {
            "Time Log": time_log,
            "Script Name": script_name,
            "User Id": destination_user_id,
            "Favorite Type": target_type,
            "Target Id": destination_target_id,
            "Status": status,
        }

        if status == "SUCCESS":
            logging.info(results)
            row["Status"] = "SUCCESS"
            success_list.append(results)

        else:
            logging.error(results)
            row["Status"] = "ERROR"
            error_list.append(results)

# Write results to file for review
success_df = pd.DataFrame(success_list)
error_df = pd.DataFrame(error_list)

logging.info(f"\nWriting results to file...")
with pd.ExcelWriter(fav_dest_file) as writer:
    success_df.to_excel(writer, sheet_name="Favorites Created", index=False)
    error_df.to_excel(writer, sheet_name="Favorites Errored", index=False)

# Test function to write-back to file with the new status column
with pd.ExcelFile(favorites_file) as writer:
    favorites_df.to_excel(writer, sheet_name="Favorites List", index=False)

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
\tFavorites in import file: {count_fav_source}.
\tFavorites created: {count_fav}.
Please check {fav_dest_file} for any errors."""
)
