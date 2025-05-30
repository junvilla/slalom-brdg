import sys
import os

# Get the parent directory and add it to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import tableauserverclient as TSC
import time
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *

# -----------------------------------enter session variables here
# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will download data sources from your site."

# Prompt the user with the script name and description
print(f"\nYou are running {script_name} script. {script_description}")


# call the perform_action function with dynamic environment names
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

# ------------------------------- RemoveProjectPermission
# This section will:
# Remove all project permissions
start_time = time.time()

# sign in to Tableau
with server.auth.sign_in(tableau_auth):
    try:
        # get list of existing projects
        req_options = TSC.RequestOptions(pagesize=1000)
        all_projects = list(TSC.Pager(server.projects, req_options))

        for proj in all_projects:
            # get default permissions on newly created projects then delete
            server.projects.populate_permissions(proj)
            server.projects.populate_workbook_default_permissions(proj)
            server.projects.populate_datasource_default_permissions(proj)
            server.projects.populate_flow_default_permissions(proj)
            server.projects.populate_lens_default_permissions(proj)

            # projects
            permissions = proj.permissions
            # workbook
            default_wb_permissions = proj.default_workbook_permissions
            # data source
            default_ds_permissions = proj.default_datasource_permissions
            # flow
            default_flow_permissions = proj.default_flow_permissions
            # data lens
            default_lens_permissions = proj.default_lens_permissions

            # remove default project permissions for each group/grantee

            if permissions:
                for permission in permissions:
                    grantee = permission.grantee
                    capabilities = permission.capabilities
                    rules_to_delete = [
                        TSC.PermissionsRule(grantee=grantee, capabilities=capabilities)
                    ]
                    server.projects.delete_permission(proj, rules_to_delete)

            # remove default workbook permissions
            if default_wb_permissions:
                for wb_permission in default_wb_permissions:
                    grantee = wb_permission.grantee
                    new_capability = wb_permission.capabilities
                    rules_to_delete = TSC.PermissionsRule(
                        grantee=wb_permission.grantee, capabilities=new_capability
                    )
                    server.projects.delete_workbook_default_permissions(
                        proj, rules_to_delete
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
                        proj, rules_to_delete
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
                        proj, rules_to_delete
                    )

            # remove default lens permissions
            if default_lens_permissions:
                for lens in default_lens_permissions:
                    grantee = lens.grantee
                    capabilities = lens.capabilities
                    rules_to_delete = TSC.PermissionsRule(
                        grantee=grantee, capabilities=capabilities
                    )
                    server.projects.delete_lens_default_permissions(
                        proj, rules_to_delete
                    )

    except TSC.ServerResponseError as err:
        error = time_log + str(err)
        f = open(log_file, "a")
        f.write(error + "\n")
        f.close()
        print(err)

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
    f"Completed {script_name} in {duration}. Please check your log files for any errors."
)
