import json

from Wiiisdom_Automation_GlobalFunctions import *

input_vars = read_yaml_file('Config.yaml')
views = read_workbook_list('WorkbookList.xlsx')

project_path = input_vars['project_dir']+input_vars['project_name']+'\\'
app_path = '"'+input_vars['wiiisdom_dir']+'kinesis-cli\\kinesis.bat'+'"'
json_path = project_path+'test\\'+input_vars['test_name']+'\\kinesis.json'

for i in range(1, len(views.index)):

    print('Running '+input_vars['test_name']+' on '+views['Workbook Name'].iloc[i]+':'+views['View Name'].iloc[i]+'.')

    # open and read the test\kinesis.json file
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    # edit the URL variable in the kinesis.json file
    data['tasks'][0]['url'] = input_vars['url_cloud']+'/'+views['View URL'].iloc[i]

    # write the modified URL back to the kinesis.json file
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    cli_command_input(project_path, app_path)

    print('Test complete. View results in '+project_path+'batch-reports.')