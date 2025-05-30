"""
Define Global Functions to be re-used across Scripts
"""

import ast
import glob
import os
import sys
import time
from datetime import datetime, timedelta
import functools
import itertools
import pandas as pd
import tableauserverclient as TSC
sys.path.append('.\venv\Lib\site-packages\tableau_tools')
from tableau_tools import *
from tableau_tools.tableau_documents import *
from Shared_TSC_GlobalVariables import *
import requests
import configparser
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import logging
import pickle
from logging_config import *


# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# read config file
def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config


# function to prompt user which environment to use
def tableau_environment(env1, env2):
    auth_variables = read_config("config.ini")
    load_dotenv()

    # prompt the user to enter a choice
    choice = input(
        f"""
What environment do you want to perform the action?
    1: {env1} (Source)
    2: {env2} (Destination)
Enter your choice (1-2): """
    )

    # check if the choice is valid
    if choice == "1":
        # perform action for choice 1
        # Tableau Source
        portal_url = auth_variables["SOURCE"]["URL"]
        site_id = auth_variables["SOURCE"]["SITE_CONTENT_URL"]
        token_name = auth_variables["SOURCE"]["ACCESS_TOKEN_NAME"]
        token_value = os.environ.get("SOURCE_TOKEN_SECRET")

        return token_name, token_value, portal_url, site_id

    elif choice == "2":
        # perform action for choice 2
        # Tableau Destination
        portal_url = auth_variables["DESTINATION"]["URL"]
        site_id = auth_variables["DESTINATION"]["SITE_CONTENT_URL"]
        token_name = auth_variables["DESTINATION"]["ACCESS_TOKEN_NAME"]
        token_value = os.environ.get("DESTINATION_TOKEN_SECRET")

        return token_name, token_value, portal_url, site_id

    else:
        print("Invalid choice. Exiting the program.")
        exit()


# authentication function
def tableau_authenticate(token_name, token_value, portal_url, site_id):
    server = TSC.Server(portal_url)

    # if using SSL uncomment below
    # server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
    # to bypass SSL, use below
    server.add_http_options({"verify": False})

    server.use_server_version()

    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)

    return tableau_auth


# function to create file folders if it doesn't exist
def create_file_locations():
    log_loc = os.path.join(log_file_loc)
    dl_file_loc = os.path.join(file_loc)
    manifest_file_loc = os.path.join(manifest_loc)
    if not os.path.exists(log_loc):
        os.makedirs(log_loc)
    if not os.path.exists(dl_file_loc):
        os.makedirs(dl_file_loc)
    if not os.path.exists(manifest_file_loc):
        os.makedirs(manifest_file_loc)
    return True


# function to check for required values
def search(check, csv_column_header):
    for i in range(len(check)):
        if check[i] == csv_column_header:
            return True


# function to determine hierarchy of projects using depth
def make_depth(input_df):
    idmap = dict(zip(input_df["Project ID"], input_df["Parent Project ID"]))

    @functools.lru_cache()
    def depth(id_):
        if pd.isnull(id_):
            return 1
        return depth(idmap[id_]) + 1

    return depth


# function to parse path to return depth and parent project
def parse_path(str_path_value, str_sep_value):
    # lst = list(str_path_value)
    c_depth = str_path_value.count(str_sep_value)
    f_depth = c_depth + 1
    split_l = str_path_value.split(str_sep_value)
    f_parent = split_l[c_depth]
    return [f_depth, f_parent]


def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


# function to create the hierarchy from a 2d flat file and create parent child relationship
# pass parent as first column child as 2nd column
def parse_relations(lines):
    relations = {}
    for parent, child in lines:
        relations.setdefault(parent, []).append(child)
    return relations


# function to flatten parent child hierarchy into a list
def flatten_hierarchy(relations, parent="No Parent"):
    try:
        children = relations[parent]
        for child in children:
            sub_hierarchy = flatten_hierarchy(relations, child)
            for element in sub_hierarchy:
                try:
                    yield tuple(itertools.chain([parent], element))
                except TypeError:
                    # we've tried to unpack `None` value,
                    # it means that no successors left
                    yield parent, child
    except KeyError:
        # we've reached end of hierarchy
        yield None


# function to write to log file
def log_error(str_project, err_num):
    err_log = datetime.now().strftime("%Y-%m-%d %H:%M  ")
    if err_num == 1:
        err = " Project Already Exists"
    elif err_num == 2:
        err = " Parent Project is not a row in the input file. This project was not created"
    elif err_num == 3:
        err = (
            " Number of objects created versus number of objects in input file did not match. Please check error "
            "logs. "
        )
    elif err_num == 4:
        err = " Project does not exist. "
    elif err_num == 5:
        err = " Duplicate data source name. Data Source was not downloaded"
    elif err_num == 6:
        err = " Name has special characters. Data Source was not downloaded"
    elif err_num == 7:
        err = " Workbook does not exist. Workbook not downloaded"
    else:
        err = " There was a problem"
    error = err_log + str_project + err
    f = open(log_file, "a")
    f.write(error + "\n")
    f.close()
    return True


# function to get the name of the latest file in a directory


def get_latest_file(path, *paths):
    fullpath = os.path.join(path, *paths)
    files = glob.iglob(fullpath)
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    _, filename = os.path.split(latest_file)
    return filename


# function to return the project id from Tableau Server or Tableau Cloud using project name and path
# pass a 2d list with project name in 0 index and project id in 1 index
def get_proj_id(project_list):
    f_proj_name = project_list[0]
    lst_depth = parse_path(project_list[1], str_sep_value=sep)
    lst_depth.insert(0, f_proj_name)
    return lst_depth


