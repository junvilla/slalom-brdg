# GetProject.py connects to Tableau Server
# gets projects and project attributes then prints the list in csv
# The file can be used as a source to create projects in Tableau

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
# File location for Exporting Projects metadata
project_dest_file = file_loc + "ProjectList.xlsx"

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download data sources from your site."

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

# ------------------------------- Get Projects
start_time = time.time()

# This section will:
# query Tableau and get a list of projects, workbooks, data sources and project attributes
# Save the list in a dataframe
# write to excel file

# empty array
data = []  # list to store project metadata
permission_data = []  # list to store project permissions
wb_permission_data = []  # list to store workbook permissions in a project
ds_permission_data = []  # list to store data source permissions in a project
flow_permission_data = []  # list to store flow permissions in a project
lens_permission_data = []  # list to store ask data lens permissions in a project
group_data = []  # list to store group names for project permissions
user_data = []  # list to store user names for project permissions
ds_data = []  # list to store data source metadata
wb_data = []  # list to store workbook metadata

with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)
    all_project_items = list(TSC.Pager(server.projects, req_options))
    all_users = list(TSC.Pager(server.users, req_options))
    all_groups = list(TSC.Pager(server.groups, req_options))
    # all_workbooks = list(TSC.Pager(server.workbooks, req_options))
    # all_datasource = list(TSC.Pager(server.datasources, req_options))
    # all_datasource, pagination_item = server.datasources.get()

    for groups in all_groups:
        server.groups.populate_users(groups)
        group_values = [groups.id, groups.name]
        group_data.append(group_values)
        for user in groups.users:
            user_values = [user.id, user.name]
            user_data.append(user_values)

    # for ds in all_datasource:
    #     ds_values = [ds.project_id, ds.id, ds.name]
    #     ds_data.append(ds_values)
    #
    # for wb in all_workbooks:
    #     wb_values = [wb.project_id, wb.id, wb.name]
    #     wb_data.append(wb_values)

    for proj in all_project_items:
        # get project permissions
        server.projects.populate_permissions(proj)
        server.projects.populate_workbook_default_permissions(proj)
        server.projects.populate_datasource_default_permissions(proj)
        server.projects.populate_flow_default_permissions(proj)
        server.projects.populate_lens_default_permissions(proj)

        # project
        proj_permissions = proj.permissions

        # workbook
        default_wb_permissions = proj.default_workbook_permissions
        # # data source
        default_ds_permissions = proj.default_datasource_permissions
        # # flow
        default_flow_permissions = proj.default_flow_permissions
        # # data lens
        default_lens_permissions = proj.default_lens_permissions

        if proj_permissions:
            for permission in proj_permissions:
                grantee = permission.grantee
                capabilities = permission.capabilities
                permission_values = [
                    proj.id,
                    proj.name,
                    capabilities,
                    grantee.tag_name,
                    grantee.id,
                    "Project",
                ]
                permission_data.append(permission_values)

        if default_wb_permissions:
            for wb_permissions in default_wb_permissions:
                wb_grantee = wb_permissions.grantee
                wb_capabilities = wb_permissions.capabilities
                wb_permissions_values = [
                    proj.id,
                    proj.name,
                    wb_capabilities,
                    wb_grantee.tag_name,
                    wb_grantee.id,
                    "Workbook",
                ]
                wb_permission_data.append(wb_permissions_values)

        if default_ds_permissions:
            for ds_permissions in default_ds_permissions:
                ds_grantee = ds_permissions.grantee
                ds_capabilities = ds_permissions.capabilities
                ds_permissions_values = [
                    proj.id,
                    proj.name,
                    ds_capabilities,
                    ds_grantee.tag_name,
                    ds_grantee.id,
                    "Data Source",
                ]
                ds_permission_data.append(ds_permissions_values)

        if default_flow_permissions:
            for flow in default_flow_permissions:
                flow_grantee = flow.grantee
                flow_capabilities = flow.capabilities
                flow_permissions_values = [
                    proj.id,
                    proj.name,
                    flow_capabilities,
                    flow_grantee.tag_name,
                    flow_grantee.id,
                    "Data Flow",
                ]
                flow_permission_data.append(flow_permissions_values)

        if default_lens_permissions:
            for lens in default_lens_permissions:
                lens_grantee = lens.grantee
                lens_capabilities = lens.capabilities
                lens_permissions_values = [
                    proj.id,
                    proj.name,
                    lens_capabilities,
                    lens_grantee.tag_name,
                    lens_grantee.id,
                    "Data Lens",
                ]
                lens_permission_data.append(lens_permissions_values)

        parent_proj_name = ""
        if any(char in invalid_char for char in proj.name):
            special_char_flag = "Name has special characters which might cause problems migrating this object"
        else:
            special_char_flag = ""
        values = [
            proj.id,
            proj.name,
            proj.owner_id,
            proj.description,
            proj.parent_id,
            special_char_flag,
        ]
        data.append(values)

