# This will download all Custom View data files (in JSON format)
# to the CV directory, based on CustomViews_to_Download file
import sys
import time
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download Custom Views from your site."

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

# ------------------------------- Get Workbook
start_time = time.time()

# create necessary folders
create_file_locations()

file_extension = ".json"

# check if directory to download custom views exist, if not create it
if not os.path.exists(cv_file_loc):
    os.makedirs(cv_file_loc)

# see Shared TSC GlobalVariables.py for source file format
cv_df = pd.read_excel(cv_download_file, sheet_name="Custom View List")

count_cv_source = len(cv_df)

# check if csv file has required headers, if not exit
req_header = [
    "Custom View Id",
    "Custom View Name",
    "Shared",
    "View Id",
    "Workbook Id",
    "Owner Id",
]

req_header = [req.upper() for req in req_header]

check_sum = len(req_header)
check_header = list(list(cv_df.columns))
check_header = [header.upper() for header in check_header]

x = 0

for req in req_header:
    if search(check_header, req):
        x = x + 1

if x != check_sum:
    sys.exit(f"\nFile must contain required column headers: {req_header}")

logging.info("Begin downloading Custom Views.")
logging.info(f"Number of views to download: {count_cv_source}.")
logging.info("This might take several minutes.")

success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):

    # pull necessary API authentication values from TSC Authentication
    auth_token = server._auth_token
    api_version = server.server_info.get().rest_api_version
    site_luid = server.site_id

    logging.info("***** Begin Downloading Custom Views *****\n")

    # Initialize a NoneType column for filenames
    cv_df["File Name"] = None

    # iterate file path to get custom view to download
    for index, row in cv_df.iterrows():
        cv_id = row["Custom View Id"]
        cv_name = row["Custom View Name"]

        try:
            logging.info(f"\nDownloading Custom View [{cv_name}][{cv_id}]...")

            # cv_content = customViews.views.download(
            #     portal_url, api_version, site_luid, auth_token, cv_id
            # )
            cv_item = server.custom_views.get_by_id(cv_id)
            cv_filename = f"{cv_id}{file_extension}"
            cv_path = os.path.join(cv_file_loc, cv_filename)

            cv_content = server.custom_views.download(cv_item, cv_path)

            # Name the file by the CV_ID so that if duplicate names exist,
            # they don't overwrite each other.
            # with open(f"{cv_file_loc}\\{cv_filename}", "w") as file:
            #     file.write(cv_content)

            # Give the system time to process
            time.sleep(1)

            cv_df.at[index, "File Name"] = cv_filename

            logging.info(
                f"Successfully downloaded Custom View [{cv_name}] to file [{cv_filename}]"
            )

            status = "SUCCESS"

            # Brief pause between downloads
            time.sleep(1)

        except Exception as e:
            status = "ERROR"
            logging.error(e)

        # Logging Details
        results = {
            "Time Log": time_log,
            "Script Name": script_name,
            "Custom View Id": cv_id,
            "Custom View Name": cv_name,
            "Filename": cv_filename,
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
with pd.ExcelWriter(cv_log_file) as writer:
    success_df.to_excel(writer, sheet_name="CustomViews Downloaded", index=False)
    error_df.to_excel(writer, sheet_name="CustomViews Errored", index=False)

with pd.ExcelWriter(cv_download_file, mode="a", if_sheet_exists="replace") as writer:
    cv_df.to_excel(writer, sheet_name="Custom View List", index=False)

logging.info("***** End Downloading Custom Views *****\n")

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

# Get the count of total Custom View JSON files created.
count_cv = len(
    [
        name
        for name in os.listdir(cv_file_loc)
        if os.path.isfile(os.path.join(cv_file_loc, name))
    ]
)

logging.info(
    f"""
Completed {script_name} in {duration}.
\tCustom Views to download: {count_cv_source}
\tCustom Views downloaded: {str(count_cv)}
Please check the log files for errors."""
)
