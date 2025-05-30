"""
Create Subscriptions (Migration process)

Subscriptions are emails sent to users based on views, whether a view has changed or not to inform users to keep
track of workbooks.

Requirements prior to migrating subscriptions:
    Projects are migrated
    Users are migrated
    Workbooks are migrated
    Views are migrated
    Schedules exist
"""

import pandas as pd
import numpy as np
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import sys
import time
import tableauserverclient as TSC
import openpyxl
from logging_config import *

# -----------------------------------Enter variables
# File location for Exporting Schedules metadata
subscription_dest_file = os.path.join(log_file_loc, "CreateSubscriptionLog.xlsx")
subscription_import = os.path.join(file_loc, "SubscriptionList.xlsx")
manifest_file = os.path.join(manifest_loc, "manifest.xlsx")

# check if manifest file exists. If not, exit program.
if not os.path.exists(manifest_file):
    sys.exit(
        """ERROR: 'manifest.xlsx' not found.
        Please run script 'GetDestinationContent.py' before running this script."""
    )

# check if import file already exists. If not, create it.
if not os.path.exists(subscription_import):
    importfile = openpyxl.Workbook()
    importfile.save(subscription_import)

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will create subscriptions to your site."

# Prompt the user with the script name and description
logging.info(f"You are running {script_name} script. {script_description}")

# Creating on Server or Cloud ?
# Prompt user for value: 1 (create on Server) or 2 (create on Cloud)
print("\nAre you creating subscriptions on Tableau Server or Tableau Cloud?")
print("1) Tableau Server \n2) Tableau Cloud")
dest_env = input("Enter your choice (1-2): ")

try:
    if dest_env == "1" or dest_env == "2":
        print(f"\nYou entered: {dest_env}")
    else:
        print("\nInvalid input. Please enter either '1' or '2'.")
except ValueError:
    print("\nInvalid input. Please enter a valid response.")

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

# -------------------------------end Session Authentication
start_time = time.time()

# Read the SubscriptionList.csv file
subscription_df = pd.read_excel(subscription_import, sheet_name="Subscription List")
subscription_df = subscription_df.replace(np.nan, None)
subscription_df = subscription_df.replace("TRUE", True)
subscription_df = subscription_df.replace("FALSE", False)

# Create DataFrames from manifest/ContentInventory
user_df = pd.read_excel(manifest_file, sheet_name="User List")
user_df = user_df.replace(np.nan, None)

workbook_df = pd.read_excel(manifest_file, sheet_name="Workbook List")
workbook_df = workbook_df.replace(np.nan, None)

view_df = pd.read_excel(manifest_file, sheet_name="View List")
view_df = view_df.replace(np.nan, None)

# get count of subscriptions expected to publish
count_sub_source = len(subscription_df.index)

# check if csv file has required headers, if not exit
req_header = [
    "Attach Image",
    "Attach PDF",
    "Message",
    "Schedule Id",
    "Schedule Name",
    "Send If View Empty",
    "Subject",
    "Target Id",
    "Target Type",
    "User Id",
]

req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(subscription_df.columns)
check_header = [header.upper() for header in check_header]

x = 0

for req in req_header:
    if search(check_header, req):
        x = x + 1
if x != check_sum:
    sys.exit("File must contain required column headers")

# counter for subscriptions created
count_sub = 0

