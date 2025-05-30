import os
import sys

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import ast
import time
from dotenv import load_dotenv
import pandas as pd
import tableauserverclient as TSC
from Shared_TSC_GlobalFunctions import *
from Shared_TSC_GlobalVariables import *

# Load configuration variables
auth_variables = read_config("config.ini")
load_dotenv()

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

separator = "//"

# If migrating to Tableau Cloud, set to True.
cloud_destination = False
email_domain = "slalom.com"

# Set the default content_permissions to ManagedByOwner
content_permissions = "ManagedByOwner"

# If you wish to delete default permissions when creating new Projects,
# change this value to True. Otherwise, it will leave defaults intact.
delete_default_permissions = False

# If you wish to update the project owner during migration,
# change this value to True. Otherwise, it will leave the owner unchanged.
update_project_owner = False

project_source_file = "./ProjectList.csv"
# project_permission_source_file = "./ProjectPermissions.csv"

class Projects:
    def get_top_level(path_segments):
        return path_segments[0]

    def get_parent(path_segments: list):
        if len(path_segments) >= 2:
            return path_segments[-2]
        else:
            return None
        
    def create_children(top_level_project, parent_project, project_depth):
        parent_project_id = parent_project.id
        parent_project_name = parent_project.name
        project_depth += 1

        # Filter the dataframe by depth and parent project name
        child_project_df = (
            project_df.loc[
                (project_df["Depth"] == project_depth)
                & (project_df["Path Segments"][-2] == parent_project_name)
                & (project_df["Top-Level Project"] == top_level_project)
            ]
            .sort_values(by="Project Name")
            .reset_index(drop=True)
        )

        for index, row in child_project_df.iterrows():
            project_name = row["Project Name"]
            project_description = row["Project Description"]
            top_level_project = project_name
            
            if cloud_destination:
                project_owner_name = f"{row["Grantee Name"]}@{email_domain}"
            else:
                project_owner_name = row["Grantee Name"] #for Tableau Server

            project_item = TSC.ProjectItem(
                name=project_name,
                parent_id=parent_project_id,
                description=project_description,
                content_permissions=content_permissions,
            )

            # Create the new project and return the result to create child projects
            new_project = server.projects.create(project_item)

            time.sleep(0.5)

            # Update the new Project with the Project Owner ID
            if update_project_owner:
                Projects.set_ownership(project_owner_name, new_project)

            # Remove the default permissions on the new Project
            if delete_default_permissions:
                Projects.remove_default_permissions(new_project)

            Projects.create_children(top_level_project, project_name, project_depth)

        return

    def remove_default_permissions(new_project):
        # get default permissions on newly created projects then delete them
        server.projects.populate_permissions(new_project)
        server.projects.populate_datasource_default_permissions(new_project)
        server.projects.populate_workbook_default_permissions(new_project)
        server.projects.populate_flow_default_permissions(new_project)

        permissions = new_project.permissions
        default_ds_permissions = new_project.default_datasource_permissions
        default_wb_permissions = new_project.default_workbook_permissions
        default_flow_permissions = new_project.default_flow_permissions

        # remove default project permissions for each group/grantee
        for permission in permissions:
            grantee = permission.grantee
            capabilities = permission.capabilities
            rules_to_delete = [
                TSC.PermissionsRule(grantee=grantee, capabilities=capabilities)
            ]
            server.projects.delete_permission(new_project, rules_to_delete)

            time.sleep(0.5)

        # remove default datasource permissions
        if default_ds_permissions:
            for ds_permission in default_ds_permissions:
                grantee = ds_permission.grantee
                capabilities = ds_permission.capabilities
                rules_to_delete = TSC.PermissionsRule(
                    grantee=grantee, capabilities=capabilities
                )
                server.projects.delete_datasource_default_permissions(
                    new_project, rules_to_delete
                )

                time.sleep(0.5)

        # remove default workbook permissions
        if default_wb_permissions:
            for wb_permission in default_wb_permissions:
                grantee = wb_permission.grantee
                capabilities = wb_permission.capabilities
                rules_to_delete = TSC.PermissionsRule(
                    grantee=wb_permission.grantee, capabilities=capabilities
                )
                server.projects.delete_workbook_default_permissions(
                    new_project, rules_to_delete
                )

                time.sleep(0.5)

        # remove default flow permissions
        if default_flow_permissions:
            for flow_permission in default_flow_permissions:
                grantee = flow_permission.grantee
                capabilities = flow_permission.capabilities
                rules_to_delete = TSC.PermissionsRule(
                    grantee=grantee, capabilities=capabilities
                )
                server.projects.delete_flow_default_permissions(
                    new_project, rules_to_delete
                )

                time.sleep(0.5)

        return

    def set_ownership(project_owner_name, new_project):
        req_options = TSC.RequestOptions()
        req_options.filter.add(TSC.Filter(
            TSC.RequestOptions.Field.Name,
            TSC.RequestOptions.Operator.Equals,
            project_owner_name))
        
        users = list(TSC.Pager(server.users, req_options))
        for user in users:
            project_owner = user
        
        new_project.owner_id = project_owner.id
        server.projects.update(new_project)

        time.sleep(0.5)

        return

# Read the Project source file
project_df = pd.read_csv(project_source_file)

# Interpret Path Segments as a list and determine the Top-Level and Parent Project
project_df["Path Segments"] = project_df["Path Segments"].apply(ast.literal_eval)
project_df["Parent Name"] = project_df["Path Segments"].apply(Projects.get_parent)
project_df["Top-Level Project"] = project_df["Path Segments"].apply(Projects.get_top_level)

# Sort the Project dataframe by Depth, Path, then Project Name
project_df.sort_values(by=["Depth", "Path", "Project Name"]).reset_index(drop=True)

# Get the max depth of the Project hierarchy
max_depth = project_df["Depth"].max()

# Get the count of Projects to be created
project_count = len(project_df.index)

# Create a Server Authentication Session
with server.auth.sign_in(tableau_auth):
    # Set the Parent Project ID to None for top-level projects
    parent_project_id = None
    project_depth = 0

    # Filter the dataframe by top-level projects (Depth == 0)
    top_level_project_df = project_df.loc[project_df["Depth"] == project_depth]\
        .sort_values(by="Project Name").reset_index(drop=True)

    for index, row in top_level_project_df.iterrows():
        project_name = row["Project Name"]
        project_description = row["Project Description"]
        top_level_project = project_name

        if cloud_destination:
            project_owner_name = f"{row["Grantee Name"]}@{email_domain}"
        else:
            project_owner_name = row["Grantee Name"] #for Tableau Server

        project_item = TSC.ProjectItem(
            name=project_name,
            parent_id=parent_project_id,
            description=project_description,
            content_permissions=content_permissions,
        )

        # Create the new project and return the result to create child projects
        new_project = server.projects.create(project_item)

        time.sleep(0.5)

        # Update the new Project with the Project Owner ID
        if update_project_owner:
            Projects.set_ownership(project_owner_name, new_project)

        # Remove the default permissions on the new Project
        if delete_default_permissions:
            Projects.remove_default_permissions(new_project)

        Projects.create_children(top_level_project, project_name, project_depth)
