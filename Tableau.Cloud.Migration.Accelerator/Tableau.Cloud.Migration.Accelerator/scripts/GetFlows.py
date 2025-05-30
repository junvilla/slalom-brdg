from datetime import time
import time
import pandas as pd
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables
# File location for Exporting Schedules metadata
flow_dest_file = os.path.join(file_loc, "FlowList.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will get Flows from your site."

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

flow_data = []

with server.auth.sign_in(tableau_auth):

    all_flows = Content.load(ContentItem.flows, ContentLocation.source)

    for flow in all_flows:
        # Populate the data connections for the Flow
        server.flows.populate_connections(flow)

        logging.info(f"Getting Flow: {flow.name} [{flow.id}]")
        flow_id = flow.id
        flow_name = flow.name
        flow_owner_id = flow.owner_id
        flow_project_id = flow.project_id
        flow_project_name = flow.project_name
        flow_description = flow.description
        flow_content_url = flow.webpage_url
        flow_connections = []

        for connection in flow.connections:
            connection_id: str = connection.id
            connection_type: str = connection._connection_type
            datasource_id: str = connection.datasource_id
            datasource_name: str = connection.datasource_name
            server_address: str = connection.server_address
            server_port: str = connection.server_port
            connection_username: str = connection.username
            connection_password: str = connection.password
            embed_password: bool = connection.embed_password
            connection_credentials: str = connection.connection_credentials
            query_tagging: bool = connection.query_tagging

            connection_values = [
                connection_id,
                connection_type,
                datasource_id,
                datasource_name,
                server_address,
                server_port,
                connection_username,
                connection_password,
                embed_password,
                connection_credentials,
                query_tagging,
            ]

            flow_connections.append(connection_values)

        values = [
            flow_id,
            flow_name,
            flow_owner_id,
            flow_project_id,
            flow_project_name,
            flow_description,
            flow_content_url,
            flow_connections,
        ]

        flow_data.append(values)

flow_df = pd.DataFrame(
    flow_data,
    columns=[
        "Flow Id",
        "Flow Name",
        "Owner Id",
        "Project Id",
        "Project Name",
        "Description",
        "Content Url",
        "Connections",
    ],
)

# Output results to file
logging.info(f"\nWriting results to {flow_dest_file}. Please wait.")
with pd.ExcelWriter(flow_dest_file) as writer:
    flow_df.to_excel(writer, sheet_name="Flow List", header=True, index=False)

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

logging.info(
    f"\nCompleted {script_name} in {duration}. Please view file {flow_dest_file}"
)
