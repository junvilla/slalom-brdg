# This script will publish workbooks into a project specified in import file
# The following files are needed for this script defined in Shared_TSC_GlobalVariables.py
# Workbook_Import.csv: list of workbooks to import
# Workbook_Connection_Import.csv: connection information for workbook

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import time
import numpy as np
import tableauserverclient as TSC
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *

# -----------------------------------Enter variables

# file location.
# file_loc = variable defined in Shared_tsc_GlobalVariables.py
# this is where tableau object information and workbooks/data sources will be downloaded
# wb_folder = location of downloaded workbooks.
# specify the folder name to store the downloaded files.

wb_folder = "WB"

# include updating workbook connections 1: true, 0: false
include_conn = 0

# --------------------------------- end variables

wb_dest_file = os.path.join(file_loc, log_file_loc, "Publish Workbook Log.xlsx")
wb_file_loc = os.path.join(file_loc, wb_folder)
emb_file_loc = os.path.join(file_loc, wb_folder, "Embedded")

newPath_list = (
    []
)  # list to store csv values with parents and depth derived from path column in csv file

# -----------------------------------Session Authentication to Tableau Server
# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will publish workbooks on your site."

# Prompt the user with the script name and description
print(f"\nYou are running {script_name} script. {script_description}")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()


# ------------------------------- Publish Workbooks
# This section will:
# look in a file path for data source files, publish the workbook
# The folder must only contain .twb and .twbx files
start_time = time.time()

# get file names of workbooks to publish
os_file_wb = os.listdir(wb_file_loc)
os_file_df = pd.DataFrame(os_file_wb, columns=["File Name"])

# get file names of workbooks with embedded data sources (if requested)
emb_file_wb = os.listdir(emb_file_loc)
emb_file_df = pd.DataFrame(emb_file_wb, columns=["File Name"])

proj_id = ""
wb_destination_proj_name = ""

# create dataframe to store errors and activity
log_df = pd.DataFrame(
    columns=["Time Log", "Object Name", "Script Name", "Project", "Result", "Error"]
)
log_df["Script Name"] = "PublishWorkbooks.py"

# read workbook import source file and workbook connection import file

# workbook (this is a full list - both with published and embedded data sources)
wb_csv_df = pd.read_csv(wb_source_file)
wb_csv_df.dropna(axis=0, how="all", inplace=True)


# get count of workbooks expected to publish
count_wb_source = len(wb_csv_df.index)

# check if csv file has required headers, if not exit
req_header = ["Workbook Name", "File Name", "Path", "Owner Email"]
req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(wb_csv_df.columns)
check_header = [header.upper() for header in check_header]

x = 0
for req in req_header:
    if search(check_header, req):
        x = x + 1
if x != check_sum:
    sys.exit(f"File must contain required column headers: {str(req_header)}")

# not being used, must use document API instead
# workbook connection
if include_conn == 1:
    wb_conn_csv_df = pd.read_csv(wb_conn_source_file)
    wb_conn_csv_df = wb_conn_csv_df.where(pd.notnull(wb_conn_csv_df), None)
    wb_conn_csv_df = wb_conn_csv_df.replace({np.nan: None})
    # check connection source file if it has required headers
    opt_header = [
        "Workbook Name",
        "Connection Data Source Name",
        "Connection UserName",
        "Server Address",
        "Server Port",
    ]
    opt_header = [opt.upper() for opt in opt_header]
    check_sum = len(opt_header)
    check_header = list(wb_conn_csv_df.columns)
    check_header = [header.upper() for header in check_header]

    x = 0
    for opt in opt_header:
        if search(check_header, opt):
            x = x + 1
    if x != check_sum:
        sys.exit("Connection File must contain required column headers")

# validate and clean up input dataframe
# upper case df columns
wb_csv_df.columns = wb_csv_df.columns.str.upper()

