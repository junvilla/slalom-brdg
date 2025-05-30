# This script will publish data sources into a project using project ID of the source file
#  if project does not exist, data source will be published to "Migrated Data Source"
# then refreshes the data source after publish. It will read a csv file if updating credentials
# You must specify the path of the data source files in Global Variables
# If updating connection information, provide a csv file with column headers:
# 'Data Source Name' = name of the data source that will be migrated
# 'User Name'
# 'Password'
# 'Embed Password' (True/False) = whether the user name and password should be embedded at publish
# 'Oauth' (True/False) = whether OAuth is used (optional, default is False if not provided)
#  The source file can be generated using the download data source script DownloadDataSource.py

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import time
import numpy as np
import pandas as pd
import tableauserverclient as TSC
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *

# -----------------------------------enter session variables here


# ds_folder = location of downloaded data sources. uses file_loc variable in global variable for file path
ds_folder = "DS"
ds_file_loc = os.path.join(file_loc, ds_folder)
ds_dest_file = os.path.join(file_loc, log_file_loc, "Publish Data Source Log.xlsx")

newPath_list = (
    []
)  # list to store csv values with parents and depth derived from path column in csv file

# ds_import_file = ds_source_file
ds_import_file = pd.read_csv(ds_source_file)

conn_source_file = pd.read_excel(
    os.path.join(file_loc, export_file_loc, "DataSourceList.xlsx"),
    sheet_name="Connection List",
)

ds_source_pathfile = ds_file_loc

# ds_source_file = ds_import_file
# set whether to update credentials after publish. 1 = update credentials , 0 = do not update credentials
update_credentials = 0

# set True/False whether oauth is used for connections
oauth = False

# -----------------------------------end session variables
# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will publish data sources on your site."

# Prompt the user with the script name and description
print(f"You are running {script_name} script. {script_description}")

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

x = 0

# if adding connections
if update_credentials == 1:
    df = pd.read_csv(conn_source_file)
    df.dropna(axis=0, how="all", inplace=True)
    # check if csv file has required headers, if not exit
    req_header = ["Data Source Name", "User Name", "Password", "Embed Password"]
    req_header = [req.upper() for req in req_header]
    check_sum = len(req_header)
    check_header = list(df.columns)
    check_header = [header.upper() for header in check_header]
    for req in req_header:
        if search(check_header, req):
            x = x + 1
    if x != check_sum:
        sys.exit("Connection File must contain required column headers")

# ------------------------------- Publish Data Source
# This section will:
# look in a file path for data source files, publish the data source
# The folder must only contain .tds, .tdsx, .tde or .hyper files
# The data source will be published in a top level project "Migrated Data Source"
start_time = time.time()

# get file names of data sources to publish
os_file_ds = os.listdir(ds_file_loc)
os_file_df = pd.DataFrame(os_file_ds, columns=["File Name"])

# declare variables as null in case no match in search
proj_id = ""
ds_project_name = ""
filter_user_id = ""

# create dataframe to store errors and activity
log_df = pd.DataFrame(
    columns=["Time Log", "Object Name", "Script Name", "Project", "Result", "Error"]
)

log_df["Script Name"] = "PublishDataSource.py"

# create data from data source import file to get name of data source to publish
ds_csv_df = pd.read_csv(ds_source_file)

ds_csv_df.dropna(axis=0, how="all", inplace=True)

count_ds_source = len(ds_csv_df.index)

# check if csv file has required headers, if not exit
req_header = ["Data Source Name", "File Name", "Path", "Owner Email"]
req_header = [req.upper() for req in req_header]

check_sum = len(req_header)
check_header = list(ds_csv_df.columns)
check_header = [header.upper() for header in check_header]

x = 0

for req in req_header:
    if search(check_header, req):
        x = x + 1
if x != check_sum:
    sys.exit(f"Data Source File must contain required column headers: {req_header}")

# checks if folder only has Tableau data sources, it will skip files with extensions that isn't listed
# str_remove = ['.tds', '.tdsx', '.tde', '.hyper']

# create connection credentials, use columns in file
new_conn_creds = None

# begin logging
f = open(log_file, "a")
f.write(time_log + "******* Begin Publish Data Source ********" + "\n")
f.close()

# max depth in csv file
count_ds_source = len(ds_csv_df.index)

print(f"Number of Data Sources in input file: {str(count_ds_source)}")
print(
    f"Begin Publish Data Source. Number of Data Sources to publish: {str(count_ds_source)}"
)
print(
    "This process might take several minutes. Please wait for confirmation that the process has completed."
)
print(
    "------------------------------------------------------------------------------------------------------"
)

# check if path contains Nan
if ds_csv_df["Path"].isna().any():
    # print a warning message
    print(
        "WARNING: The Path column for some data sources do not have parent project. \nWe will publish the "
        "data source to the Default folder."
    )
    # Ask the user if they want to proceed with replacing NaN values
    proceed = input(
        "Do you want to proceed with publishing the data source with no project to Default? (y/n): "
    )
    if proceed.lower() == "y":
        # Define the string to replace NaN values with
        replace_string = "//default"

        # Replace NaN values in the column with the replace_string
        ds_csv_df["Path"] = ds_csv_df["Path"].fillna(replace_string)

        # Print a message to confirm that NaN values have been replaced
        print("Data Sources with undefined projects will be published to Default.")
    else:
        # Exit the script if the user chooses not to proceed
        print(f"Exiting {script_name}...")
        exit()

