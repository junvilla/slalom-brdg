# Release notes

### Version 2.5.9 (Feb 24, 2025)
- Improvements to Log viewer
- Improvements to Settings - PAT Token Bulk Import
- Improvements to Run Bridge in K8s, with option to select Local Image Registry
- Improvements to Manage Tableau Bridge Pods in Kubernetes

### Version 2.4.33 (Jan 29, 2025)
- Add support for some .taco connector files for driver installs
- Improvements to Jobs Summary. Added Analyze Jobs with AI.
- Welcome dialog with feedback request on first load on Settings Page.

### Version 2.4.23 (Jan 17, 2025)
- Update teradata database driver install script.
- Show warning when LOCAL driver has not been downloaded.
- Add checkbox in the UI for docker network_mode = host (the default is network_mode=bridge, but some machines require the host networking configuration to run containers)
- On Jobs tab, better analysis of bridge jobs logs.

### Version 2.4.18 (Jan 12, 2025)
- Add latest version of Tableu Bridge RPM, version 20243.24.1211.0901
- Update database drivers to latest for Dremio, snowflake, amazon_athena.
- For Monitor Health, make improvements to layout and settings management.
- For Monitor Health page, add support for sending alerts to NewRelic.
- Page Layout improvements to the Publish Image page.
- Improvements to Jobs Summary page

### Version 2.4.13 (Jan 8, 2025)
- Ability to filter by column on the Bridge jobs page.
- Update stylesheet to look more Tableau-ish. (gray, orange, font-family, etc)
- Improvements to Jobs Page. Ability to summarize logs including most frequent errors and problematic brige agents.

### Version 2.4.4 (Jan 3, 2025)
- Fix Release_Notes link on Settings - App Updates page.
- Improvements to Slack notifications. Ability to send slack notifications to channels, in addition to a single user.
- Improvements to command-line automation [Command-line automation](./BridgeCTL-Automation-from-the-Command‐line.md)


### Version 2.3.88 (Dec 30, 2024)
- Automated testing as part of the BridgeCTL build and deployment pipeline which will ensure reliability as BridgeCTL becomes more popular. 
- Improvements to bridgectl command-line parameters for command-line automation scenarios, for example `bridgectl --build` and `bridgectl --run`
- Minor improvements to Health Monitoring
- Improvements to Publish Image page for pulling and pushing images to AWS Elastic Container Registry
- On Build Image and Publish Image pages, show image details of selected image.

### Version 2.3.76 (Dec 16, 2024)
- *New*: Scale up feature on Manage Bridge page to easily scale up and down the number of bridge containers in Docker.
- *New*: Update Container on Manage Bridge page to easily update all bridge agents in Docker.
- Bulk import PAT Tokens from the Settings page.
- minor updates to mysql driver install.

### Version 2.3.70 (Dec 12, 2024)
- Ability to select Locale (Language) when Building Bridge Image. This is required by some database drivers (for example mysql).

### Version 2.3.68 (Dec 9, 2024)
- Add System Test to the Settings page. This will verify that your system can build and run amd64 images which is required by Tableau Bridge. 

### Version 2.3.65 (Dec 5, 2024)
- Add support for Azure Container Registry (in beta) in addition to AWS Container Registry.
- Update multiple bridge agents running in Docker at once from the Manage Bridge page.
- Improvements to help text around adding Tokens in the Add PAT Token dialog.
- Improvements to Command-line menu: Edit UI Server Address 

### Version 2.3.58 (Nov 27, 2024)
- Add bridge version 20243.24.1112.0850
- improved security around handling of TOKEN_VALUE when staring bridge containers.
- TableauClientConfiguration.txt fixes.
- Minor fixes in User Interface settings.

### Version 2.3.56 (Nov 19, 2024)
- Fix driver download url in Example Scripts page
- On build image page, fix permissions on TableauClientConfiguration.txt when container user is non-root user.
- Fix links to README.md and LICENSE on the home page.

