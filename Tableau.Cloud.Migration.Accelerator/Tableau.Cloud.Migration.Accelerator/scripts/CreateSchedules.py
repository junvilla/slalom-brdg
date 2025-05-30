"""
Create Schedules (Migration process)

While Schedules are handled differently in Tableau Cloud, they still exist as an essential part of orchestrating tasks.
This script will help create any schedules that don't already exist as part of Tableau Cloud's default ecosystem.

Requirements prior to migrating schedules:
    Schedules extracted from source environment

"""

import pandas as pd
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time as tme
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables
# File location for writing Schedule metadata
schedule_dest_file = os.path.join(file_loc, log_file_loc, "Create Schedule Log.xlsx")

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will create Schedules for your site."

# Prompt the user with the script name and description
logging.info(f"\nYou are running {script_name} script. {script_description}")

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
start_time = tme.time()

# read schedule import source file file
all_schedules = Content.load(ContentItem.schedules, ContentLocation.source)

# get count of subscriptions expected to publish
count_sch_source = len(all_schedules)

# counter for schedules created
count_sub = 0

# create a list to store current schedule ids/names
# we don't want to create duplicates
current_sch_df = []
success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)

    # Get a list of current Schedules already in Tableau Server
    current_schedules = list(TSC.Pager(server.schedules, request_opts=req_options))

    # iterate through schedules in the import file
    for schedule in all_schedules:
        try:
            schedule_name = schedule.name
            priority = schedule.priority
            schedule_type = schedule.schedule_type
            exec_order = schedule.execution_order
            interval_item = schedule.interval_item

            # check if a schedule by that name already exists, if so, skip it
            for sch in current_schedules:
                if sch.name == schedule_name:
                    logging.info(
                        f"Schedule of name [{schedule_name}] already exists. Skipping..."
                    )
                    continue
                else:
                    logging.info(f"Creating new Schedule [{schedule_name}]")
                    # build the final schedule_item class
                    schedule_item = TSC.ScheduleItem(
                        schedule_name,
                        priority,
                        schedule_type,
                        exec_order,
                        interval_item,
                    )

                    # Create the new subscription on the site you are logged in.
                    server.schedules.create(schedule_item)

                    count_sch = count_sch + 1

                    # Logging Details
                    status = "SUCCESS"

        # Write errors to log file
        except Exception as e:
            status = "ERROR"
            logging.error(e)

        results = {
            "Time Log": time_log,
            "Object Name": schedule_type,
            "Script Name": script_name,
            "Schedule Name": schedule_name,
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
with pd.ExcelWriter(schedule_dest_file) as writer:
    success_df.to_excel(writer, sheet_name="Schedules Created", index=False)
    error_df.to_excel(writer, sheet_name="Schedules Errored", index=False)

# Calculate script execution time
end_time = tme.time()
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
\tSchedules in import file: {count_sch_source}.
\tSchedules created: {count_sub}.
Please check {schedule_dest_file} for any errors."""
)
