"""
Create Tasks (Migration process)

Tasks are scheduled jobs run by Tableau Cloud to update workbooks and data sources.

Requirements prior to migrating Tasks:
    Projects are migrated
    Data sources are migrated
    Workbooks are migrated
    Schedules exist in source environment (Tableau Server only)
    GetSchedules.py has been run
    GetDestinationContent.py has been run

"""

import pandas as pd
import numpy as np
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import sys
import time
import openpyxl
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables
# File location for Exporting Tasks metadata
task_log_file = os.path.join(log_file_loc, "Create Tasks Log.xlsx")
task_import = os.path.join(file_loc, "TaskList.xlsx")
manifest_file = os.path.join(manifest_loc, "manifest.xlsx")

# check if manifest file exists. If not, exit program.
if not os.path.exists(manifest_file):
    sys.exit(
        """ERROR: 'manifest.xlsx' not found.
        Please run script 'GetDestinationContent.py' before running this script."""
    )

# check if import file already exists. If not, create it.
if not os.path.exists(task_log_file):
    importfile = openpyxl.Workbook()
    importfile.save(task_log_file)

# check if import file already exists. If not, create it.
if not os.path.exists(task_import):
    importfile = openpyxl.Workbook()
    importfile.save(task_import)

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will migrate Tasks to your Tableau Cloud site."

# Prompt the user with the script name and description
logging.info(f"You are running {script_name} script. {script_description}")

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

# read TaskList and manifest files
task_df = pd.read_excel(task_import, sheet_name="Task List")
task_df = task_df.replace(np.nan, None)

# Create DataFrames from manifest.json/ContentInventory.xlsx
workbook_df = pd.read_excel(manifest_file, sheet_name="Workbook List")
workbook_df = workbook_df.replace(np.nan, None)

datasource_df = pd.read_excel(manifest_file, sheet_name="Data Source List")
datasource_df = datasource_df.replace(np.nan, None)

# get count of tasks expected to publish
count_task_source = len(task_df)

# check if csv file has required headers, if not exit
req_header = [
    "Task Type",
    "Priority",
    "Target Type",
    "Target Id",
    "Schedule Id",
]

req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(task_df.columns)
check_header = [header.upper() for header in check_header]

x = 0

for req in req_header:
    if search(check_header, req):
        x = x + 1
if x != check_sum:
    sys.exit("File must contain required column headers.")

# counter for tasks created
count_task = 0

success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):

    # pull necessary API authentication values from TSC Authentication
    auth_token = server._auth_token
    api_version = server.server_info.get().rest_api_version
    site_luid = server.site_id

    req_options = TSC.RequestOptions(pagesize=1000)

    for index, row in task_df.iterrows():

        try:
            destination_target_id = None

            task_type = row["Task Type"]  # define the type of task to create
            if task_type == "extractRefresh":
                task_type = "FullRefresh"
            else:
                task_type = "IncrementalRefresh"

            target_id = row["Target Id"]  # used to acquire new target Id
            target_type = row["Target Type"]  # Determine target type of refresh task

            # schedule id from Tableau Server. Needed if migrating to Tableau Cloud.
            schedule_id = row["Schedule Id"]

            # set Target based on Subscription Target Type
            if target_type == "workbook":
                # Get the Destination Id by matching Target Id to Source Id
                workbook_id = workbook_df[workbook_df["Source Id"] == target_id]
                destination_target_id = workbook_id.iloc[0]["Destination Id"]

            elif target_type == "datasource":
                # Get the Destination Id by matching Target Id to Source Id
                datasource_id = datasource_df[datasource_df["Source Id"] == target_id]
                destination_target_id = datasource_id.iloc[0]["Destination Id"]

            # Check if target destination ID was found. If not, skip the task.
            if not destination_target_id:
                logging.error(
                    "Target object not found on destination site. Skipping..."
                )
                continue

            else:
                # Create the new Task
                schedule_element = schedules.get(schedule_id)

                cloud_task_item = tasks.request.create(
                    task_type, target_type, destination_target_id, schedule_element
                )

                logging.info(
                    f"\nAttempting to create Task [{task_type}] for target [{target_type}][{destination_target_id}]."
                )
                result, message = tasks.create(
                    portal_url, api_version, site_luid, auth_token, cloud_task_item
                )

                if result == "Success":
                    status = "SUCCESS"
                    logging.info(
                        f"Task [{task_type}] for target [{target_type}][{destination_target_id}] successfully created."
                    )
                    count_task += 1

                elif result == "Error":
                    status = "ERROR"
                    logging.error(f"\tFailed to create task. Error message: {message}")

        # Write errors to log file
        except Exception as e:
            status = "ERROR"
            logging.error(e)

        results = {
            "Time Log": time_log,
            "Script Name": script_name,
            "Target Id": destination_target_id,
            "Target Type": target_type,
            "Task Type": task_type,
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
with pd.ExcelWriter(task_log_file) as writer:
    success_df.to_excel(writer, sheet_name="Tasks Created", index=False)
    error_df.to_excel(writer, sheet_name="Tasks Errored", index=False)

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

# Log final script results
logging.info(
    f"""
Completed {script_name} in {duration}.
\tTasks in import file: {count_task_source}.
\tTasks created: {count_task}.
Please check {task_log_file} for any errors.
    """
)
