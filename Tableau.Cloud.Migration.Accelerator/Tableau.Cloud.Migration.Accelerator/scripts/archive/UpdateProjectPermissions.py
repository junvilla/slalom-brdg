"""
Update Project Permissions

Requires Project and Project permissions populated into the required file and migrated.

The list begins with Project level permissions, followed by Workbook and Data Source.
The script will run through each row and apply the permissions on the matched project.
"""

import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import time
import tableauserverclient as TSC
from Shared_TSC_GlobalFunctions import *
from Shared_TSC_GlobalVariables import *

separator = "//"


def get_child_projects_recursive(parent_id, path_segments):
    req_options = TSC.RequestOptions(pagesize=1000)
    req_options.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.ParentProjectId,
            TSC.RequestOptions.Operator.Equals,
            parent_id,
        )
    )

    child_projects = list(TSC.Pager(server.projects, req_options))
    proj_list = []

    for project in child_projects:
        new_path_segments = path_segments + [project.name]
        new_path = separator.join(new_path_segments)

        project_data = [
            project.id,
            project.name,
            new_path,
        ]

        proj_list.append(project_data)

        time.sleep(0.5)

        # Recursively get child projects
        proj_list.extend(get_child_projects_recursive(project.id, new_path_segments))

    return proj_list


def build_project_paths():
    # Set the initial filter to fetch top-level projects only
    request_opts = TSC.RequestOptions(pagesize=1000)
    request_opts.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.TopLevelProject,
            TSC.RequestOptions.Operator.Equals,
            True,
        )
    )

    top_level_projects = list(TSC.Pager(server.projects, req_options))
    project_list = []

    for project in top_level_projects:
        path_segments = [project.name]
        project_data = [
            project.id,
            project.name,
            project.name,  # In this case, also Path
        ]

        project_list.append(project_data)

        time.sleep(0.5)

        # Recursively get all child projects
        project_list.extend(get_child_projects_recursive(project.id, path_segments))

    # Create a dataframe of the Project list contents
    project_df = pd.DataFrame(
        project_list,
        columns=[
            "Project ID",
            "Project Name",
            "Path",
        ],
    )

    # Save the dataframe to CSV for future use
    print(f"Saving Project list to {proj_base_file}")
    project_df.to_csv(proj_base_file, index=False)

    return project_df


# -----------------------------------enter session variables here
proj_perm_dest_file = os.path.join(log_file_loc, "Update Project Permissions Log.xlsx")

proj_base_file = os.path.join(file_loc, "ProjectsForPermissions.csv")

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will update project permissions on your site."

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

# ------------------------------- UpdateProjectPermission
# This section will:
# Add and update project, workbook, data source, data lens and data flow permissions
start_time = time.time()

# create dataframe to store errors and activity
log_df = pd.DataFrame(
    columns=[
        "Time Log",
        "Object Name",
        "Script Name",
        "Project",
        "Permission Type",
        "Result",
        "Error",
    ]
)
log_df["Script Name"] = "UpdateProjectPermissions.py"

# read csv file
csv_df = pd.read_csv(project_permission_source_file)
csv_df.dropna(axis=0, how="all", inplace=True)

# csv_df.columns = csv_df.columns.str.upper()

# check if csv file has required headers
req_header = [
    "Path",
    "Capability",
    "Permission Type",
    "Grantee Name",
    "Grantee Type",
]
req_header = [req.upper() for req in req_header]

check_sum = len(req_header)
check_header = list(list(csv_df.columns))
check_header = [header.upper() for header in check_header]

count_perm_source = len(csv_df.index)

x = 0
for req in req_header:
    if search(check_header, req):
        x = x + 1

if x != check_sum:
    sys.exit(f"File must contain required column headers: {req_header}")

count_perm_target = 0

message = (
    time_log
    + " Begin Updating Project Permissions. Number of Rows in Input File: "
    + str(count_perm_source)
)
f = open(log_file, "a")
f.write(message + "\n")
f.close()

print(f"Begin {script_name}. Number of rows in input file: {str(count_perm_source)}")
print(
    "This process might take several minutes. Please wait for confirmation that the process has completed."
)
print(
    "------------------------------------------------------------------------------------------------------"
)

