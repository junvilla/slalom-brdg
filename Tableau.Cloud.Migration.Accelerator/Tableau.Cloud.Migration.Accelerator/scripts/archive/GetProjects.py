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
project_dest_file = os.path.join(file_loc, export_file_loc, "ProjectList.xlsx")

create_file_locations()

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about the projects on your site."

# Prompt the user with the script name and description
print(f"\nYou are running the {script_name} script. {script_description}")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

print(f"\nBegin {script_name}. This might take several minutes.")

# # -----------------------------------Session Authentication to Tableau Server

server = TSC.Server(portal_url)

# # if using SSL uncomment below
# # server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# # to bypass SSL, use below
# # server.add_http_options({'verify': False})

server.use_server_version()

# -------------------------------end Session Authentication

# ------------------------------- Get Projects
# This section will:
# query Tableau and get a list of projects, workbooks, data sources and project attributes
# Save the list in a dataframe
# write to excel file
separator = "/"
invalid_chars = {"-", ".", "_", "/"}

start_time = time.time()

def get_child_projects_recursive(parent_id, path_segments):
    req_options = TSC.RequestOptions(pagesize=1000)
    req_options.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.ParentProjectId,
            TSC.RequestOptions.Operator.Equals,
            parent_id,
        )
    )

    project_list = list(TSC.Pager(server.projects, req_options))
    project_paths = []

    for project in project_list:
        print(f"\nExtracting project: {project.name}")

        new_path_segments = path_segments + [project.name]
        new_path = separator.join(new_path_segments)

        project_data = [
            project.id,
            project.name,
            project.owner_id,
            project.description,
            special_char_flag,
            new_path,
            new_path_segments,
            len(new_path_segments) - 1,
        ]

        project_paths.append(project_data)

        # Get project permissions
        server.projects.populate_permissions(project)
        server.projects.populate_datasource_default_permissions(project)
        server.projects.populate_workbook_default_permissions(project)
        server.projects.populate_flow_default_permissions(project)

        extract_permissions(project, new_path, new_path_segments)

        time.sleep(0.5)

        # Recursively get child projects
        project_paths.extend(
            get_child_projects_recursive(project.id, new_path_segments)
        )

    return project_paths


def extract_permissions(project, path, segments):
    print(f"Extracting project permissions for: {project.name}")
    project_permissions = project.permissions
    project_datasource_permissions = project.default_datasource_permissions
    project_workbook_permissions = project.default_workbook_permissions
    project_flow_permissions = project.default_flow_permissions

    if project_permissions:
        for permission in project_permissions:
            grantee = permission.grantee
            capabilities = permission.capabilities
            permission_values = [
                project.id,
                project.name,
                path,
                segments,
                capabilities,
                grantee.tag_name,
                grantee.id,
                "Project",
            ]
            permission_data.append(permission_values)

        time.sleep(0.5)

    print(f"Extracting default datasource permissions for: {project.name}")
    if project_datasource_permissions:
        for ds_permissions in project_datasource_permissions:
            ds_grantee = ds_permissions.grantee
            ds_capabilities = ds_permissions.capabilities
            ds_permissions_values = [
                project.id,
                project.name,
                path,
                segments,
                ds_capabilities,
                ds_grantee.tag_name,
                ds_grantee.id,
                "Data Source",
            ]
            ds_permission_data.append(ds_permissions_values)

        time.sleep(0.5)

    print(f"Extracting default workbook permissions for: {project.name}")
    if project_workbook_permissions:
        for wb_permissions in project_workbook_permissions:
            wb_grantee = wb_permissions.grantee
            wb_capabilities = wb_permissions.capabilities
            wb_permissions_values = [
                project.id,
                project.name,
                path,
                segments,
                wb_capabilities,
                wb_grantee.tag_name,
                wb_grantee.id,
                "Workbook",
            ]
            wb_permission_data.append(wb_permissions_values)

        time.sleep(0.5)

    print(f"Extracting default flow permissions for: {project.name}")
    if project_flow_permissions:
        for flow in project_flow_permissions:
            flow_grantee = flow.grantee
            flow_capabilities = flow.capabilities
            flow_permissions_values = [
                project.id,
                project.name,
                path,
                segments,
                flow_capabilities,
                flow_grantee.tag_name,
                flow_grantee.id,
                "Data Flow",
            ]
            flow_permission_data.append(flow_permissions_values)

        time.sleep(0.5)

    print(f"Project and permissions extraction completed for: {project.name}")

    return


# Establish empty lists/arrays to store data
data = []
permission_data = []
ds_permission_data = []
wb_permission_data = []
flow_permission_data = []
group_data = []
user_data = []

