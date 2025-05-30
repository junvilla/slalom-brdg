# PublishFlows.py connects to Tableau Cloud using the Tableau REST API,
# and publishes Tableau Prep Flows using the FlowList.xlsx file.

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import ast
import time
import pandas as pd
import numpy as np
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables
flow_import = os.path.join(file_loc, "FlowList.xlsx")
log_file = os.path.join(log_file_loc, "Create Flows Log.xlsx")
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
script_description = "This script will publish Tableau Prep Flows on your site."

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
# Read the Flows list exported from the GetFlows.py script
# If you haven't run this script, you must do so before executing this script or it will fail.

# Read FlowList.xlsx and check if it has the correct headers:
flow_df = pd.read_excel(flow_import, sheet_name="Flow List")

# Get a count of Flows to migrate from the source
count_flows_source = len(flow_df)
count_flows = 0

# Set the NaN values to None
flow_df = flow_df.replace(np.nan, None)

# Create DataFrames from manifest/ContentInventory
user_df = pd.read_excel(manifest_file, sheet_name="User List")
user_df = user_df.replace(np.nan, None)

project_df = pd.read_excel(manifest_file, sheet_name="Project List")
project_df = project_df.replace(np.nan, None)

datasource_df = pd.read_excel(manifest_file, sheet_name="Data Source List")
datasource_df = datasource_df.replace(np.nan, None)

start_time = time.time()

flow_data = []
success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):

    # ----------------------------------- Publish Flows
    # iterate through Flows list and create a dataframe of details to import new Flows
    for index, row in flow_df.iterrows():
        owner_id = row["Owner Id"]
        flow_name = row["Flow Name"]
        project_id = row["Project Id"]
        flow_filename = row["File Name"]
        connections = ast.literal_eval(row["Connections"])

        filtered_user = user_df[user_df["Source Id"] == owner_id]
        destination_owner_id = filtered_user.iloc[0]["Destination Id"]

        # If owner/user doesn't exist, continue with next Flow
        if not destination_owner_id:
            logging.error("Target Owner not found on destination site. Skipping...")
            continue

        else:
            # Get the Destination Id by matching Target Id to Source Id
            filtered_project = project_df[project_df["Source Id"] == project_id]
            destination_project_id = filtered_project.iloc[0]["Destination Id"]

            # If Project doesn't exist, continue with next Flow
            if not destination_project_id:
                logging.error(
                    "Target Project not found on destination site. Skipping..."
                )
                continue

            else:
                logging.info(
                    f"Publishing Flow [{flow_name}] for Owner [{destination_owner_id}]..."
                )

                flow_item = TSC.FlowItem(
                    project_id=destination_project_id, name=flow_name
                )

                flow_item.owner_id = destination_owner_id
                flow_file = os.path.join(flow_file_loc, flow_filename)

                """
                connection_list = []

                for connection in connections:
                    if connection[4] != "":
                        connection_item = TSC.ConnectionItem()
                        connection_item.server_address = connection[4]
                        connection_item.server_port = connection[5]
                        connection_item.username = None
                        connection_item.password = None
                        connection_item.embed_password = False
                        connection_item.connection_credentials = None

                        if connection[10] == "True":
                            connection_item.query_tagging = True
                        else:
                            connection_item.query_tagging = False

                        if connection[6] != "":
                            if connection[8] == "True":
                                embed = True
                            else:
                                embed = False

                            connection_item.connection_credentials = TSC.ConnectionCredentials(
                                name=connection[6],
                                embed=embed,
                                password=connection[7],
                                oauth=False
                            )
                        
                        connection_list.append(connection_item)
                """

                try:
                    destination_flow = server.flows.publish(
                        flow_item,
                        flow_file,
                        mode=TSC.Server.PublishMode.CreateNew,
                        connections=None,
                    )

                    logging.info(
                        f"Success. Flow [{flow_item.name}] published to Project [{flow_item.project_name}]"
                    )
                    logging.info(f"Destination Flow Id: {destination_flow.id}")

                    status = "SUCCESS"

                    count_flows += 1

                except Exception as e:
                    status = "ERROR"
                    logging.info(f"Failed to publish Flow. Error: {e}.")

                results = {
                    "Time Log": time_log,
                    "Script Name": script_name,
                    "Destination Owner Id": destination_owner_id,
                    "Flow Name": flow_name,
                    "Destination Project Id": destination_project_id,
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
    success_df.to_excel(writer, sheet_name="Flows Published", index=False)
    error_df.to_excel(writer, sheet_name="Flows Errored", index=False)

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
    Flows in import file: {count_flows_source}
    Flows created: {count_flows}
    Please check {log_file} for any errors."""
)
