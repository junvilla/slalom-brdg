"""
Define Global Variables to re-used across Scripts
"""

import os
import string
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# Source Directory and File

# file location. this is where tableau object information and workbooks/data sources will be downloaded
# Read the INI file
file_loc = config["LOG"]["FILE_PATH"]
manifest_loc = config["LOG"]["MANIFEST_FOLDER_PATH"]
log_file_loc = config["LOG"]["FOLDER_PATH"]
export_file_loc = "Export"
import_file_loc = "Import"

log_file = os.path.join(log_file_loc, "Logger.txt")

invalid_char = set(
    string.punctuation.replace("_", "").replace(".", "").replace("-", "")
)
# begin logging
time_log = datetime.now().strftime("%Y-%m-%d %H:%M  ")

# separator for path
sep = "/"

# define whether to include extracts when downloading workbooks
# specify whether to include the extract when downloading the workbook
# IMPORTANT - sometimes including extracts causes issues with publishing via script but not CMT
# set this to True if there are errors in publishing a workbook
# True is the negation of the parameter no_extract
inc_extract = True

# this is where tableau datasources will be downloaded
ds_folder = "DS"
ds_file_loc = os.path.join(file_loc, ds_folder)
ds_dest_file = os.path.join(file_loc, "DataSourceList.csv")

# this is where tableau workbooks will be downloaded
wb_folder = "WB"
wb_dest_file = os.path.join(file_loc, "WorkbookList.csv")
wb_file_loc = file_loc + wb_folder

# this is where custom views will be downloaded
cv_folder = "CV"
cv_dest_file = os.path.join(file_loc, "CustomViewList.xlsx")
cv_log_file = os.path.join(log_file_loc, "DownloadCustomViewsLog.xlsx")
cv_file_loc = os.path.join(file_loc, cv_folder)

# this is where Flows will be downloaded
flow_folder = "FLOWS"
flow_dest_file = os.path.join(file_loc, "FlowList.xlsx")
flow_log_file = os.path.join(log_file_loc, "DownloadFlowsLog.xlsx")
flow_file_loc = os.path.join(file_loc, flow_folder)

# file location to import groups
group_source_file = os.path.join(file_loc, "GroupList.csv")

# file location to add existing users to existing groups
# The csv file must contain a header as the first row
# group_source_file: to import groups
#        The csv file must contain the group name, user id and AD domain (if using Active Directory)
#        The column with the group information must have a column name 'Group Name'. Group Names are case-sensitive
#        If adding users to a group, the file must contain user id (not user name) with column name 'User ID'
#        If creating Active Directory group, the file must also contain the domain name, with column name 'AD Domain'

source_file = os.path.join(file_loc, "AddUserToGroup.csv")
source_usergroups = os.path.join(file_loc, "AddUserToGroup.csv")
source_users = os.path.join(file_loc, "Userlist.csv")

# file location to import projects
# The csv file must contain a header as the first row
# proj_source_file: to import projects
#   The csv file must contain the project name and path. project description is optional
#   Required columns (and column names):
#   1) Project Name (required): name of the project - can only have letters, numbers & underscores
#   2) Path (required): path to determine hierarchy and parent child relationship
#           The format is /Parent/Child/Grandchild, beginning each path with a /.
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

project_source_file = os.path.join(file_loc, import_file_loc, "ProjectList.csv")

# file to update project permissions
# The csv file must contain a header as the first row. Use GetProjects_20230124.py for template of permissions
#   Required columns (and column names):
#   1. Project ID: guid of target project
#   2. Capability: permissions in JSON format
#           example - {'Write': 'Allow', 'Read': 'Allow', 'ProjectLeader': 'Allow'}
#   3. Grantee Type: values must be either user or group
#   4. Grantee Name: if user, email address. if group, group name
#   5. Permission Type: values must be one of the following - Project, Workbook, Data Source, Data Flow, Data Lens

project_permission_source_file = os.path.join(file_loc, "ProjectPermissions.csv")

# file location that identifies workbooks to download from source site
# The csv file must contain a header as the first row. Use GetWorkbook.py to get the metadata from source
# Required columns:
#       1. Workbook ID = guid of workbook (from Tableau Server)
#       2. Include Extract = True/False (note: due to errors in publishing, include extract will always be set to false)

wb_download_file = os.path.join(file_loc, "WorkbookList.csv")

# file location that identifies data sources to download from source site
# The csv file must contain a header as the first row. Use GetDataSource.py to get the metadata from source
# Required columns:
#       1. Datasource ID = guid of data source (from Tableau Server)

ds_download_file = os.path.join(file_loc, "DatasourceList.csv")

# file location to publish workbooks
# The csv file must contain a header as the first row. Use DownloadWorkbook.py to get the metadata from source
# Required columns:
#       1. Workbook Name = name of workbook (from Tableau Server)
#       2. File Name = name of downloaded *.tdsx file (example: Samples.tdsx)
#       3. Project ID = guid of destination project (use GetProjects.py to get project id)
#       4. Owner ID = email of the user in the destination that will be the workbook owner
#       5. Embedded Data Source = True/False True if workbook has data source embedded. This flag will determine whether
#               the workbook needs connections added
#       (use GetWorkbook.py to get owner id)

