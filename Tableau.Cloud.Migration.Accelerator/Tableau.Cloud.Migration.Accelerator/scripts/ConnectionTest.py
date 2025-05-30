####
# This script tests the server connection and returns server details.
####

from Shared_TSC_GlobalVariables import *
from Shared_TSC_GlobalFunctions import *
from logging_config import *
import tableauserverclient as TSC

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the name of the current script
script_name = os.path.basename(__file__)

# Define a description of the script
script_description = "This script will run a test authentication session with Tableau."

# Prompt the user with the script name and description
logging.info(f"You are running the {script_name} script. {script_description}")

# -----------------------------------Read the authentication variables
auth_variables = read_config("config.ini")

token_name, token_value, portal_url, site_id = tableau_environment(
    auth_variables["SOURCE"]["URL"], auth_variables["DESTINATION"]["URL"]
)

tableau_auth = tableau_authenticate(token_name, token_value, portal_url, site_id)


def main():
    if site_id == "":
        site = "Default"
    else:
        site = site_id

    logging.info(
        "\nSigning in...\nServer: {}\nSite: {}\nToken name: {}".format(
            portal_url, site, token_name
        )
    )

    if not tableau_auth:
        raise TabError(
            "Did not create authentication object. Check the variables in your config.ini file."
        )

    # Only set this to False if you are running against a server you trust AND you know why the cert is broken
    check_ssl_certificate = False

    server = TSC.Server(portal_url)
    server.use_server_version()
    server.add_http_options({"verify": check_ssl_certificate})

    server.auth.sign_in(tableau_auth)

    s_info = server.server_info.get()

    logging.info(
        f"""\nServer Info:
\tServer: {server.server_address}
\tSite LUID: {server.site_id}
\tProduct version: {s_info.product_version}
\tREST API version: {s_info.rest_api_version}
\tBuild number: {s_info.build_number}\n"""
    )


if __name__ == "__main__":
    main()
