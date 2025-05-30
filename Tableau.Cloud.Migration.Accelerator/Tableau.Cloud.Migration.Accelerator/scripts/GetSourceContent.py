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
from logging_config import *


# -----------------------------------Enter variables
# File location for Exporting Projects metadata
content_inventory_file = os.path.join(file_loc, "ContentInventory.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = (
    "This script gets information about the content on your source site."
)

# Prompt the user with the script name and description
logging.info(f"You are running the {script_name} script. {script_description}")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")
load_dotenv()

# Load the authentication variables for the SOURCE environment
portal_url = config["SOURCE"]["URL"]
site_id = config["SOURCE"]["SITE_CONTENT_URL"]
token_name = config["SOURCE"]["ACCESS_TOKEN_NAME"]
token_value = os.environ.get("SOURCE_TOKEN_SECRET")

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
                new_path_segments,  # Mapped PathSegments
                separator,  # Mapped PathSeparator
                new_path,  # Mapped Path
                project.name,  # Mapped Name
                None,  # Destination Id
                None,  # Destination ContentUrl
                None,  # Destination PathSegments
                separator,  # Destination PathSeparator,
                None,  # Destination Path
                None,  # Destination Name
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
    Content.get_all(server, ContentLocation.source)

    logging.info("Extracting Users...")
    all_users: list[TSC.UserItem] = Content.load(
        ContentItem.users, ContentLocation.source
    )

    logging.info("Extracting Groups...")
    all_groups: list[TSC.GroupItem] = Content.load(
        ContentItem.groups, ContentLocation.source
    )

    logging.info("Extracting Projects...")
    all_projects: list[TSC.ProjectItem] = Content.load(
        ContentItem.projects, ContentLocation.source
    )

    logging.info("Extracting Data Sources...")
    all_datasources: list[TSC.DatasourceItem] = Content.load(
        ContentItem.datasources, ContentLocation.source
    )

    logging.info("Extracting Workbooks...")
    all_workbooks: list[TSC.WorkbookItem] = Content.load(
        ContentItem.workbooks, ContentLocation.source
    )

    logging.info("Extracting Views...")
    all_views: list[TSC.ViewItem] = Content.load(
        ContentItem.views, ContentLocation.source
    )

    logging.info("Extracting Flows...")
    all_flows: list[TSC.FlowItem] = Content.load(
        ContentItem.flows, ContentLocation.source
    )

    logging.info("Building a list of top-level Projects...")
    # Get the list of all top-level projects
    top_level_projects: list[TSC.ProjectItem] = []

    for project in all_projects:
        if project.parent_id is None:
            top_level_projects.append(project)

    project_data = []

    logging.info("Building Project list...")
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
            path_segments,  # Mapped PathSegments
            separator,  # Mapped PathSeparator
            path,  # Mapped Path
            project.name,  # Mapped Name
            None,  # Destination Id
            None,  # Destination ContentUrl
            None,  # Destination PathSegments
            separator,  # Destination PathSeparator
            None,  # Destination Path
            None,  # Destination Name
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
    path_segments = [user.domain_name, user.name]
    path = separator.join(path_segments)  # Path, in this case, 'domain\username'

    if user.email is None:
        user_email = user.name + "@" + config["USERS"]["EMAIL_DOMAIN"]
    else:
        user_email = user.email

    mapped_segments = ["TABID_WITH_MFA", user_email]
    mapped_path = separator.join(mapped_segments)

    u_data = [
        user.id,
        "",  # ContentUrl
        path_segments,
        separator,
        path,
        user.name,
        mapped_segments,  # Mapped PathSegments
        separator,  # Mapped PathSeparator
        mapped_path,  # Mapped Path
        user_email,  # Mapped Name, default = user email address
        None,  # Destination Id
        "",  # Destination ContentUrl
        None,  # Destination PathSegments
        separator,  # Destination PathSeparator
        None,  # Destination Path
        None,  # Destination Name, default = user email address
    ]

    user_data.append(u_data)