wb_source_file = os.path.join(file_loc, "WorkbookList.csv")

# file location to update connections of workbooks with embedded data source
# The csv file must contain a header as the first row. Use DownloadWorkbook.py
# & GetWorkbook.py to get the metadata from source
# Required columns:
#       1. Workbook Name = name of workbook (from Tableau Server)
#       2. Project ID = guid of destination project (use GetProjects.py to get project id)
#       3. Connection Data Source Name = name of connection
#       4. Connection UserName = username to connect to the data source
#       5. Server Address = server address of data source
#       6. Server Port = server port of data source

wb_conn_source_file = os.path.join(file_loc, "WorkbookConnectionList.csv")

# file location to publish datasource
# The csv file must contain a header as the first row. Use DownloadDataSource.py to get the metadata from source
# Required columns:
#       1. Data Source Name = name of data source (from Tableau Server)
#       2. File Name = name of downloaded *.tdsx file (example: Samples.tdsx)
#       3. Project ID = guid of destination project (use GetProjects.py to get project id)
#       4. Owner ID = email of data source owner (use GetDataSource.py to get owner id)

ds_source_file = os.path.join(file_loc, "DataSourceList.csv")

# file location to update data source connections
# Import Connections
# The csv file must contain a header as the first row
# conn_source_file: to import data source connection with columns
#       1.Data Source Name = name of the data source that will be migrated
#       2.File Name = file name of the tdsx file (use DownloadDataSource.py to get information)
#       3.User Name
#       4.Password
#       5.Embed Password (True/False) = whether the user name and password should be embedded at publish
#       6.Server Address
#       7.Server Port
#       8.Oauth (True/False) = whether OAuth is used (optional, default is False if not provided)

conn_source_file = os.path.join(file_loc, "ConnectionsList.csv")

# file location to add schedules
# The csv file must contain a header as the first row
# sch_source_file: to import or create schedules. Use GetSchedules.py to get data
#             1. Schedule ID - luid of schedule item
#             2. Schedule Name - name of schedule item
#             3. Priority - integer, lower values represent higher priorities; 0 is highest
#             4. Schedule Type - Extract, Flow, Subscription
#             5. Execution Order - Parallel or Serial
#             6. Frequency - Hourly, Daily, Weekly, Monthly
#             7. Start Time - 00:00:00 24HR format
#             8. Interval - list; day of month (1-31), FirstDay, LastDay, or
#                           Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

sch_source_file = os.path.join(file_loc, "ScheduleList.csv")

# file location to add subscriptions
# The csv file must contain a header as the first row
# sub_source_file: to import or create subscriptions. Use GetSubscriptions.py to get data
#             1. Target ID - workbook guid or view guid
#             2. Target Type - workbook or view
#             3. Attach Image - True/False
#             4. Attach PDF - True/False
#             5. Message - message in email
#             6. Schedule ID - guid of schedule
#             7. Send If View Empty - True/False
#             8. Subject - subject in email
#             9. User Name - subscriber (email of user)

# sub_source_file = os.path.join(file_loc, import_file_loc, 'Subscription_Import.csv')
sub_source_file = os.path.join(file_loc, "SubscriptionList.csv")

# file location to add tasks
# The csv file must contain a header as the first row
# task_source_file: to import or create tasks. Use GetTasks.py to get data
#             1. Task ID - task guid
#             2. Task Type - FullRefresh/IncrementalRefresh
#             3. Priority - the priority of the task on the server
#             4. Target ID - workbook or datasource guid
#             5. Target Name - workbook or datasource name
#             6. Project ID - guid of project
#             7. Project Name - project name
#             8. Schedule ID - schedule guid
#             9. Schedule Name - schedule name
#             10.Schedule State - Active/Inactive
#             11.Schedule Type - Extract/Subscription/Flow
#             12.Schedule Interval - list of days, 1, LastDay, etc.
#             13.Schedule Start Time - 24-hour start time with seconds (e.g., 23:00:00)

# task_source_file = os.path.join(file_loc, import_file_loc, 'Task_Import.csv')
task_source_file = os.path.join(file_loc, "TaskList.csv")

# file location that identifies Custom Views to download from source site
# The csv file must contain a header as the first row. Use GetCustomViews.py to get the metadata from source
# Required columns:
#       1. Custom View ID = guid of Custom View (from Tableau Server)
#       2. Custom View Name = name of Custom View (from Tableau Server)
#       3. Shared = public visibility flag of the Custom View
#       4. View Name = name of the original View (from Tableau Server)
#       5. Workbook Name = name of the workbook containing the original View (from Tableau Server)
#       6. Owner Name = guid of Custom View (from Tableau Server)

cv_download_file = os.path.join(file_loc, "CustomViewList.xlsx")