# sign in to Tableau
with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)

    # Get a list of all projects, because we need the ProjectItem objects
    all_projects = list(TSC.Pager(server.projects, req_options))

    # Check if a project list file was already created
    if os.path.exists(proj_base_file):
        # Prompt user to see if they want to use existing file or create a new one
        user_input = (
            input(
                f"Project List '{proj_base_file}' found.\nWould you like to import it? (Y/n)"
            )
            .strip()
            .lower()
        )

        if user_input == "y":
            project_df = pd.read_csv(proj_base_file)

        else:
            # Get the list of all top-level projects to start building Project Paths
            print("Building a new list of existing Projects and paths. Please wait.")
            project_df = build_project_paths()

    else:
        # Get the list of all top-level projects to start building Project Paths
        print("Getting a list of existing projects and building paths. Please wait.")
        project_df = build_project_paths()

    for i in csv_df.index:

        # iterate through data frame containing list of projects
        try:
            project_id = csv_df["Project ID"][i]
            project_name = csv_df["Project Name"][i]
            if project_name == "Default":
                project_name = project_name.lower()  # sometimes default can be Default
            capability = eval(csv_df["Capability"][i])
            grantee_type = csv_df["Grantee Type"][i]
            grantee_id = csv_df["LUID"][i]
            permission_type = csv_df["Permission Type"][i]
            grantee_name = csv_df["Grantee Name"][i]
            project_path = csv_df["Path"][i]
            # capability in dict format must not be read as string using eval

            req_options_grantee = TSC.RequestOptions(pagesize=1000)
            req_options_grantee.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    grantee_name,
                )
            )

            if grantee_type.upper() == "GROUP":
                filtered_grantee = list(TSC.Pager(server.groups, req_options_grantee))

            if grantee_type.upper() == "USER":
                filtered_grantee = list(TSC.Pager(server.users, req_options_grantee))

            for f_g in filtered_grantee:
                grantee = f_g

            # Filter the project_df DataFrame by matching the Path value
            filtered_project = project_df[project_df["Path"] == project_path]

            # Check if a match was found, if not, move on to the next Project
            if filtered_project.empty:
                continue
            else:
                proj_id = filtered_project["Project ID"].iloc[0]
                proj_name = filtered_project["Project Name"].iloc[0]
                proj_path = filtered_project["Path"].iloc[0]

                # Get the ProjectItem from the list of Projects
                for proj in all_projects:
                    if proj.id == proj_id:
                        filtered_proj = proj
                        proj_name = proj.name
                        break

                server.projects.populate_permissions(filtered_proj)

                print(
                    f"Source Project: {project_name} [{project_id}] at Path [{project_path}]"
                )
                print(
                    f"Built Project permissions for: {proj_name} [{proj_id}] at Path [{proj_path}]"
                )

                try:
                    rules_to_update = [
                        TSC.PermissionsRule(grantee=grantee, capabilities=capability)
                    ]
                    if permission_type == "Project":
                        server.projects.update_permissions(
                            filtered_proj, rules_to_update
                        )
                        print(
                            f"Updating Project permissions for: [{proj_name}] at [{project_path}] - "
                            f"Grantee Name: [{grantee_name}] - rules: [{capability}]"
                        )
                    if permission_type == "Workbook":
                        server.projects.update_workbook_default_permissions(
                            filtered_proj, rules_to_update
                        )
                        print(
                            f"Updating Workbook permissions for: [{proj_name}] at [{project_path}] - "
                            f"Grantee Name: [{grantee_name}] - rules: [{capability}]"
                        )
                    if permission_type == "Data Source":
                        server.projects.update_datasource_default_permissions(
                            filtered_proj, rules_to_update
                        )
                        print(
                            f"Updating Data source permissions for: [{proj_name}] at [{project_path}] - "
                            f"Grantee Name: [{grantee_name}] - rules: [{capability}]"
                        )
                    if permission_type == "Data Flow":
                        server.projects.update_flow_default_permissions(
                            filtered_proj, rules_to_update
                        )
                        print(
                            f"Updating Data flow permissions for: [{proj_name}] at [{project_path}] - "
                            f"Grantee Name: [{grantee_name}] - rules: [{capability}]"
                        )

                    count_perm_target = count_perm_target + 1

                    new_row = {
                        "Time Log": time_log,
                        "Object Name:": grantee_name,
                        "Script Name": "UpdateProjectPermissions.py",
                        "Project": proj_name,
                        "Permission Type": permission_type,
                        "Result": "Success",
                        "Error": "Project Permissions successfully applied",
                    }
                    log_df = pd.concat(
                        [log_df, pd.DataFrame([new_row])], ignore_index=True
                    )

                    time.sleep(0.5)

                except TSC.ServerResponseError as err:
                    error = time_log + str(err)
                    new_row = {
                        "Time Log": time_log,
                        "Object Name:": grantee_name,
                        "Script Name": "UpdateProjectPermissions.py",
                        "Project": proj_name,
                        "Permission Type": permission_type,
                        "Result": "Failed",
                        "Error": error,
                    }
                    log_df = pd.concat(
                        [log_df, pd.DataFrame([new_row])], ignore_index=True
                    )

                    time.sleep(0.5)

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            new_row = {
                "Time Log": time_log,
                "Object Name:": grantee_name,
                "Script Name": "UpdateProjectPermissions.py",
                "Project": proj_name,
                "Permission Type": permission_type,
                "Result": "Failed",
                "Error": error,
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

            time.sleep(0.5)

with pd.ExcelWriter(proj_perm_dest_file) as writer:
    log_df.to_excel(writer, sheet_name="UpdateProjectPermissions", index=False)

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
    time_log
    + " End updating project permissions. Number of Permissions Expected: "
    + str(count_perm_source)
    + "\n"
)
f.write("Permissions Updated: " + str(count_perm_target) + "\n")
f.close()

print(
    f"\nCompleted {script_name} in {duration}. Please check your log files for any errors."
)