# function to build path hierarchy using parent / child relationship
# Input is dataframe with parent id and child id and depth using depth function
# build the parent child list one level at a time, then iterate each parent child relationship
# to build the project path
# returns a dict of paths with project ID as key


def get_hierarchy_path(project_df):
    level_path = list()
    max_depth = project_df["Depth"].max()
    for i in range(0, max_depth + 1):
        level_df = project_df.loc[project_df["Depth"] <= i]
        level_list = list(zip(level_df["Parent ID"], level_df["Child ID"]))
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
            proj_name = project_df.loc[(project_df["Child ID"] == x)]
            if proj_name.empty:
                proj_name = [""]
            else:
                proj_name = list(proj_name["Name"].values)
            if index < level_path_len - 1:
                new_path.append(proj_name)
            project_path = sum(new_path, [])
        project_path_final = sep.join(project_path)
        project_path_dict.setdefault(l_path[level_path_len - 1], []).append(
            project_path_final
        )

    return project_path_dict


class ContentItem(object):
    users = 'users'
    groups = 'groups'
    projects = 'projects'
    datasources = 'datasources'
    workbooks = 'workbooks'
    views = 'views'
    customviews = 'customviews'
    flows = 'flows'
    favorites = 'favorites'
    schedules = 'schedules'
    subscriptions = 'subscriptions'

class ContentLocation:
    source = "source"
    destination = "destination"

class Content:
    def get(server, content_item: ContentItem, site: str):
        """Gets a list of ContentItem objects from Tableau Server
        and writes them to a local pickle (.pkl) file.

        Args:
            server (TSC.Server): a TableauServerClient Server item
            content_item (ContentItem): the type of content to be retrieved
            
            \nEligible ContentItems: users, groups, projects, datasources, workbooks, views, 
            customviews, flows, favorites, schedules, subscriptions, tasks
        """

        file_dict = {
            'users': 'UserItems',
            'groups': 'GroupItems',
            'projects': 'ProjectItems',
            'datasources': 'DatasourceItems',
            'workbooks': 'WorkbookItems',
            'views': 'ViewItems',
            'customviews': 'CustomViewItems',
            'flows': 'FlowItems',
            'favorites': 'FavoriteItems',
            'schedules': 'ScheduleItems',
            'subscriptions': 'SubscriptionItems',
            'tasks': 'TaskItems'
        }

        content_dict = {
            'users': server.users,
            'groups': server.groups,
            'projects': server.projects,
            'datasources': server.datasources,
            'workbooks': server.workbooks,
            'views': server.views,
            'customviews': server.custom_views,
            'flows': server.flows,
            'favorites': server. favorites,
            'schedules': server.schedules,
            'subscriptions': server.subscriptions,
            'tasks': server.tasks,
        }

        filename = file_dict.get(content_item)
        api_request = content_dict.get(content_item)

        request_opts = TSC.RequestOptions(pagesize=1000)
        content_list = list(TSC.Pager(api_request, request_opts))

        logging.info(f"Writing [{filename.split('.')[0]}] to file. Please wait...")
        with open(f"./FILES/{filename}_{site}.pkl", mode='wb') as file:
            pickle.dump(content_list, file)
            logging.info(f"Finished writing [{filename.split('.')[0]}] to file [{filename}_{site}.pkl]")

        logging.info("Finished writing ContentItems from Tableau Server to file.")
        logging.info("Please see the output files and log file for details.")
        

    def get_all(server, site: str):
        """Gets a list of all ContentItem objects from Tableau Server 
        and writes them to a local pickle (.pkl) files.

        Args:
            server (TSC.Server): a TableauServerClient Server item
            get_groups (bool): True/False - whether to include GroupItems
        """
        request_opts = TSC.RequestOptions(pagesize=1000)

        # Get a list of content Items (needed for updating permissions later)
        logging.info("Getting a list of UserItems from Tableau Server.")
        all_users = list(TSC.Pager(server.users, request_opts))
        time.sleep(2)

        logging.info("Getting a list of GroupItems from Tableau Server.")
        all_groups = list(TSC.Pager(server.groups, request_opts))
        time.sleep(2)

        logging.info("Getting a list of ProjectItems from Tableau Server.")
        all_projects = list(TSC.Pager(server.projects, request_opts))
        time.sleep(2)

        logging.info("Getting a list of DatasourceItems from Tableau Server.")
        all_datasources = list(TSC.Pager(server.datasources, request_opts))
        time.sleep(2)

        logging.info("Getting a list of WorkbookItems from Tableau Server.")
        all_workbooks = list(TSC.Pager(server.workbooks, request_opts))
        time.sleep(2)

        logging.info("Getting a list of ViewItems from Tableau Server.")
        all_views = list(TSC.Pager(server.views, request_opts))
        time.sleep(2)

        logging.info("Getting a list of CustomViewItems from Tableau Server.")
        all_customviews = list(TSC.Pager(server.custom_views, request_opts))
        time.sleep(2)

        logging.info("Getting a list of FlowItems from Tableau Server.")
        all_flows = list(TSC.Pager(server.flows, request_opts))
        time.sleep(2)

        logging.info("Getting a list of ScheduleItems from Tableau Server.")
        all_schedules = []

        sch_list = list(TSC.Pager(server.schedules, request_opts))

        # Getting schedules by Id so that we have IntervalItem details
        for sch in sch_list:
            sch = server.schedules.get_by_id(sch.id)
            all_schedules.append(sch)

        time.sleep(2)

        logging.info("Getting a list of SubscriptionItems from Tableau Server.")
        all_subscriptions = list(TSC.Pager(server.subscriptions, request_opts))
        time.sleep(2)

        logging.info("Getting a list of TaskItems from Tableau Server.")
        all_tasks = list(TSC.Pager(server.tasks, request_opts))
        time.sleep(2)

        logging.info("Getting a list of FavoriteItems from Tableau Server.")
        all_favorites = []
        for user in all_users:
            user_favorites = server.favorites.get(user, request_opts)
            if user_favorites:
                all_favorites.extend(user_favorites)
                time.sleep(0.5)

        logging.info("Tableau Server authentication session terminated.")

        file_dict = {
            'UserItems': all_users,
            'GroupItems': all_groups,
            'ProjectItems': all_projects,
            'DatasourceItems': all_datasources,
            'WorkbookItems': all_workbooks,
            'ViewItems': all_views,
            'CustomViewItems': all_customviews,
            'FlowItems': all_flows,
            'FavoriteItems': all_favorites,
            'ScheduleItems': all_schedules,
            'SubscriptionItems': all_subscriptions,
            'TaskItems': all_tasks,
        }

        for filename, data in file_dict.items():
            if data:
                logging.info(f"Writing [{filename.split('.')[0]}] to file. Please wait...")
                with open(f"./FILES/{filename}_{site}.pkl", mode='wb') as file:
                    pickle.dump(data, file)
                    logging.info(f"Finished writing [{filename.split('.')[0]}] to file [{filename}_{site}.pkl]")

        logging.info("Finished writing ContentItems from Tableau Server to file.")
        logging.info("Please see the output files and log file for details.")


    def load(content_type: ContentItem, site: str)-> list:
        """Load the ContentItems from a pickle (.pkl) file to a list.

        Args:
            content_type (ContentItem): the content type to be loaded

            \nEligible ContentItems: 
            users, groups, projects, datasources, workbooks, views, 
            customviews, flows, favorites, schedules, subscriptions, tasks

        Returns:
            list: a list of TableauServerClient ContentItems (e.g., UserItems)
        """
        file_dict = {
            'users': 'UserItems',
            'groups': 'GroupItems',
            'projects': 'ProjectItems',
            'datasources': 'DatasourceItems',
            'workbooks': 'WorkbookItems',
            'views': 'ViewItems',
            'customviews': 'CustomViewItems',
            'flows': 'FlowItems',
            'favorites': 'FavoriteItems',
            'schedules': 'ScheduleItems',
            'subscriptions': 'SubscriptionItems',
            'tasks': 'TaskItems',
        }
        
        filename = file_dict.get(content_type)
        content_list = []

        with open(f"./FILES/{filename}_{site}.pkl", mode='rb') as file:
            logging.info(f"Reading [{filename}_{site}] to list variable. Please wait...")
            content_data = pickle.load(file)
            content_list.extend(content_data)

        return content_list


