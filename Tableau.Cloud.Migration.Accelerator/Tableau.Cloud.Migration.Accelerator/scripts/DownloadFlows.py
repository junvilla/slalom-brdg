# This will download all Tableau Prep Flow files (TFS/TFSX)
# to the FLOWS directory, based on FlowList.xlsx file
import sys
import time as t
import datetime
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import tableauserverclient as TSC

# -----------------------------------Enter variables
# Get the list of Flows to download
flow_download_file = os.path.join(file_loc, "FlowList.xlsx")

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download Flows from your site."

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

# ------------------------------- Download Flows
start_time = t.time()

# create necessary folders
create_file_locations()

# check if directory to download flows exists, if not create it
if not os.path.exists(flow_file_loc):
    os.makedirs(flow_file_loc)

# see Shared TSC GlobalVariables.py for source file format
flow_df = pd.read_excel(flow_download_file, sheet_name="Flow List")

count_flows_source = len(flow_df)

# check if csv file has required headers, if not exit
req_header = [
    "Flow Id",
    "Flow Name",
]

req_header = [req.upper() for req in req_header]

check_sum = len(req_header)
check_header = list(list(flow_df.columns))
check_header = [header.upper() for header in check_header]

x = 0

for req in req_header:
    if search(check_header, req):
        x = x + 1

if x != check_sum:
    sys.exit(f"\nFile must contain required column headers: {req_header}")

logging.info("Begin downloading Flows.")
logging.info(f"Number of Flows to download: {count_flows_source}.")
logging.info("This might take several minutes.")

count_flows = 0

success_list = []
error_list = []

with server.auth.sign_in(tableau_auth):

    all_flows = Content.load(ContentItem.flows, ContentLocation.source)

    # start logging
    logging.info("***** Begin Downloading Flows *****\n")

    # Initialize a NoneType column for filenames
    flow_df["File Name"] = None

    # iterate file path to get flow to download
    for index, row in flow_df.iterrows():
        flow_id = row["Flow Id"]
        flow_name = row["Flow Name"]

        try:
            logging.info(f"Downloading flow [{flow_name}][{flow_id}]...")
            for flow in all_flows:
                if flow.id == flow_id:
                    flow_item = flow

            file_path = server.flows.download(flow_item.id, flow_file_loc)

            # Pause for 5 seconds - the pace of the downloads was causing issues with the filenames reporting correctly in get_latest_file()
            time.sleep(5)

            # Split the file name and extension, and rename the file to LUID.ext
            _, filename = os.path.split(file_path)
            f_name, f_ext = os.path.splitext(filename)

            flow_filename = f"{flow_item.id}{f_ext}"
            os.rename(f"{file_path}", f"{flow_file_loc}\\{flow_filename}")

            flow_df.at[index, "File Name"] = flow_filename

            logging.info(
                f"Successfully downloaded Flow [{flow_name}] to file [{flow_filename}]"
            )

            status = "SUCCESS"

            count_flows += 1

            # Brief pause between downloads
            time.sleep(1)

        except Exception as e:
            status = "ERROR"
            logging.error(e)

        # Logging Details
        results = {
            "Time Log": time_log,
            "Script Name": script_name,
            "Flow Id": flow_id,
            "Flow Name": flow_name,
            "Filename": flow_filename,
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
with pd.ExcelWriter(flow_log_file) as writer:
    success_df.to_excel(writer, sheet_name="Flows Downloaded", index=False)
    error_df.to_excel(writer, sheet_name="Flows Errored", index=False)

with pd.ExcelWriter(flow_download_file, mode="a", if_sheet_exists="replace") as writer:
    flow_df.to_excel(writer, sheet_name="Flow List", index=False)

logging.info("***** End Downloading Flows *****\n")

end_time = t.time()
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
    f"""
Completed {script_name} in {duration}.
\tCustom Views to download: {count_flows_source}
\tCustom Views downloaded: {str(count_flows)}
Please check the log files for errors."""
)
