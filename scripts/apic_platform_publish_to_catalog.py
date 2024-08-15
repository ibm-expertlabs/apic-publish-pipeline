import os
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import json
import yaml
import apic_platform_get_bearer_token
import raw_file_download_from_git
import Audit_res
import utils

FILE_NAME = "apic_platform_publish_to_catalog.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 
WORKING_DIR_BASIC = "../WORKSPACE"


def get_api_name_from_product(env_local_target_dir, product_file_name):
    
    var_apilist = []
    try:
        with open(env_local_target_dir + "/" + product_file_name) as f:
            # use safe_load instead load
            dataMap = yaml.safe_load(f)
        if "product" in dataMap and "apis" in dataMap:
            for api_id, api_info in dataMap["apis"].items():
                if "name" in api_info:
                    var_apilist.append(api_info["name"].replace(":", "_"))
    except Exception as e:
        raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))
    return var_apilist

def delete_all_products(apic_platform_base_url, apic_mgmt_provorg, apic_mgmt_catalog, var_bearer_token): 
    try:

        url = "https://" + apic_platform_base_url + "/catalogs/" + apic_mgmt_provorg + "/" + apic_mgmt_catalog + "/products?confirm=" + apic_mgmt_catalog
                
        print(INFO + "Deleting all existing products in org: " + apic_mgmt_provorg + " and catalog: " + apic_mgmt_catalog)

        reqheaders = {
            "Accept" : "application/json",
            "Authorization" : "Bearer " + var_bearer_token
        }

        s = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        s.mount(url, HTTPAdapter(max_retries=retries))

        response = s.delete(url, headers=reqheaders, verify=False, timeout=300)
        print(INFO + "Response status_code:",response.status_code)
        if "204" not in str(response.status_code):
            raise Exception("An error occurred deleting all products")

    except Exception as e:
        raise Exception("An exception occurred deleting all products")

def publish_to_catalog_using_platform_api(apic_platform_base_url, apic_mgmt_provorg, apic_mgmt_catalog, env_local_target_dir, product_file_name, var_bearer_token): 
    resp_json = {}
    try:
        url = "https://" + apic_platform_base_url + "/catalogs/" + apic_mgmt_provorg + "/" + apic_mgmt_catalog + "/publish?migrate_subscriptions=true"
        
        product_file_name = product_file_name + '.yaml'
        
        multiple_files = [('product',(product_file_name, open(env_local_target_dir + "/" + product_file_name, 'rb'), 'application/json'))]
        var_apilist = get_api_name_from_product(env_local_target_dir, product_file_name)

        if var_apilist:
            print(INFO + "Publish product:", product_file_name)
            print(INFO + "with APIs:", var_apilist)
            for apiname in var_apilist:
                multiple_files.append(('openapi', (apiname + '.yaml', open(env_local_target_dir+ "/" + apiname + '.yaml', 'rb'), 'application/json')))

            reqheaders = {
                "Accept" : "application/json",
                "Authorization" : "Bearer " + var_bearer_token
            }

            s = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
            s.mount(url, HTTPAdapter(max_retries=retries))
            response = s.post(url, headers=reqheaders, files=multiple_files, verify=False, timeout=300)
            print(INFO + "Response:",response.status_code)
            resp_json = response.json()
        else:
            print(INFO + "Publish product:", product_file_name)
            print(INFO + "No APIs found for this product")
            resp_json = {
                "errorresponse" : "no APIs in product yaml - " + product_file_name
            }

    except Exception as e:
        resp_json = {
            "errorresponse" : e
        }
    
    return resp_json

def orchestrate():
    try:

        toolkit_credentials = utils.get_toolkit_credentials(os.environ["CONFIG_FILES_DIR"])
        environment_config = utils.get_env_config(os.environ["CONFIG_FILES_DIR"])

        var_product_tuple = raw_file_download_from_git.get_all_file_names_from_git_enterprise(os.environ["GIT_PRODUCTS_APIS_URL"],
                                                                                            os.environ["GIT_PRODUCTS_APIS_BRANCH"],
                                                                                            os.environ["GIT_PRIV_TOKEN"],
                                                                                            os.environ['GIT_PRODUCTS_PATH'])

        gbt_resp = apic_platform_get_bearer_token.get_bearer_token(environment_config["APIC_PLATFORM_API_URL"] + "/api",
                                                                   os.environ["PROV_ORG_OWNER_USERNAME"],
                                                                   os.environ["PROV_ORG_OWNER_PASSWORD"],
                                                                   os.environ["PROV_ORG_REALM"],
                                                                   toolkit_credentials["toolkit"]["client_id"],
                                                                   toolkit_credentials["toolkit"]["client_secret"])

        if "access_token" in gbt_resp:
            var_bearer_token = gbt_resp['access_token']

            delete_all_products(environment_config["APIC_PLATFORM_API_URL"] + "/api",
                                            os.environ["PROV_ORG_TITLE"].strip().replace(" ","-").lower(),
                                            os.environ["PROV_ORG_CATALOG_NAME"], 
                                            var_bearer_token)
            apic_publish_audit = {}
            for product_file_name in var_product_tuple:
                publish_resp = publish_to_catalog_using_platform_api(environment_config["APIC_PLATFORM_API_URL"] + "/api",
                                                                    os.environ["PROV_ORG_TITLE"].strip().replace(" ","-").lower(),
                                                                    os.environ["PROV_ORG_CATALOG_NAME"], 
                                                                    WORKING_DIR_BASIC,
                                                                    product_file_name,
                                                                    var_bearer_token)
                if "errorresponse" in publish_resp:
                    apic_publish_audit[product_file_name] = "FAILED" + publish_resp['errorresponse']
                elif "state" in publish_resp:
                    apic_publish_audit[product_file_name] = "SUCCESS"
                else:
                    apic_publish_audit[product_file_name] = "FAILED" + publish_resp['errorresponse']
            
            print(INFO + "apic_publish_audit: ",apic_publish_audit)
            Audit_res.update_apic_publish_audit(WORKING_DIR_BASIC, apic_publish_audit)
            
            isSuccess = True
            for key,value in apic_publish_audit.items():
                if "FAILED" in value:
                    isSuccess = False

            if isSuccess == True:
                Audit_res.update_stage_res(WORKING_DIR_BASIC, "Products_API_publish", "SUCCESS")
                print(INFO + "Products_API_publish SUCCESS")
            else:
                raise Exception("An error occurred publishing a product or API")
        else:
            raise Exception("An error occurred getting the bearer token: " + json.dumps(gbt_resp))
    except Exception as e:
        Audit_res.update_stage_res(WORKING_DIR_BASIC, "Products_API_publish", "FAILED")
        raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))



orchestrate()
