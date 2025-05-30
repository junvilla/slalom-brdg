# This will query Tableau, get all workbook, connection & view information
# downloads workbooks into the specified directory
# saves the workbook information to csv

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import time
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import tableauserverclient as TSC

# -----------------------------------Enter variables
# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download workbooks from your site."

# Prompt the user with the script name and description
print(f"\nYou are running {script_name} script. {script_description}")

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

# create necessary folders
create_file_locations()

wb_data = []
wb_embedded_data = []
file_extension = ".twbx"
wb_embedded = "Embedded"
wb_embedded_file_loc = os.path.join(wb_file_loc, wb_embedded)

start_time = time.time()

# check if directory to download workbooks exist, if not create
if not os.path.exists(wb_file_loc):
    os.makedirs(wb_file_loc)

# check if directory to store embedded workbooks exist, if not create
if not os.path.exists(wb_embedded_file_loc):
    os.makedirs(wb_embedded_file_loc)

# see Shared TSC GlobalVariables.py for source file format
csv_df = pd.read_csv(wb_download_file)

count_wb_source = len(csv_df.index)

# check if csv file has required headers, if not exit
req_header = ["Workbook ID"]

req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(list(csv_df.columns))
check_header = [header.upper() for header in check_header]

x = 0
for req in req_header:
    if search(check_header, req):
        x = x + 1


if x != check_sum:
    sys.exit(f"\nFile must contain required column headers: {req_header}")

# Include Extracts?
extract_choice = input(
    "Do you want to download data extracts embedded in Tableau workbooks? (Y/n)? "
)
if extract_choice.casefold() == "Y":
    no_extract = False
else:
    no_extract = True

print(
    f"\nBegin downloading workbooks. Number of workbooks to download: {count_wb_source}. \nThis might take several minutes."
)

with server.auth.sign_in(tableau_auth):
    count_wb = 0

    # start logging
    f = open(log_file, "a")
    f.write(time_log + "***** Begin Downloading Workbooks ******" + "\n")
    f.close()

    # iterate file path to get workbook to download
    for index, row in csv_df.iterrows():
        f_wb = row["Workbook ID"]
        f_path = row["Path"]

        try:
            wb_to_download = server.workbooks.get_by_id(f_wb)
            if not wb_to_download:
                log_error(wb_to_download.name, 7)
                continue
            wb_name = wb_to_download.name

            wb_owner = server.users.get_by_id(wb_to_download.owner_id)
            wb_owner_email = wb_owner.email
            wb_owner_name = wb_owner.name

            print(
                f"Downloading workbook: {wb_name} from project [{wb_to_download.project_name}]. Filename: {wb_to_download.id}"
            )
            file_path = server.workbooks.download(
                wb_to_download.id, filepath=wb_file_loc, no_extract=no_extract
            )

            # Pause for 5 seconds - the pace of the downloads was causing issues with the filenames reporting correctly in get_latest_file()
            time.sleep(5)

            # Split the file name and extension, and rename the file to LUID.ext
            _, filename = os.path.split(file_path)
            f_name, f_ext = os.path.splitext(filename)

            updated_wb_name = f"{wb_to_download.id}{f_ext}"
            os.rename(f"{file_path}", f"{wb_file_loc}\\{updated_wb_name}")

            count_wb += 1

            # get project name
            wb_projects, pagination_item = server.projects.get()

            for wb_proj in wb_projects:
                if wb_proj.id != wb_to_download.project_id:
                    continue
                wb_project_name = wb_proj.name

            values = [
                wb_to_download.id,
                wb_to_download.name,
                updated_wb_name,
                wb_to_download.project_id,
                wb_project_name,
                wb_owner_email,
                wb_owner_name,
                f_path,
            ]

            wb_data.append(values)

            f = open(log_file, "a")
            f.write(
                time_log
                + " Download successful: "
                + wb_to_download.name
                + " File: "
                + updated_wb_name
                + " from Project: "
                + wb_project_name
                + "\n"
            )
            f.close()

            time.sleep(5)

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            f = open(log_file, "a")
            f.write(error + "\n")
            f.close()
            print(err)

    # we cycle through the downloaded workbooks to identify workbooks that contain
    # unpublished embedded data source. these workbooks will be moved to a separate folder
    # the embedded data source must be published first manually before the workbook can be migrated

    wb_files = {}
    wb_embedded_data = []

    # read the contents of the wb_file_loc folder which is where the workbooks are downloaded
    for file_name in os.listdir(wb_file_loc):
        file_path = os.path.join(wb_file_loc, file_name)

        # only get workbooks with twbx file extension
        if os.path.isfile(file_path) and file_name.endswith(file_extension):
            # add the file name to the dictionary
            wb_files[file_name] = file_path

    # open the file to check if it has embedded data source that is not published
    # if is_published = False, then datasource is embedded. Workbook will be moved to a folder
    # the unpublished data source should be published first before it can be migrated

    for wb in wb_files:
        try:
            wb_filename = wb_files[wb]
            try:
                wb_obj = TableauFileManager.open(filename=wb_filename)
                dses = wb_obj.datasources

                for ds in dses:
                    try:
                        print(
                            f"\nChecking if Data source Name [{ds.ds_name}] is a published datasource..."
                        )

                        # if is_published is false, it means the data source is embedded
                        # move the workbook to the Embedded folder
                        if ds.is_published is False:
                            print(
                                f"\n{ds.ds_name} in workbook [{wb}] is an embedded data source."
                            )
                            new_file_path = os.path.join(wb_embedded_file_loc, wb)
                            shutil.move(wb_filename, new_file_path)
                            wb_embedded_values = [
                                wb,
                                ds.ds_name,
                                ds.connections[0].connection_type,
                            ]
                            wb_embedded_data.append(wb_embedded_values)
                            break

                    except IndexError as err:
                        error = time_log + str(err)
                        f = open(log_file, "a")
                        f.write(error + "\n")
                        f.close()
                        print(err)
                        break

            except:
                error = time_log + "Unable to read XML data with Tableau File Manager."
                f = open(log_file, "a")
                f.write(error + "\n")
                f.close()
                print("Unable to read XML data with Tableau File Manager.")
                break

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            f = open(log_file, "a")
            f.write(error + "\n")
            f.close()
            print(err)

