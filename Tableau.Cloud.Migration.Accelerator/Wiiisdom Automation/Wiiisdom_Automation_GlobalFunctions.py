import subprocess
import yaml
import pandas as pd

def read_yaml_file(filename):
    with open(filename) as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data

def read_workbook_list(filename):    
    data = pd.read_excel(filename, sheet_name="Workbook View List", header=0)
    return data

def cli_command_input(project_path, app_path):

    timeout = ' --canvas-timeout=20'
    test_path = ' --path '+'"'+project_path+'test'+'"'
    output_path = ' --output '+'"'+project_path+'batch-reports'+'"'
    context_vars = ' --context-vars '+'"'+project_path+'context\\Tableau_Cloud.json'+'"'
    language = ' --accept-language en-US'
    max_rows = ' --max-data-rows 250'
    driver = ' --driver-name edgedriver'
    window_size = ' --window-size 1366x768'
    recursive = ' --recursive'
    on_fail = ' --continue-on-failure'

    command = app_path+timeout+test_path+output_path+context_vars+language+max_rows+driver+window_size+recursive+on_fail

    # run a command using subprocess and communicate with it
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # send input to the CLI
    input_text = "input to send to CLI:\n"

    print(input_text, command)

    process.stdin.write(input_text)
    process.stdin.flush()

    # get and print the output
    output, errors = process.communicate()

    print("\nOutput:\n"+output)
    print("\nErrors:\n"+errors)

    # close the process
    process.stdin.close()
    process.stdout.close()
    process.stderr.close()
    process.wait()

    return True