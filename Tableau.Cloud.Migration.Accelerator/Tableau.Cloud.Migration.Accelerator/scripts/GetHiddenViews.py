# GetHiddenViews.py reads WorkbookItem objects from TableauServerClient,
# gets a list of hidden views, then stores the list of of hidden views to an Excel file.
# The output file contain the necessary information to set hidden views when using
# the Tableau Migration SDK / CoreMigration.py script.


from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time
import pandas as pd
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables

hidden_view_file = os.path.join(file_loc, "HiddenViewList.csv")

create_file_locations()

config = configparser.ConfigParser()
config.read("config.ini")

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = (
    "This script gets information about hidden views within Workbooks on your site."
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
server.add_http_options({"verify": False})

server.use_server_version()

# -----------------------------------end Session Authentication

# -----------------------------------Get Hidden Views from Workbooks
# This section will:
# Read the Workbook list exported from the GetSourceContent.py script

# Set up base variables
hidden_view_data = []

filtering = input("Are you filtering by project in config.ini? (Y/n) ")

if filtering.casefold() == "Y".casefold():
    project_filter = (
        f'(filter: {{ projectName: "{config["FILTERS"]["MIGRATE_PROJECT"]}" }})'
    )
else:
    project_filter = ""

start_time = time.time()

with server.auth.sign_in(tableau_auth):

    # Build the query
    query = f"""
        query {{
            workbooksConnection {project_filter}{{
                nodes {{
                    luid
                    name
                    views {{
                        luid
                        name
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}"""

    variables = {"first": 10000, "afterToken": None}

    # Send the query
    response_data = server.metadata.paginated_query(query, variables)

    if response_data.get("errors"):
        logging.error(response_data["errors"])

    elif response_data.get("pages"):
        try:
            for page in response_data["pages"]:
                for workbook in page["data"]["workbooksConnection"]["nodes"]:
                    workbook_id = workbook["luid"]
                    view_names = []
                    for view in workbook["views"]:
                        if view["luid"] == "":
                            view_names.append(view["name"])
                    hidden_view_data.append(
                        {"Workbook Id": workbook_id, "Hidden Views": view_names}
                    )

        except Exception as e:
            logging.error(e)

    # Create a DataFrame
    try:
        hidden_view_df = pd.DataFrame(hidden_view_data)

    except Exception as e:
        logging.error(e)

# Output results to file
logging.info(f"Writing results to {hidden_view_file}. Please wait.")
hidden_view_df.to_csv(hidden_view_file, header=True, index=False)

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
    f"Completed {script_name} in {duration}. Please view file {hidden_view_file}"
)