# start building the data frames to store project metadata
df = pd.DataFrame(
    data,
    columns=[
        "Project ID",
        "Project Name",
        "Project Owner ID",
        "Project Description",
        "Parent Project ID",
        "Special Character Flag",
    ],
)

# identify the depth of each project whether level 1 (top level), level 2 (child), level 3 (grand child) etc
df["depth"] = df["Parent Project ID"].apply(make_depth(df))

# remove projects with no parents, create new data frame to join
parent_df = df[["Parent Project ID"]].copy()

# build dataframe to get project name and other attributes

parent_df = parent_df.dropna()
parent_df = parent_df[["Parent Project ID"]].drop_duplicates()

parent_df = pd.merge(
    parent_df,
    df[["Project ID", "Project Name"]],
    left_on="Parent Project ID",
    right_on="Project ID",
    how="left",
)

parent_df = parent_df.drop("Project ID", axis=1)

parent_df.rename(columns={"Project Name": "Parent Project Name"}, inplace=True)

# final df will have project id/name and parent project id/name
project_df = pd.merge(df, parent_df, on="Parent Project ID", how="left")

# build dataframe to store groups and users permissions to the project
group_df = pd.DataFrame(group_data)
user_df = pd.DataFrame(user_data)
group_user_df = pd.concat([group_df, user_df], ignore_index=True)
group_user_df.columns = ["Group or User ID", "Grantee Name"]
group_user_df.drop_duplicates(inplace=True)

permission_df = pd.DataFrame(
    permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Capability",
        "Grantee Type",
        "Group or User ID",
        "Permission Type",
    ],
)

permission_df = pd.merge(
    permission_df, group_user_df, on="Group or User ID", how="inner"
)

wb_permission_df = pd.DataFrame(
    wb_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Capability",
        "Grantee Type",
        "Group or User ID",
        "Permission Type",
    ],
)

wb_permission_df = pd.merge(
    wb_permission_df, group_user_df, on="Group or User ID", how="inner"
)

ds_permission_df = pd.DataFrame(
    ds_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Capability",
        "Grantee Type",
        "Group or User ID",
        "Permission Type",
    ],
)

ds_permission_df = pd.merge(
    ds_permission_df, group_user_df, on="Group or User ID", how="inner"
)

flow_permission_df = pd.DataFrame(
    flow_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Capability",
        "Grantee Type",
        "Group or User ID",
        "Permission Type",
    ],
)

flow_permission_df = pd.merge(
    flow_permission_df, group_user_df, on="Group or User ID", how="inner"
)

lens_permission_df = pd.DataFrame(
    lens_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Capability",
        "Grantee Type",
        "Group or User ID",
        "Permission Type",
    ],
)

lens_permission_df = pd.merge(
    lens_permission_df, group_user_df, on="Group or User ID", how="inner"
)

project_df = project_df[
    [
        "Project ID",
        "depth",
        "Project Name",
        "Project Description",
        "Parent Project ID",
        "Parent Project Name",
        "Project Owner ID",
        "Special Character Flag",
    ]
].sort_values(by="depth")

# set up project path by declaring None as top level project
project_df["Parent Project ID"].fillna("No Parent", inplace=True)
project_df["Parent Project Name"].fillna("No Parent", inplace=True)
project_df["Object Type"] = "Project"

# variables to build the project path data frame
sep = "//"
level_path = []