# Create a Server Authentication Session
with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)

    # Before adding the filter, get groups and users
    all_groups = list(TSC.Pager(server.groups, req_options))
    all_users = list(TSC.Pager(server.users, req_options))

    # Build basic lists of group/user data
    for group in all_groups:
        server.groups.populate_users(group)
        group_values = [group.id, group.name]
        group_data.append(group_values)

    for user in all_users:
        user_values = [user.id, user.name]
        user_data.append(user_values)

    # Set the initial filter of null parent_project_id
    req_options.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.TopLevelProject,
            TSC.RequestOptions.Operator.Equals,
            True,
        )
    )

    # Get the list of all top-level projects
    top_level_projects = list(TSC.Pager(server.projects, req_options))

    project_paths = []

    for project in top_level_projects:
        print(f"\nExtracting project: {project.name}")

        if any(char in invalid_chars for char in project.name):
            special_char_flag = "WARNING"
        else:
            special_char_flag = None

        path_segments = [project.name]
        project_data = [
            project.id,
            project.name,
            project.owner_id,
            project.description,
            special_char_flag,
            project.name,  # In this case, also Path
            path_segments,
            len(path_segments) - 1,
        ]

        project_paths.append(project_data)

        # Get project permissions
        server.projects.populate_permissions(project)
        server.projects.populate_datasource_default_permissions(project)
        server.projects.populate_workbook_default_permissions(project)
        server.projects.populate_flow_default_permissions(project)

        extract_permissions(project, project.name, path_segments)

        time.sleep(0.5)

        # Recursively get all child projects
        project_paths.extend(get_child_projects_recursive(project.id, path_segments))

# Build a dataframe of Project components
project_df = pd.DataFrame(
    project_paths,
    columns=[
        "Project ID",
        "Project Name",
        "Project Owner ID",
        "Project Description",
        "Special Character Flag",
        "Path",
        "Path Segments",
        "Depth",
    ],
)

# Build a dataframe to store user/group permissions
group_df = pd.DataFrame(group_data)
user_df = pd.DataFrame(user_data)
group_user_df = pd.concat([group_df, user_df], ignore_index=True)
group_user_df.columns = ["LUID", "Grantee Name"]
group_user_df.drop_duplicates(inplace=True)

permission_df = pd.DataFrame(
    permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Path",
        "Path Segments",
        "Capability",
        "Grantee Type",
        "LUID",
        "Permission Type",
    ],
)

permission_df = pd.merge(permission_df, group_user_df, on="LUID", how="inner")

ds_permission_df = pd.DataFrame(
    ds_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Path",
        "Path Segments",
        "Capability",
        "Grantee Type",
        "LUID",
        "Permission Type",
    ],
)

ds_permission_df = pd.merge(ds_permission_df, group_user_df, on="LUID", how="inner")

wb_permission_df = pd.DataFrame(
    wb_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Path",
        "Path Segments",
        "Capability",
        "Grantee Type",
        "LUID",
        "Permission Type",
    ],
)

wb_permission_df = pd.merge(wb_permission_df, group_user_df, on="LUID", how="inner")

flow_permission_df = pd.DataFrame(
    flow_permission_data,
    columns=[
        "Project ID",
        "Project Name",
        "Path",
        "Path Segments",
        "Capability",
        "Grantee Type",
        "LUID",
        "Permission Type",
    ],
)

flow_permission_df = pd.merge(flow_permission_df, group_user_df, on="LUID", how="inner")

# Add owner details to the final Project dataframe
project_df = pd.merge(
    project_df,
    group_user_df,
    left_on="Project Owner ID",
    right_on="LUID",
    how="left",
)

project_df.rename(columns={"Grantee Name": "Project Owner Name"}, inplace=True)

all_permissions_df = pd.concat(
    [
        permission_df,
        ds_permission_df,
        wb_permission_df,
        flow_permission_df,
    ],
    ignore_index=True,
)

# Export Project information to CSV files
project_df.to_csv(project_source_file, header=True, index=False)
all_permissions_df.to_csv(project_permission_source_file, header=True, index=False)

# Export Project information to Excel files
with pd.ExcelWriter(project_dest_file) as writer:
    project_df.to_excel(writer, sheet_name="Project List", index=False)
    permission_df.to_excel(writer, sheet_name="Project Permission", index=False)
    ds_permission_df.to_excel(
        writer, sheet_name="Project DataSource Permission", index=False
    )
    wb_permission_df.to_excel(
        writer, sheet_name="Project Workbook Permission", index=False
    )

    flow_permission_df.to_excel(
        writer, sheet_name="Project Flow Permission", index=False
    )

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

print(f"\nCompleted {script_name} in {duration}. Please view file {project_dest_file}.")
