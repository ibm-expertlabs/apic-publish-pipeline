#!/usr/bin/env python
import os
import json
import shell_command

FILE_NAME = "raw_file_download_from_git.py"
INFO = "[INFO]["+ FILE_NAME +"] - "

def get_all_file_names_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download):
    list_of_product_names = []

    try:
        # Construct the URL
        url = (
            git_base_url.replace("https://github", "https://api.github", 1)
            .replace(".com/", ".com/repos/", 1)
            + "contents/" + file_path_to_download + "?ref=" + git_branch
        )
        curl_auth_header = "'Authorization: token " + git_priv_token + "'"
        cmd = "curl -k -H " + curl_auth_header + " '" + url + "'"
        
        # Debugging
        print(INFO + "Constructed URL: ", url)
        print(INFO + "Using header: ", curl_auth_header)
        
        download_file_from_git_res = shell_command.shcmd(cmd)
        
        # Debug the raw response
        print(INFO + "Raw API Response:", download_file_from_git_res['stdout'])
        
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
    git_base_url = os.getenv("GIT_PRODUCTS_APIS_URL")
    git_branch = "master"
    git_priv_token = os.getenv("GITLAB_PRIV_TOKEN")
    file_path_to_download = "Demo/Products"
    
    # Test the function
    try:
        product_names = get_all_file_names_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download)
        print("Product names retrieved:", product_names)
    except Exception as e:
        print(f"Failed to retrieve product names: {str(e)}")