# check if path contains Nan
if wb_csv_df["PATH"].isna().any():
    # print a warning message
    print(
        "WARNING: The Path column for some workbooks do not have parent project. \nWe will publish the "
        "workbook to the Default folder."
    )
    # Ask the user if they want to proceed with replacing NaN values
    proceed = input(
        "Do you want to proceed with publishing the workbook with no project to Default? (y/n): "
    )
    if proceed.lower() == "y":
        # Define the string to replace NaN values with
        replace_string = "//Default"

        # Replace NaN values in the column with the replace_string
        wb_csv_df["PATH"] = wb_csv_df["PATH"].fillna(replace_string)

        # Print a message to confirm that NaN values have been replaced
        print("Workbooks with undefined projects will be published to Default.")
    else:
        # Exit the script if the user chooses not to proceed
        print(f"Exiting {script_name}...")
        exit()

# check if user wants to publish workbooks with Embedded data sources (default: True)
publish_embedded = True

# print a notice about workbooks with embedded data sources
print(
    "Workbooks with Embedded datasources were downloaded to a separate folder."
    "\nPublishing workbooks with embedded extracts to Tableau Cloud may require Tableau Bridge"
    "\nin order for extract refreshes tasks to process."
)

# prompt the user to choose whether to publish workbooks with embedded dat sources
embedded_choice = input(
    "Do you want to publish workbooks that contain embedded data sources? (y/n)"
)
if embedded_choice.casefold() == "y":
    publish_embedded = True
    print(
        "Script will publish workbooks containing embedded data sources. Please verify connections in the destination environment when finished."
    )
else:
    publish_embedded = False
    print(
        "Skipping workbooks with embedded data sources. These workbooks will need to be manually published to the destination environment."
    )

# check that Path uses separator value
check_path_sep = wb_csv_df["PATH"].str.contains(sep).any()
if not check_path_sep:
    sys.exit(f"Path column must use separator {sep}")

## clean up the input file
wb_csv_df["PATH"] = wb_csv_df["PATH"].str.strip().str.upper()

### parse the path in the csv file to get the parent project where the workbook will be published
path_list = [
    list(path)
    for path in zip(
        wb_csv_df["WORKBOOK NAME"],
        wb_csv_df["PATH"],
        wb_csv_df["FILE NAME"],
        wb_csv_df["OWNER EMAIL"],
    )
]

# parse path to build parent project name
# get the depth of the project to build the project hierarchy
# check if first character is a slash if not, add it
for path in path_list:
    check_str = str(path[1])
    if check_str == "nan" or check_str == "":
        check_str = "No Parent"
    if check_str[0:2] != sep and check_str != "No Parent":
        new_path = sep + check_str
    else:
        new_path = check_str
    depth_parent_lst = parse_path(new_path, sep)
    path.append(depth_parent_lst)
    path = flatten_list(path)
    newPath_list.append(path)

wb_csv_df = pd.DataFrame(
    newPath_list,
    columns=[
        "Workbook Name",
        "Path",
        "File Name",
        "Owner Email",
        "Depth",
        "Parent Project Name",
    ],
)

# checks if folder only has Tableau data sources, it will skip files with extensions that isn't listed
str_remove = [".twb", ".twbx"]

# begin logging
f = open(log_file, "a")
f.write(time_log + "******* Begin Publish Workbook ********" + "\n")
f.close()

count_wb = 0

print(f"Number of workbooks in input file: {str(count_wb_source)}")
print(f"Begin {script_name} . Number of workbooks to publish: {str(count_wb_source)}")
print(
    "This process might take several minutes. Please wait for confirmation that the process has completed."
)