### Version 2.3.53 (Nov 15, 2024)
- Improved Support for Multiple sites: Ability to easily switch between multiple Tableau Cloud Sites.
- Tableau Bridge RPM selection
- Display link to help docs for installing Docker if Docker is not installed
- Add a --profile parameter to Container Registry options which will be used in any AWS Commands
- Support for the new Minerva run-bridge.sh in version 2024.3
- Improved support for Azure Container Registry in addition to AWS Container Registry
- Improved Monitoring. When BridgeCTL UI starts, kick off background monitoring if it had been turned on previously.
- For each build image, write build log to disk in the `bridgectl/log` folder


### Version 2.3.43 (Nov 10, 2024)
- Improvements to build bridge page and run bridge page - use modal dialog.
- Prep code for open source (still waiting final approval)


### Version 2.3.29 (Oct 25, 2024)
- Build bridge base image with only drivers, but no bridge_rpm
- Configure Login Password for BridgeCTL User Interface
- Improvements to monitoring Bridge feature
- BridgeCTL now has the ability to easily switch between multiple sites from the Settings page

### Version 2.3.4 (Sep 24, 2024)
- Updates for Minerva RPM. 
- BridgeCTL gives you the option to select "use minerva". Which will use the run_bridge.sh to start the minerva bridge agent at container start time, instead of the old TabBridgeClientWorker script.

### Version 2.2.84 (Sept 16, 2024)
- Improvements to Add/Remove PAT Tokens Dialog
- Small improvements to Jobs and Tasks report to include embeded extract refresh in addition to published data source.
- Addional improvements to UNC path support for file-based data sources.
- Update to ESRI and MS Sql driver install scripts.

