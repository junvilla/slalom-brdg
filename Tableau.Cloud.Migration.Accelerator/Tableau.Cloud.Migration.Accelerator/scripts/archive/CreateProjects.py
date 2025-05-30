# Create Projects. Use GetProject.py to create a template
# This module will create new projects and remove default permissions in the newly created projects
# The csv file must contain a header as the first row
# proj_source_file: to import projects
#   The csv file must contain the project name and path. project description is optional
#   Required columns (and column names):
#   1) Project Name (required): name of the project - can only have letters, numbers & underscores
#   2) Path (required): path to determine hierarchy and parent child relationship
#           The format is /Parent/Child/Grandchild, beginning each path with a //.
#           Leave Path blank if it is a top level project (no parent)
#           For example:
#           HR project is a project under Marketing. Marketing is a subproject of Company A. The path will be
#           /Company A/Marketing
#   3) Project Description (optional)
#  ------------------------------------------------------------------------------------------------------------
#       A sample entry:
#       Marketing is a parent project for HR. Company A is the parent project for Marketing. Company A
#       is a top level project. The csv file should have entries like below:
#
#       Project Name    |   Path
#       ---------------------------------------
#       Company A       |
#       Marketing       |  /Company A
#       HR              |  /Company A/Marketing

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

# -----------------------------------enter session variables here
proj_dest_file = os.path.join(file_loc, log_file_loc, "Create Projects Log.xlsx")

# include project description
include = True

# delimiter for path
sep = "/"

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will create projects on your site."

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

# create dataframe to store errors and activity
log_df = pd.DataFrame(
    columns=[
        "Time Log",
        "Object Name",
        "Script Name",
        "Parent Project",
        "Path",
        "Result",
        "Error",
    ]
)
log_df["Script Name"] = "CreateProjects.py"

# read csv file
csv_df = pd.read_csv(project_source_file)
csv_df.dropna(axis=0, how="all", inplace=True)
csv_df.columns = csv_df.columns.str.upper()

# check if csv file has required headers
req_header = ["Project Name", "Path"]
req_header = [req.upper() for req in req_header]
check_sum = len(req_header)
check_header = list(list(csv_df.columns))
check_header = [header.upper() for header in check_header]

# optional columns
optional_header = ["Project Description"]
optional_header = [opt.upper() for opt in optional_header]

x = 0
for req in req_header:
    if search(check_header, req):
        x = x + 1

for opt in optional_header:
    if search(check_header, opt):
        include = True

if x != check_sum:
    sys.exit(f"File must contain required column headers: {req_header}")

data = []  # list to store existing projects in Tableau to compare to new projects
proj_data = []  # list to store the projects that will be created
newPath_list = (
    []
)  # list to store csv values with parents and depth derived from path column in csv file
content_permissions = "ManagedByOwner"

# --------------------------------------------- Create Projects

# check path and verify the values of the csv input file
if not include:
    csv_df["PROJECT DESCRIPTION"] = time_log

path_list = [
    list(path)
    for path in zip(
        csv_df["PROJECT NAME"], csv_df["PATH"], csv_df["PROJECT DESCRIPTION"]
    )
]
# else:
#     path_list = [list(path) for path in zip(csv_df['PROJECT NAME'], csv_df['PATH'])]

# parse path to build parent project name
# get the depth of the project to build the project hierarchy
# check if first character is a slash if not, add it
for path in path_list:
    check_str = str(path[1])
    print(check_str)
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
    # print(newPath_list)

csv_df = pd.DataFrame(
    newPath_list,
    columns=[
        "Project Name",
        "Path",
        "Project Description",
        "Depth",
        "Parent Project Name",
    ],
)

# add separator in path if it does not start with it
csv_df.fillna("", inplace=True)
csv_df["Path"] = csv_df["Path"].str.strip().str.upper()
csv_df["Project Name"] = csv_df["Project Name"].str.strip()
csv_df["Parent Project Name"] = csv_df["Parent Project Name"].str.strip()

# add separator in beginning of string
csv_df["Path"] = np.where(
    csv_df["Path"].str[0:2] != sep, sep + csv_df["Path"].astype(str), csv_df["Path"]
)
csv_df.fillna("None", inplace=True)

# create concatenated key column to remove projects that already exist
csv_df["key"] = (
    csv_df["Project Name"].str.upper().str.strip()
    + "-"
    + csv_df["Depth"].astype(str).str.upper().str.strip()
    + "-"
    + csv_df["Path"].str.upper().str.strip()
)

csv_df.sort_values(by=["Depth", "Path", "Project Name"])

# max depth in csv file
max_depth_import = csv_df["Depth"].max()
count_proj_source = len(csv_df.index)