class projects:
    # function to get a list of all project IDs and names
    def get(server, site_auth):
        with server.auth.sign_in(site_auth):
            req_options = TSC.RequestOptions(pagesize=1000)
            all_projects = list(TSC.Pager(server.projects, req_options))
            project_list = []

            for project in all_projects:
                project_id = project.id
                project_name = project.name
                parent_id = project.parent_id
                parent_name = None

                # find the parent project name using the parent project id
                for row in all_projects:
                    if row.id == parent_id:
                        parent_name = row.name
                        break

                project_list.append((project_id, project_name, parent_name))

            # Create a dataframe containing the project ID and name
            project_df = pd.DataFrame(
                project_list, columns=["Project ID", "Project Name", "Parent Name"]
            )

            return project_df


class workbooks:
    # function to get a list of all workbook IDs, names, projects, and content URLs
    def get(server, site_auth):
        with server.auth.sign_in(site_auth):
            req_options = TSC.RequestOptions(pagesize=1000)
            all_wbs = list(TSC.Pager(server.workbooks, req_options))
            wb_list = []

            for wb in all_wbs:
                wb_list.append((wb.id, wb.name, wb.project_name, wb.content_url))

            # Create a dataframe containing the project ID and name
            wb_df = pd.DataFrame(
                wb_list,
                columns=["Workbook ID", "Workbook Name", "Project Name", "Content URL"],
            )

            return wb_df

    class permissions:
        # function to get a list of permissions for all Workbook IDs, names, owners, grantee types, and capabilities
        def get(portal_url, site_luid, api_version, auth_token, wb_id):
            url = f"{portal_url}/api/{api_version}/sites/{site_luid}/workbooks/{wb_id}/permissions"
            headers = {"X-Tableau-Auth": f"{auth_token}", "Accept": "application/json"}
            payload = {}

            # Establish a Session
            session = requests.session()

            # Prepare the Request
            request = requests.Request("GET", url, headers=headers, data=payload)
            prepared_request = session.prepare_request(request)

            # Send the request
            response = session.send(prepared_request)

            # Parse the results into a list
            response = response.json()
            wb_permissions = response["permissions"]
            wb_name = wb_permissions["workbook"]["name"]
            wb_owner = wb_permissions["workbook"]["owner"]["id"]
            grantee_name = None

            permission_list = []

            for item in wb_permissions["granteeCapabilities"]:
                if "user" in item:
                    grantee_type = "User"
                    grantee = item["user"]["id"]
                    capabilities = {}
                    for p in item["capabilities"]["capability"]:
                        c_name = p["name"]
                        c_mode = p["mode"]
                        capabilities[c_name] = c_mode
                if "group" in item:
                    grantee_type = "Group"
                    grantee = item["group"]["id"]
                    capabilities = {}
                    for p in item["capabilities"]["capability"]:
                        c_name = p["name"]
                        c_mode = p["mode"]
                        capabilities[c_name] = c_mode

                permission_list.append(
                    (
                        wb_id,
                        wb_name,
                        wb_owner,
                        grantee_type,
                        grantee_name,
                        grantee,
                        capabilities,
                    )
                )

            return permission_list


