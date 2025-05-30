# GetDestinationContent.py connects to the destination (e.g., Tableau Cloud)
# and gets a list of all content, building project paths for each content item.
# The script then matches content by full path to the contents of the file
# created by GetContentInventory.py.
#
# This script is designed for retroactive alignment of content resources,
# and the results should be evaluated and validated before using the results
# in any subsequent content creation script, such as:
#   CreateTasks.py
#   CreateSubscriptions.py
#   CreateFavorites.py
#   PublishCustomViews.py

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
from dotenv import load_dotenv
import time
import numpy as np
import pandas as pd
import tableauserverclient as TSC
from logging_config import *

config = read_config("config.ini")
load_dotenv()

# File location for Content Inventory metadata
destination_inventory_file = os.path.join(file_loc, "destination_manifest.xlsx")

content_inventory_file = os.path.join(manifest_loc, "manifest.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets destination site content and maps it to the source by the full project path."

# Prompt the user with the script name and description
logging.info(f"You are running the {script_name} script. {script_description}")

# Load the authentication variables for the Destination environment
portal_url = config["DESTINATION"]["URL"]
site_id = config["DESTINATION"]["SITE_CONTENT_URL"]
token_name = config["DESTINATION"]["ACCESS_TOKEN_NAME"]
token_value = os.environ.get("DESTINATION_TOKEN_SECRET")

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)

logging.info(f"\nBegin {script_name}. This might take several minutes.")

# # -----------------------------------Session Authentication to Tableau Server

server = TSC.Server(portal_url)

# # if using SSL uncomment below
# # server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
# # to bypass SSL, use below
# # server.add_http_options({'verify': False})

server.use_server_version()

# -------------------------------end Session Authentication

invalid_chars = {"-", ".", "_", "/"}

start_time = time.time()


def get_child_projects_recursive(
    project_list: list[TSC.ProjectItem], parent_id: str, path_segments: list[str]
):

    project_data = []

    for project in project_list:
        if project.parent_id == parent_id:
            separator = "/"
            new_path_segments = path_segments + [project.name]
            new_path = separator.join(new_path_segments)

            p_data = [
                project.id,
                "",  # ContentUrl, null for Projects
                new_path_segments,
                separator,
                new_path,
                project.name,
            ]

            project_data.append(p_data)

            # Recursively get child projects
            project_data.extend(
                get_child_projects_recursive(
                    project_list, project.id, new_path_segments
                )
            )

    return project_data


# Establish empty lists/arrays to store data
group_data = []
user_data = []
# project_data is created in the main/recursive function
datasource_data = []
workbook_data = []
view_data = []
flow_data = []

# Create a Server Authentication Session
with server.auth.sign_in(tableau_auth):

    logging.info("Getting TableauItem inventory from Tableau Server.")
    Content.get_all(server, ContentLocation.destination)

    logging.info("Extracting Users...")
    all_users: list[TSC.UserItem] = Content.load(
        ContentItem.users, ContentLocation.destination
    )

    logging.info("Extracting Groups...")
    all_groups: list[TSC.GroupItem] = Content.load(
        ContentItem.groups, ContentLocation.destination
    )

    logging.info("Extracting Projects...")
    all_projects: list[TSC.ProjectItem] = Content.load(
        ContentItem.projects, ContentLocation.destination
    )

    logging.info("Extracting Data Sources...")
    all_datasources: list[TSC.DatasourceItem] = Content.load(
        ContentItem.datasources, ContentLocation.destination
    )

    logging.info("Extracting Workbooks...")
    all_workbooks: list[TSC.WorkbookItem] = Content.load(
        ContentItem.workbooks, ContentLocation.destination
    )

    logging.info("Extracting Views...")
    all_views: list[TSC.ViewItem] = Content.load(
        ContentItem.views, ContentLocation.destination
    )

    logging.info("Extracting Flows...")
    try:
        all_flows: list[TSC.FlowItem] = Content.load(
            ContentItem.flows, ContentLocation.destination
        )
    except:
        all_flows = []

    logging.info("Building a list of top-level Projects...")
    # Get the list of all top-level projects
    top_level_projects: list[TSC.ProjectItem] = []

    for project in all_projects:
        if project.parent_id is None:
            top_level_projects.append(project)

    project_data = []

    logging.info("\nBuilding Project list...")
    for project in top_level_projects:
        separator = "/"
        path_segments = [project.name]
        path = project.name  # for top-level Projects, the path is the Project name

        p_data = [
            project.id,
            "",  # ContentUrl, null for Projects
            path_segments,
            separator,
            path,
            project.name,
        ]

        project_data.append(p_data)

        # Recursively get all child projects
        project_data.extend(
            get_child_projects_recursive(all_projects, project.id, path_segments)
        )


