# GetFavorites.py reads User Favorites from the UserItems.pkl file created by GetSourceContent.py.
# The output files contain the necessary information to import favorites using the Tableau REST API


from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
import time
import pandas as pd
from logging_config import *

# -----------------------------------Enter variables

fav_dest_file = os.path.join(file_loc, "FavoritesList.xlsx")

create_file_locations()

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script gets information about User Favorites on your site."

# Prompt the user with the script name and description
logging.info(f"You are running the {script_name} script. {script_description}")

# call the perform_action function with dynamic environment names

logging.info(f"Begin {script_name}. This might take several minutes.")

# -----------------------------------Get Favorites
# This section will:
# Read the user list exported from the GetSourceContent.py script

# Set up base variables
fav_data = []
project = TSC.ProjectItem
datasource = TSC.DatasourceItem
workbook = TSC.WorkbookItem
view = TSC.ViewItem
flow = TSC.FlowItem

item_dict = {
    "projects": project,
    "datasources": datasource,
    "workbooks": workbook,
    "views": view,
    "flows": flow,
}

start_time = time.time()

all_users = Content.load(ContentItem.users, ContentLocation.source)

# iterate through site users from UserItem.pkl
for user in all_users:

    logging.info(f"Getting Favorites for User [{user.name}]...")

    # iterate through the list of favorites returned for each user
    for obj, var_name in item_dict.items():
        for var_name in user.favorites[obj]:
            target_id = var_name.id
            target_type = obj[:-1]
            label = var_name.name

            # normalize values to be appended as new rows in the data list
            values = [
                user.id,
                target_type,
                target_id,
                label,
            ]

            # write favorites to the data list
            fav_data.append(values)

# convert the data list to a dataframe
fav_df = pd.DataFrame(
    fav_data,
    columns=[
        "User Id",
        "Target Type",
        "Target Id",
        "Label",
    ],
).drop_duplicates()

# Output results to file
logging.info(f"\nWriting results to {fav_dest_file}. Please wait.")
with pd.ExcelWriter(fav_dest_file) as writer:
    fav_df.to_excel(writer, sheet_name="Favorites List", header=True, index=False)

end_time = time.time()
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
logging.info(
    f"""\n
    Total Users: {len(all_users)}
    Total Favorites extracted: {len(fav_df)}
    """
)
logging.info(f"Completed {script_name} in {duration}. Please view file {fav_dest_file}")
