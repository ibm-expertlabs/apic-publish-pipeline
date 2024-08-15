#!/usr/bin/env python
import os
import json
import shell_command

FILE_NAME = "raw_file_download_from_git.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 

def download_file_from_gitlab(git_base_url, git_proj_id, git_branch, git_priv_token, file_path_to_download, filename_to_download, local_target_dir):
    try:
        print("in download_file_from_git : local_target_dir = ",local_target_dir)
        curl_auth_header = "'PRIVATE-TOKEN: " + git_priv_token + "'"
        cmd = "curl -H " + curl_auth_header + " -L " + git_base_url.replace("https://github","https://raw.github",1) + git_proj_id + "/repository/files/" + file_path_to_download + "%2F"+ filename_to_download + "%2Eyaml/raw?ref=" + git_branch + " > " + local_target_dir + "/" + filename_to_download + ".yaml"
        print("my command: ", cmd)
        if not os.path.isdir(local_target_dir):
            os.makedirs(local_target_dir)

        download_file_from_git_res = shell_command.shcmd(cmd)
        return download_file_from_git_res
    except Exception as e:
        raise Exception("ERROR in " + FILE_NAME + " : " + repr(e))

def get_all_file_names_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download):

    list_of_product_names=[]

    try:
        url = git_base_url.replace("https://github","https://api.github",1).replace(".com/",".com/repos/",1) + "contents/" + file_path_to_download + "?ref=" + git_branch
        curl_auth_header = "'Authorization: token " + git_priv_token + "'"
        cmd = "curl -k -H " + curl_auth_header + " '" + url + "'"
        print(INFO + "Getting all Products names from: ", url)
        download_file_from_git_res = shell_command.shcmd(cmd)
        files=list(json.loads(download_file_from_git_res['stdout']))
        for file in files:
            product_name=file['name']
            if '.yaml' in product_name:
                list_of_product_names.append(product_name.replace(".yaml",""))
        # print("in download_all_files_from_git_enterprise : list_of_product_names = ",list_of_product_names)
        return list_of_product_names
    except Exception as e:
        raise Exception("ERROR in " + FILE_NAME + " : " + repr(e))

def download_file_from_git_enterprise(git_base_url, git_branch, git_priv_token, file_path_to_download, filename_to_download, local_target_dir):
    try:
        curl_auth_header = "'Authorization: token " + git_priv_token + "'"
        cmd = "curl -s -k -H " + curl_auth_header + " -H 'Accept: application/vnd.github.v3.raw' -L " + git_base_url.replace("https://github","https://raw.githubusercontent",1) + git_branch + "/" + file_path_to_download + "/" + filename_to_download + ".yaml > " + local_target_dir + "/" + filename_to_download + ".yaml" + " && cat " + local_target_dir + "/" + filename_to_download + ".yaml"
        # print("my command: ", cmd)
        if not os.path.isdir(local_target_dir):
            os.makedirs(local_target_dir)

        download_file_from_git_res = shell_command.shcmd(cmd)
        return download_file_from_git_res
    except Exception as e:
        raise Exception("ERROR in " + FILE_NAME + " : " + repr(e))