print(f"Number of Projects in input file: {str(count_proj_source)}")
print(f"Begin Create Projects. Number of Projects to create: {str(count_proj_source)}")
print(
    "This process might take several minutes. Please wait for confirmation that the process has completed."
)

message = (
    time_log
    + " Begin Create Projects. Number of Projects in Input File To Create: "
    + str(count_proj_source)
)
f = open(log_file, "a")
f.write(message + "\n")
f.close()

# start creating projects iterating through source file by depth.
# need to terminate tableau session after creating new
# project to get the newly created project id

# counter / timer
proj_created = 0
start_time = time.time()

# begin logging
f = open(log_file, "a")
f.write(time_log + "******* Begin Create Projects ********" + "\n")
f.close()

for i in range(0, max_depth_import + 1):
    parent_proj_id = ""
    # sign in to Tableau
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

            parent_df.rename(
                columns={"Project Name": "Parent Project Name"}, inplace=True
            )

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
            current_proj_df["Path"].fillna("/", inplace=True)

            # create concatenated key column to remove projects that already exist
            current_proj_df["key"] = (
                current_proj_df["Project Name"].str.upper().str.strip()
                + "-"
                + current_proj_df["Depth"].astype(str).str.upper().str.strip()
                + "-"
                + current_proj_df["Path"].str.upper().str.strip()
            )

            current_proj_df = current_proj_df[
                [
                    "Project ID",
                    "Project Name",
                    "Path",
                    "Depth",
                    "Parent Project ID",
                    "Parent Project Name",
                    "key",
                ]
            ].sort_values(by=["Depth", "Path", "Project Name"])

            # remove projects in csv df that already exist in Tableau
            # use suffixes to remove the duplicate columns
            new_csv_df = pd.merge(
                csv_df,
                current_proj_df,
                # on=['Project Name', 'Path', 'Depth', 'Parent Project Name'],
                on=["key"],
                how="left",
                suffixes=("", "_y"),
            )

            new_csv_df.drop(
                new_csv_df.filter(regex="_y$").columns, axis=1, inplace=True
            )

            # for logging, list of projects that already exist in tableau
            temp_csv_df = new_csv_df.dropna(subset=["Project ID"])

            # no project id means it isn't in Tableau yet, so it must be created
            new_csv_df = new_csv_df[new_csv_df["Project ID"].isna()]

            new_csv_df = new_csv_df[
                [
                    "Project Name",
                    "Parent Project Name",
                    "Depth",
                    "Project Description",
                    "Path",
                    "key",
                ]
            ].sort_values(by=["Depth", "Path", "Project Name"])
            new_csv_df.fillna("None", inplace=True)
            new_csv_df.sort_values(by=["Depth", "Path", "Project Name"])
            new_csv_df.reset_index(drop=True, inplace=True)

            new_csv_df["lstPath"] = new_csv_df["Path"].str.split(pat="/")

            new_csv_df["Parent Path"] = [
                "//".join(map(str, value)) for value in new_csv_df["lstPath"].str[:-1]
            ]

            new_csv_df["Parent Path"].fillna(sep, inplace=True)
            new_csv_df["Parent Path"].replace("", sep, inplace=True)

            # count number of projects in source csv for final check
            count_proj_to_create = 0
            count_proj_to_create = len(new_csv_df.index)

            f = open(log_file, "a")
            f.write("New Projects To Create: " + str(proj_created) + "\n")
            f.close()

            # print('New Projects To Create: ' + str(proj_created))

            filter_csv_df = new_csv_df.loc[new_csv_df["Depth"] == i]

            if filter_csv_df.empty:
                continue

            for j in filter_csv_df.index:
                proj_name = filter_csv_df["Project Name"][j]
                proj_parent_depth = filter_csv_df["Depth"][j] - 1
                proj_path = filter_csv_df["Path"][j]
                proj_parent_name = filter_csv_df["Parent Project Name"][j]
                proj_parent_path = filter_csv_df["Parent Path"][j]

                if include:
                    if filter_csv_df["Project Description"][j] == "None":
                        proj_description = time_log
                    else:
                        proj_description = filter_csv_df["Project Description"][j]

                else:
                    proj_description = time_log

                #  if top level project create, if not get parent project id from parent project name
                if i == 1:
                    if proj_name.upper() == "DEFAULT":
                        continue
                    else:
                        new_project = TSC.ProjectItem(
                            name=proj_name,
                            content_permissions=content_permissions,
                            description=proj_description,
                        )

                else:
                    temp_current_proj_df = current_proj_df[
                        (
                            current_proj_df["Path"].str.upper().str.strip()
                            == proj_parent_path.upper().strip()
                        )
                        & (current_proj_df["Depth"] == proj_parent_depth)
                        & (
                            current_proj_df["Project Name"].str.upper().str.strip()
                            == proj_parent_name.upper().strip()
                        )
                    ]

                    if temp_current_proj_df.empty:
                        new_row = {
                            "Time Log": time_log,
                            "Object Name": proj_name,
                            "Script Name": "CreateProjects.py",
                            "Parent Project": proj_parent_name,
                            "Path": proj_path,
                            "Result": "Failed",
                            "Error": "Parent Project is not a row in the input file. This project was not created.",
                        }
                        log_df = pd.concat(
                            [log_df, pd.DataFrame([new_row])], ignore_index=True
                        )
                        continue

                    temp_proj_parent_id = temp_current_proj_df[
                        "Project ID"
                    ].values.tolist()
                    proj_parent_id = temp_proj_parent_id[0]

                    new_project = TSC.ProjectItem(
                        name=proj_name,
                        parent_id=proj_parent_id,
                        content_permissions=content_permissions,
                        description=proj_description,
                    )

                # create new project
                print(f"Creating project: {proj_name}")
                new_project = server.projects.create(new_project)
                proj_created = proj_created + 1

                new_row = {
                    "Time Log": time_log,
                    "Object Name": proj_name,
                    "Script Name": "CreateProjects.py",
                    "Parent Project": proj_parent_name,
                    "Path": proj_path,
                    "Result": "Success",
                    "Error": "Project successfully created",
                }

                log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

                # get default permissions on newly created projects then delete
                server.projects.populate_permissions(new_project)
                server.projects.populate_workbook_default_permissions(new_project)
                server.projects.populate_datasource_default_permissions(new_project)
                server.projects.populate_flow_default_permissions(new_project)

                permissions = new_project.permissions
                default_wb_permissions = new_project.default_workbook_permissions
                default_ds_permissions = new_project.default_datasource_permissions
                default_flow_permissions = new_project.default_flow_permissions

                # remove default project permissions for each group/grantee
                for permission in permissions:
                    grantee = permission.grantee
                    capabilities = permission.capabilities
                    rules_to_delete = [
                        TSC.PermissionsRule(grantee=grantee, capabilities=capabilities)
                    ]
                    server.projects.delete_permission(new_project, rules_to_delete)

                # remove default workbook permissions
                if default_wb_permissions:
                    for wb_permission in default_wb_permissions:
                        grantee = wb_permission.grantee
                        new_capability = wb_permission.capabilities
                        rules_to_delete = TSC.PermissionsRule(
                            grantee=wb_permission.grantee, capabilities=new_capability
                        )
                        server.projects.delete_workbook_default_permissions(
                            new_project, rules_to_delete
                        )

                # remove default datasource permissions
                if default_ds_permissions:
                    for ds_permission in default_ds_permissions:
                        grantee = ds_permission.grantee
                        new_capability = ds_permission.capabilities
                        rules_to_delete = TSC.PermissionsRule(
                            grantee=grantee, capabilities=new_capability
                        )
                        server.projects.delete_datasource_default_permissions(
                            new_project, rules_to_delete
                        )

                # remove default flow permissions
                if default_flow_permissions:
                    for flow in default_flow_permissions:
                        grantee = flow.grantee
                        capabilities = flow.capabilities
                        rules_to_delete = TSC.PermissionsRule(
                            grantee=grantee, capabilities=capabilities
                        )
                        server.projects.delete_flow_default_permissions(
                            new_project, rules_to_delete
                        )

        except TSC.ServerResponseError as err:
            error = time_log + str(err)
            new_row = {
                "Time Log": time_log,
                "Object Name": proj_name,
                "Script Name": "CreateProjects.py",
                "Parent Project": proj_parent_name,
                "Path": proj_path,
                "Result": "Failed",
                "Error": error,
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

temp_csv_df.drop_duplicates()
for k in temp_csv_df.index:
    new_row = {
        "Time Log": time_log,
        "Object Name": temp_csv_df["Project Name"][k],
        "Script Name": "CreateProjects.py",
        "Parent Project": temp_csv_df["Parent Project Name"][k],
        "Path": temp_csv_df["Path"][k],
        "Result": "Failed",
        "Error": "Project already exists in target site",
    }
    log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)

with pd.ExcelWriter(proj_dest_file) as writer:
    print(f"\nWriting results to {proj_dest_file}. Please wait.")
    log_df.to_excel(writer, sheet_name="CreateProjects", index=False)

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
    + " End Create Projects. Number of Projects in Input File To Create: "
    + str(count_proj_source)
    + "\n"
)
f.write("Projects Created: " + str(proj_created) + "\n")
if proj_created != count_proj_to_create:
    log_error(str(proj_created), 3)
f.close()

print(
    f"Completed {script_name} in {duration}. \nProjects created: {str(proj_created)}. \nPlease check your log files for any errors."
)
