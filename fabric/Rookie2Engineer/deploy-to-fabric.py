# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Example demonstrating:  
1. Access variable group values from Python. Note for sensitive variables ensure the variable group is linked to key vault. See https://learn.microsoft.com/en-us/azure/devops/pipelines/library/link-variable-groups-to-key-vaults?view=azure-devops
2. Use of Service Principal Name (SPN) with a Secret credential flow, leveraging the ClientSecretCredential class. 
3. Use the Fabric reset APIs to lookup the workspace ID based on workspace name
4. Using enable_shortcut_publish feature flag to deploy Lakehouse shortcuts
5. Using debug log level
"""
# START-EXAMPLE

# argparse is required to gracefully deal with the arguments
import os,argparse, requests, ast
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items,change_log_level,append_feature_flag
from azure.identity import ClientSecretCredential
#from clean_visual_json import clean_all_visuals

# function to return the workspace ID
def get_workspace_id(p_ws_name, p_token):
    url = "https://api.fabric.microsoft.com/v1/workspaces"
    headers = {
        "Authorization": f"Bearer {p_token.token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    ws_id =''
    if response.status_code == 200:
        workspaces = response.json()["value"]
        for workspace in workspaces:
            if workspace["displayName"] == p_ws_name:   
                ws_id = workspace["id"] 
                return workspace["id"]
        if ws_id == '':
            return f"Error: Workspace {p_ws_name} could not found."
    else:
        return f"Error: {response.status_code}, {response.text}"

# --- Feature Flags and Logging ---
append_feature_flag("enable_shortcut_publish")
# set log level
change_log_level("DEBUG")

# parse arguments from yaml pipeline. These are typically secrets from a variable group linked to an Azure Key Vault
parser = argparse.ArgumentParser(description='Process Azure Pipeline arguments.')
parser.add_argument('--aztenantid',type=str, help= 'tenant ID')
parser.add_argument('--azclientid',type=str, help= 'SP client ID')
parser.add_argument('--azspsecret',type=str, help= 'SP secret')
parser.add_argument('--target_env',type=str, help= 'target environment')

parser.add_argument('--items_in_scope',type=str, help= 'Defines the item types to be deployed')
args = parser.parse_args()
item_types_in_scope = args.items_in_scope

#get the token#
print('Obtaining token...')
token_credential = ClientSecretCredential(tenant_id=args.aztenantid, client_id=args.azclientid, client_secret=args.azspsecret)

# get target environment name
tgtenv = args.target_env
print(f'Target environment set to {tgtenv}')

# determine the target workspace using the variable group which stores the target workspace name in a variable with the naming convention "[tgtenv]WorkspaceName"
ws_name = f'{tgtenv}WorkspaceName'
print(f'Variable group to determine workspace is set to {ws_name}')

# define workspace name to be deployed to based on value in variable group based on target environment name. This variable group is not linked to a Key Vault hence the values can be access through os.environ 
workspace_name = os.environ[ws_name.upper()]
print(f'Obtaining GUID for {workspace_name}')

# generating the token used to call the Fabric REST API
resource = 'https://api.fabric.microsoft.com/'
scope = f'{resource}.default'
print(f'scope set to {scope}')
token = token_credential.get_token(scope)

# call the workspace ID lookup function
lookup_response = get_workspace_id(workspace_name, token)
if lookup_response.startswith("Error"):
    errmsg=f"{lookup_response}. Perhaps workspace name is set incorrectly in the variable group of does not map to environment name + 'WorkspaceName'"
    raise ValueError(errmsg)
else:
    wks_id = lookup_response
    print(f"Workspace ID for {workspace_name} set to {wks_id}")

# set repo folder based on the variable group value of gitDirectory
repository_directory = os.environ["GITDIRECTORY"]

# convert the item types argument into a valid list
item_types = args.items_in_scope.strip("[]").split(",")


# debug for repo and target env and scope and type
print("=" * 60)
print(f"Environment: {tgtenv}")
print(f"Workspace Name: {workspace_name}")
print(f"Workspace ID: {wks_id}")
print(f"Repository Directory: {repository_directory}")
print(f"Items In Scope Raw: {args.items_in_scope}")
print(f"Items In Scope Parsed: {item_types}")
print("=" * 60)


# Initialize the FabricWorkspace object with the required parameters
target_workspace = FabricWorkspace(
    workspace_id=wks_id,
    environment=tgtenv,
    repository_directory=repository_directory,
    item_type_in_scope=item_types,
    token_credential=token_credential,
)


#clean_all_visuals(repository_directory)
# Publish items to the workspace
print(f'Publish branch to workspace...')
publish_all_items(target_workspace,item_name_exclude_regex="sharing")
# print workspace name id and scope
print(f"Workspace Name: {workspace_name}")
print(f"Workspace ID: {wks_id}")
print(f"Items in Scope: {item_types}")

# Unpublish orphaned items from the workspace
#unpublish_all_orphan_items(target_workspace)