f = open(log_file, "a")
f.write(time_log + "***** End Downloading Workbooks ******" + "\n")
f.close()

wb_df = pd.DataFrame(
    wb_data,
    columns=[
        "Workbook ID",
        "Workbook Name",
        "File Name",
        "Project ID",
        "Project Name",
        "Owner Email",
        "Owner Name",
        "Path",
    ],
)

wb_embedded_df = pd.DataFrame(
    wb_embedded_data,
    columns=[
        "Workbook Name",
        "Embedded Data Source Name",
        "Connection Type",
    ],
)

wb_df.to_csv(
    os.path.join(file_loc, import_file_loc, "Workbook_Import.csv"),
    header=True,
    index=False,
)

with pd.ExcelWriter(wb_dest_file) as writer:
    print(f"\nWriting results to {wb_dest_file}. Please wait.")
    wb_df.to_excel(writer, sheet_name="Workbook List", index=False)
    wb_embedded_df.to_excel(writer, sheet_name="Embedded Workbook List", index=False)

end_time = time.time()
seconds = end_time - start_time

if seconds < 60:
    duration = f"{round(seconds,2)} second(s)"
elif seconds > 60 and seconds < 3600:
    duration_s = round(seconds % 60, 2)
    duration_m = round(seconds / 60)
    duration = f"{duration_m} minute(s) and {duration_s} second(s)"
elif seconds >= 3600:
    duration_m = round(seconds % 3600, 2)
    duration_h = round(seconds / 3600)
    duration = f"{duration_h} hour(s) and {duration_m} minute(s)"

if count_wb != count_wb_source:
    err_msg = (
        "Number of workbooks to download: "
        + str(count_wb_source)
        + "\n"
        + "Number of workbooks downloaded: "
        + str(count_wb)
    )
    log_error(err_msg, 3)

print(
    f"Completed {script_name} in {duration}. \nDownloaded {str(count_wb)} workbooks. \nPlease check the log files for errors."
)