# Build a list of User data
logging.info("Building User list...")
for user in all_users:
    separator = "\\"
    path_segments = [user.domain_name, user.email]
    path = separator.join(path_segments)  # Path, in this case, 'domain\username'

    u_data = [
        user.id,
        "",  # ContentUrl
        path_segments,
        separator,
        path,
        user.email,
    ]

    user_data.append(u_data)

# Build a list of Group data
logging.info("Building Group list...")
for group in all_groups:
    separator = "\\"
    path_segments = [group.domain_name, group.name]
    path = separator.join(path_segments)  # Path, in this case, 'domain\group name'

    g_data = [
        group.id,
        "",  # ContentUrl
        path_segments,
        separator,
        path,
        group.name,
    ]

    group_data.append(g_data)

# Build a list of Data Source data
logging.info("Building Data Source list...")
for datasource in all_datasources:
    # Get the path segments of the parent Project
    for project in project_data:
        if project[0] == datasource.project_id:
            path_segments = project[2]
            break

    separator = "/"
    path_segments = path_segments + [datasource.name]
    path = separator.join(path_segments)  # Path, in this case, path/datasource.name

    ds_data = [
        datasource.id,
        datasource.content_url,
        path_segments,
        separator,
        path,
        datasource.name,
    ]

    datasource_data.append(ds_data)

# Build a list of Workbook data
logging.info("Building Workbook list...")
for workbook in all_workbooks:
    # Get the path segments of the parent Project
    for project in project_data:
        if project[0] == workbook.project_id:
            path_segments = project[2]
            break

    separator = "/"
    path_segments = path_segments + [workbook.name]
    path = separator.join(path_segments)  # Path, in this case, path/workbook.name

    wb_data = [
        workbook.id,
        workbook.content_url,
        path_segments,
        separator,
        path,
        workbook.name,
    ]

    workbook_data.append(wb_data)


# Build a list of View data
logging.info("Building View list...")
for view in all_views:
    # Get the path segments of the Workbook containing the View
    for workbook in workbook_data:
        if workbook[0] == view.workbook_id:
            path_segments = workbook[2]
            break

    separator = "/"
    path_segments = path_segments + [view.name]
    path = separator.join(path_segments)  # Path, in this case, path/workbook/view.name

    v_data = [
        view.id,
        view.content_url,
        path_segments,
        separator,
        path,
        view.name,
    ]

    view_data.append(v_data)


if len(all_flows) > 0:
    # Build a list of Flow data
    logging.info("Building Flow list...")
    for flow in all_flows:
        # Get the path segments of the parent Project
        for project in project_data:
            if project[0] == flow.project_id:
                path_segments = project[2]
                break

        separator = "/"
        path_segments = path_segments + [flow.name]
        path = separator.join(path_segments)  # Path, in this case, path/flow.name

        f_data = [
            flow.id,
            flow.webpage_url,
            path_segments,
            separator,
            path,
            flow.name,
        ]

        flow_data.append(f_data)


column_headers = [
    "Destination Id",
    "Destination ContentUrl",
    "Destination PathSegments",
    "Destination PathSeparator",
    "Destination Path",
    "Destination Name",
]

logging.info("\nWriting results to DataFrames...")
# Build a dataframe of User components
destination_user_df = pd.DataFrame(user_data, columns=column_headers)

# Build a dataframe of Group components
destination_group_df = pd.DataFrame(group_data, columns=column_headers)

# Build a dataframe of Project components
destination_project_df = pd.DataFrame(project_data, columns=column_headers)

# Build a dataframe of Data Source components
destination_datasource_df = pd.DataFrame(datasource_data, columns=column_headers)

# Build a dataframe of Workbook components
destination_workbook_df = pd.DataFrame(workbook_data, columns=column_headers)

# Build a dataframe of View components
destination_view_df = pd.DataFrame(view_data, columns=column_headers)

if len(flow_data) > 0:
    # Build a dataframe of Flow components
    destination_flow_df = pd.DataFrame(flow_data, columns=column_headers)
else:
    destination_flow_df = pd.DataFrame(None, columns=column_headers)


logging.info("Updating and concatenating dataframes...")

# Add column with object type to each dataframe
destination_user_df.insert(0, "Content Type", "User")
destination_group_df.insert(0, "Content Type", "Group")
destination_project_df.insert(0, "Content Type", "Project")
destination_datasource_df.insert(0, "Content Type", "Datasource")
destination_workbook_df.insert(0, "Content Type", "Workbook")
destination_view_df.insert(0, "Content Type", "View")
destination_flow_df.insert(0, "Content Type", "Flow")

# Concatenate the separate dataframes into a single dataframe
destination_content_df = pd.concat(
    [
        destination_user_df,
        destination_group_df,
        destination_project_df,
        destination_datasource_df,
        destination_workbook_df,
        destination_view_df,
        destination_flow_df,
    ]
)

# For testing, write the destination content to an XLSX file.
with pd.ExcelWriter(destination_inventory_file) as writer:
    destination_content_df.to_excel(
        writer, sheet_name="Destination Content", index=False
    )

