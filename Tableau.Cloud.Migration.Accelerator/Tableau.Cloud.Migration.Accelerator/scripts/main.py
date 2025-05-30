"""
Main wrapper to run so that user can call different TCM scripts from main
"""

import os
import subprocess

# Get the absolute path of the main.py script
script_path = os.path.abspath(__file__)

# Get the directory of the script
script_directory = os.path.dirname(script_path)

# Set the working directory to the script directory
os.chdir(script_directory)

# ---------- update introduction

script_introduction = "------------------------------------------------------\
    \nWelcome to Slalom Tableau Cloud Migration Accelerator!\
    \n------------------------------------------------------"


# ------------------------------


# Function to execute a Python script
def execute_script(script_name):
    if os.name == "posix":  # for Unix/Linux/MacOS
        subprocess.run(["python", f"{script_name}"])
    elif os.name == "nt":  # for Windows
        subprocess.run(["python", f"{script_name}"])


print(f"{script_introduction}")


# Ask user for input
# prompt the user to enter a choice
def get_action_choice():
    print("\nWhat migration activity do you want to perform?")
    print("\n--- Configuration and Testing ---------------------")
    print("\t1: Test Connection/Authentication")
    print("\n--- Users/Groups/Projects/Datasources/Workbooks ---")
    print("--- Extract Refresh Tasks/Custom Views ------------")
    print("\t2: Get Hidden Views for Workbooks")
    print("\t3: Migrate Content")
    print("\n--- Flows/Extract Refresh Tasks/Subscriptions -----")
    print("--- User Favorites/Custom Views -------------------")
    print("\t4: Get Content Details")
    print("\t5: Download Content")
    print("\t6: Create/Publish Content")
    print("\t7: Access the Deprecated Script Archive")

    choice = input('\nEnter your choice (1-7) or "EXIT" (0): ')
    return choice