class views:
    # function to get a list of all View IDs, names, workbook names, and content URLs
    def get(server, site_auth):
        with server.auth.sign_in(site_auth):
            req_options = TSC.RequestOptions(pagesize=1000)
            all_views = list(TSC.Pager(server.views, req_options))
            view_list = []

            for view in all_views:
                workbook = server.workbooks.get_by_id(view.workbook_id)
                workbook_name = workbook.name
                view_list.append((view.id, view.name, workbook_name, view.content_url))

            # Create a dataframe containing the project ID and name
            view_df = pd.DataFrame(
                view_list,
                columns=["View ID", "View Name", "Workbook Name", "Content URL"],
            )

            return view_df


class datasources:
    # function to get a list of all Datasource IDs, names, projects, and content URLs
    def get(server, site_auth):
        with server.auth.sign_in(site_auth):
            req_options = TSC.RequestOptions(pagesize=1000)
            all_ds = list(TSC.Pager(server.datasources, req_options))
            ds_list = []

            for ds in all_ds:
                ds_list.append((ds.id, ds.name, ds.project_name, ds.content_url))

            # Create a dataframe containing the project ID and name
            ds_df = pd.DataFrame(
                ds_list,
                columns=[
                    "Datasource ID",
                    "Datasource Name",
                    "Project Name",
                    "Content URL",
                ],
            )

            return ds_df


class flows:
    # function to get a list of all Flow IDs, names, projects, and content URLs
    # flows are not supported by TableauServerClient - must use direct API calls
    def get(portal_url, api_version, site_luid, auth_token):
        url = f"{portal_url}/api/{api_version}/sites/{site_luid}/flows?pageSize=1000"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tableau-Auth": f"{auth_token}",
        }
        payload = "{}"

        auth_response = requests.request("GET", url, headers=headers, data=payload)

        all_flows = json.loads(auth_response.text)
        all_flows = all_flows["flows"]["flow"]

        flow_list = []

        for flow in all_flows:
            flow_id = flow["id"]
            name = flow["name"]
            project = flow["project"]["name"]

            flow_list.append((flow_id, name, project))

        # Create a dataframe containing the project ID and name
        flow_df = pd.DataFrame(
            flow_list, columns=["Flow ID", "Flow Name", "Project Name"]
        )

        return flow_df


class users:
    # function to get a list of all user IDs and names
    def get(server, site_auth):
        with server.auth.sign_in(site_auth):
            req_options = TSC.RequestOptions(pagesize=1000)
            all_users = list(TSC.Pager(server.users, req_options))
            user_list = []

            for user in all_users:
                user_list.append((user.id, user.name))

            # create a dataframe containing the user ID and name
            user_df = pd.DataFrame(user_list, columns=["User ID", "User Name"])

            return user_df


class favorites:
    # function to get favorites by user LUID
    def get(portal_url, api_version, site_luid, user_luid, auth_token):
        fav_url = (
            f"{portal_url}/api/{api_version}/sites/{site_luid}/favorites/{user_luid}"
        )
        fav_headers = {
            "X-Tableau-Auth": f"{auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        fav_payload = {}

        auth_response = requests.request(
            "GET", fav_url, headers=fav_headers, data=fav_payload
        )

        if auth_response.status_code < 400:
            favorites = json.loads(auth_response.text)

            if "favorites" in favorites:
                fav_list = favorites["favorites"]["favorite"]
            else:
                fav_list = None
        else:
            fav_list = None

        return fav_list

    # -----------------------------------Create function to send Favorites to API

    def create(portal_url, api_version, site_luid, auth_token, user_id, payload):
        api_url = (
            f"{portal_url}/api/{api_version}/sites/{site_luid}/favorites/{user_id}"
        )

        api_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tableau-Auth": f"{auth_token}",
        }

        response = requests.request("PUT", api_url, headers=api_headers, data=payload)
        status = response.status_code
        body = response.text

        return body, status

    class request:
        def create(type, dest_id, label):
            payload = json.dumps(
                {
                    "favorite": {
                        f"{type.lower()}": {"id": f"{dest_id}"},
                        "label": f"{label}",
                    }
                }
            )

            return payload