success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):

    # pull necessary API authentication values from TSC Authentication
    auth_token = server._auth_token
    api_version = server.server_info.get().rest_api_version
    site_luid = server.site_id

    req_options = TSC.RequestOptions(pagesize=1000)

    for index, row in subscription_df.iterrows():

        target_id = row["Target Id"]
        user_id = row["User Id"]
        schedule_id = row["Schedule Id"]

        target_type = row["Target Type"]  # View/Workbook
        subject = row["Subject"]
        message = row["Message"]
        attach_image = row["Attach Image"]
        attach_pdf = row["Attach PDF"]
        send_if_view_empty = row["Send If View Empty"]
        schedule_name = row["Schedule Name"]

        try:
            # Get the Destination User by matching User Id to Source Id
            filtered_user = user_df[user_df["Source Id"] == user_id].reset_index(
                drop=True
            )
            destination_user_id = filtered_user.iloc[0]["Destination Id"]

            # If user doesn't exist, continue with next subscription
            if not destination_user_id:
                logging.error("Target User not found on destination site. Skipping...")
                continue

            else:
                # set Target based on Subscription Target Type
                if target_type == "Workbook":
                    # Get the Destination Id by matching Target Id to Source Id
                    filtered_workbook = workbook_df[
                        workbook_df["Source Id"] == target_id
                    ].reset_index(drop=True)
                    destination_target_id = filtered_workbook.iloc[0]["Destination Id"]

                elif target_type == "View":
                    # Get the Destination Id by matching Target Id to Source Id
                    filtered_view = view_df[
                        view_df["Source Id"] == target_id
                    ].reset_index(drop=True)
                    destination_target_id = filtered_view.iloc[0]["Destination Id"]

                # If target object doesn't exist, continue with next subscription
                if not destination_target_id:
                    logging.error(
                        "Target object not found on destination site. Skipping..."
                    )
                    continue

                else:
                    # create target item to create subscription target
                    target = TSC.Target(destination_target_id, target_type)
                    new_sub = TSC.SubscriptionItem(
                        subject, schedule_id, destination_user_id, target
                    )

                    # (Optional) Set other fields. Any of these can be added or removed.
                    if attach_image:
                        new_sub.attach_image = True
                    if attach_pdf:
                        new_sub.attach_pdf = True
                    if send_if_view_empty:
                        new_sub.send_if_view_empty = True
                    new_sub.message = message
                    new_sub.subject = subject

                    # Create the new subscription on the site you are logged in.

                    ###-------------------------------TABLEAU SERVER SUBSCRIPTION CREATION
                    # ---------------------------------------------------------------------
                    if dest_env == "1":
                        logging.info(
                            f"""Attempting to create Subscription for User [{destination_user_id}]
                            to {target_type} [{destination_target_id}]."""
                        )
                        server.subscriptions.create(new_sub)
                        count_sub += 1

                    ###-------------------------------TABLEAU CLOUD SUBSCRIPTION CREATION
                    # --------------------------------------------------------------------
                    elif dest_env == "2":
                        schedule_element = schedules.get(schedule_id)
                        cloud_sub_item = subscriptions.request.create(
                            new_sub, schedule_element
                        )

                        logging.info(
                            f"""
Attempting to create Subscription for User [{destination_user_id}]
to {target_type} [{destination_target_id}]."""
                        )
                        result, message = subscriptions.create(
                            portal_url,
                            api_version,
                            site_luid,
                            auth_token,
                            cloud_sub_item,
                        )

                        if result == "Success":
                            status = "SUCCESS"
                            logging.info(
                                f"""Subscription for User [{destination_user_id}]
successfully created to {target_type} [{destination_target_id}]."""
                            )
                            count_sub += 1

                        elif result == "Error":
                            status = "ERROR"
                            logging.error(
                                f"\tFailed to create subscription. Error message: {message}"
                            )

                    time.sleep(1)

        except Exception as e:
            status = "ERROR"
            logging.error(e)

        results = {
            "Time Log": time_log,
            "Script Name": script_name,
            "Target Id": target_id,
            "Target Type": target_type,
            "User Id": user_id,
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
with pd.ExcelWriter(subscription_dest_file) as writer:
    success_df.to_excel(writer, sheet_name="Subscriptions Created", index=False)
    error_df.to_excel(writer, sheet_name="Subscriptions Errored", index=False)

# Calculate script execution time
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
    f"""Completed {script_name} in {duration}.
    Subscriptions in import file: {count_sub_source}.
    Subscriptions created: {count_sub}.
    Please check {subscription_dest_file} for any errors."""
)
