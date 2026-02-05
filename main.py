import json
import shutil
import requests
from requests.auth import HTTPBasicAuth
import os
import concurrent.futures
from itertools import repeat

my_user = "user"
my_pass = 'password'
my_base_url = "https://10.10.10.10:443" #your ISE PAN ip address and port
my_encryption_pass = "encryptionpassword" #this will be used to encrypt the .pvk files
my_path = r"C:\\path" #the folder path where you want the certs exported

def get_ise_nodes(base_url): #outputs a list of nodes in the deplyment
    url = f"{base_url}/api/v1/deployment/node"
    response = requests.request("GET", url, auth=HTTPBasicAuth(my_user, my_pass), verify=False)
    hostnames = []
    for item in response.json()["response"]:
        hostnames.append(item["hostname"])
    return hostnames

def get_cert_list(base_url,hostname): #outputs a dictionnary list of certs for a specific node
    url= f"{base_url}/api/v1/certs/system-certificate/{hostname}"
    response = requests.request("GET", url, auth=HTTPBasicAuth(my_user, my_pass), verify=False)
    certs = []
    for item in response.json()["response"]:
        dict = {}
        dict["id"] = item["id"]
        dict["name"] = item["friendlyName"]
        certs.append(dict)
    return certs

def get_node_certs(base_url,hostname): #outputs a list of certs for a specific node
    cert_list = get_cert_list(base_url,hostname)
    url = f"{my_base_url}/api/v1/certs/system-certificate/export"
    for cert in cert_list:
        payload = json.dumps({"export": "CERTIFICATE_WITH_PRIVATE_KEY", "hostName": hostname, "id": cert["id"], "password": my_encryption_pass})
        headers = {'Content-Type': 'application/json',}
        response = requests.request("POST", url, headers=headers, auth=HTTPBasicAuth(my_user, my_pass), data=payload, verify=False, stream=True)
        filename = f"{cert["name"]}.zip"
        path = f"{my_path}/{hostname}"
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, filename), "wb") as f:
            shutil.copyfileobj(response.raw, f)

def get_node_certs_par(base_url,nodes): #concurrent function that exports all certificates
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(nodes)) as executor:
        return (list(executor.map(get_node_certs, repeat(base_url), nodes)))

get_node_certs_par(my_base_url, get_ise_nodes(my_base_url))