# first let's create the projects dataframe to find the project id to publish workbooks
with server.auth.sign_in(tableau_auth):
    try:
        # get list of existing projects
        req_options = TSC.RequestOptions(pagesize=1000)
        all_projects = list(TSC.Pager(server.projects, req_options))
        data = []
        for proj in all_projects:
            values = [proj.id, proj.name, proj.parent_id]
            data.append(values)

        current_proj_df = pd.DataFrame(
            data, columns=["Project ID", "Project Name", "Parent Project ID"]
        )

        # identify the depth of each existing project whether level 1 (top level),
        # level 2 (child), level 3 (grand child) etc
        current_proj_df["Depth"] = current_proj_df["Parent Project ID"].apply(
            make_depth(current_proj_df)
        )
        # remove projects with no parents, create new data frame to join
        parent_df = current_proj_df[["Parent Project ID"]].copy()

        # build dataframe to get project name and other attributes - need to do this for first time building path

        parent_df = parent_df.dropna()
        parent_df = parent_df[["Parent Project ID"]].drop_duplicates()

        parent_df = pd.merge(
            parent_df,
            current_proj_df[["Project ID", "Project Name"]],
            left_on="Parent Project ID",
            right_on="Project ID",
            how="left",
        )

        parent_df = parent_df.drop("Project ID", axis=1)

        parent_df.rename(columns={"Project Name": "Parent Project Name"}, inplace=True)

        # final df will have project id/name and parent project id/name
        current_proj_df = pd.merge(
            current_proj_df, parent_df, on="Parent Project ID", how="left"
        )

        # get the path for current projects

        current_proj_df.rename(
            columns={
                "Parent Project ID": "Parent ID",
                "Project ID": "Child ID",
                "Project Name": "Name",
            },
            inplace=True,
        )

        # set parent id with no parent for function to work
        current_proj_df["Parent ID"].fillna("No Parent", inplace=True)
        current_proj_df["Parent Project Name"].fillna("No Parent", inplace=True)
        current_proj_df.sort_values(by=["Depth", "Name"])

        # generate project path
        project_path_dict = get_hierarchy_path(current_proj_df)

        path_proj_df = pd.DataFrame.from_dict(
            project_path_dict, orient="index", columns=["Path"]
        )

        path_proj_df["newPath"] = np.where(
            path_proj_df["Path"].str[0:2] != sep,
            sep + path_proj_df["Path"].astype(str),
            path_proj_df["Path"],
        )

        # if dataframe is empty, dict returned empty, it means all projects are level 1
        if not bool(project_path_dict):
            path_proj_df["Path"] = "None"

        current_proj_df.rename(
            columns={
                "Parent ID": "Parent Project ID",
                "Child ID": "Project ID",
                "Name": "Project Name",
            },
            inplace=True,
        )

        current_proj_df = pd.merge(
            current_proj_df,
            path_proj_df,
            left_on="Project ID",
            how="left",
            right_index=True,
        )

        # removing leading spaces and upper case to match to input file path
        current_proj_df["Path"] = current_proj_df["Path"].str.strip().str.upper()

        # fill nan with none for path join
        current_proj_df.mask(current_proj_df == "", inplace=True)
        current_proj_df["Path"].fillna("//", inplace=True)

        # create concatenated key column to be the project path of the workbook
        current_proj_df["WB Path"] = (
            current_proj_df["Path"].str.upper().str.strip()
            + sep
            + current_proj_df["Project Name"].str.upper().str.strip()
        )
        current_proj_df["WB Path"] = current_proj_df["WB Path"].str.replace(
            sep + sep, sep
        )

    except TSC.ServerResponseError as err:
        error = time_log + str(err)
        new_row = {
            "Time Log": time_log,
            "Object Name": "",
            "Script Name": "PublishWorkbooks.py",
            "Project": "",
            "Result": "Failed",
            "Error": str(err),
        }
        log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

