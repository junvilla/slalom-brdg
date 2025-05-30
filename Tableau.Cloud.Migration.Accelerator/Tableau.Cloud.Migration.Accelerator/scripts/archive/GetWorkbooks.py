# This will query Tableau, get all workbook, connection & view information
# downloads workbooks into the specified directory
# saves the workbook information to csv

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import numpy as np
from Shared_TSC_GlobalFunctions import *
from Shared_TSC_GlobalVariables import *
import time
import pandas as pd
import tableauserverclient as TSC

# -----------------------------------Enter variables
# file location
# file_loc = variable defined in Global variables
include_extract = False
wb_dest_file = os.path.join(file_loc, export_file_loc, "WorkbookList.xlsx")

create_file_locations()

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about workbooks on your site."

# Prompt the user with the script name and description
print(f"\nYou are running the {script_name} script. {script_description}")

# Include Extracts ?
# Prompt user for value: y (to download extracts) or n (to skip extracts)
print("Do you want to include workbooks with extracts when retrieving data? (y/n)")
include_extract = input("Enter your choice (y/n): ")

try:
    if include_extract.upper() == "Y" or include_extract.upper() == "N":
        print(f"\nYou entered: {include_extract}")
    else:
        print("\nInvalid input. Please enter either 'y' or 'n'.")
except ValueError:
    print("\nInvalid input. Please enter a valid response.")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

print(f"\nBegin {script_name}. This might take several minutes.")

# -----------------------------------Session Authentication to Tableau Server
server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()

# -------------------------------end Session Authentication

# ------------------------------- Get Workbook

# empty array
wb_data = []  # list to store workbook information
proj_data = []  # list to store project information
data = []  # list to store workbook connection information
vw_data = []  # list to store workbook view information

start_time = time.time()

with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)
    all_projects = list(TSC.Pager(server.projects, req_options))
    all_workbooks = list(TSC.Pager(server.workbooks, req_options))

    for proj in all_projects:
        proj_values = [proj.id, proj.name, proj.parent_id]
        proj_data.append(proj_values)

    for wb in all_workbooks:
        print(f"Extracting workbook [{wb.name}] from project [{wb.project_name}]")
        server.workbooks.populate_connections(wb)
        server.workbooks.populate_views(wb)

        # get name of owner
        wb_owners = server.users.get_by_id(wb.owner_id)

        wb_owner_name = wb_owners.email

        wb_values = [
            wb.id,
            wb.name,
            wb.owner_id,
            wb_owner_name,
            wb.project_id,
            wb.project_name,
            wb.size,
            wb.webpage_url,
            wb.content_url,
            "",
        ]

        wb_data.append(wb_values)
        for connection in wb.connections:
            values = [
                wb.id,
                wb.name,
                connection.id,
                connection.datasource_name,
                connection.connection_type,
                connection.username,
                connection.password,
                connection.embed_password,
                connection.server_address,
                connection.server_port,
            ]

            data.append(values)

        for view in wb.views:
            vw_values = [
                view.workbook_id,
                wb.name,
                view.id,
                view.name,
                view.content_url,
            ]

            vw_data.append(vw_values)

# build the project data frame that will be the source for the workbook project path
print("\nCreating data frames with Project details. Please wait.")

proj_df = pd.DataFrame(
    proj_data, columns=["Project ID", "Project Name", "Parent Project ID"]
)

proj_df["Depth"] = proj_df["Parent Project ID"].apply(make_depth(proj_df))

# remove projects with no parents, create new data frame to join
parent_df = proj_df[["Parent Project ID"]].copy()

# build dataframe to get project name and other attributes
parent_df = parent_df.dropna()

parent_df = parent_df[["Parent Project ID"]].drop_duplicates()

parent_df = pd.merge(
    parent_df,
    proj_df[["Project ID", "Project Name"]],
    left_on="Parent Project ID",
    right_on="Project ID",
    how="left",
)

parent_df = parent_df.drop("Project ID", axis=1)

