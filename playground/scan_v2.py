import paramiko
import logging
import requests
import time

# Set up logging to write to run_log.out
logging.basicConfig(filename='run_log.out', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_session(api_url, auth_token):
    """
    Create a session to use with the Index Engines API.
    """
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = requests.post(f"{api_url}/session", headers=headers)
    
    if response.status_code == 200:
        session_id = response.json().get("sessionid")
        logging.info(f"Session created successfully with ID: {session_id}")
        return session_id
    else:
        logging.error(f"Failed to create session: {response.text}")
        raise Exception("Failed to create session")

def start_cybersense_scan(api_url, session_id, policy, nfs_export):
    """
    Starts the CyberSense scan via the PolicyExec API using a session.
    """
    headers = {
        "sessionid": session_id,
        "Content-Type": "application/json"
    }
    
    logging.info(f"Starting CyberSense scan for policy: {policy} on NFS export: {nfs_export}")
    scan_payload = {
        "policy": policy,
        "nfs_export": nfs_export
    }
    
    response = requests.post(f"{api_url}/PolicyExec", headers=headers, json=scan_payload)
    
    if response.status_code == 200 or response.status_code == 202:
        scan_id = response.json().get("job_id")
        logging.info(f"CyberSense scan started successfully with Scan ID: {scan_id}")
        return scan_id
    else:
        logging.error(f"Failed to start CyberSense scan: {response.text}")
        raise Exception("Scan failed to start")

def monitor_scan(scan_id, api_url, session_id):
    """
    Monitors the progress of the scan and logs the results.
    """
    headers = {
        "sessionid": session_id
    }
    
    logging.info(f"Monitoring scan ID: {scan_id}")
    while True:
        status_response = requests.get(f"{api_url}/JobStatus", headers=headers, params={"job_id": scan_id})
        
        if status_response.status_code == 200:
            scan_status = status_response.json().get("state")
            
            if scan_status == "Done":
                logging.info(f"Scan ID {scan_id} completed successfully.")
                break
            elif scan_status in ["Failed", "Canceled"]:
                logging.error(f"Scan ID {scan_id} failed or was canceled.")
                break
            else:
                logging.info(f"Scan ID {scan_id} in progress... Status: {scan_status}")
        else:
            logging.error(f"Failed to retrieve status for Scan ID {scan_id}: {status_response.text}")
            break
        
        # Poll the status every 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    # Set the SUSE server details
    suse_ip = "suse_ip_address"
    suse_user = "suse_user"

    # Define the 4 IP addresses of the 25GB adapters
    adapter_ips = [
        "adapter_ip_1",
        "adapter_ip_2",
        "adapter_ip_3",
        "adapter_ip_4"
    ]

    # Define NFS mounts: Format (nfs_server, nfs_export, mount_point)
    nfs_mounts = [
        ("aix_server_ip", "/export/data1", "/mnt/data1"),
        ("aix_server_ip", "/export/data2", "/mnt/data2"),
    ]
    
    # Define the CyberSense API URL and authentication token
    cybersense_api_url = "https://9.11.235.194/v1"
    auth_token = "your_auth_token"  # Assuming you have some way of getting a token
    
    # Define the CyberSense policy to execute
    policy_name = "YourPolicyName"

    try:
        # Step 1: Create a session with the CyberSense API
        session_id = create_session(cybersense_api_url, auth_token)

        # Step 2: Set up SSH connection to the SUSE server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(suse_ip, username=suse_user)

        # Step 3: Mount NFS exports across the 4x25GB adapters
        mount_nfs_on_suse(ssh, nfs_mounts, adapter_ips)

        # Step 4: Start CyberSense scan via API
        nfs_export = nfs_mounts[0][1]  # Use the first NFS export for simplicity
        scan_id = start_cybersense_scan(cybersense_api_url, session_id, policy_name, nfs_export)

        # Step 5: Monitor the scan progress and log output
        monitor_scan(scan_id, cybersense_api_url, session_id)

    except Exception as e:
        logging.error(f"An error occurred during the SUSE scan process: {e}")
    finally:
        ssh.close()
