import os
import shutil
import configparser
import subprocess
from logging_config import *

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)


def environment_check():
    # Check if virtual environment loaded correctly. If not, exit.
    if "VIRTUAL_ENV" not in os.environ:
        logging.error("Virtual environment is not loaded. Exiting...")
        exit(1)


def install_dependencies():
    # Install dependencies from requirements.txt
    if os.name == "posix":  # for Unix/Linux/MacOS
        logging.info("Installed required libraries. Please wait...")
        subprocess.run(["pip3", "install", "-r", "requirements.txt"])
    elif os.name == "nt":  # for Windows
        logging.info("Installed required libraries. Please wait...")
        subprocess.run(["pip", "install", "-r", "requirements.txt"])
    else:
        raise OSError("Unsupported operating system")


def install_libraries():
    # If required DLL files are missing, add them to
    # .venv/Lib/site-packages/tableau_migration/bin
    libs_to_install = [
        "./src/CommunityToolkit.Diagnostics.dll",
        "./src/Tableau.Migration.TestApplication.dll",
        "./src/Tableau.Migration.TestComponents.dll",
    ]

    for lib in libs_to_install:
        dest_file = os.path.join(
            "venv",
            "Lib",
           # "python3.12",  ##added venv version
            "site-packages",
            "tableau_migration",
            "bin",
            lib.split("/")[2],
        )

        if not os.path.exists(dest_file):
            shutil.copyfile(lib, dest_file)


def update_config():
    config = configparser.ConfigParser()
    config.read("config.ini")

    for section in config.sections():
        print(f"Section: {section}")
        for key, value in config.items(section):
            new_value = input(f"Enter value for {key} (current: {value}): ")
            if new_value:
                config.set(section, key, new_value)

    with open("config.ini", "w") as configfile:
        config.write(configfile)


def update_env():
    from dotenv import dotenv_values, set_key

    config = dotenv_values(".env")

    for key, value in config.items():
        if not value:
            config[key] = input(f"Enter value for {key}: ")
            set_key(".env", key, config[key])


def main():
    environment_check()
    install_dependencies()
    install_libraries()

    choice = input("\nDo you want to input values for configuration files now? (Y/n): ")

    if choice.upper() == "Y":
        update_config()
        update_env()

    if os.name == "posix":  # for Unix/Linux/MacOS
        cmd = "python3"
    elif os.name == "nt":  # for Windows
        cmd = "python"

    logging.info(f"\nSetup is complete. Run '{cmd} ./main.py' to begin migration.")


if __name__ == "__main__":
    # Set the working directory to the script directory
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    os.chdir(script_directory)

    main()