# function to get a list of Custom Views on a site
class customViews:
    class views:
        def get(portal_url, api_version, site_luid, auth_token):
            cv_url = f"{portal_url}/api/{api_version}/sites/{site_luid}/customviews"
            cv_headers = {
                "X-Tableau-Auth": f"{auth_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            cv_payload = {}
            params = {}
            all_results = []

            params["pageSize"] = 1000
            page = 1

            while True:
                params["pageNumber"] = page

                # Establish a session
                session = requests.Session()

                # Prepare the request
                request = requests.Request(
                    "GET", cv_url, headers=cv_headers, data=cv_payload, params=params
                )
                prepared_request = session.prepare_request(request)

                # Send the request
                response = session.send(prepared_request)
                status = response.status_code

                if status == 200:
                    custom_views = response.json()
                    results = custom_views["customViews"]["customView"]

                    if not results:
                        break

                    all_results.extend(results)
                    page += 1

                else:
                    break

            return all_results

        ### function to download Custom Views from a site
        # Downloads a custom view in .json format
        ### Security note: content in .json files downloaded using this method is stored in plain text.
        ### All data, including filter values that might give semantic clues to the data,
        ### is readable by anyone who opens the files.
        def download(portal_url, api_version, site_luid, auth_token, cv_id):
            # Placeholder in case Tableau pushes the Custom View API to Tableau Server production API endpoints
            # cv_url = f"{portal_url}/api/{api_version}/sites/{site_luid}/customviews/{cv_id}/content"
            cv_url = (
                f"{portal_url}/api/exp/sites/{site_luid}/customviews/{cv_id}/content"
            )
            cv_headers = {"X-Tableau-Auth": f"{auth_token}"}

            cv_payload = {}

            auth_response = requests.request(
                "GET", cv_url, headers=cv_headers, data=cv_payload
            )
            custom_view = auth_response.text

            return custom_view

        # Create the payload object (body) for the POST Publish Custom View API method
        def payload(cv_name, shared, workbook_id, owner_id, cv_filename):
            # Set the JSON file directory
            json_file = os.path.join(cv_file_loc, cv_filename)

            # Set the XML file directory
            xml_file = os.path.join(cv_file_loc, "publish-customview.xml")

            # Build the XML Data element
            data_element = ET.Element("tsRequest")
            cv_element = ET.SubElement(data_element, "customView")
            cv_element.attrib["name"] = cv_name
            cv_element.attrib["shared"] = str(shared).lower()
            wb_element = ET.SubElement(cv_element, "workbook")
            wb_element.attrib["id"] = workbook_id
            owner_element = ET.SubElement(cv_element, "owner")
            owner_element.attrib["id"] = owner_id

            tree = ET.ElementTree(data_element)

            # Write the Custom View data to the XML file
            tree.write(xml_file, encoding="utf-8", xml_declaration=True)
            # with open(xml_file, 'w') as file:
            #     ET.ElementTree.write(tree, file)

            cv_body = [
                (
                    "request_payload",
                    ("publish-customview.xml", open(xml_file, "rb"), "text/xml"),
                ),
                (
                    "tableau_customview",
                    (
                        f"{cv_filename}",
                        open(json_file, "rb"),
                        "application/octet-stream",
                    ),
                ),
            ]

            return cv_body

        # Publish the Custom View using the payload created from the cv_payload function
        def publish(portal_url, api_version, site_luid, auth_token, cv_body):
            # cv_url = f"{portal_url}/api/{api_version}/sites/{site_luid}/customviews"
            cv_url = f"{portal_url}/api/exp/sites/{site_luid}/customviews"
            cv_headers = {
                "X-Tableau-Auth": f"{auth_token}",
                "Accept": "application/json",
            }

            payload = {}

            # Establish a session
            session = requests.Session()

            # Prepare the request
            request = requests.Request(
                "POST", cv_url, headers=cv_headers, data=payload, files=cv_body
            )
            # print(request.prepare().url)
            # print(request.prepare().headers)
            # print(request.prepare().body)

            prepared_request = session.prepare_request(request)

            # Send the request
            response = session.send(prepared_request)

            status = response.status_code

            body = response.json()

            # Return the response status
            return status, body

    class users:
        # Function to get a list of users with a Custom View set as their default view for a workbook
        def getDefault(portal_url, api_version, site_luid, auth_token, cv_id):
            cv_url = f"{portal_url}/api/{api_version}/sites/{site_luid}/customviews/{cv_id}/default/users"
            cv_headers = {
                "X-Tableau-Auth": f"{auth_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            cv_payload = {}
            params = {}
            all_results = []

            params["pageSize"] = 1000
            page = 1

            # Iterate through the pages of results
            while True:
                params["pageNumber"] = page

                # Establish a session
                session = requests.Session()

                # Prepare the request
                request = requests.Request(
                    "GET", cv_url, headers=cv_headers, data=cv_payload, params=params
                )
                prepared_request = session.prepare_request(request)

                # Send the request
                response = session.send(prepared_request)
                status = response.status_code

                # If request was successful, process results; else, break loop and return.
                if status == 200:
                    user_list = response.json()

                    # If no users are returned, break loop.
                    if user_list["users"]["user"] == []:
                        break
                    # Else, generate a list of the user LUIDs
                    else:
                        results = user_list["users"]
                        user_ids = [user["id"] for user in results["user"]]

                        # If results is empty, break the loop
                        if not results:
                            break

                    # Extend the all_results list with the user_ids list
                    all_results.extend(user_ids)
                    page += 1

                else:
                    break

            return all_results

        # once a Custom View has been created, assign it as a default view for users
        def setDefault(portal_url, api_version, site_luid, auth_token, cv_id, users):
            cv_url = f"{portal_url}/api/{api_version}/sites/{site_luid}/customviews/{cv_id}/default/users"
            cv_headers = {
                "X-Tableau-Auth": f"{auth_token}",
                "Content-Type": "application/xml",
                "Accept": "application/json",
            }

            # Build the XML Request element
            request_element = ET.Element("tsRequest")
            users_element = ET.SubElement(request_element, "users")

            # iterate through users list provided
            for user in users:
                user_element = ET.SubElement(users_element, "user")
                user_element.attrib["id"] = user

            # transform the request element into a string
            request_payload = ET.tostring(request_element)

            # Establish a session
            session = requests.Session()

            # Prepare the request
            request = requests.Request(
                "POST", cv_url, headers=cv_headers, data=request_payload
            )
            prepared_request = session.prepare_request(request)

            # Send the request and store the results
            response = session.send(prepared_request)
            status = response.status_code

            cv_response = response.json()
            cv_response = cv_response["customViewAsUserDefaultResults"][
                "customViewAsUserDefaultViewResult"
            ][0]["success"]

            return status, cv_response


class schedules:
    def get(schedule_id):
        # Open the file generated by GetSchedules.py
        all_schedules = Content.load(ContentItem.schedules, ContentLocation.source)

        # find the schedule by Schedule Id in the import file
        for sch in all_schedules:
            if sch.id == schedule_id:
                schedule: TSC.ScheduleItem = sch

        frequency = schedule.interval_item._frequency
        start_time = schedule.interval_item.start_time
        interval = str(schedule.interval_item.interval)

        # convert start_time from string to time object
        # start_time = str(start_time)
        # start_time = datetime.strptime(start_time, "%H:%M:%S").time()

        # convert interval string to list
        interval = ast.literal_eval(interval)

        # build the XML Schedule element
        schedule_element = ET.Element("schedule")
        schedule_element.attrib["frequency"] = frequency

        frequency_element = ET.SubElement(schedule_element, "frequencyDetails")
        frequency_element.attrib["start"] = str(start_time)

        if frequency == "Hourly":
            end_time = str(schedule.interval_item.end_time)
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()
            frequency_element.attrib["end"] = str(end_time)

        intervals_element = ET.SubElement(frequency_element, "intervals")

        # check if interval contains values, if not, process as daily
        if frequency == "Monthly":
            expression = "monthDay"
            value = interval[0]

            single_interval_element = ET.SubElement(intervals_element, "interval")
            single_interval_element.attrib[expression] = value

        elif frequency == "Weekly":
            expression = "weekDay"
            # weekly schedules can only support one weekDay element, so pull the first
            value = interval[0]

            single_interval_element = ET.SubElement(intervals_element, "interval")
            single_interval_element.attrib[expression] = value

        elif frequency == "Daily":
            # frequency end time is required - default to start_time + 2 hours
            # Not supposed to be required on 24 hour frequency, but API forces it.
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = start_datetime + timedelta(hours=2)
            end_time = end_datetime.time()
            frequency_element.attrib["end"] = str(end_time)

            if interval:
                for j in interval:
                    if j in ["2", "4", "6", "8", "12", "24"]:
                        expression = "hours"
                    else:
                        expression = "weekDay"

                    single_interval_element = ET.SubElement(
                        intervals_element, "interval"
                    )
                    single_interval_element.attrib[expression] = value

            else:
                # when a blank interval value returns (daily), populate the
                # daily interval with hours=24
                single_interval_element = ET.SubElement(intervals_element, "interval")
                single_interval_element.attrib["hours"] = "24"

                # Tableau does not automatically infer schedules to run every day.
                # Instead, set the weekDay interval for every day
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for d in days:
                    weekday_interval_element = ET.SubElement(
                        intervals_element, "interval"
                    )
                    weekday_interval_element.attrib["weekDay"] = d

        elif frequency == "Hourly":
            for j in interval:
                value = j
                if value == "60":
                    expression = "minutes"
                elif value == "1":
                    expression = "hours"
                elif value in [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]:
                    expression = "weekDay"

                single_interval_element = ET.SubElement(intervals_element, "interval")
                single_interval_element.attrib[expression] = value

        return schedule_element


class tasks:
    class request:
        def create(task_type, target_type, target_id, schedule_item):
            xml_request = ET.Element("tsRequest")
            extract_element = ET.SubElement(xml_request, "extractRefresh")

            # Main attributes
            extract_element.attrib["type"] = task_type

            # Target attributes
            if target_type == "workbook":
                target_item = ET.SubElement(extract_element, "workbook")
                target_item.attrib["id"] = target_id
            if target_type == "datasource":
                target_item = ET.SubElement(extract_element, "datasource")
                target_item.attrib["id"] = target_id

            # Append the schedule element to the task element
            schedule_element = schedule_item
            xml_request.append(schedule_element)

            # print(ET.tostring(xml_request))
            return ET.tostring(xml_request)

    def create(portal_url, api_version, site_luid, auth_token, cloud_task_item):
        result = "Success"
        base_url = (
            f"{portal_url}/api/{api_version}/sites/{site_luid}/tasks/extractRefreshes"
        )
        headers = {
            "X-Tableau-Auth": f"{auth_token}",
            "Content-Type": "application/xml",
            "Accept": "application/json",
        }

        payload = cloud_task_item

        auth_response = requests.request(
            "POST", base_url, headers=headers, data=payload
        )
        response_body = json.loads(auth_response.text)
        # print(response_body)

        try:
            task_response = response_body["extractRefresh"]

        except KeyError:
            task_response = response_body["error"]["detail"]
            result = "Error"

        # print(sub_response)
        return result, task_response


# -----------------------------------Create Functions
class subscriptions:
    class request:
        def create(subscription_item, schedule_item):
            xml_request = ET.Element("tsRequest")
            subscription_element = ET.SubElement(xml_request, "subscription")

            # Main attributes
            subscription_element.attrib["subject"] = subscription_item.subject
            if subscription_item.attach_image is not None:
                subscription_element.attrib["attachImage"] = str(
                    subscription_item.attach_image
                ).lower()
            if subscription_item.attach_pdf is not None:
                subscription_element.attrib["attachPdf"] = str(
                    subscription_item.attach_pdf
                ).lower()
            if subscription_item.page_orientation is not None:
                subscription_element.attrib["pageOrientation"] = (
                    subscription_item.page_orientation
                )
            if subscription_item.page_size_option is not None:
                subscription_element.attrib["pageSizeOption"] = (
                    subscription_item.page_size_option
                )
            if subscription_item.message is not None:
                subscription_element.attrib["message"] = subscription_item.message

            # Content element
            content_element = ET.SubElement(subscription_element, "content")
            content_element.attrib["id"] = subscription_item.target.id
            content_element.attrib["type"] = subscription_item.target.type
            if subscription_item.send_if_view_empty is not None:
                content_element.attrib["sendIfViewEmpty"] = str(
                    subscription_item.send_if_view_empty
                ).lower()

            # User element
            user_element = ET.SubElement(subscription_element, "user")
            user_element.attrib["id"] = subscription_item.user_id

            # Append the schedule element to the subscription element
            schedule_element = schedule_item
            xml_request.append(schedule_element)

            return ET.tostring(xml_request)

    def create(portal_url, api_version, site_luid, auth_token, cloud_sub_item):
        result = "Success"
        base_url = f"{portal_url}/api/{api_version}/sites/{site_luid}/subscriptions"
        headers = {
            "X-Tableau-Auth": f"{auth_token}",
            "Content-Type": "application/xml",
            "Accept": "application/json",
        }

        payload = cloud_sub_item

        auth_response = requests.request(
            "POST", base_url, headers=headers, data=payload
        )
        response_body = json.loads(auth_response.text)

        try:
            sub_response = response_body["subscription"]

        except KeyError:
            sub_response = response_body["error"]["detail"]
            result = "Error"

        return result, sub_response


class Manifest:
    """Reads and processes a Tableau Migration manifest."""

    def get_views(manifest_df):
        """Get a list of Views to append to the CoreMigration.py manifest file.

        Args:
            manifest_df (DataFrame): a DataFrame containing the content details.

        Returns:
            DataFrame: manifest_df appended with details on Views from the source site.
        """

        # Load the authentication variables for the Source environment
        portal_url = config["SOURCE"]["URL"]
        site_id = config["SOURCE"]["SITE_CONTENT_URL"]
        token_name = config["SOURCE"]["ACCESS_TOKEN_NAME"]
        token_value = os.environ.get("SOURCE_TOKEN_SECRET")

        tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)
        server = TSC.Server(portal_url)

        # # if using SSL uncomment below
        # # server.add_http_options({'verify':True, 'cert': ssl_chain_cert})
        # # to bypass SSL, use below
        server.add_http_options({'verify': False})
        server.use_server_version()

        workbook_df = manifest_df[manifest_df["Content Type"] == "Workbook"]
        view_data = []

        with server.auth.sign_in(tableau_auth):
            req_options = TSC.RequestOptions(pagesize=1000)

            logging.info("Extracting Views...")
            all_views = list(TSC.Pager(server.views, req_options))

        # Build a list of View data
        logging.info("Building View list...")
        for view in all_views:
            # Get the path segments of the Workbook containing the View
            workbook = workbook_df[workbook_df["Source Id"] == view.workbook_id]
            path_segments = workbook.iloc[0]["Source PathSegments"]

            separator = "/"
            path_segments = path_segments + [view.name]
            path = separator.join(path_segments)  # Path, in this case, path/workbook/view.name

            row = {
                "Content Type": 'View',
                "Source Id": view.id,
                "Source ContentUrl": view.content_url,
                "Source PathSegments": path_segments,
                "Source PathSeparator": separator,
                "Source Path": path,
                "Source Name": view.name,
                "Mapped PathSegments": path_segments, # Mapped PathSegments
                "Mapped PathSeparator": separator, # Mapped PathSeparator
                "Mapped Path": path, # Mapped Path
                "Mapped Name": view.name, # Mapped Name
                "Destination Id": None, # Destination Id
                "Destination ContentUrl": None, # Destination ContentUrl
                "Destination PathSegments": None, # Destination PathSegments
                "Destination PathSeparator": None, # Destination PathSeparator
                "Destination Path": None, # Destination Path
                "Destination Name": None, # Destination Name
            }

            view_data.append(row)
        
        # Create a DataFrame from view_data
        view_df = pd.DataFrame(view_data)

        updated_manifest_df = pd.concat([manifest_df, view_df])

        return updated_manifest_df

    # function to check for manifest.json or ContentInventory.xlsx
    def read():
        """Attempts to read 'manifest.json' or 'ContentInventory.xlsx'.

        Args:
            None

        Returns:
            manifest_df (DataFrame): a DataFrame containing the content details
        """

        # Define the default manifest.json file location
        manifest_file = os.path.join(manifest_loc, "manifest.json")

        # If manifest.json does not exist, read ContentInventory.xlsx instead
        if os.path.exists(manifest_file):
            logging.info("Reading file [manifest.json], please wait...")
            manifest_df = Manifest.deserialize(manifest_file)

        else:
            logging.info("File [manifest.json] not found. Attempting to read [ContentInventory.xlsx] instead...")
            content_file = os.path.join(
                file_loc, "ContentInventory.xlsx"
            )

            # read the sheets of ContentInventory.xlsx to dataframes, if it exists
            if os.path.exists(content_file):
                logging.info("Reading file [ContentInventory.xlsx], please wait...")
                user_df = pd.read_excel(content_file, sheet_name="User List")
                group_df = pd.read_excel(content_file, sheet_name="Group List")
                project_df = pd.read_excel(content_file, sheet_name="Project List")
                datasource_df = pd.read_excel(
                    content_file, sheet_name="Data Source List"
                )
                workbook_df = pd.read_excel(content_file, sheet_name="Workbook List")
                view_df = pd.read_excel(content_file, sheet_name="View List")
                flow_df = pd.read_excel(content_file, sheet_name="Flow List")

                # Add column with object type to each dataframe
                user_df.insert(0,"Content Type", "User")
                group_df.insert(0,"Content Type", "Group")
                project_df.insert(0,"Content Type", "Project")
                datasource_df.insert(0,"Content Type", "Datasource")
                workbook_df.insert(0,"Content Type", "Workbook")
                view_df.insert(0,"Content Type", "View")
                flow_df.insert(0,"Content Type", "Flow")

                # Concatenate the separate dataframes into a single dataframe
                manifest_df = pd.concat(
                    [user_df, group_df, project_df, datasource_df, workbook_df, view_df, flow_df]
                )

            else:
                sys.exit(
"""Neither manifest.json nor ContentInventory.xlsx exist.\n
You must run GetSourceContent.py or CoreMigration.py to continue."""
                )

        return manifest_df

    # Clean values and replace empty strings with None
    def clean(value):
        """Cleans a manifest entry value and returns None if empty, else the value.

        Args:
            value (string, list): A value from the manifest.json entry details.

        Returns:
            value (string, list, None): None if value is empty, else value
        """
        return None if value == "" else value

    # Extract relevant fields from manifest entries and create a dataframe
    def create_dataframe(entry_type, entry_data):
        """Creates a Dataframe containing details from the Tableau Migration manifest.json file.

        Args:
            entry_type (string): The type of entry from the manifest (e.g. IUser, IGroup, IProject)
            entry_data (varies): The entry data from the manifest (source, mapping, destination details)

        Returns:
            extracted_data (DataFrame): a DataFrame containing the manifest entry details.
        """
        extracted_data = []

        # Iterate through the data fields from the manifest JSON file
        for entry in entry_data:
            if entry_type == "Tableau.Migration.Content.IUser":
                content_type = "User"
            elif entry_type == "Tableau.Migration.Content.IGroup":
                content_type = "Group"
            elif entry_type == "Tableau.Migration.Content.IProject":
                content_type = "Project"
            elif entry_type == "Tableau.Migration.Content.IDataSource":
                content_type = "Datasource"
            elif entry_type == "Tableau.Migration.Content.IWorkbook":
                content_type = "Workbook"
            elif (
                entry_type
                == "Tableau.Migration.Content.Schedules.Server.IServerExtractRefreshTask"
            ):
                content_type = "ExtractRefreshTask"
            elif entry_type == "Tableau.Migration.Content.ICustomView":
                content_type = "CustomView"

            # If Destination is empty (not yet migrated), populate with None.
            if entry["Destination"] == None:
                destination_id = None
                destination_contenturl = None
                destination_pathsegments = None
                destination_pathseparator = None
                destination_path = None
                destination_name = None
            else:
                destination_id = Manifest.clean(entry["Destination"]["Id"])
                destination_contenturl = Manifest.clean(
                    entry["Destination"]["ContentUrl"]
                )
                destination_pathsegments = Manifest.clean(
                    entry["Destination"]["Location"]["PathSegments"]
                )
                destination_pathseparator = Manifest.clean(
                    entry["Destination"]["Location"]["PathSeparator"]
                )
                destination_path = Manifest.clean(
                    entry["Destination"]["Location"]["Path"]
                )
                destination_name = Manifest.clean(entry["Destination"]["Name"])

            row = {
                "Content Type": content_type,
                "Source Id": Manifest.clean(entry["Source"]["Id"]),
                "Source ContentUrl": Manifest.clean(entry["Source"]["ContentUrl"]),
                "Source PathSegments": Manifest.clean(
                    entry["Source"]["Location"]["PathSegments"]
                ),
                "Source PathSeparator": Manifest.clean(
                    entry["Source"]["Location"]["PathSeparator"]
                ),
                "Source Path": Manifest.clean(entry["Source"]["Location"]["Path"]),
                "Source Name": Manifest.clean(entry["Source"]["Name"]),
                "Mapped PathSegments": Manifest.clean(
                    entry["MappedLocation"]["PathSegments"]
                ),
                "Mapped PathSeparator": Manifest.clean(
                    entry["MappedLocation"]["PathSeparator"]
                ),
                "Mapped Path": Manifest.clean(entry["MappedLocation"]["Path"]),
                "Mapped Name": Manifest.clean(entry["MappedLocation"]["Name"]),
                "Destination Id": destination_id,
                "Destination ContentUrl": destination_contenturl,
                "Destination PathSegments": destination_pathsegments,
                "Destination PathSeparator": destination_pathseparator,
                "Destination Path": destination_path,
                "Destination Name": destination_name,
            }
            extracted_data.append(row)
        return pd.DataFrame(extracted_data)

    def deserialize(manifest_file):
        """_summary_

        Args:
            manifest_file (file): a Manifest JSON file created by the Tableau Migration SDK application.

        Returns:
            manifest_df (DataFrame): a concatenated DataFrame containing all manifest entry details.
        """

        # Load the JSON file
        with open(manifest_file) as manifest:
            data = json.load(manifest)

        # Extract the entries
        entries = data["Entries"]

        # Create a list to store the dataframes
        dataframes = []

        # Iterate over each entry type in the manifest and create dataframes
        for entry_type, entry_data in entries.items():
            print(f"Processing {entry_type}...")
            
            if not entry_data:
                continue
            else:
                df = Manifest.create_dataframe(entry_type, entry_data)
                dataframes.append(df)

        # Concatenate all the dataframes into a single dataframe with all content
        manifest_df = pd.concat(dataframes, ignore_index=True)

        # Since CoreMigration doesn't populate views, get those now.
        final_df = Manifest.get_views(manifest_df)

        # Return the concatenated manifest dataframe
        return final_df
