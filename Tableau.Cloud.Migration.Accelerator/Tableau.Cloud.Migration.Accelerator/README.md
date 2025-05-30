# Tableau Cloud Migration Accelerator
<!-- TOC -->
- [Tableau Cloud Migration Accelerator](#tableau-cloud-migration-accelerator)
  - [Introduction to the Tableau Cloud Migration Accelerator](#introduction-to-the-tableau-cloud-migration-accelerator)
  - [Pre-Migration Setup](#pre-migration-setup)
    - [Download and Install Python](#download-and-install-python)
      - [Windows](#windows)
      - [MacOS](#macos)
      - [Adding Python to PATH without Admininistrator role](#adding-python-to-path-without-admininistrator-role)
    - [Download and Install Visual Studio Code](#download-and-install-visual-studio-code)
      - [Recommended Extensions](#recommended-extensions)
    - [Download and Install .NET SDK](#download-and-install-net-sdk)
    - [Set your Working Directory in Visual Studio Code](#set-your-working-directory-in-visual-studio-code)
    - [Create a Virtual Environment and Run Setup](#create-a-virtual-environment-and-run-setup)
      - [Activate the virtual environment](#activate-the-virtual-environment)
      - [Run `setup.py`](#run-setuppy)
    - [Store Authentication Credentials and Environment Details](#store-authentication-credentials-and-environment-details)
      - [Update config.ini and .env variables](#update-configini-and-env-variables)
  - [Running the Tableau Cloud Migration Accelerator](#running-the-tableau-cloud-migration-accelerator)
  - [Preparing for Migration](#preparing-for-migration)
    - [Extract Tableau Metadata](#extract-tableau-metadata)
    - [Review Content and Update Source Environment](#review-content-and-update-source-environment)
    - [Build a Migration Plan](#build-a-migration-plan)
    - [Build Custom Functions (Filters, Mappings, Transformations) for the Tableau Migration Application](#build-custom-functions-filters-mappings-transformations-for-the-tableau-migration-application)
  - [Begin the Migration](#begin-the-migration)
    - [Prepare Tableau Cloud for Migration](#prepare-tableau-cloud-for-migration)
      - [Add Users to Site](#add-users-to-site)
      - [Add Users To Groups](#add-users-to-groups)
    - [Tableau Migration Program](#tableau-migration-program)
      - [Importing and Adding Filters, Mappings, and Transformers](#importing-and-adding-filters-mappings-and-transformers)
      - [Running the Tableau Migration Program](#running-the-tableau-migration-program)
      - [Tableau Migration Manifests](#tableau-migration-manifests)
        - [Importing an Existing Manifest](#importing-an-existing-manifest)
    - [Using the Premade Filter and Mapping Functions](#using-the-premade-filter-and-mapping-functions)
      - [Migrate Specific Users Only](#migrate-specific-users-only)
      - [Skip Content by Parent Location](#skip-content-by-parent-location)
      - [Migrate Tagged Data Sources and Workbooks](#migrate-tagged-data-sources-and-workbooks)
      - [Map Content from Skipped Projects to New Destination](#map-content-from-skipped-projects-to-new-destination)
    - [Sample Tableau Migration Program Functions](#sample-tableau-migration-program-functions)
      - [Migrate Content by Project Name](#migrate-content-by-project-name)
      - [Update Project Root (Top-Level Project)](#update-project-root-top-level-project)
    - [Extract Refresh Tasks, Subscriptions, Favorites, and Custom Views](#extract-refresh-tasks-subscriptions-favorites-and-custom-views)
      - [Extract Refresh Tasks](#extract-refresh-tasks)
      - [Subscriptions](#subscriptions)
      - [Favorites](#favorites)
      - [Custom Views](#custom-views)
  - [Using the Archived Tableau Cloud Migration Accelerator Scripts](#using-the-archived-tableau-cloud-migration-accelerator-scripts)
    - [Extract and Download Data Sources and Workbooks from Source Site](#extract-and-download-data-sources-and-workbooks-from-source-site)
      - [Prepare the files needed to download workbooks](#prepare-the-files-needed-to-download-workbooks)
    - [Create Projects](#create-projects)
      - [Example](#example)
    - [Update project permissions](#update-project-permissions)
    - [Publish Data Sources](#publish-data-sources)
    - [Publish Workbooks](#publish-workbooks)
  - [Python Scripts](#python-scripts)
    - [General Purpose Scripts](#general-purpose-scripts)
    - [Shared scripts](#shared-scripts)
    - [Tableau Migration Program Scripts](#tableau-migration-program-scripts)
    - [User/Group Scripts](#usergroup-scripts)
    - [Project Scripts](#project-scripts)
    - [Data Source Scripts](#data-source-scripts)
    - [Workbook Scripts](#workbook-scripts)
    - [Schedule, Task, and Subscription Scripts](#schedule-task-and-subscription-scripts)
    - [Favorites Scripts](#favorites-scripts)
    - [Custom View Scripts](#custom-view-scripts)
  - [Troubleshooting](#troubleshooting)
    - [Getting errors connecting to Server/Cloud using the script](#getting-errors-connecting-to-servercloud-using-the-script)
    - [Errors indicating Python package not installed](#errors-indicating-python-package-not-installed)
    - [Errors related to Virtual Environments](#errors-related-to-virtual-environments)
<!-- TOC -->

## Introduction to the Tableau Cloud Migration Accelerator

This set of Python scripts utilizes the Tableau Server Client and Tableau Migration libraries, as well as the Tableau REST API to accelerate a client's migration between Tableau Server and/or Tableau Cloud environments. The scripts perform various actions to streamline the migration process and can be customized to fit the client's needs.

By automating migration tasks, the Tableau Cloud Migration Accelerator reduces the amount of manual effort and time required to complete the migration. This means that clients can migrate their Tableau environment quickly and efficiently, with minimal disruption to their business operations.

To use the Tableau Cloud Migration Accelerator, follow the steps outlined in the documentation provided within the scripts. Clients can customize the scripts to suit their specific needs, ensuring a tailored migration experience that meets their unique requirements.

***

## Pre-Migration Setup

Before beginning a Tableau Cloud Migration, complete the follow steps to prepare yourself and your technical environment.

### Download and Install Python

If you do not have Python installed, you can download and run the official Python installer for your operating system.  

Here are the steps you can follow to install Python and the required libraries for both Windows and macOS:

#### Windows

Go to the official Python website at <https://www.python.org/downloads/windows/> and download the latest version of Python.
Run the downloaded executable file and follow the instructions to install Python on your system.
***Please be sure to install Python on the PATH environment variable.***

#### MacOS

Go to the official Python website at <https://www.python.org/downloads/mac-osx/> and download the latest version of Python.
Double-click the downloaded .pkg file and follow the instructions to install Python on your system.

#### Adding Python to PATH without Admininistrator role

If you do not have access to add Python to the PATH environment variable due to insufficient privileges, you can still add Python to your User Environment Variables:
<https://learn.microsoft.com/en-US/troubleshoot/windows-client/performance/cannot-modify-user-environment-variables-system-properties>

***

### Download and Install Visual Studio Code

This guide is written using Visual Studio Code as the preferred IDE; however, you may use another IDE to your preference.

Go to the official Visual Studio Code website at <https://code.visualstudio.com/download> and download the latest version of VSC.
Run the installer file and follow the instructions to install Visual Studio Code on your system.

#### Recommended Extensions

It is highly recommended that you install the following Visual Studio Code extensions to more easily read and navigate the source files:

- json
- Python
- Rainbow CSV
- XML

***

### Download and Install .NET SDK

The Tableau Migration application uses the Microsoft .NET Framework for libraries written and compiled from C#.  Before running the Tableau Cloud Migration Accelerator, you will need to download and install .NET 8.0.

Go to the official .NET website at <https://dotnet.microsoft.com/en-us/download/dotnet/8.0> and download the latest version of the .NET SDK (not the ASP.NET Core Runtime, .NET Desktop Runtime, or .NET Runtime).
Run the installer file and follow the instructions to install .NET on your system.

### Set your Working Directory in Visual Studio Code

Once you have installed Python, download and install the latest code release from Bitbucket.  You can do this by clicking on the menu button (`...`) and choosing 'Download Repository'.  Unzip the files.

In Visual Studio Code, in the `Explorer (Ctrl+Shift+E)`, click 'Open Folder' and select the `Tableau Cloud Migration Accelerator` folder.

You should see a list of folders and scripts load into the Explorer navigation column.

Open a new ``Terminal (Ctrl+Shift+`)`` and install run the following command:
  `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip_system_certs` (Windows)
  `pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip_system_certs` (Linux/Unix/MacOS)

Navigate to the `scripts` folder, e.g.: `Documents\Bitbucket\tableau-cloud-migration-accelerator\Tableau Cloud Migration Accelerator\Scripts`
  `cd Scripts` or `cd 'Tableau Cloud Migration Accelerator\Scripts`

***

### Create a Virtual Environment and Run Setup

In the Terminal with your directory set to the `scripts` folder, enter the following command:

  `python -m venv venv` (Windows)\
  `python3 -m venv venv` (Linux/Unix/MacOS)

#### Activate the virtual environment

In the Terminal, enter the following command:

  `.\venv\Scripts\Activate.ps1` (Windows)\
  `source ./venv/bin/activate` (Linux/Unix/MacOS)

  OR if that fails, you can open the script from the Explorer and click `Run (Ctrl+F5)`

#### Run `setup.py`

With your virtual environment activated, you can now install the required libraries and update the config.ini variables.

In the Terminal with your directory set to the `scripts` folder, enter the following command:
  `python setup.py` (Windows)\
  `python3 setup.py` (Linux/Unix/MacOS)

***Note: setup.py will fail if your virtual environment is not active.***

The necessary Python libraries will be installed automatically in your virtual environment.

Once this process is complete, you will be prompted for configuration variables to populate ***config.ini*** and ***.env***

***

### Store Authentication Credentials and Environment Details

Enter file locations for all input and output files to be saved, authentication credentials, site URLs, and other details.

#### Update config.ini and .env variables  

- Personal Access Tokens are now required. Refer to the section [Create Personal Access Token](https://help.tableau.com/current/pro/desktop/en-us/useracct.htm) in Tableau Help.  
  
- Define the source and destination sites. You do not need to include a forward slash in the end of the url. For Tableau Server, if your site is Default, leave SITE_CONTENT_URL blank
  
    ```ini
    [SOURCE]
    URL = https://server.tableau.com
    SITE_CONTENT_URL = 
    ACCESS_TOKEN_NAME = 

    [DESTINATION]
    URL = https://cloud.tableau.com
    SITE_CONTENT_URL = sitename
    ACCESS_TOKEN_NAME = 
    ```  

- Enter the logging/file storage details.  Manifest is currently only used by the Tableau Migration SDK scripts.  You can press enter to leave these variables unchanged.
  
    ```ini
    [LOG]
    FOLDER_PATH = ./LOG/
    FILE_PATH = ./FILES/
    MANIFEST_FOLDER_PATH = ./MANIFEST/
    ```

- Enter the details for users on Tableau Cloud.  The SPECIAL_USERS section is optional, and only used by specific filters/hooks/mappings in the Tableau Migration SDK.
  
    ```ini
    [USERS]
    EMAIL_DOMAIN = email.com

    [SPECIAL_USERS]
    ADMIN_DOMAIN = 
    ADMIN_USERNAME = 
    EMAILS = []
    ```

- Enter the details for migrating users to Tableau Cloud from Tableau Server.  Press enter to leave these variables unchanged.
  
    ```ini
    [TEST_TABLEAU_CLOUD_USERNAME_OPTIONS]
    BASE_OVERRIDE_MAIL_ADDRESS =
    ALWAYS_OVERRIDE_ADDRESS = true
    ```

- When using the Tableau Migration Application scripts, if you have already migrated some content, enter the path to the most recent Manifest (JSON) file.
- The Manifest files allow the Tableau Migration Application to interpret what content has already been migrated and skip that content, focusing only on new migration content.
  
    ```ini
    [MANIFEST]
    PREVIOUS_MANIFEST =
    ```

- At the end of configuration, the setup.py script will prompt you for the personal access token secrets for your source and destination environments.
  
    ```ini
    SOURCE_TOKEN_SECRET = 
    DESTINATION_TOKEN_SECRET = 
    ```

***

## Running the Tableau Cloud Migration Accelerator

In the VSCode terminal, enter the following:
  `code .` (This will launch the virtual environment in a new window using the venv interpreter)

In the Terminal, with your directory set to the `scripts` folder, enter the following command:\
  `python main.py` (Windows)\
  `python3 main.py` (Linux/Unix/MacOS)

You will be prompted with the following selections:

```shell
------------------------------------------------------    
Welcome to Slalom Tableau Cloud Migration Accelerator!    
------------------------------------------------------

What migration activity do you want to perform?

--- Configuration and Testing ---------------------
        1: Test Connection/Authentication

--- Users/Groups/Projects/Datasources/Workbooks ---
        2: Migrate Content

--- Tasks/Subscriptions/Favorites/Custom Views ----
        3: Get Content Details
        4: Download Content
        5: Create/Publish Content

Enter your choice (1-5) or "EXIT":
```

***Test Connection/Authentication*** - Runs a script that will test your configuration variables and return details about the Tableau Server/Cloud instance. This is useful for ensuring that you have configured your technical environment and the Tableau Cloud Migration Accelerator correctly.

***Migrate Content*** - Executes the Tableau Migration Program, built off the Tableau Migration SDK. This program will automate the migration of users, groups, projects, data sources, workbooks, and extract refresh tasks. This application is highly customizable using Python functions.

- ***Filters*** can be configured to limit the content migrated.
- ***Mapping*** functions can be configured to re-map content as it is published to Tableau Cloud.
- ***Transformations*** can be configured to make changes to content, such as activating Tableau Bridge refreshes or adding tags to items.

***Get Content Details*** - Access a list of scripts that extract information on schedules, subscriptions, extract refresh tasks, favorites, and custom views from your site.

***Download Content*** - Downloads the necessary JSON files to migrate custom views from Tableau Server to Tableau Cloud. This will download both hidden and public custom views.

***Create/Publish Content*** - Access a list of scripts that allow you to create subscriptions, extract refresh tasks, and favorites, as well as publish custom views.

***

***If you need to access archived Python scripts***, enter `6` at the menu (a hidden option) to see a list of scripts that allow you to:

- Get lists of users, groups, projects, data sources, workbooks, and permissions
- Create groups, add users to groups, and create projects
- Download data sources and workbooks
- Publish data sources and workbooks
- Update project permissions
- Update data source and workbook ownership

*Note: These scripts are no longer maintained unless needed specifically for a client project.*

***

Tableau REST API has limits on the number of API calls per user per hour. For instance, when creating projects using the script, it might be necessary to split content into multiple batches or run the script several times for a larger migration.

Most scripts have built in rate limits and/or pauses to help regulate the number of API calls being sent to prevent errors.

***

## Preparing for Migration  

***Note: The remainder of this README file assumes that users/groups are already created/provisioned in Tableau Cloud. \ While you can complete some migration steps without Users/Groups, such as migrating projects, data sources, and workbooks, the permissions for these content items cannot be migrated without Users/Groups.***

### Extract Tableau Metadata

As a best practice, it is recommended to extract Tableau Content Metadata from Tableau Server before initiating a migration. Not only does this help build a migration plan, but can be used to track migrated content throughout the process. Many of these scripts reside in the Archive section (hidden option `6` from the Tableau Cloud Migration Accelerator main menu).

| Your Selection         | Files Generated          | Description                                                                                        |
|------------------------|--------------------------|----------------------------------------------------------------------------------------------------|
| Get Users and Groups   | GroupUserList.xlsx       | This script generates a list of users, groups, site roles, and group membership. <br>Use this template to map users and groups when creating permissions, assigning ownership, creating favorites and subscriptions, and publishing custom views. |
| Get Projects           | ProjectList.csv <br>ProjectPermission.csv <br>ProjectList.xlsx         | This generates the list of projects, project permissions, project owners and project hierarchy. <br>Use this as a template to import projects to your destination site. |
| Get Data Sources       | DataSourceList.xlsx      | Extracts datasource metadata. <br>Use this as a template to download and publish datasources. |
| Get Workbooks & Workbook Connections | WorkbookList.xlsx <br>Workbook_To_Download.csv | Extracts workbook metadata. <br>Use this as a template to download and publish workbooks. |
| Get List of Schedules  | Schedules.xlsx           | Generates a list of schedules of workbook extracts. |
| Get Subscriptions      | Subscriptions.xlsx       | Generates a list of user subscriptions to workbooks. |
| Get Extract Refresh Tasks              | Task List.xlsx           | Generates a list of workbook & datasources with refresh extract tasks and schedule refresh. <br>It will indicate if the refresh task is active or inactive. |
| Get User Favorites     | FavoritesList.xlsx       | Generates a list of user favorites. <br>Use this as a template to re-assign favorites based on Tableau Cloud LUIDs. |
| Get Custom Views       | CustomViewList.xlsx <br>CustomView_UserList.xlsx | Generates two lists: a list of custom views, and a list of users with custom views set as default. <br>Use this as a template to publish custom views and assign them as default for users in Tableau Cloud. |

### Review Content and Update Source Environment

The Tableau Migration Application maps specific content items by `contentUrl`, a unique field generated when creating or publishing items to Tableau.
If any content has identical names, this can cause content to be mapped incorrectly when published to Tableau Cloud.

*`contentUrl` is not a value that can be set when publishing content to Tableau. It is automatically generated.*

For example:

- Tableau Server has two published data sources named `Superstore Data`; one residing in the `Tableau Samples` project, and the other in `Archive`
- These will each have unique contentUrls.  One may be `SuperstoreData` and the other `SuperstoreData_123456`
- If `Superstore Data` from the `Archive` project is migrated first, it may take the contentUrl `SuperstoreData`
- This can cause any workbook or metric connected to `Superstore Data` from `Tableau Samples` to be remapped to the archived version of the data source.

To prevent problems like this from occurring, it is important to ensure that no workbooks or data sources have identical names before initiating a migration.

***

### Build a Migration Plan

While the Tableau Migration Program can migrate an entire Tableau Server in one run, this is not recommended. Instead, a typical approach to migrating a server will fall into one of two categories:

- Migrating content by Site (if there are multiple sites on Tableau Server)
- Migrating content by top-level Project

If Tableau Server has multiple sites, an important component of your migration plan should be mapping sites to projects in Tableau Cloud, since most Tableau Cloud organizations will only have one site.

If mapping multiple sites (or projects) to new projects, be cautious to use identical names. Instead, use unique but consistent naming conventions:

- `Site_1//Site_1_Archive` instead of `Site_1//Archive`

While content will be mapped by contentUrl or project path, having unique project names is beneficial for navigating the Tableau environment.

When building a migration plan, it is important to communicate estimated timelines for migrating content from Tableau Server to Tableau Cloud. This helps prevent updates to content in Tableau Server after that content has been migrated to Tableau Cloud. If approved, disable Publish permissions to Tableau Server prior to migrating content to Tableau Cloud. Otherwise, allocate time to conduct a delta analysis for changes to content since the date of its migration.

***

### Build Custom Functions (Filters, Mappings, Transformations) for the Tableau Migration Application

***Coming Soon***

Due to the highly technical nature of this section, there will be a separate README file on building custom functions. If you need to build custom functions, work with a Tableau Migration SME and prepare a sandbox environment for testing functions before deploying them in a production migration.

***

## Begin the Migration

### Prepare Tableau Cloud for Migration

1. Set up Authentication - See [Tableau Authentication](https://help.tableau.com/current/online/en-us/security_auth.htm)
2. Install and configure your data sources for Tableau Bridge - See [Tableau Bridge](https://help.tableau.com/current/online/en-us/qs_refresh_local_data.htm)
3. If you are not provisioning users/groups directly to Tableau Cloud via SCIM from Active Directory, OneLogin, etc., ***continue to the next step.***\
  Otherwise, move ahead to [Extract and Download Data Sources and Workbooks from Source Site](#extract-and-download-data-sources-and-workbooks-from-source-site).

#### Add Users to Site

You can provision users in Tableau Cloud in several ways:

- Provision users from Identity Provider (IdP) such as Entra ID (Azure Active Directory), Okta, or OneLogin.
    - [Automate User Provisioning and Group Synchronization through an External Identity Provider](https://help.tableau.com/current/online/en-us/scim_config_online.htm)
- Import Users from File
    - [Import Users](https://help.tableau.com/current/online/en-us/users_import.htm)
- Import Users with Stand-alone Script (not yet implemented)
- Import Users with Tableau Migration program
    - [Tableau Migration Program](#tableau-migration-program)

#### Add Users To Groups

There are three methods to add users to a group:

- Add Users to Groups via SCIM
    - [Automate User Provisioning and Group Synchronization through an External Identity Provider](https://help.tableau.com/current/online/en-us/scim_config_online.htm)
- Add Users to Groups via the Tableau Migration Program
    - [Tableau Migration Program](#tableau-migration-program)
- Add Users to Groups via the Tableau Cloud Migration scripts (see below)

***Adding Users to Groups with the Tableau Cloud Migration Accelerator***

- Select `6` to access the menu of archived scripts, and then select option `7. Add Users to Groups`.
- Prepare input file.
- Save in the Import folder with name *AddUserToGroup.csv*.

| Group Name             | User ID                  |
|------------------------|--------------------------|
| *Required, case sensitive* | *Required*           |
| Group Name             | User email address       |

### Tableau Migration Program

The Tableau Migration Program (the CoreMigration.py script) is built on the Tableau Migration Python library.

Utilizing a set of scripts and libraries developed, maintained, and supported by Tableau, this component of the Tableau Cloud Migration Accelerator assists users in easily and efficiently migrating the following assets to Tableau Cloud:

- Users/Groups
- Projects
- Data Sources
- Workbooks
- Extract Refresh Tasks

In addition to these content items, the Tableau Migration Program migrates permissions, and can be customized with Python functions (hooks) to:

- Filter content, only migrating items that meet (or don't meet) a declared criteria
- Map content, such as assigning top-level projects or reassigning projects entirely
- Transform content, such as adding tags to migrated content or activating the remote query agent (Tableau Bridge capability)

Several filters, mapping functions, and transformers have been included in the repository. However, custom functions can be designed to meet specific client use cases.

Creating custom functions for the Tableau Migration Program requires the following competencies.  

- Intermediate knowledge of Python
- Advanced knowledge of the Tableau REST API
- General knowledge of Tableau administration and infrastructure
- Advanced knowledge of the Tableau Migration library/SDK

If you need support with building filters, mapping functions, or transformers, please contact the Global Salesforce - Tableau team.

***

#### Importing and Adding Filters, Mappings, and Transformers

As a best practice, all filters, mapping functions, and transformers should be saved in a separate Python file, such as `migration_filters.py`, `migration_mappings.py`, or `migration_transformers.py`.

To import an existing function, edit the `CoreMigration.py` file and ensure that the base file is included in the import statements:

```python
import migration_filters
import migration_mappings
```

OR

```python
from migration_filters import (
    # Skip Filters: Uncomment when necessary.
    SkipAllUsersFilter,
    SkipAllGroupsFilter,
)
```

Once the files/functions have been imported into `CoreMigration.py`, they must be added to the migration plan.

Navigate to the `Program` class and `migrate` function, and find the code blocks with the following comments. You will likely see pre-defined functions already added.

```python
### Add filters here.
plan_builder.filters.add(SkipAllUsersFilter)
plan_builder.filters.add(SkipAllGroupsFilter)

### Add mappings here.

### Add transformers here.
```

To add a function to the migration plan, use the following code:

| Filters | Mappings | Transformers |
|---------|----------|--------------|
| `plan_builder.filters.add(function_name)` | `plan_builder.mappings.add(function_name)` | `plan_builder.transformers.add(function_name)` |

To remove a function from the migration plan, add a hash tag (#) in front of the code that added it to comment it out:

```python
# plan_builder.filters.add(function_name)
```

It is best to test your functions before using them in a production migration. If you wish to test a function but do not have access to a sandbox environment, you can create a Tableau Cloud Developer Environment or use filters to skip all content (essentially apply the functions without migrating any content) and review the logs/manifest file to ensure they are working as intended.

***

#### Running the Tableau Migration Program

To run the Tableau Migration Program, start by running `main.py` to access the Tableau Cloud Migration Accelerator menu.

```shell
------------------------------------------------------    
Welcome to Slalom Tableau Cloud Migration Accelerator!    
------------------------------------------------------

What migration activity do you want to perform?

--- Configuration and Testing ---------------------
        1: Test Connection/Authentication

--- Users/Groups/Projects/Datasources/Workbooks ---
        2: Migrate Content

--- Tasks/Subscriptions/Favorites/Custom Views ----
        3: Get Content Details
        4: Download Content
        5: Create/Publish Content

Enter your choice (1-5) or "EXIT":
```

From the main menu, choose ***2. Migrate Content***

The program will warn you that it is set to skip all content by default. This is a static message, and will appear even if you have disabled the skip filters by commenting them out.

If you provided an existing manifest (covered in the next section - [Importing an Existing Manifest](#importing-an-existing-manifest)), you will be asked if you wish to use it or not.

Then program will proceed to build the migration plan using the defined filters, mappings, and transformers, and then ask if you are ready to run the migration.

Choosing `Y` will initiate the program and begin the migration, creating a `Manifest.json` file in the `/MANIFEST/` folder as well as a `log` file in the `/LOG/` folder. \
*Note: These folders can be changed in `config.ini`.*

***

#### Tableau Migration Manifests

If you have run the Tableau Migration Program already, it will have created a `Manifest.json` file in the `/MANIFEST/` folder.  This file contains all the objects migrated:

- Users
- Groups
- Projects
- Data Sources
- Workbooks
- Extract Refresh Tasks

as well as details about the migration:

- Source
    - ID, ContentUrl, Location, Name
- Mapped Location
    - Path Segments, Path, Name
- Destination
    - ID, ContentUrl, Location, Name
- Status
- HasMigrated (true/false)
- Errors

By default, the Tableau Migration Program will not attempt to migrate content that is tagged as ```"HasMigrated": true```, allowing you to import an existing manifest and re-run a migration plan if any content failed to migrate due to errors.

***

##### Importing an Existing Manifest

To import an existing manifest, copy the absolute (full) path of the manifest file and paste it into `config.ini` under the `[MANIFEST]` header:

```ini
[MANIFEST]
previous_manifest = C:\Users\me\MANIFEST\manifest.json
```

If the Tableau Migration Program correctly finds the manifest file, you will be prompted whether to include it or not:\
`Existing Manifest found at C:\Users\me\MANIFEST\manifest.json. Should it be used? [Y/n]`

To include it, type `Y` and followed by Enter.

***

### Using the Premade Filter and Mapping Functions

Using the premade filters, mappings, and transformers requires minimal skill with Python, as the functions are already built and tested.

Generally speaking, these functions only require input in the `config.ini` file, as well as un-commenting the imports/functions within the `CoreMigration.py` script.

If using these functions, it is important to only comment them out when they are no longer needed. Otherwise, your migration may have inconsistent results.

***

#### Migrate Specific Users Only

***CoreMigration.py***

Confirm the following function is imported:

```python
from migration_filters import (
  MigrateSpecificUsers,
)
```

and uncomment the following function:

```python
### Add filters here.
plan_builder.filters.add(MigrateSpecificUsers)
```

When using this filter, you must also comment out the SkipAllUsersFilter function:

```python
### Skip Filters: Uncomment when necessary.
# plan_builder.filters.add(SkipAllUsersFilter)
```

***config.ini***

Add a comma-separated list of users here:

```ini
[FILTERS]
user_list = jsmith@slalom.com,jdoe@slalom.com
```

*Note: It's best not to use this function for large lists of users. If you need to migrate an extensive list of specific users, it is best to write a custom filter function that reads an external file.*

***

#### Skip Content by Parent Location

***CoreMigration.py***

Confirm the following functions are imported:

```python
from migration_filters import (
  SkipProjectByParentLocationFilter,
  SkipDataSourceByParentLocationFilter,
  SkipWorkbooksByParentLocationFilter,
)
```

and uncomment the following functions:

```python
### Add filters here.
# plan_builder.filters.add(SkipProjectByParentLocationFilter)
# plan_builder.filters.add(SkipDataSourceByParentLocationFilter)
# plan_builder.filters.add(SkipWorkbooksByParentLocationFilter)
```

When using this filter, you must also comment out the following functions:

```python
### Skip Filters: Uncomment when necessary.
# plan_builder.filters.add(SkipAllProjectsFilter)
# plan_builder.filters.add(SkipAllDataSourcesFilter)
# plan_builder.filters.add(SkipAllWorkbooksFilter)
```

***config.ini***

Add the Project name to be skipped:

```ini
[FILTERS]
skipped_project = Emerge
```

*Note: This function can be used in tandem with the ProjectWithinSkippedLocationMapping, DataSourceWithinSkippedLocationMapping, and WorkbookWithinSkippedLocationMapping to remap the parent project for any content skipped by the filter. See [Map Content from Skipped Projects to New Destination](#map-content-from-skipped-projects-to-new-destination).*

***

#### Migrate Tagged Data Sources and Workbooks

***CoreMigration.py***

Confirm the following functions are imported:

```python
from migration_filters import (
  # Tag-Based Filters
  MigrateTaggedDataSources,
  MigrateTaggedWorkbooks,
)
```

and uncomment the following functions:

```python
### Add filters here.
plan_builder.filters.add(MigrateTaggedDataSources)
plan_builder.filters.add(MigrateTaggedWorkbooks)
```

When using this filter, you must also comment out the SkipAllDataSourcesFilter and SkipAllWorkbooksFilter functions:

```python
### Skip Filters: Uncomment when necessary.
# plan_builder.filters.add(SkipAllDataSourcesFilter)
# plan_builder.filters.add(SkipAllWorkbooksFilter)
```

***config.ini***

Add the Tag (string) to search for:

```ini
[FILTERS]
migrate_tag = MOVE ME
```

*Note: This function does not currently searching for multiple tags. Use a single Tag value only.*

***

#### Map Content from Skipped Projects to New Destination

***CoreMigration.py***

Confirm the following functions are imported:

```python
from migration_mappings import (
    ProjectWithinSkippedLocationMapping,
    DataSourceWithinSkippedLocationMapping,
    WorkbookWithinSkippedLocationMapping,
)
```

and uncomment the following functions:

```python
### Add mappings here.
plan_builder.mappings.add(ProjectWithinSkippedLocationMapping)
plan_builder.mappings.add(DataSourceWithinSkippedLocationMapping)
plan_builder.mappings.add(WorkbookWithinSkippedLocationMapping)
```

When using this filter, you must also comment out the SkipAllDataSourcesFilter and SkipAllWorkbooksFilter functions:

```python
### Skip Filters: Uncomment when necessary.
# plan_builder.filters.add(SkipAllProjectsFilter)
# plan_builder.filters.add(SkipAllDataSourcesFilter)
# plan_builder.filters.add(SkipAllWorkbooksFilter)
```

***config.ini***

Add the Project skipped (in the example, Emerge) and the new destination (Global Technology):

```ini
[FILTERS]
skipped_project = Emerge
skipped_parent_destination = Global Technology
```

*Note: This function works in tandem with the SkipProjectByParentLocationFilter or similar functions to skip Projects by name. See [Skip Content by Parent Location](#skip-content-by-parent-location).*

***

### Sample Tableau Migration Program Functions

Using these sample functions can add much more power and depth to your migration program, but require more knowledge of Python to properly integrate them and execute a migration properly.

These functions are intended to be samples, and may require modification before they can be added to the Tableau Migration Program and included in a migration plan. They are not currently designed to simply be imported and added as-is.

***

#### Migrate Content by Project Name

This function is an inverse of the [Skip Content by Parent Location](#skip-content-by-parent-location) filter. Instead of skipping content based on Project name, it only migrates content contained within a Project of a given name.

This function can be found in the `Sample SDK Functions/migration_filter_by_parent.py` file.

To use it, copy the four classes (and functions) and add them to `migration_filters.py`.

***CoreMigration.py***

Confirm the following functions are imported:

```python
from migration_filters import (
  MigrateProjectByNameFilter,
  MigrateDataSourceByProjectFilter,
  MigrateWorkbookByProjectFilter,
)
```

and uncomment the following functions:

```python
### Add filters here.
# plan_builder.filters.add(MigrateProjectByNameFilter)
# plan_builder.filters.add(MigrateDataSourceByProjectFilter)
# plan_builder.filters.add(MigrateWorkbookByProjectFilter)
```

When using this filter, you must also comment out the following functions:

```python
### Skip Filters: Uncomment when necessary.
# plan_builder.filters.add(SkipAllProjectsFilter)
# plan_builder.filters.add(SkipAllDataSourcesFilter)
# plan_builder.filters.add(SkipAllWorkbooksFilter)
```

***config.ini***

Add the Project name to be migrated:

```ini
[FILTERS]
migrate_project = Archive
```

***

#### Update Project Root (Top-Level Project)

This file (`Sample SDK Functions/migration_update_root.py`) is included purely as an example or proof of concept. It has been tested and used to execute a client migration, but requires extensive Python code editing as it is customized for a very specific use-case/environment.

Importing and using this set of functions is similar to other Tableau Migration Program functions; however, it does not require any updates to `config.ini`.

If you would like to use a modified version of this function and need support configuring the script, contact the Global Salesforce - Tableau team.

***

### Extract Refresh Tasks, Subscriptions, Favorites, and Custom Views

#### Extract Refresh Tasks

The Tableau Migration Program can now create extract refresh tasks in Tableau Cloud; however, if you need to migrate these separately, a stand-alone script can be accessed under `5. Create/Publish Content` `3. Create Extract Refresh Tasks`.

Two scripts must be run against the ***source*** site (Tableau Server) prior to executing the `Create Extract Refresh Tasks` script:

1. `Get Schedules`
2. `Get Extract Refresh Tasks`

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Create Extract Refresh Tasks    | Input file: <br>TaskImport.xlsx <br>Schedule_Import.csv |

The script will pull schedule details from **Schedule_Import.csv** and then create an extract refresh task by matching the object name and project from Tableau Server to the target name and project in Tableau Cloud.

***Note: Tableau Cloud does not have Schedule objects like Tableau Server, since Schedules are stored at the Server level. Because of this, Tableau Cloud subcriptions (and extract refresh tasks) have an embedded schedule object instead of a schedule ID.***

***

#### Subscriptions

To create subscriptions in Tableau Cloud, from the main menu, under `5. Create/Publish Content`, select `2. Create Subscriptions`.

Subscriptions require a workbook or view a target, as well as the schedule details from Tableau Server. This task is done after users and workbooks have been migrated to the target site.

Two scripts must be run against the ***source*** site (Tableau Server) prior to executing the `Create Subscriptions` script:

1. `Get Schedules`
2. `Get Subscriptions`

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Create Subscription    | Input file: <br>Subscription_Import.csv <br>Schedule_Import.csv |

***Subscription_Import.csv required headers:***

| Target ID              | Target Type                  | Attach Image | Attach PDF   | Message      | Schedule ID  | Send If View Empty   | Subject      | User Name    | Project Name |
|------------------------|------------------------------|--------------|--------------|--------------|--------------|--------------|--------------|--------------|---|
| Workbook or View LUID <br>This can be retrieved using Get Subscription script.| Workbook or View             | True / False | True / False | The message in the email body. | LUID of the schedule | True/False   | The text in the email subject line. | Email address of the user/subscriber | Name of the Project where the target object is saved. |

Additionally, permissions for workbooks must be migrated. If a user does not have access to an object, the subscription will not be created.

The script will pull schedule details from **Schedule_Import.csv** and then create a subscription by matching the object name and project from Tableau Server to the target name and project in Tableau Cloud.

***Note: Tableau Cloud does not have Schedule objects like Tableau Server, since Schedules are stored at the Server level. Because of this, Tableau Cloud subcriptions (and extract refresh tasks) have an embedded schedule object instead of a schedule ID.***

***

#### Favorites

To create user favorites in Tableau Cloud, from the main menu, under `5. Create/Publish Content`, select `4. Create User Favorites`.

This script has the following dependencies:

- `Get Favorites` run against the ***source*** site (Tableau Server)
- Users migrated to Tableau Cloud
- Projects, Data Sources, Workbooks, Metrics, Flows migrated to Tableau Cloud
- Permissions populated for all objects in Tableau Cloud

If a user does not have access to an object because the permissions have not been migrated, the favorite will not be created.

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Create User Favorites  | Input file: <br>FavoritesList.xlsx |

Additionally, the `Create User Favorites` script will create a list of content from Tableau Cloud and save it to `FavoritesImport.xlsx`, which it will attempt to re-load as opposed to re-querying the site for all content with each run.

***

#### Custom Views

To create custom views in Tableau Cloud, from the main menu, under `5. Create/Publish Content`, select `5. Publish Custom Views and Add as User Defaults`.

This script has the following dependencies:

- `Get Custom Views` run against the ***source*** site (Tableau Server)
- `Download Custom Views` run against the ***source*** site (Tableau Server)
    - This will create a folder `/FILES/CV/` that will contain JSON files for each custom view.
- Users migrated to Tableau Cloud
- Workbooks migrated to Tableau Cloud
- Permissions populated for all workbooks in Tableau Cloud

If a user does not have access to a workbook because the permissions have not been migrated, the custom view will not be created.

The script will publish the custom views and, if applicable, assign them as users' default views. Any views marked as 'hidden' will remain hidden, and public views will remain public.

***

## Using the Archived Tableau Cloud Migration Accelerator Scripts

Reminder: to access the archived scripts, enter `6` from the main menu.

```shell
----WELCOME TO THE SUPER SECRET GALLERY OF SCRIPTS-----

Get Content -------------------------------------------
        1. Get Users and Groups
        2. Get Projects
        3. Get Data Sources
        4. Get Workbooks & Workbook Connections
        5. Get Asset Permissions

Migrate Content ---------------------------------------
        6. Create Groups
        7. Add Users to Groups
        8. Create Projects
        9. Update Project Permissions
        10. Download & Publish Data Sources
        11. Download & Publish Workbooks
        12. Update Asset Permissions -- NOT YET IMPLEMENTED

        13. Exit

Enter your choice (1-13):
```

***

### Extract and Download Data Sources and Workbooks from Source Site  

Under **Get Content**, select option **3. Get Data Sources** or **4. Get Workbooks & Workbook Connections** to get a list of data sources and workbooks.

Under **Migrate Content**, select option **10. Download & Publish Data Sources** or **11. Download & Publish Workbooks**. Then, select option **1** to download data sources and workbooks.

```shell
Enter your choice (1-13): 10

You have selected to download and publish data sources.
What would you like to do?

        1. Download Data Sources
        2. Publish Data Sources

Enter your choice:
```

Download workbooks and data sources using the scripts. You can define the specific workbooks to download by editing the input file.  Downloading data sources will download all data sources in your source environment.

Tableau allows for same names in workbook & data sources, the downloaded files may overwrite earlier files. To prevent that, for workbooks, only select to download one project at a time. For data sources, rename any duplicate data source name in the source site first before downloading data sources.

#### Prepare the files needed to download workbooks

**Workbooks:** Prepare Workbook_To_Download.csv in Import folder, and edit as needed to your desired list of workbooks to download.  

**Data Sources:** The script will download all data sources

The folders where the workbooks & data sources are downloaded are defined in *Shared_TSC_GlobalVariables.py*.

| Your Selection         | Files Generated          |
|------------------------|--------------------------|
| Download Data Sources  | Published tdsx/tds files <br>DataSource_Import.csv |
| Download Workbooks     | Published twbx/twb files <br>Workbook_Import.csv |

***Workbook_to_Download.csv required headers:***

| Workbook ID            | Include Extract          |
|------------------------|--------------------------|
| *Required* <br>This is the guid of the workbook | *Optional* <br>True/False |

- TRUE: Downloads the workbook with the extract. This will increase processing time, but otherwise you must publish the datasource separately and connect the workbook to it.
- FALSE: Download the workbook without the extract.
- Packaged workbooks automatically include extracts in the download.

***Note:*** Workbooks with embedded data sources will be flagged during the download process. These workbooks are moved to a separate folder.

***Warning:*** If Tableau Server contains workbooks with .tde extract files, these workbooks must be downloaded and the extracts manually updated to .hyper using Tableau Desktop. This process cannot be automated at this time. This is rare and typically only applies to workbooks not edited/published since 2018. See [Extract Upgrade to .hyper Format](https://help.tableau.com/current/pro/desktop/en-us/extracting_upgrade.htm) for more details on upgrading data extracts.

***

### Create Projects

Under **Get Content**, select option **2. Get Projects** to get a list of all projects.

Under **Migrate Content**, select option **8. Create Projects**.

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Create Projects        | An input file: <br>ProjectList.csv |

- *ProjectList.csv* is located in the Import folder.
- The script will return a log file.
- Verify that all projects have been created and all permissions are accurate.

Check log file for any errors after running the script.

***ProjectList.csv required headers:***

| Project Name           | Path                     | Project Description                                                                                |
|------------------------|--------------------------|----------------------------------------------------------------------------------------------------|
| *Required* <br>This is the name of the project. | *Required* <br>Determines hierarchy and parent relationship. | *Optional* |

- The format of *Path* is: `//Parent//Child//...//etc`. Begin each path/segmentwith a double forward slash `//`.
- Leave Path blank if it is a top-level project (no parent).

#### Example

`HR` is a project under `Marketing`. `Marketing` is a subproject of `Company A`.
`Company A` is a top-level project.

The CSV file should have entries like below:

| Project Name           | Path                     | Project Description       |
|------------------------|--------------------------|---------------------------|
| Company A              |                          | Top level                 |
| Marketing              | //Company A              | Department VP: Jane Smith |
| HR                     | //Company A//Marketing   |                           |

### Update project permissions

**This assumes users/groups and projects have already been added to your target site.**

Under **Get Content**, select option **2. Get Projects** to get a list of all projects with their associated permissions.

Under **Migrate Content**, select option **9. Update Project Permissions**.

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Update Project Permissions | Input file: <br>ProjectPermission.csv <br>ProjectList.csv <br>*(Optional)* ProjectsForPermissions.csv |

If the ProjectsForPermissions.csv files already exists, the script will ask if you want to use it or create a new one. \
If it does not exist, the script will read *ProjectList.csv* to build a list of projects.

Check log file for any errors after running the script.

***ProjectPermission.csv required headers:***

| Path                   | Capability               | Grantee Type           | Grantee Name             | Permission Type          |
|------------------------|--------------------------|------------------------|--------------------------|--------------------------|
| Path of the Project    | Permissions in JSON: <br>`{'Read': 'Allow', 'Write': 'Allow'}` | Either *user* or *group* | If *user*, email address <p>If *group*, group name | Must be one of: <br>-Project <br>-Workbook <br>-Data Source <br>-Data Flow |

This script maps permissions for projects based on the Path. If project mapping was updated in Tableau Cloud, be sure to update the Path values accordingly.

***

### Publish Data Sources

Under **Migrate Content**, select option **10. Download & Publish Data Sources**. Then, select option **2. Publish Data Sources**.

```shell
Enter your choice (1-13): 10

You have selected to download and publish data sources.
What would you like to do?

        1. Download Data Sources
        2. Publish Data Sources

Enter your choice:
```

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Publish Data Source    | Input file: <br> DataSource_Import.csv |

Check log file for any errors after running the script.

***DataSource_Import.csv required headers:***

| Data Source Name       | File Name                | Path                   | Owner Email              |
|------------------------|--------------------------|------------------------|--------------------------|
| Name of data source    | Name of downloaded \*.tds or \*.tdsx file | *Required* <br>Project Path of data source. | Email address of data source owner. |

### Publish Workbooks

Under **Migrate Content**, select option **11. Download & Publish Workbooks**. Then, select option **2. Publish Workbooks**.

| Your Selection         | Requirements             |
|------------------------|--------------------------|
| Publish Workbooks      | Input file: <br>Workbook_Import.csv |

Check log file for any errors after running the script.

***Workbook_Import.csv required headers:***

| Workbook Name          | File Name                | Path                   | Owner Email              |
|------------------------|--------------------------|------------------------|--------------------------|
| Name of workbook       | Name of downloaded \*.twb or \*.twbx file | *Required* <br>Project Path of workbook. | Email address of workbook owner.        |

## Python Scripts

Scripts are separated by getting metadata or objects from the source site, and creating or importing content to the target site.

### General Purpose Scripts

1. *setup.py* - installs necessary libraries and helps the user prepare the accelerator for use
2. *main.py* - the primary script to run the accelerator and execute all other scripts
3. *ConnectionTest.py* - allows the user to test configuration and get Tableau site details

### Shared scripts

1. *Shared_TSC_GlobalVariables.py* - defines global variables to be re-used across scripts
2. *Shared_TSC_GlobalFunctions.py* - functions to be re-used across scripts

### Tableau Migration Program Scripts

1. *CoreMigration.py* - the script that runs the Tableau Migration (SDK) program
2. *migration_filters.py* - contains filter functions that can be imported and used by the Tableau Migration Program
3. *migration_hooks.py* - contains hooks (functions) that can be imported and used by the Tableau Migration Program
4. *migration_mappings.py* - contains mapping functions that can be imported and used by the Tableau Migration Program
5. *migration_transformers.py* - contains transformation functions that can be imported and used by the Tableau Migration Program

Additional sample migration filter/mapping files/functions can be found in the ***Sample SDK Functions*** folder.

### User/Group Scripts

1. *GetUsers.py* or *GetUsersGroups.py* - fetches users and groups from the target site and writes the data to an excel file
2. *AddUsersToGroups.py* - adds users to specified groups from an input csv file

### Project Scripts

1. *GetProjects.py* - fetches projects and relevant metadata to an excel file
2. *CreateProjects.py* - creates projects, updates project owner, removes default permissions
3. *UpdateProjectPermissions.py* - updates project permissions. Input file must include a dictionary of permissions and groups

### Data Source Scripts

1. *GetDataSource.py* - fetches data source information to an excel file
2. *DownloadDataSource.py* - downloads the published data source as a *.tds/tdsx file for import to the target site
3. *PublishDataSource.py* - publishes a *.tds/tdsx file to a target site. The input file needs to define the parent project of the data source

### Workbook Scripts

1. *GetWorkbooks.py* - fetched workbook information to an excel file
2. *DownloadWorkbooks.py* - downloads a workbook to a file location. Specify the workbook to download using a csv file
3. *PublishWorkbooks.py* - published a workbook to a parent project. Specify the workbook project location using a csv file
4. *UpdateWorkbook.py* - updates workbook owner. Specify workbook owner from a csv file

### Schedule, Task, and Subscription Scripts

1. *GetSchedule.py* - fetches schedule information
2. *GetTasks.py* - fetches extract refresh task information
3. *GetSubscriptions.py* - fetches subscription information
4. *CreateTasks.py* - creates extract refresh tasks
5. *CreateSchedules.py* - (Tableau Server only) creates schedule items
6. *CreateSubscriptions.py* - creates subscriptions in Tableau Server (using schedule IDs) or Tableau Cloud (using schedule details)

### Favorites Scripts

1. *GetFavorites.py* - fetches favorite information by user
2. *CreateFavorites.py* - creates favorites for users

### Custom View Scripts

1. *GetCustomViews.py* - fetches a list of custom views and users with custom views set as default
2. *DownloadCustomViews.py* - downloads encrypted JSON files used to recreate custom views on Tableau Cloud
3. *PublishCustomViews.py* - publishes custom views on Tableau Cloud and attempts to reassign them as default for users

## Troubleshooting

### Getting errors connecting to Server/Cloud using the script

Use `ConnectionTest.py` to validate that the server and token credentials entered in `config.ini` are correct.

Ensure that personal access tokens have not expired. By default, PATs expire after 14 days of inactivity, or 180 days total.

### Errors indicating Python package not installed

Re-run the following command:

- `pip install -r requirements.txt` (Windows)

- `pip3 install -r requirements.txt` (MacOS/Unix/Linux)

### Errors related to Virtual Environments

Ensure that Visual Studio Code is using the virtual environment as the Python interpreter.

See [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments) for details.
