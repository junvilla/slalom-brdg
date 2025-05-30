# This script will download data sources from Tableau Server or Tableau Cloud
# into a specified file location
# and create export files of data source and connection information which can be used to import into Tableau Cloud

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time
import pandas as pd
import tableauserverclient as TSC

# -----------------------------------Enter variables

# file location. this is where tableau object information and workbooks/data sources will be downloaded
# ds_folder = location of downloaded data sources. uses file_loc variable in global variable for file path
# specify the folder name to store the downloaded files.
# these folder must already exist

ds_folder = "DS"
ds_dest_file = os.path.join(file_loc, export_file_loc, "DataSourceList.xlsx")
ds_file_loc = os.path.join(file_loc, ds_folder)

create_file_locations()

# -----------------------------------Session Authentication to Tableau Server
# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about the data sources on your site."

# Prompt the user with the script name and description
print(f"\nYou are running the {script_name} script. {script_description}")


# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

print(f"Begin {script_name}. This might take several minutes.")

server = TSC.Server(portal_url)

# if using SSL uncomment below
# server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# to bypass SSL, use below
# server.add_http_options({'verify': False})

server.use_server_version()


# ------------------------------- Download Data Source
# This section will:
# download data source in a specified folder location

start_time = time.time()

create_file_locations()

ds_data = []  # list to store all datasource information
proj_data = []  # list to store all project information
conn_data = []  # list to store all data connection data

with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)
    all_projects = list(TSC.Pager(server.projects, req_options))
    all_datasources = list(TSC.Pager(server.datasources, req_options))

    for proj in all_projects:
        proj_values = [proj.id, proj.name, proj.parent_id]
        proj_data.append(proj_values)

    for ds in all_datasources:
        # get owner of the data source
        ds_owners = server.users.get_by_id(ds.owner_id)
        ds_owner_name = ds_owners.email

        values = [
            ds.name,
            ds.id,
            ds.project_id,
            ds.project_name,
            ds.has_extracts,
            ds.description,
            ds_owner_name,
        ]
        ds_data.append(values)

        # get connection information for each data source
        server.datasources.populate_connections(ds)
        for connection in ds.connections:
            conn_values = [
                ds.name,
                ds.id,
                connection.id,
                connection.connection_type,
                connection.username,
                connection.password,
                connection.embed_password,
                connection.server_address,
                connection.server_port,
            ]
            conn_data.append(conn_values)
            print(
                f"Extracting data source [{ds.name}] from project [{ds.project_name}] with connection type [{connection.connection_type}]"
            )
            time.sleep(1)

        time.sleep(1)

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
print("Creating data frames with Data Source details. Please wait.")
ds_df = pd.DataFrame(
    ds_data,
    columns=[
        "Datasource Name",
        "Datasource ID",
        "Project ID",
        "Project Name",
        "Has Extracts",
        "Description",
        "Owner Name",
    ],
)

# build project path of datasources
print("Building Project Paths, please wait.")
temp_proj_df = proj_df[["Project ID", "Project Name", "Parent Project ID"]].copy()
temp_proj_df.rename(columns={"Project ID": "ID", "Project Name": "Name"}, inplace=True)
temp_ds_df = ds_df[["Datasource ID", "Datasource Name", "Project ID"]].copy()
temp_ds_df.rename(
    columns={
        "Datasource ID": "ID",
        "Datasource Name": "Name",
        "Project ID": "Parent Project ID",
    },
    inplace=True,
)

union_proj_ds_df = pd.concat([temp_proj_df, temp_ds_df])
union_proj_ds_df_list = list(
    zip(union_proj_ds_df["Parent Project ID"], union_proj_ds_df["ID"])
)

relations_ds = parse_relations(union_proj_ds_df_list)
path_ds = list(flatten_hierarchy(relations_ds))

path_key_ds = {}
sep = "//"
for path in path_ds:
    temp_ds = []
    if not path:
        continue
    path_len = len(path)
    for index, y in enumerate(path):
        name = union_proj_ds_df.loc[(union_proj_ds_df["ID"] == y)]
        if name.empty:
            name = [""]
        else:
            name = list(name["Name"].values)
        if index < path_len - 1:
            temp_ds.append(name)
        sum_list = sum(temp_ds, [])
    path_final = sep.join(sum_list)
    path_key_ds.setdefault(path[path_len - 1], []).append(path_final)

path_df_ds = pd.DataFrame.from_dict(path_key_ds, orient="index", columns=["Path"])

ds_df_path = pd.merge(ds_df, path_df_ds, left_on="Datasource ID", right_index=True)

conn_df = pd.DataFrame(
    conn_data,
    columns=[
        "Data Source Name",
        "Data Source ID",
        "Connection ID",
        "Connection Type",
        "User Name",
        "Password",
        "Embed Password",
        "Server Address",
        "Server Port",
    ],
)

print("Writing results to file. Please wait.")
ds_df_path.to_csv(ds_download_file, header=True, index=False)

with pd.ExcelWriter(ds_dest_file) as writer:
    ds_df_path.to_excel(writer, sheet_name="Data Source List", index=False)
    conn_df.to_excel(writer, sheet_name="Connection List", index=False)

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

print(f"Completed {script_name} in {duration}. Please view file {ds_dest_file}.")
