import os, json

FILE_NAME = "utils.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 
DEBUG = os.getenv('DEBUG','')

def get_toolkit_credentials(CONFIG_FILES_DIR):
    toolkit_credentials = None
    if os.path.isfile(CONFIG_FILES_DIR + "/toolkit-creds.json"):
        with open(CONFIG_FILES_DIR + "/toolkit-creds.json") as f:
            toolkit_credentials = json.load(f)
    else:
        toolkit_credentials = {}
    return toolkit_credentials

def get_env_config(CONFIG_FILES_DIR):
    env_config = None
    if os.path.isfile(CONFIG_FILES_DIR + "/config.json"):
        with open(CONFIG_FILES_DIR + "/config.json") as f:
            config_content = f.read()

            # Check if multiple JSON objects are present
            json_objects = config_content.split('}{')
            if len(json_objects) > 1:
                print(INFO + "Multiple JSON objects detected. Merging them.")
                # Fix the split by adding back the missing braces
                json_objects = [json_objects[0] + '}', '{' + json_objects[1]]
                # Convert the JSON strings into dictionaries
                env_config_1 = json.loads(json_objects[0])
                env_config_2 = json.loads(json_objects[1])
                # Merge the dictionaries
                env_config = {**env_config_1, **env_config_2}
            else:
                env_config = json.loads(config_content)
            
    else:
        env_config = {}

    print(INFO + "Final combined env_config: ", env_config)
    return env_config

def pretty_print_request(req):
    print(INFO + "---------- Request start ----------")
    print(INFO + req.method + ' ' + req.url)
    for k, v in req.headers.items():
        print(INFO + '{}: {}'.format(k, v))
    print(INFO, req.body)
    print(INFO + "---------- Request end ----------")
