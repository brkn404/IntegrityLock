# curl command to check the status of a policy:
#  
# curl -X GET "https://9.11.235.194/cybersense/v1/PolicyStatus?policy=YourPolicyName" \
#    -H "Authorization: Bearer your-auth-token"

# min request 

#curl -X POST "https://your-api-server/cybersense/v1/PolicyExec" \
#    -H "Content-Type: application/json" \
#    -H "Authorization: Bearer your-auth-token" \
#    -d '{
#          "policy": "SimplePolicy",
#          "nfs_export": "/mnt/simple_export"
#        }'

# Full Request 

#curl -X POST "https://your-api-server/cybersense/v1/PolicyExec" \
#    -H "Content-Type: application/json" \
#    -H "Authorization: Bearer your-auth-token" \
#    -d '{
#          "policy": "CyberRecoveryPolicy",
#          "nfs_export": "/mnt/exported_path",
#          "mtree": "ReplicationMTreeName",
#          "copyid": "CopyID123",
#          "vault_fqdn": "vault.example.com",
#          "vault_ip": "192.168.1.10",
#          "List_of_email_addresses": ["admin@example.com"]
#        }'

import requests

# Define the base URL
base_url = "https://your-api-server/cybersense/v1"

# Example: Getting DeltaBlockStatus
response = requests.get(f"{base_url}/DeltaBlockStatus")

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print("Delta Block Status:", data)
else:
    print(f"Failed to get status: {response.status_code}")


job_cancel_url = f"{base_url}/JobCancel"
data = {"job_id": 12345}  # Example job_id

response = requests.post(job_cancel_url, json=data)

if response.status_code == 200:
    print("Job cancelled successfully.")
else:
    print(f"Failed to cancel job: {response.status_code}")




job_statistics_url = f"{base_url}/JobStatistics"
params = {"job_id": 12345}  # Example job_id

response = requests.get(job_statistics_url, params=params)

if response.status_code == 200:
    # Assuming it returns a CSV file as mentioned in the response description
    with open('job_statistics.csv', 'wb') as f:
        f.write(response.content)
    print("Job statistics saved to job_statistics.csv")
else:
    print(f"Failed to retrieve statistics: {response.status_code}")



import requests

# Define the base URL for the API
base_url = "https://your-api-server/cybersense/v1"

# Define the PolicyExec endpoint
policy_exec_url = f"{base_url}/PolicyExec"

# Request body with required fields
data = {
    "policy": "CyberRecoveryPolicy",  # Replace with the actual policy name
    "nfs_export": "/mnt/exported_path",  # Replace with the actual NFS export path
    "mtree": "ReplicationMTreeName",  # Optional, replace if needed
    "copyid": "CopyID123",  # Optional, replace if needed
    "vault_fqdn": "vault.example.com",  # Optional, replace if needed
    "vault_ip": "192.168.1.10",  # Optional, replace if needed
    "List_of_email_addresses": ["admin@example.com"]  # Optional, replace with actual emails
}

# Make the POST request to start the scan
response = requests.post(policy_exec_url, json=data)

# Check if the request was successful
if response.status_code == 200:
    print("Scan job successfully initiated.")
elif response.status_code == 202:
    print("Scan job was accepted for processing.")
else:
    print(f"Failed to start scan: {response.status_code}")


