from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import datetime
import time as t
import tableauserverclient as TSC
from logging_config import *

# -----------------------------------Enter variables
# File location for Exporting Schedules metadata
task_dest_file = os.path.join(file_loc, "TaskList.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will get tasks from your site."

# Prompt the user with the script name and description
logging.info(f"You are running {script_name} script. {script_description}")

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

# Get timezone details for processing Subscription timestamps
dt_tz = datetime.datetime.now()
dt = dt_tz.replace(tzinfo=None)

task_data = []

start_time = t.time()

with server.auth.sign_in(tableau_auth):
    req_options = TSC.RequestOptions(pagesize=1000)
    all_tasks = list(TSC.Pager(server.tasks, request_opts=req_options))

    for task in all_tasks:
        schedule_id = ""
        schedule_name = ""
        schedule_interval = ""
        schedule_start_time = ""

        # Check if Schedule Id is null
        if task.schedule_id is None:
            schedule_id = None
        # If schedule exists, pull details from Schedule item
        else:
            schedule_id = task.schedule_id

            all_schedules = Content.load(ContentItem.schedules, ContentLocation.source)
            for schedule in all_schedules:
                if schedule.id == schedule_id:
                    f_schedule = schedule

            schedule_name = f_schedule.name
            schedule_interval = f_schedule.interval_item.interval
            schedule_start_time = f_schedule.interval_item.start_time

        values = [
            task.id,
            task.task_type,
            task.priority,
            task.target.id,
            task.target.type,
            task.schedule_item.state,
            schedule_id,
            schedule_name,
            schedule_interval,
            schedule_start_time,
        ]
        task_data.append(values)

        logging.info(
            f"Extracting Task [{task.task_type}] for target [{task.target.type}][{task.target.id}]"
        )

logging.info("Creating data frames with Task details. Please wait.")

task_df = pd.DataFrame(
    task_data,
    columns=[
        "Task Id",
        "Task Type",
        "Priority",
        "Target Id",
        "Target Type",
        "Schedule State",
        "Schedule Id",
        "Schedule Name",
        "Schedule Interval",
        "Schedule Start Time",
    ],
)


# Write data frame to Excel file
with pd.ExcelWriter(task_dest_file) as writer:
    logging.info(f"\nWriting results to {task_dest_file}. Please wait.")
    task_df.to_excel(writer, sheet_name="Task List", header=True, index=False)

end_time = t.time()
seconds = end_time - start_time

if seconds < 60:
    duration = f"{round(seconds,2)} second(s)"
elif seconds > 60 and seconds < 3600:
    duration_s = round(seconds % 60, 2)
    duration_m = round(seconds / 60)
    duration = f"{duration_m} minute(s) and {duration_s} second(s)"
elif seconds >= 3600:
    duration_m = round((seconds % 3600) / 60, 2)
    duration_h = round(seconds / 3600)
    duration = f"{duration_h} hour(s) and {duration_m} minute(s)"

# Print final script results
logging.info(f"\nTotal Extract Refresh Tasks extracted: {len(task_df)}")
logging.info(
    f"\nCompleted {script_name} in {duration}. Please view file {task_dest_file}."
)
