import datetime
import time as t
import pandas as pd
from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
from logging_config import *

# -----------------------------------Enter variables
# File location for Exporting Schedules metadata
schedule_dest_file = os.path.join(file_loc, "ScheduleList.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will get schedules from your site."

# Prompt the user with the script name and description
logging.info(f"You are running {script_name} script. {script_description}")

dt_tz = datetime.datetime.now()
dt = dt_tz.replace(tzinfo=None)
start_time = t.time()

schedule_data = []

all_schedules = Content.load(ContentItem.schedules, ContentLocation.source)

for sch in all_schedules:

    if sch.schedule_type == "Extract":

        logging.info(f"Getting Schedule: {sch.name} [{sch.id}]")
        schedule_id = sch.id
        schedule_name = sch.name
        priority = sch.priority
        schedule_type = sch.schedule_type
        exec_order = sch.execution_order
        interval_item = sch.interval_item

        if interval_item is None:
            logging.error(
                f"Schedule [{schedule_name}][{schedule_id}] has no Interval value. Skipping..."
            )
            continue

        frequency = interval_item._frequency
        start = interval_item.start_time
        if interval_item._frequency == "Hourly":
            end = interval_item.end_time
        else:
            end = None
        interval = interval_item.interval

        values = [
            schedule_id,
            schedule_name,
            priority,
            schedule_type,
            exec_order,
            frequency,
            start,
            end,
            interval,
        ]

        schedule_data.append(values)

sch_df = pd.DataFrame(
    schedule_data,
    columns=[
        "Schedule Id",
        "Schedule Name",
        "Priority",
        "Schedule Type",
        "Execution Order",
        "Frequency",
        "Start Time",
        "End Time",
        "Interval",
    ],
)

# Output results to file
logging.info(f"\nWriting results to {schedule_dest_file}. Please wait.")
with pd.ExcelWriter(schedule_dest_file) as writer:
    sch_df.to_excel(writer, sheet_name="Schedule List", header=True, index=False)

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

logging.info(
    f"\nCompleted {script_name} in {duration}. Please view file {schedule_dest_file}"
)