while True:
    main_choice = get_action_choice()

    # Execute script based on choice
    if main_choice == "1":
        print(
            "\nTest Connection/Authentication."
            "\nRuns a brief authorization to the Tableau site using config.ini"
            " & env variables."
        )
        execute_script("ConnectionTest.py")
    elif main_choice == "2":
        execute_script("GetHiddenViews.py")
    elif main_choice == "3":
        print(
            "\nMigrate content from source to destination."
            "\nMigrates users, groups, projects, datasources, and workbooks."
            "\nNote: Core Migrator skips users, groups, projects, workbooks,"
            " and datasources without initial configuration."
        )
        sub_choice = input("\nDo you wish to continue (Y/n): ")

        if sub_choice.upper() == "Y":
            execute_script("CoreMigration.py")
        elif sub_choice.upper() == "N":
            continue
        else:
            print("\nInvalid choice!")

    elif main_choice == "4":
        print(
            "\nYou selected to get content details from your environment."
            "\nThis process will generate Excel/csv files "
            "with metadata information.\nWhat would you like to do?"
        )
        print(" ")
        print("\t1. Get Source Content")
        print("\t2. Get Tableau Prep Flows")
        print("\t3. Get Schedules")
        print("\t4. Get Subscriptions")
        print("\t5. Get Extract Refresh Tasks")
        print("\t6. Get User Favorites")
        print("\t7. Get Custom Views")
        print("\t8. Get Destination Content")
        print("\n\t0. Exit")

        sub_choice = input("\nEnter your choice (1-8) or 0 to Exit: ")

        if sub_choice == "1":
            execute_script("GetSourceContent.py")
        elif sub_choice == "2":
            execute_script("GetFlows.py")
        elif sub_choice == "3":
            execute_script("GetSchedules.py")
        elif sub_choice == "4":
            execute_script("GetSubscriptions.py")
        elif sub_choice == "5":
            execute_script("GetTasks.py")
        elif sub_choice == "6":
            execute_script("GetFavorites.py")
        elif sub_choice == "7":
            execute_script("GetCustomViews.py")
        elif sub_choice == "8":
            execute_script("GetDestinationContent.py")
        elif sub_choice == "0":
            continue
        else:
            print("\nInvalid choice!")

    elif main_choice == "5":
        print(
            "\nYou selected to download content."
            "\nThis step is necessary before publishing Flows and"
            " Custom Views to the destination environment."
            "\nWhat would you like to do?"
        )
        print(" ")

        print("\t1. Download Prep Flows")
        print("\t2. Download Custom Views")
        print("\n\t0. Exit")

        sub_choice = input("\nEnter your choice (1-2) or 0 to Exit: ")

        if sub_choice == "1":
            execute_script("DownloadFlows.py")
        elif sub_choice == "2":
            execute_script("DownloadCustomViews.py")
        elif sub_choice == "0":
            continue
        else:
            print("\nInvalid choice!")

    elif main_choice == "6":
        # ask user for input (second level)
        print(
            "\nYou selected to create and publish content."
            "\nReads metadata and external files to create content &"
            " publish to the destination site."
            "\nWhat would you like to do?"
        )
        print(" ")
        print("\t1. Publish Tableau Prep Flows")
        print("\t2. Publish Custom Views and Add as User Defaults")
        print("\t3. Create Extract Refresh Tasks")
        print("\t4. Create Subscriptions")
        print("\t5. Create User Favorites")
        print("\n\t0. Exit")

        sub_choice = input("\nEnter your choice (1-5) or 0 to Exit: ")

        if sub_choice == "1":
            print(
                "\nYou have selected to publish Tableau Prep Flows."
                "\nThe steps below are required before publishing Flows:"
            )
            print("\t1. Run GetSourceContent.py")
            print(
                "\t2. Migrate Users, Groups, and Projects to"
                " the Destination environment."
            )
            print("\t3. Run GetDestinationContent.py")
            print("\t4. Run DownloadFlows.py")
            print(" ")

            sub_sub_choice = input("\nHave you completed these steps (Y/n): ")

            if sub_sub_choice.upper() == "Y":
                execute_script("PublishFlows.py")
            elif sub_sub_choice.upper() == "N":
                continue
            else:
                print("\nInvalid choice!")

        elif sub_choice == "2":
            print(
                "\nYou have selected to publish Custom Views."
                "\nThe steps below are required before publishing Custom Views:"
            )
            print("\t1. Run GetSourceContent.py")
            print(
                "\t2. Migrate Users, Projects, Data Sources, and Workbooks to"
                " Destination environment."
            )
            print("\t3. Run GetDestinationContent.py")
            print("\t4. Run DownloadCustomViews.py")
            print(" ")

            sub_sub_choice = input("\nHave you completed these steps (Y/n): ")

            if sub_sub_choice.upper() == "Y":
                execute_script("PublishCustomViews.py")
            elif sub_sub_choice.upper() == "N":
                continue
            else:
                print("\nInvalid choice!")

        elif sub_choice == "3":
            print(
                "\nYou have selected to create extract refresh tasks."
                "\nThe steps below are required before creating tasks:"
            )
            print("\t1. Run GetSourceContent.py")
            print(
                "\t2. Migrate Projects, Data Sources, and Workbooks to"
                " Destination environment."
            )
            print("\t3. Run GetDestinationContent.py")
            print(" ")

            sub_sub_choice = input("\nHave you completed these steps (Y/n): ")

            if sub_sub_choice.upper() == "Y":
                execute_script("CreateTasks.py")
            elif sub_sub_choice.upper() == "N":
                continue
            else:
                print("\nInvalid choice!")

        elif sub_choice == "4":
            print("\nCreate subscriptions. Steps required:")
            print("\t1. Run GetSourceContent.py")
            print(
                "\t2. Migrate Users, Projects, Data, and Workbooks to"
                "Destination environment"
            )
            print("\t3. Run GetDestinationContent.py")
            print(" ")

            sub_sub_choice = input("\nHave you completed these steps (Y/n): ")

            if sub_sub_choice.upper() == "Y":
                execute_script("CreateSubscriptions.py")
            elif sub_sub_choice.upper() == "N":
                continue
            else:
                print("\nInvalid choice!")

        elif sub_choice == "5":
            print(
                "\nYou have selected to user Favorites."
                "\nThe steps below are required before creating Favorites:"
            )
            print("\t1. Run GetSourceContent.py")
            print(
                "\t2. Migrate Users, Projects, Data Sources, Workbooks, and Flows"
                " to the Destination environment."
            )
            print("\t3. Run GetDestinationContent.py")
            print(" ")

            sub_sub_choice = input("\nHave you completed these steps (Y/n): ")

            if sub_sub_choice.upper() == "Y":
                execute_script("CreateFavorites.py")
            elif sub_sub_choice.upper() == "N":
                continue
            else:
                print("\nInvalid choice!")

        elif sub_choice == "0":
            continue

        else:
            print("\nInvalid choice!")

    elif main_choice == "7":
        print("\n----WELCOME TO THE DEPRECATED SCRIPT ARCHIVE-------------")
        print(" ")
        print("WARNING: These scripts are no longer maintained or updated.")
        print(" ")
        print("\nGet Content ---------------------------------------------")
        print("\t1. Get Users and Groups")
        print("\t2. Get Projects")
        print("\t3. Get Data Sources")
        print("\t4. Get Workbooks & Workbook Connections")
        print("\t5. Get Asset Permissions")
        print("\nMigrate Content -----------------------------------------")
        print("\t6. Create Groups")
        print("\t7. Add Users to Groups")
        print("\t8. Create Projects")
        print("\t9. Update Project Permissions")
        print("\t10. Download & Publish Data Sources")
        print("\t11. Download & Publish Workbooks")
        print("\t12. Update Asset Permissions -- NOT YET IMPLEMENTED")
        print("\n\t0. Exit")

        sub_choice = input("\nEnter your choice (1-12) or 0 to Exit: ")

        if sub_choice == "1":
            execute_script("./archive/GetUsersGroups.py")

        elif sub_choice == "2":
            execute_script("./archive/GetProjects.py")

        elif sub_choice == "3":
            execute_script("./archive/GetDataSource.py")

        elif sub_choice == "4":
            execute_script("./archive/GetWorkbooks.py")

        elif sub_choice == "5":
            execute_script("./archive/GetWorkbookPermissions.py")

        if sub_choice == "6":
            execute_script("./archive/CreateGroup.py")

        elif sub_choice == "7":
            execute_script("./archive/AddUserToGroup.py")

        elif sub_choice == "8":
            execute_script("./archive/CreateProjects.py")

        elif sub_choice == "9":
            execute_script("./archive/UpdateProjectPermissions.py")

        elif sub_choice == "10":
            print(
                "\nYou have selected to download and publish data sources."
                "\nWhat would you like to do?"
            )
            print(" ")
            print("\t1. Download Data Sources")
            print("\t2. Publish Data Sources")

            sub_sub_choice = input("\nEnter your choice: ")

            if sub_sub_choice == "1":
                execute_script("./archive/DownloadDataSource.py")
            elif sub_sub_choice == "2":
                execute_script("./archive/PublishDataSource.py")
            else:
                print("\nInvalid choice!")

        elif sub_choice == "11":
            print(
                "\nYou have selected to download and publish workbooks."
                "\nWhat would you like to do?"
            )
            print(" ")
            print("\t1. Download Workbooks")
            print("\t2. Publish Workbooks")

            sub_sub_choice = input("\nEnter your choice (1-2): ")

            if sub_sub_choice == "1":
                execute_script("./archive/DownloadWorkbooks.py")
            elif sub_sub_choice == "2":
                execute_script("./archive/PublishWorkbooks.py")
            else:
                print("\nInvalid choice!")

        elif sub_choice == "12":
            execute_script("./archive/UpdateWorkbookPermissions.py")

        elif sub_choice == "0":
            continue

        else:
            print("\nInvalid choice!")

    elif (
        main_choice.upper().strip() == "EXIT"
        or main_choice.upper().strip() == '"EXIT"'
        or main_choice == "0"
    ):
        print("\nExiting the program")
        break

    elif main_choice is None:
        continue

    else:
        print("\nInvalid choice!")