parent_df.rename(columns={"Project Name": "Parent Project Name"}, inplace=True)

# final df will have project id/name and parent project id/name
proj_df = pd.merge(proj_df, parent_df, on="Parent Project ID", how="left")

proj_df.fillna("No Parent", inplace=True)

# workbook data frame
print("\nCreating data frames with Workbook details. Please wait.")
wb_df = pd.DataFrame(
    wb_data,
    columns=[
        "Workbook ID",
        "Workbook Name",
        "Workbook Owner ID",
        "Workbook Owner Name",
        "Project ID",
        "Project Name",
        "Workbook Size (MB)",
        "Webpage URL",
        "Content URL",
        "Migrate?",
    ],
)
df = pd.DataFrame(
    data,
    columns=[
        "Workbook ID",
        "Workbook Name",
        "Connection ID",
        "Connection Data Source Name",
        "Connection Type",
        "Connection UserName",
        "Connection Password",
        "Embed Password",
        "Server Address",
        "Server Port",
    ],
)
df2 = pd.DataFrame(
    vw_data,
    columns=["Workbook ID", "Workbook Name", "View ID", "View Name", "View URL"],
)

# check if workbook is a copy using content url name if different from workbook name
wb_df["Flag"] = np.where(
    wb_df["Workbook Name"].str.replace(" ", "") == wb_df["Content URL"],
    "",
    "Check the content URL against the workbook name " + wb_df["Workbook Name"],
)

# build project path of workbook
temp_proj_df = proj_df[["Project ID", "Project Name", "Parent Project ID"]].copy()
temp_proj_df.rename(columns={"Project ID": "ID", "Project Name": "Name"}, inplace=True)
temp_wb_df = wb_df[["Workbook ID", "Workbook Name", "Project ID"]].copy()
temp_wb_df.rename(
    columns={
        "Workbook ID": "ID",
        "Workbook Name": "Name",
        "Project ID": "Parent Project ID",
    },
    inplace=True,
)

union_proj_wb_df = pd.concat([temp_proj_df, temp_wb_df])
union_proj_wb_df_list = list(
    zip(union_proj_wb_df["Parent Project ID"], union_proj_wb_df["ID"])
)

relations_wb = parse_relations(union_proj_wb_df_list)
path_wb = list(flatten_hierarchy(relations_wb))

path_key_wb = {}
sep = "//"
for path in path_wb:
    temp_wb = []
    if not path:
        continue
    path_len = len(path)
    for index, y in enumerate(path):
        name = union_proj_wb_df.loc[(union_proj_wb_df["ID"] == y)]
        if name.empty:
            name = [""]
        else:
            name = list(name["Name"].values)
        if index < path_len - 1:
            temp_wb.append(name)
        sum_list = sum(temp_wb, [])
    path_final = sep.join(sum_list)
    path_key_wb.setdefault(path[path_len - 1], []).append(path_final)

path_df_wb_ds = pd.DataFrame.from_dict(path_key_wb, orient="index", columns=["Path"])

wb_df_path = pd.merge(wb_df, path_df_wb_ds, left_on="Workbook ID", right_index=True)

if include_extract.upper() == "y":
    wb_df_path["Include Extract"] = True
elif include_extract.upper() == "n":
    wb_df_path["Include Extract"] = False

# wb_df_path.to_csv(os.path.join(file_loc, import_file_loc, 'Workbook_Import.csv'),header=True, index=False)
wb_df_path.to_csv(wb_download_file, header=True, index=False)

with pd.ExcelWriter(wb_dest_file) as writer:
    print(f"\nWriting results to {wb_dest_file}. Please wait.")
    wb_df_path.to_excel(writer, sheet_name="Workbook List", index=False)
    df.to_excel(writer, sheet_name="Workbook Data Source List", index=False)
    df2.to_excel(writer, sheet_name="Workbook View List", index=False)

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

print(f"\nCompleted {script_name} in {duration}. Please view file {wb_dest_file}")