### Version 2.2.77 (Sept 5, 2024)
- Ability to add custom DNS mappings to the /etc/hosts file. Read more in [feature details](./Features.md#custom-dns-mappings-released-on-sept-5-2024).
- (coming soon) support for UNC filemappings for File-based data sources.

### Version 2.2.62 (August 22, 2024)
- Improvements to Example Scripts
- Add screenshots to readme.md

### Version 2.2.57 (August 20, 2024)
- New menu
- New beta feature: Auto-scale bridge pods in kubernetes.

### Version 2.2.50 (August 8, 2024)
- On Logging page, ability to download log files from k8s pods and docker containers.
- Ability to customize the TabBridgeClientConfiguration.txt use by bridge to customize how it runs.
- Monitoring feature enabled. 
A background job will check regularly if any of the bridge agents are not connected by calling the Tableau Cloud APIs. If at least one bridge agent is not status=connected, a slack notification will be sent.
- Improved support for multiple sites. Ability to add PAT tokens from multiple Tableau Cloud sites and then when running bridge agents you can select which site to target.
- improved documentation on customizing driver caddy driver definition files.

### Version 2.2.44 (July 23, 2024)
- Add Features tab on Settings page to toggle on/off some pages.
- Fix bug: folder 'buildimg/drivers' doesn't exist when importing drivers on the build image page.
- Improve build image name. Example image name: "tableau_bridge_rhel9_20242.24.0613.1930"

### Version 2.2.33 (Jul 13, 2024)
- update BridgeCTL to use latest Tableau Bridge RPM version 20242.24.0613.1930 which was released on July 1
- bugfix: fix push image to AWS ECR on Windows.

### Version 2.2.29 (Jul 12, 2024)
- New Publish Images page. This feature makes it easier to publish images up to AWS ECR or pull images down from AWS ECR.
- Show Run Script":
On the Docker - Run Bridge page there is now an option to "Show Run script". With this feature you can generate a bash script for running the bridge container and pulling the image from AWS ECR. This means that you can install BridgeCTL on one machine and build your image and publish to AWS Elastic Container Registry. Then just run this generated "run bridge container" bash script on each of the target machines where you'd like to run the bridge container. As long as those target machines have docker and access to AWS ECR, then you don't need to install bridgectl on those target bridge agent machines or rebuild your image. The "run bridge container" script contains all the parameters needed including the PAT token ID and value, the poolID, site URL, etc. Remember create a separate PAT token for each bridge agent.
- bug fixes for Save settings
- Update to bridgectl_setup.py to allow installation as root user (it just gives a warning). Note that installing in the root directory /root is not allowed, but you can simply create a directory and install it in that subdirectory.
- bugfix: fixed support for tableau cloud sitename with dashes.
- bugfix: prevent PAT tokens in BridgeCTL with spaces or other invalid characters now allowed in docker container names.

### Version 2.2.23 (Jul 9, 2024)
- New! The "Example Scripts" page has been added which shows bash scripts for building and running bridge linux containers.
- Bug fix: PAT tokens with spaces are not allowed because these cause issues with extract refreshes. Also, since bridgectl uses the PAT token name to name the docker container invalid characters like spaces are not allowed.
- bridgectl_setup.py creates a python virtual environment called "tabenv" in the bridgectl folder, and installs pip libraries here instead of in the system python.
- bugfix: Fix the cloudera_impala driver install issue.

### Version 2.1.166 (May 15, 2024)
- Improvements to driver_download and driver_install scripts.
- Ability to install bridgectl from a zip file (bridgectl_download.zip)
- Improvements to the Web only page which shows bridge image creation scripts in the browser for instructional purposes. to run bridgectl in this mode simply run `streamlit run Web.py` from the bridgectl directory.

### Version 2.1.135 (April 24, 2024)
- Fix mysql drivers not working because of environment variables (modified Dockerfile)

### Version 2.1.134 (April 23, 2024)
- Improvements to devbuilds downloads
- Bugfix on publish bridge image to ECR.
- Add web-only mode which will generate and show in the user's browser a Dockerfile and the other scripts needed to build a tableau bridge container image, without executing the build.
- bugfix for installing drivers on windows

### Version 2.1.122 (April 16, 2024)
- Ability to show script for push image to ECR.
- Improvements to 'show script' on 'Docker - Run Bridge' page.
- add parameter `--init_settings` to batch mode.

### Version 2.1.118 (April 14, 2024)
- Addition of the `--push_image`command-line parameter to push the last locally built container image to AWS ECR Container Registry.
- Add support for Minerva Bridge RPM. (Minerva is the new bridge query engine which will be released sometime later this year.)
- Add check that when running on Windows, the docker OsType is correctly set to linux, not windows.
- On Docker - Manage page, The "Detail: button will include a list of installed JDBC and ODBC database drivers.

### Version 2.1.108 (April 10, 2024)
- BridgeCTL now supports building bridge images on Arm processors even though tableau bridge rpm uses x86.
- On run bridge container, there is now an option to show a complete bash script which can be copied/pasted to a remove machine to run a bridge agent without having to install bridgectl on that remote machine. (This requires pushing the built image to ECR)

### Version 2.1.98 (April 6, 2024)
- Add support for downloading latest Tableau Bridge RPM from tableau.com
- Fix log paths for release version of bridge

### Version 2.1.93 (April 3, 2024)
- Added support for adding bridge agents to the Default Pool
- Additional validation improvements when running bridge agents.
- Improved instructions for Settings - Bulk import PAT tokens.

### Version 2.1.90 (April 2, 2024)
- Improved validation when adding PAT tokens, make sure it has the right permissions (SiteAdministrator).

### Version 2.1.88 (March 31, 2024)
- Improve instructions for building and running bridge containers, and error messages for connecting to ECR.

### Version 2.1.72 (Mar 28, 2024)
- Improvements to bridgectl_setup script
- Example bash scripts for running bridge on linux from the terminal
- Switch from Public ECR to private ECR support

### Version 2.1.61 (Mar 23, 2024)
- Settings page - Bulk Import PAT Token YAML
- Fixes and improvements for Private ECR support
- Improvements to running bridge containers in K8s

### Version 2.1.53 (Mar 20, 2024)
- Add a button to check for updates from Settings Page in the UI
- Add uninstall command to help menu
- Additional Kubernetes integration features
  
### Version 2.1.48 (Mar 19,2024)
- Add jobs detail checkbox which will include job luid and other details about the bridge job.
- Add feedback survey link to Home page.

### Version 2.1.41 (Mar 1, 2024)
- Add cli menu command to configure systemctl service startup on Linux
- Bugfix: fix error when no jobs in job report
 
### Version 2.1.20 (Feb 19, 2024)
- Add Kubernetes and AWS Elastic Container Registry (ECR) support

### Version 2.1.9 (April, 2023)
- Improvementts to devbuilds downloads
- Bugfix on publish bridge image to ECR.
- Add web-only mode which will generate and show in the user's browser a Dockerfile and the other scripts needed to build a tableau bridge container image, without executing the build.

### Version 2.0.124 (Jan 8, 2024)
- Improve Windows support for BridgeCTL. Fix bug: duplicate PATH entries.
- Filewatcher prototype
- Auto-update BridgeCTL: Deployment of BridgeCTL via github releases

### Version 2.0.6 (Dec 13, 2023)
- Search Bridge logs
- Bug fixes on windows
- Bug fixes for Manage bridge containers
- Auth token editing
- Edit Bridge Settings from web UI: ability to edit the bridge settings
- Mockup of DC-PAT Web UI

### Version 2.0.1 (Nov 28, 2023)
- Add new Streamlit UI
- Rename to BridgeCTL
- add docker pip library for interacting with docker instead of using subprocess calls to docker commands, this reduces the amount of code, and improves cross-platform support.

### Version 1.2.157 (Aug 30, 2023)
- fix base dockerimage to point to Redhat a base image from dockerhub instead of artifactory.
- move setup script to DC WebApp instead of Artifactory.
- ability to specify specific the latest rpm for a branch for bridge RPMs, for example "tableau-2023-2.latest" 
- ability to specify a specific bridge rpm version, for example: "tableau-2022-4.23.0519.1315"

### Version 1.1.70
- Add beta menu - k8s cluster onboarding wizard for collecting customer info and returning a cluster.tar.
- Ability to call the Jobs API, and display in the Beta -> Show Jobs Report
- Switch bridge image to use environment variables instead of creating start-bridgeclient.sh and tokenFile.json outside the container. This will make the images more reusable.
- Enable BridgeCTL to work on Windows (still in beta)

### Version 1.1.29
- Improved manage bridge containers menu which includes these functions: 
  + Agent Logs Summary
  + Container info from DB
  + Docker logs
  + Kill container
- add commandline parameters  (--build, --run or --update) for automation scenarios. See [Documentation](https://salesforce.okta.com/app/salesforce_confluence_1/exk171qpzbBxPEXKI697/sso/saml)

### Version 1.1.7
- Tokens.yml includes a pod_url property which contains the tableau_cloud_serverpod_url so that other TC environments can be used. 
- Also, the pod_url in the tokens.yml is checked when running a container that the target site+pod_url matches from settings.yml.
- Containers DB (config/containers.yml) tracks which tokens are used per container so we ensure each token is only used once. Menu command added which displays database record information for Container
- Various improvements to edit settings on Linux
- fixes to download file

### Version 1.0.51
- default bridge rpm source set to github.com/tableau/bridge/releases/latest/download/tableau-bridge.rpm for easier first-time download (see the settings.yml bridge_rpm_source: which can be set to 'devbuilds' (internal daily builds) or 'github' (public beta releases)
- docker login to artifactory before build image to download base image
- store Tableau Cloud sitename in settings.yml (it will need to match the sitename from the token found in tokens.yml
- Improved Container management: ability to kill and report logs for stopped bridge containers

### Version 1.0.46
- In settings.yml, you can set the bridge.tableau_cloud_serverpod_url, and that will set in the container. 
TC Prod: https://prod-useast-a.online.tableau.com
executed in start-bridgeclient.sh: 
 /opt/tableau/tableau_bridge/bin/TabBridgeClientCmd setServiceConnection \
    --service="https://"

### Version 1.0.37
- define list of drivers in settings.yml
- download drivers and build into Docker image
- Build local bridge image with drivers
- Download rpm file from devbuilds web
- Manage local bridge containers (display commands to kill container or to view logs of container)

### Version 1.0.20 (June 10, 2023)
- Build local bridge image with RPM file
- Browse to Tableau Cloud Bridge Settings
- Edit settings in text editor