# Import the manifest.json/ContentInventory.xlsx details
logging.info("Importing the source content...")
manifest_df = Manifest.read()

# Set the nan values to None
manifest_df = manifest_df.replace(np.nan, None)

# Report details from each dataframe
logging.info(f"Source DataFrame contains {str(len(manifest_df))} rows.")
logging.info(f"Destination DataFrame contains {str(len(destination_content_df))} rows.")

updated_manifest = []

# Iterate through manifest_df, matching items by "Path"
logging.info(
    "Matching content from source and destination DataFrames by Path. This will take a while."
)
for index, row in manifest_df.iterrows():
    content_type = row["Content Type"]
    source_id = row["Source Id"]
    source_contenturl = row["Source ContentUrl"]
    source_pathsegments = row["Source PathSegments"]
    path_separator = row["Source PathSeparator"]
    source_path = row["Source Path"]
    source_name = row["Source Name"]
    mapped_pathsegments = row["Mapped PathSegments"]
    mapped_path = row["Mapped Path"]
    mapped_name = row["Mapped Name"]
    destination_id = row["Destination Id"]
    destination_contenturl = row["Destination ContentUrl"]
    destination_pathsegments = row["Destination PathSegments"]
    destination_path = row["Destination Path"]
    destination_name = row["Destination Name"]

    # If Destination Id is empty/None, try to match the values by Path.
    if not destination_id:

        # Filter destination_content_df by Mapped Path to get the matching row
        destination_details = destination_content_df[
            destination_content_df["Destination Path"] == mapped_path
        ]

        if not destination_details.empty:
            # Populate the destination content details
            destination_id = destination_details.iloc[0]["Destination Id"]
            destination_contenturl = destination_details.iloc[0][
                "Destination ContentUrl"
            ]
            destination_pathsegments = destination_details.iloc[0][
                "Destination PathSegments"
            ]
            destination_path = destination_details.iloc[0]["Destination Path"]
            destination_name = destination_details.iloc[0]["Destination Name"]

        # If no match was found based on Mapped Path, presume content was not migrated
        # Destination content details set to None
        else:
            destination_id = None
            destination_contenturl = None
            destination_pathsegments = None
            destination_path = None
            destination_name = None

    # Create an updated manifest entry of content details
    manifest_entry = {
        "Content Type": content_type,
        "Source Id": source_id,
        "Source ContentUrl": source_contenturl,
        "Source PathSegments": source_pathsegments,
        "Source PathSeparator": path_separator,
        "Source Path": source_path,
        "Source Name": source_name,
        "Mapped PathSegments": mapped_pathsegments,
        "Mapped PathSeparator": path_separator,
        "Mapped Path": mapped_path,
        "Mapped Name": mapped_name,
        "Destination Id": destination_id,
        "Destination ContentUrl": destination_contenturl,
        "Destination PathSegments": destination_pathsegments,
        "Destination PathSeparator": path_separator,
        "Destination Path": destination_path,
        "Destination Name": destination_name,
    }

    # Append the updated manifest entry to the list
    updated_manifest.append(manifest_entry)

# Write the updated_manifest list to a DataFrame
manifest_df = pd.DataFrame(updated_manifest)

# Split manifest_df into separate dataframes by Content Type
user_df = manifest_df[manifest_df["Content Type"] == "User"]
group_df = manifest_df[manifest_df["Content Type"] == "Group"]
project_df = manifest_df[manifest_df["Content Type"] == "Project"]
datasource_df = manifest_df[manifest_df["Content Type"] == "Datasource"]
workbook_df = manifest_df[manifest_df["Content Type"] == "Workbook"]
view_df = manifest_df[manifest_df["Content Type"] == "View"]
flow_df = manifest_df[manifest_df["Content Type"] == "Flow"]

# Export Content Inventory information to sheets in the Excel file
logging.info("\nWriting results to XLSX file...")
with pd.ExcelWriter(content_inventory_file) as writer:
    user_df.to_excel(writer, sheet_name="User List", index=False)
    group_df.to_excel(writer, sheet_name="Group List", index=False)
    project_df.to_excel(writer, sheet_name="Project List", index=False)
    datasource_df.to_excel(writer, sheet_name="Data Source List", index=False)
    workbook_df.to_excel(writer, sheet_name="Workbook List", index=False)
    view_df.to_excel(writer, sheet_name="View List", index=False)
    flow_df.to_excel(writer, sheet_name="Flow List", index=False)

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

# Print final script results
logging.info(
    f"""\n
    Total Users: {len(user_df)}
    Total Groups: {len(group_df)}
    Total Projects: {len(project_df)}
    Total Data Sources: {len(datasource_df)}
    Total Workbooks: {len(workbook_df)}
    Total Views: {len(view_df)}
    Total Flows: {len(flow_df)}
    """
)
logging.info(
    f"\nCompleted {script_name} in {duration}. Please view file: {content_inventory_file}."
)
