from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import datetime
import time as t
from logging_config import *

# -----------------------------------Enter variables
# File location for Exporting Schedules metadata
subscription_dest_file = os.path.join(file_loc, "SubscriptionList.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will get subscriptions from your site."

# Prompt the user with the script name and description
logging.info(f"You are running {script_name} script. {script_description}")

# Get timezone details for processing Subscription timestamps
dt_tz = datetime.datetime.now()
dt = dt_tz.replace(tzinfo=None)

subscription_data = []

start_time = t.time()

all_subscriptions = Content.load(ContentItem.subscriptions, ContentLocation.source)
all_schedules = Content.load(ContentItem.schedules, ContentLocation.source)

for sub in all_subscriptions:
    # Check if Schedule Id is null
    if sub.schedule_id is None:
        schedule_name = None
    # If schedule exists, pull details from Schedule item
    else:
        for sch in all_schedules:
            if sch.id == sub.schedule_id:
                schedule_name = sch.name

    # Store all neeeded values in a list
    values = [
        sub.id,
        sub.attach_image,
        sub.attach_pdf,
        sub.message,
        sub.page_orientation,
        sub.page_size_option,
        sub.schedule_id,
        schedule_name,
        sub.send_if_view_empty,
        sub.subject,
        sub.suspended,
        sub.target.id,
        sub.target.type,
        sub.user_id,
    ]

    # Append values to data table
    subscription_data.append(values)

    logging.info(
        f"Extracting Subscription [{sub.subject}] for user [{sub.user_id}] on [{sub.target.type}][{sub.target.id}]"
    )

logging.info("\nCreating data frames with Subscription details. Please wait.")

# Create data frame using Subscription data
sub_df = pd.DataFrame(
    subscription_data,
    columns=[
        "Subscription Id",
        "Attach Image",
        "Attach PDF",
        "Message",
        "Page Orientation",
        "Page Size Option",
        "Schedule Id",
        "Schedule Name",
        "Send If View Empty",
        "Subject",
        "Suspended",
        "Target Id",
        "Target Type",
        "User Id",
    ],
)

# Write data frame to Excel file
with pd.ExcelWriter(subscription_dest_file) as writer:
    logging.info(f"\nWriting results to {subscription_dest_file}. Please wait.")
    sub_df.to_excel(writer, sheet_name="Subscription List", header=True, index=False)

# Calculate script run time
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
logging.info(f"\nTotal Subscriptions extracted: {len(sub_df)}")
logging.info(
    f"Completed {script_name} in {duration}. Please view file {subscription_dest_file}"
)
