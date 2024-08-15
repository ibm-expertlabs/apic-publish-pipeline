#!/usr/bin/env python
import os
import json
import shell_command

FILE_NAME = "raw_file_download_from_git.py"
INFO = "[INFO]["+ FILE_NAME +"] - "

def get_all_file_names_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download):
    list_of_product_names = []

    try:
        # Construct the correct URL
        url = f"{git_base_url}/repos/ibm-expertlabs/apic-products-apis-yaml/contents/{file_path_to_download}?ref={git_branch}"
        headers = {
            'Authorization': f"token {git_priv_token}"
        }
        cmd = f"curl -s -H 'Authorization: token {git_priv_token}' '{url}'"
        
        # Debugging
        print(INFO + "Constructed URL: ", url)
        print(INFO + "Using header: ", headers)
        
        download_file_from_git_res = shell_command.shcmd(cmd)
        
        if download_file_from_git_res['stdout'].strip() == "":
            raise Exception("No response received from the GitHub API. Check the URL or token.")

        response_json = json.loads(download_file_from_git_res['stdout'])

        # Debug output to verify the response
        print(INFO + "Parsed GitHub API Response:", response_json)
        
        if isinstance(response_json, list):
            for file in response_json:
                product_name = file['name']
                if '.yaml' in product_name:
                    list_of_product_names.append(product_name.replace(".yaml", ""))
        else:
            raise Exception("Unexpected response format. Expected a list but got " + str(type(response_json)))

        return list_of_product_names
    except Exception as e:
        raise Exception("ERROR in " + FILE_NAME + " : " + repr(e))

if __name__ == "__main__":
    # Example usage - replace with actual values
    git_base_url = "https://api.github.com"
    git_branch = "master"
    git_priv_token = os.getenv("GITLAB_PRIV_TOKEN")
    file_path_to_download = "Demo/Products"
    
    # Test the function
    try:
        product_names = get_all_file_names_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download)
        print("Product names retrieved:", product_names)
    except Exception as e:
        print(f"Failed to retrieve product names: {str(e)}")
