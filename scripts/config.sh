#!/bin/bash

#######################################
# Configuration Initialization Script #
#######################################

if [[ -z "$1" ]]
then
  echo "[ERROR][config.sh] - An IBM API Connect installation OpenShift project was not provided"
  exit 1
else
  APIC_NAMESPACE=$1
  echo "IBM API Connect has been installed in the ${APIC_NAMESPACE} OpenShift project"
fi

# Make a configuration files directory
cd ..
mkdir -p config
cd config

# Function to get the route host by a pattern
get_route_host() {
  local route_pattern=$1
  local exclude_pattern=$2
  if [[ -n "$exclude_pattern" ]]; then
    local route_host=$(oc get routes -n ${APIC_NAMESPACE} --no-headers | grep "${route_pattern}" | grep -v "${exclude_pattern}" | awk '{print $2}')
  else
    local route_host=$(oc get routes -n ${APIC_NAMESPACE} --no-headers | grep "${route_pattern}" | awk '{print $2}')
  fi
  echo ${route_host}
}

# Get the needed URLs for the automation
APIC_ADMIN_URL=$(get_route_host "admin")
if [[ -z "${APIC_ADMIN_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Admin url"; exit 1; fi

APIC_API_MANAGER_URL=$(get_route_host "api-manager")
if [[ -z "${APIC_API_MANAGER_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Management url"; exit 1; fi

APIC_GATEWAY_URL=$(get_route_host "gateway" "manager")
if [[ -z "${APIC_GATEWAY_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Gateway url"; exit 1; fi

APIC_GATEWAY_MANAGER_URL=$(get_route_host "gateway-manager")
if [[ -z "${APIC_GATEWAY_MANAGER_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Gateway Manager url"; exit 1; fi

APIC_ANALYTICS_CONSOLE_URL=$(get_route_host "ai-endpoint")
if [[ -z "${APIC_ANALYTICS_CONSOLE_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Analytics Console url"; exit 1; fi

APIC_PORTAL_DIRECTOR_URL=$(get_route_host "portal-director")
if [[ -z "${APIC_PORTAL_DIRECTOR_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Portal Director url"; exit 1; fi

APIC_PORTAL_WEB_URL=$(get_route_host "portal-web")
if [[ -z "${APIC_PORTAL_WEB_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Portal Web url"; exit 1; fi

APIC_PLATFORM_API_URL=$(get_route_host "platform-api")
if [[ -z "${APIC_PLATFORM_API_URL}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Platform API url"; exit 1; fi

# Storing the URLs in the JSON config file
echo "{" >> config.json
echo "\"APIC_ADMIN_URL\":\"${APIC_ADMIN_URL}\"," >> config.json
echo "\"APIC_API_MANAGER_URL\":\"${APIC_API_MANAGER_URL}\"," >> config.json
echo "\"APIC_GATEWAY_URL\":\"${APIC_GATEWAY_URL}\"," >> config.json
echo "\"APIC_GATEWAY_MANAGER_URL\":\"${APIC_GATEWAY_MANAGER_URL}\"," >> config.json
echo "\"APIC_ANALYTICS_CONSOLE_URL\":\"${APIC_ANALYTICS_CONSOLE_URL}\"," >> config.json
echo "\"APIC_PORTAL_DIRECTOR_URL\":\"${APIC_PORTAL_DIRECTOR_URL}\"," >> config.json
echo "\"APIC_PORTAL_WEB_URL\":\"${APIC_PORTAL_WEB_URL}\"," >> config.json
echo "\"APIC_PLATFORM_API_URL\":\"${APIC_PLATFORM_API_URL}\"," >> config.json

# Realms
ADMIN_REALM="admin/default-idp-1"

# Get the APIC CLI
echo "Downloading APIC toolkit from: https://${APIC_ADMIN_URL}/client-downloads/toolkit-linux.tgz"
HTTP_CODE=$(curl -s -o toolkit-linux.tgz -w "%{http_code}" https://${APIC_ADMIN_URL}/client-downloads/toolkit-linux.tgz --insecure)
if [[ "${HTTP_CODE}" != "200" ]]
then 
  echo "[ERROR][config.sh] - An error occurred downloading the APIC toolkit to get the APIC CLI (HTTP Code: ${HTTP_CODE})"
  exit 1
fi

# Verify download
if [[ ! -f "toolkit-linux.tgz" ]]; then 
  echo "[ERROR][config.sh] - APIC toolkit download failed, file toolkit-linux.tgz not found"
  exit 1
fi

# List contents of the tarball
echo "Contents of the toolkit-linux.tgz tarball:"
tar -tzvf toolkit-linux.tgz

# Extract the toolkit
tar -zxvf toolkit-linux.tgz
if [[ $? -ne 0 ]]; then 
  echo "[ERROR][config.sh] - An error occurred extracting the APIC toolkit"
  exit 1
fi

# Verify extraction
if [[ ! -f "apic" ]]; then 
  echo "[ERROR][config.sh] - Extracted APIC CLI not found"
  exit 1
fi

chmod +x apic

# Get the IBM APIC Connect Cloud Manager Admin password
APIC_ADMIN_PASSWORD=$(oc get secret $(oc get secrets -n ${APIC_NAMESPACE} | grep mgmt-admin-pass | awk '{print $1}') -n ${APIC_NAMESPACE} -o jsonpath='{.data.password}' | base64 -d)
if [[ -z "${APIC_ADMIN_PASSWORD}" ]]; then echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Admin password"; exit 1; fi

# Store the IBM APIC Connect Cloud Manager Admin password in the JSON config file
echo "\"APIC_ADMIN_PASSWORD\":\"${APIC_ADMIN_PASSWORD}\"" >> config.json
echo "}" >> config.json

# Login to IBM API Connect Cloud Manager through the APIC CLI
./apic login --server ${APIC_ADMIN_URL} --username admin --password ''"${APIC_ADMIN_PASSWORD}"'' --realm ${ADMIN_REALM} --accept-license > /dev/null
if [[ $? -ne 0 ]]; then 
  echo "[ERROR][config.sh] - An error occurred logging into IBM API Connect using the APIC CLI"
  exit 1
fi

# Get the toolkit credentials
./apic cloud-settings:toolkit-credentials-list --server ${APIC_ADMIN_URL} --format json > toolkit-creds.json
if [[ $? -ne 0 ]]; then 
  echo "[ERROR][config.sh] - An error occurred getting the IBM API Connect Toolkit Credentials using the APIC CLI"
  exit 1
fi

# DEBUG information
if [[ ! -z "${DEBUG}" ]]
then
  echo "This is the environment configuration"
  echo "-------------------------------------"
  cat config.json
  echo "These are the IBM API Connect ToolKit Credentials"
  echo "-------------------------------------------------"
  cat toolkit-creds.json
fi