max_depth = project_df["depth"].max()

# below could probably be a function - pass list object, filter data frame for name - BACKLOG
# build the parent child list one level at a time, then iterate each parent child relationship to build the project path
for i in range(0, max_depth + 1):
    level_df = project_df.loc[project_df["depth"] <= i]
    level_list = list(zip(level_df["Parent Project ID"], level_df["Project ID"]))
    level_relations = parse_relations(level_list)
    level_path_key = list(flatten_hierarchy(level_relations))
    level_path.append(level_path_key)
    path_key_project = sum(level_path, [])
    path_key_project = pd.unique(path_key_project).tolist()

project_path_dict = {}

for l_path in path_key_project:
    new_path = []
    if not l_path:
        continue
    level_path_len = len(l_path)
    for index, x in enumerate(l_path):
        proj_name = project_df.loc[(project_df["Project ID"] == x)]
        if proj_name.empty:
            proj_name = [""]
        else:
            proj_name = list(proj_name["Project Name"].values)
        if index < level_path_len - 1:
            new_path.append(proj_name)
        project_path = sum(new_path, [])
    project_path_final = sep.join(project_path)
    project_path_dict.setdefault(l_path[level_path_len - 1], []).append(
        project_path_final
    )

path_df_project = pd.DataFrame.from_dict(
    project_path_dict, orient="index", columns=["Path"]
)

# add permissions and groups to final df
project_df = pd.merge(
    project_df,
    group_user_df,
    left_on="Project Owner ID",
    right_on="Group or User ID",
    how="left",
)

project_df.rename(columns={"Name": "Project Owner Name"}, inplace=True)

# let's build the data frame to separate all Tableau Objects and print to excel
project_df_path = pd.merge(
    project_df, path_df_project, left_on="Project ID", how="left", right_index=True
)

project_df_path["Parent Project ID"].replace({"No Parent": ""}, inplace=True)
project_df_path["Parent Project Name"].replace({"No Parent": ""}, inplace=True)

project_df_path.drop_duplicates(inplace=True)
permission_df_path = pd.merge(
    permission_df, path_df_project, left_on="Project ID", how="left", right_index=True
)
wb_permission_df_path = pd.merge(
    wb_permission_df,
    path_df_project,
    left_on="Project ID",
    how="left",
    right_index=True,
)
ds_permission_df_path = pd.merge(
    ds_permission_df,
    path_df_project,
    left_on="Project ID",
    how="left",
    right_index=True,
)
flow_permission_df_path = pd.merge(
    flow_permission_df,
    path_df_project,
    left_on="Project ID",
    how="left",
    right_index=True,
)
lens_permission_df_path = pd.merge(
    lens_permission_df,
    path_df_project,
    left_on="Project ID",
    how="left",
    right_index=True,
)

# export the permissions of the project. this file can be used as a template to update permissions
permission_df_path_final = pd.concat(
    [
        permission_df_path,
        wb_permission_df_path,
        ds_permission_df_path,
        flow_permission_df_path,
        lens_permission_df_path,
    ],
    ignore_index=True,
)

# export project information, to be used as the import file
project_df_path.to_csv(file_loc + "ProjectList.csv", header=True, index=False)
permission_df_path_final.to_csv(
    file_loc + "ProjectPermission.csv", header=True, index=False
)

with pd.ExcelWriter(project_dest_file) as writer:
    project_df_path.to_excel(writer, sheet_name="Project List", index=False)
    permission_df_path.to_excel(writer, sheet_name="Project Permission", index=False)
    wb_permission_df_path.to_excel(
        writer, sheet_name="Project Workbook Permission", index=False
    )
    ds_permission_df_path.to_excel(
        writer, sheet_name="Project DataSource Permission", index=False
    )
    lens_permission_df_path.to_excel(
        writer, sheet_name="Project AskDataLens Permission", index=False
    )
    flow_permission_df_path.to_excel(
        writer, sheet_name="Project Flow Permission", index=False
    )
    # wb_ds_df_path.to_excel(writer, sheet_name='Workbook Data Source List', index=False)

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

print(
    f"\nCompleted {script_name} in {duration}. Please check your log files for any errors."
)