for k in wb_csv_df.index:
    with server.auth.sign_in(tableau_auth):
        try:
            # iterate through data frame containing list of workbooks to publish

            wb_file_name = wb_csv_df["File Name"][k]
            wb_csv_name = wb_csv_df["Workbook Name"][k]
            wb_destination_project = wb_csv_df["Path"][k]
            wb_owner_id = wb_csv_df["Owner Email"][k]
            wb_file_path = os.path.join(wb_file_loc, wb_csv_df["File Name"][k])

            # check that file exists in folder
            temp_wb_file_df = os_file_df[(os_file_df["File Name"] == wb_file_name)]

            if temp_wb_file_df.empty:
                if publish_embedded == True:
                    print(
                        f"{wb_file_name} not found in WB folder. Checking if it is in the Embedded folder."
                    )
                    temp_wb_file_df = emb_file_df[
                        (emb_file_df["File Name"] == wb_file_name)
                    ]

                    if not temp_wb_file_df.empty:
                        wb_file_path = os.path.join(
                            emb_file_loc, wb_csv_df["File Name"][k]
                        )

                    elif temp_wb_file_df.empty:
                        print(
                            f"{wb_file_name} does not exist in the WB or Embedded folders."
                        )
                        new_row = {
                            "Time Log": time_log,
                            "Object Name": wb_csv_name,
                            "Script Name": "PublishWorkbooks.py",
                            "Project": str(wb_destination_project),
                            "Result": "Failed",
                            "Error": wb_file_name
                            + " File does not exist in WB or Embedded folder.",
                        }

                        log_df = pd.concat(
                            [log_df, pd.DataFrame([new_row])], ignore_index=True
                        )
                        continue
                else:
                    new_row = {
                        "Time Log": time_log,
                        "Object Name": wb_csv_name,
                        "Script Name": "PublishWorkbooks.py",
                        "Project": str(wb_destination_project),
                        "Result": "Failed",
                        "Error": wb_file_name + " File does not exist in WB folder.",
                    }

                    log_df = pd.concat(
                        [log_df, pd.DataFrame([new_row])], ignore_index=True
                    )
                    continue

            temp_proj_df = current_proj_df[
                (
                    current_proj_df["WB Path"].str.upper().str.strip()
                    == wb_destination_project.upper().strip()
                )
            ]
            if temp_proj_df.empty:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": wb_csv_name,
                    "Script Name": "PublishWorkbooks.py",
                    "Project": str(wb_destination_project),
                    "Result": "Failed",
                    "Error": str(wb_destination_project)
                    + "Parent Project is not a row in the input file. "
                    "This workbook was not published ",
                }

                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
                continue

            temp_proj_parent_id = temp_proj_df["Project ID"].values.tolist()
            proj_id = temp_proj_parent_id[0]

            default_proj_owner_id = wb_owner_id

            # Define publish mode - Overwrite, Append, or CreateNew
            publish_mode = TSC.Server.PublishMode.CreateNew

            # Publish workbooks
            print(f"Publishing Workbook [{wb_csv_name}] - Filename [{wb_file_name}]")

            # create new workbook item to publish. as_job should be False,
            # otherwise it will trigger a false publish success
            new_workbook = TSC.WorkbookItem(
                name=wb_csv_name, project_id=proj_id, show_tabs=True
            )

            new_workbook = server.workbooks.publish(
                workbook_item=new_workbook,
                file=wb_file_path,
                mode=publish_mode,
                # connections=all_connections,
                as_job=False,
                skip_connection_check=True,
            )

            count_wb = count_wb + 1

            new_row = {
                "Time Log": time_log,
                "Object Name": wb_csv_name,
                "Script Name": "PublishWorkbooks.py",
                "Project": wb_destination_proj_name,
                "Result": "Success",
                "Error": "Publish successful: " + wb_file_name,
            }

            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            new_row = {
                "Time Log": time_log,
                "Object Name": wb_csv_name,
                "Script Name": "PublishWorkbooks.py",
                "Project": str(wb_destination_project),
                "Result": "Failed",
                "Error": str(err),
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

with pd.ExcelWriter(wb_dest_file) as writer:
    log_df.to_excel(writer, sheet_name="PublishWorkbook", index=False)

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

f = open(log_file, "a")
f.write(
    "Number of workbooks to publish: "
    + str(count_wb_source)
    + "\n"
    + "Number of workbooks published: "
    + str(count_wb)
    + "\n"
)
if count_wb != count_wb_source:
    log_error(wb_source_file, 3)
f.write("Check detailed logs in " + wb_dest_file + "\n")
f.write(time_log + "******* End Publish Workbook ********" + "\n")
f.close()

print(
    f"Completed {script_name} in {duration}. \nWorkbooks published: {str(count_wb)}. \nPlease check your log files for any errors."
)
