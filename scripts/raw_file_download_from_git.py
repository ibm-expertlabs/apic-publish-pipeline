#!/usr/bin/env python
import os
import json
import shell_command

FILE_NAME = "raw_file_download_from_git.py"
INFO = "[INFO]["+ FILE_NAME +"] - "

def download_file_from_gitlab(git_base_url, git_proj_id, git_branch, git_priv_token, file_path_to_download, filename_to_download, local_target_dir):
    try:
        print("in download_file_from_git : local_target_dir = ", local_target_dir)
        curl_auth_header = "'PRIVATE-TOKEN: " + git_priv_token + "'"
        cmd = (
            "curl -H " + curl_auth_header + " -L "
            + git_base_url.replace("https://github", "https://raw.github", 1)
            + git_proj_id + "/repository/files/" + file_path_to_download + "%2F"
            + filename_to_download + "%2Eyaml/raw?ref=" + git_branch + " > "
            + local_target_dir + "/" + filename_to_download + ".yaml"
        )
        print("my command: ", cmd)
        if not os.path.isdir(local_target_dir):
            os.makedirs(local_target_dir)

        download_file_from_git_res = shell_command.shcmd(cmd)
        return download_file_from_git_res
    except Exception as e:
        raise Exception("ERROR in " + FILE_NAME + " : " + repr(e))

def get_all_file_names_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download):
    list_of_product_names = []

    try:
        url = (
            git_base_url.replace("https://github", "https://api.github", 1)
            .replace(".com/", ".com/repos/", 1)
            + "contents/" + file_path_to_download + "?ref=" + git_branch
        )
        curl_auth_header = "'Authorization: token " + git_priv_token + "'"
        cmd = "curl -k -H " + curl_auth_header + " '" + url + "'"
        print(INFO + "Getting all Products names from: ", url)
        download_file_from_git_res = shell_command.shcmd(cmd)
        response_json = json.loads(download_file_from_git_res['stdout'])
        
        # Debug output to verify the response
        print(INFO + "GitHub API Response:", response_json)
        
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

def download_file_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download, filename_to_download, local_target_dir):
    try:
        curl_auth_header = "'Authorization: token " + git_priv_token + "'"
        cmd = (
            "curl -s -k -H " + curl_auth_header
            + " -H 'Accept: application/vnd.github.v3.raw' -L "
            + git_base_url.replace("https://github", "https://raw.githubusercontent", 1)
            + git_branch + "/" + file_path_to_download + "/" + filename_to_download + ".yaml > "
            + local_target_dir + "/" + filename_to_download + ".yaml"
            + " && cat " + local_target_dir + "/" + filename_to_download + ".yaml"
        )
        # print("my command: ", cmd)
        if not os.path.isdir(local_target_dir):
            os.makedirs(local_target_dir)

        download_file_from_git_res = shell_command.shcmd(cmd)
        return download_file_from_git_res
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