# check that Path uses separator value
check_path_sep = ds_csv_df["Path"].str.contains(sep).any()
if not check_path_sep:
    sys.exit(f"Path column must use separator {sep}")

## clean up the input file
ds_csv_df["Path"] = ds_csv_df["Path"].str.strip().str.upper()

### parse the path in the csv file to get the parent project where the data source will be published
path_list = [
    list(path)
    for path in zip(
        ds_csv_df["Data Source ID"],
        ds_csv_df["Data Source Name"],
        ds_csv_df["Path"],
        ds_csv_df["File Name"],
        ds_csv_df["Owner Email"],
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

ds_csv_df = pd.DataFrame(
    newPath_list,
    columns=[
        "Data Source ID",
        "Data Source Name",
        "Path",
        "File Name",
        "Owner Email",
        "Depth",
        "Parent Project Name",
    ],
)

count_ds = 0

# authenticate to server
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
        current_proj_df["Path"] = current_proj_df["Path"].str.strip()

        # fill nan with none for path join
        current_proj_df.mask(current_proj_df == "", inplace=True)
        current_proj_df["Path"].fillna("//", inplace=True)

        # create concatenated key column to be the project path of the datasource
        current_proj_df["DS Path"] = (
            current_proj_df["Path"].str.strip()
            + sep
            + current_proj_df["Project Name"].str.strip()
        )
        current_proj_df["DS Path"] = current_proj_df["DS Path"].str.replace(
            sep + sep, sep
        )

    except TSC.ServerResponseError as err:
        error = time_log + str(err)
        new_row = {
            "Time Log": time_log,
            "Object Name": "",
            "Script Name": "PublishDataSource.py",
            "Project": "",
            "Result": "Failed",
            "Error": str(err),
        }
        log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

# merging Project ID on Project Name match from migrated projects to ds df
# merge_df = pd.merge(ds_csv_df, proj_df, on=['Project Name'])

# conn_source_obj = pd.read_excel(conn_source_file, sheet_name='Connection List')
conn_source_df = pd.DataFrame(
    conn_source_file, columns=["Data Source Name", "Connection Type"]
)

merge_df = pd.merge(ds_csv_df, conn_source_df, on=["Data Source Name"])


with server.auth.sign_in(tableau_auth):
    for k in merge_df.index:
        try:
            # iterate through dataframe containing list of datasources to publish
            ds_file_name = merge_df["File Name"][k]
            ds_name = merge_df["Data Source Name"][k]
            ds_destination_project = merge_df["Path"][k]
            ds_owner = merge_df["Owner Email"][k]
            conn_type = merge_df["Connection Type"][k]

            # check that the file exists in the folder
            temp_ds_file_df = os_file_df[(os_file_df["File Name"] == ds_file_name)]

            if temp_ds_file_df.empty:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": ds_name,
                    "Script Name": "PublishDatSource.py",
                    "Project": str(ds_destination_project),
                    "Result": "Failed",
                    "Error": ds_file_name + " File does not exist in folder",
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
                continue

            temp_proj_df = current_proj_df[
                (
                    current_proj_df["DS Path"].str.upper().str.strip()
                    == ds_destination_project.upper().strip()
                )
            ]

            if temp_proj_df.empty:
                new_row = {
                    "Time Log": time_log,
                    "Object Name": ds_name,
                    "Script Name": "PublishDataSource.py",
                    "Project": str(ds_destination_project),
                    "Result": "Failed",
                    "Error": str(ds_destination_project)
                    + "Parent Project is not a row in the input file."
                    "This data source was not published ",
                }

                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
                continue

            temp_proj_parent_id = temp_proj_df["Project ID"].values.tolist()
            proj_id = temp_proj_parent_id[0]

            default_proj_owner_id = ds_owner

            just_update = False  # if you just want to change DS owner and not republish

            if not just_update:
                # for i in merge_df.index:
                try:
                    # print(i)
                    # ds_name = merge_df['Data Source Name'][i]
                    # ds_owner = merge_df['Owner Email'][i]
                    # conn_type = merge_df['Connection Type'][i]
                    # newproj_id = proj_id
                    print(
                        f"{k}: Publishing Data source: {ds_name}\nConnection type: {conn_type}\n"
                        f"Project Path: {ds_destination_project}\nProject ID: {proj_id}\nOwner: {ds_owner}\n"
                    )
                    ds_file_loc = os.path.join(
                        ds_source_pathfile, str(merge_df["File Name"][k])
                    )

                    publish_mode = TSC.Server.PublishMode.Overwrite

                    # if update_credentials == 1:
                    #     conn_df = df[df['Data Source Name'] == df['Data Source Name']]
                    #     # connection list does not have the data source listed, publish without credentials
                    #     if conn_df.empty:
                    #         new_conn_creds = None
                    #     else:
                    #         conn_df = conn_df[['Data Source Name',
                    #                            'User Name', 'Password',
                    #                            'Embed Password']].fillna('')
                    #         conn_list = conn_df.values.tolist()
                    #         username = conn_list[0][1]
                    #         # password = conn_list[0][2]
                    #         password = 'test'
                    #         embed = conn_list[0][3]
                    #
                    #         if username:
                    #             new_conn_creds = TSC.ConnectionCredentials(username, password, embed,
                    #                                                        oauth)
                    #

                    new_datasource = TSC.DatasourceItem(
                        name=ds_name, project_id=proj_id
                    )
                    new_datasource.use_remote_query_agent = True
                    new_datasource = server.datasources.publish(
                        new_datasource, ds_file_loc, publish_mode
                    )

                    count_ds += 1

                    new_row = {
                        "Time Log": time_log,
                        "Object Name": ds_name,
                        "Script Name": "PublishDataSource.py",
                        "Project": ds_destination_project,
                        "Result": "Success",
                        "Error": "Publish successful: " + ds_file_name,
                    }
                    log_df = pd.concat(
                        [log_df, pd.DataFrame([new_row])], ignore_index=True
                    )

                except TSC.ServerResponseError as err:
                    error = time_log + str(err)
                    new_row = {
                        "Time Log": time_log,
                        "Object Name": ds_name,
                        "Script Name": "PublishDataSource.py",
                        "Project": proj_id,
                        "Result": "Failed",
                        "Error": str(err),
                    }

                    log_df = pd.concat(
                        [log_df, pd.DataFrame([new_row])], ignore_index=True
                    )

            outputfile = os.path.join(
                file_loc, log_file_loc, "PublishDataSources-output.xlsx"
            )

            with pd.ExcelWriter(outputfile) as writer:
                merge_df.to_excel(writer, sheet_name="PublishDataSources", index=False)

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            new_row = {
                "Time Log": time_log,
                "Object Name": "",
                "Script Name": "PublishDataSource.py",
                "Project": "",
                "Result": "Failed",
                "Error": str(err),
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

    # iterate through source ds file again
    # then fetch the 'just published' data sources to get the new [ds ID]
    # get the [ds name], match them from published to source
    # get [owner email] from source, match to migrated users [user name]
    # then get [user ID] from migreated users
    # update published datasource with [user ID]

    # we already have merge_df as source ds (above)
    # Data Source Name
    # Owner Email

    # create df of published ds
    pub_ds_df = []
    pub_ds_obj = list(TSC.Pager(server.datasources, req_options))

    # print(pub_ds_obj)
    for pub_ds in pub_ds_obj:
        values = [pub_ds.id, pub_ds.name, pub_ds.owner_id]
        pub_ds_df.append(values)

    pub_ds_df = pd.DataFrame(
        pub_ds_df, columns=["Data Source ID", "Data Source Name", "Owner ID"]
    )

    # create df of migrated users to match [Owner Email] to [User Name]
    migrated_users_df = []
    migrated_users_obj = list(TSC.Pager(server.users, req_options))

    for user in migrated_users_obj:
        values = [user.id, user.name]
        migrated_users_df.append(values)

    migrated_users_df = pd.DataFrame(
        migrated_users_df, columns=["User ID", "User Name"]
    )

    # merge source and published df into one df on [Data Source Name]
    new_merge_df = pd.merge(merge_df, pub_ds_df, on=["Data Source Name"])
    new_merge_df = new_merge_df.rename(columns={"Owner Email": "User Name"})

    # now merge the above merged df to migrated users on [User Name]
    new_merge_df = pd.merge(new_merge_df, migrated_users_df, on=["User Name"])
    # print(new_merge_df.columns)

    # now we need to iterate over each Datasource by [Data Source ID] and update the data source on Cloud
    # with the User ID
    # note that we have two Data Source IDs in the final df, _x and _y, we are using _y to iterate over
    # the published ds so we can update the owner id with the [user id]
    for i in new_merge_df.index:
        ds_id = new_merge_df["Data Source ID_y"][i]
        ds_name = new_merge_df["Data Source Name"][i]
        ds_owner = new_merge_df["User ID"][i]
        ds_owneruser = new_merge_df["User Name"][i]
        ds = server.datasources.get_by_id(ds_id)
        ds.owner_id = ds_owner

        try:
            server.datasources.update(ds)
        except:
            continue

        # new_datasource = TSC.server.DatasourceItem.use_remote_query_agent = True
        print(f"Data source [{ds_name}] has been updated with owner [{ds_owneruser}]")

with pd.ExcelWriter(ds_dest_file) as writer:
    log_df.to_excel(writer, sheet_name="PublishDataSource", index=False)

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
    "Number of data source to publish: "
    + str(count_ds_source)
    + "\n"
    + "Number of data source published: "
    + str(count_ds)
    + "\n"
)

if count_ds != count_ds_source:
    log_error(ds_name, 3)

f.write(time_log + "******* End Publish Data Source ********" + "\n")
f.close()

print(
    f"\nCompleted {script_name} in {duration}. \nData Sources created: {str(count_ds)}. \nPlease check your log files for any errors."
)