# Build a list of Group data
logging.info("Building Group list...")
for group in all_groups:
    separator = "\\"
    path_segments = [group.domain_name, group.name]
    path = separator.join(path_segments)  # Path, in this case, 'domain\group name'
    mapped_segments = ["local", group.name]
    mapped_path = separator.join(mapped_segments)

    g_data = [
        group.id,
        "",  # ContentUrl
        path_segments,
        separator,
        path,
        group.name,
        path_segments,  # Mapped PathSegments
        separator,  # Mapped PathSeparator
        path,  # Mapped Path
        group.name,  # Mapped Name
        None,  # Destination Id
        "",  # Destination ContentUrl
        mapped_segments,  # Destination PathSegments
        separator,  # Destination PathSeparator
        mapped_path,  # Destination Path
        group.name,  # Destination Name
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
        path_segments,  # Mapped PathSegments
        separator,  # Mapped PathSeparator
        path,  # Mapped Path
        datasource.name,  # Mapped Name
        None,  # Destination Id
        None,  # Destination ContentUrl
        None,  # Destination PathSegments
        separator,  # Destination PathSeparator
        None,  # Destination Path
        None,  # Destination Name
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
        path_segments,  # Mapped PathSegments
        separator,  # Mapped PathSeparator
        path,  # Mapped Path
        workbook.name,  # Mapped Name
        None,  # Destination Id
        None,  # Destination ContentUrl
        None,  # Destination PathSegments
        separator,  # Destination PathSeparator
        None,  # Destination Path
        None,  # Destination Name
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
        path_segments,  # Mapped PathSegments
        separator,  # Mapped PathSeparator
        path,  # Mapped Path
        view.name,  # Mapped Name
        None,  # Destination Id
        None,  # Destination ContentUrl
        None,  # Destination PathSegments
        separator,  # Destination PathSeparator
        None,  # Destination Path
        None,  # Destination Name
    ]

    view_data.append(v_data)

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
        path_segments,  # Mapped PathSegments
        separator,  # Mapped PathSeparator
        path,  # Mapped Path
        flow.name,  # Mapped Name
        None,  # Destination Id
        None,  # Destination ContentUrl
        None,  # Destination PathSegments
        separator,  # Destination PathSeparator
        None,  # Destination Path
        None,  # Destination Name
    ]

    flow_data.append(f_data)


column_headers = [
    "Source Id",
    "Source ContentUrl",
    "Source PathSegments",
    "Source PathSeparator",
    "Source Path",
    "Source Name",
    "Mapped PathSegments",
    "Mapped PathSeparator",
    "Mapped Path",
    "Mapped Name",
    "Destination Id",
    "Destination ContentUrl",
    "Destination PathSegments",
    "Destination PathSeparator",
    "Destination Path",
    "Destination Name",
]

logging.info("Writing results to DataFrames...")
# Build a dataframe of User components
user_df = pd.DataFrame(user_data, columns=column_headers)

# Build a dataframe of Group components
group_df = pd.DataFrame(group_data, columns=column_headers)

# Build a dataframe of Project components
project_df = pd.DataFrame(project_data, columns=column_headers)

# Build a dataframe of Data Source components
datasource_df = pd.DataFrame(datasource_data, columns=column_headers)

# Build a dataframe of Workbook components
workbook_df = pd.DataFrame(workbook_data, columns=column_headers)

# Build a dataframe of View components
view_df = pd.DataFrame(view_data, columns=column_headers)

# Build a dataframe of Flow components
flow_df = pd.DataFrame(flow_data, columns=column_headers)

# Export Project information to CSV files
# project_df.to_csv(project_source_file, header=True, index=False)

# Export Content Inventory information to Excel files
logging.info("Writing results to XLSX file...")
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
logging.info(
    '\nIMPORTANT: If you are remapping content, update the values in the "Mapped Path" column.'
)
