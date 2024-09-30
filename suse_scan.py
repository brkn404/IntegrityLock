import paramiko
import logging
import requests
import time

# Set up logging to write to run_log.out
logging.basicConfig(filename='run_log.out', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ssh_execute_command(ssh_client, command):
    """
    Executes a command on the remote SUSE server via SSH.
    """
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()

    if error:
        logging.error(f"Command failed: {command}, Error: {error}")
        raise Exception(f"Error: {error}")

    logging.info(f"Command succeeded: {command}, Output: {output}")
    return output

def mount_nfs_on_suse(ssh_client, mounts, adapter_ips):
    """
    Mounts NFS exports on the SUSE server across the specified IP adapters.
    """
    adapter_index = 0
    total_adapters = len(adapter_ips)  # Number of adapters provided

    for mount_info in mounts:
        nfs_server, nfs_export, mount_point = mount_info
        adapter_ip = adapter_ips[adapter_index]  # Get the next adapter IP

        logging.info(f"Mounting {nfs_export} to {mount_point} via adapter {adapter_ip}")
        
        # Construct the mount command with the specified NFS options
        mount_command = (
            f"sudo mount -o ro,nfsvers=4,tcp,actimeo=0,acregmin=300,acregmax=7200,"
            f"acdirmin=300,acdirmax=7200 {nfs_server}:{nfs_export} {mount_point} "
            f"-o rw,async,noatime,nodiratime,proto=tcp,nolock"
        )

        # Execute the mount command
        ssh_execute_command(ssh_client, mount_command)

        # Cycle to the next adapter IP
        adapter_index = (adapter_index + 1) % total_adapters

def start_cybersense_scan(api_url, policy, nfs_export):
    """
    Starts the CyberSense scan via the PolicyExec API.
    """
    logging.info(f"Starting CyberSense scan for policy: {policy} on NFS export: {nfs_export}")
    scan_payload = {
        "policy": policy,
        "nfs_export": nfs_export
    }
    
    response = requests.post(f"{api_url}/PolicyExec", json=scan_payload)
    
    if response.status_code == 200 or response.status_code == 202:
        scan_id = response.json().get("job_id")
        logging.info(f"CyberSense scan started successfully with Scan ID: {scan_id}")
        return scan_id
    else:
        logging.error(f"Failed to start CyberSense scan: {response.text}")
        raise Exception("Scan failed to start")

def monitor_scan(scan_id, api_url):
    """
    Monitors the progress of the scan and logs the results.
    """
    logging.info(f"Monitoring scan ID: {scan_id}")
    while True:
        status_response = requests.get(f"{api_url}/JobStatus", params={"job_id": scan_id})
        
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
        # Add more mounts for remaining file systems...
    ]
    
    # Define the CyberSense API URL
    cybersense_api_url = "https://9.11.235.194/cybersense/v1"

    # Define the CyberSense policy to execute
    policy_name = "YourPolicyName"

    try:
        # Set up SSH connection to the SUSE server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(suse_ip, username=suse_user)

        # Step 1: Mount NFS exports across the 4x25GB adapters
        mount_nfs_on_suse(ssh, nfs_mounts, adapter_ips)

        # Step 2: Start CyberSense scan via API
        nfs_export = nfs_mounts[0][1]  # Use the first NFS export for simplicity
        scan_id = start_cybersense_scan(cybersense_api_url, policy_name, nfs_export)

        # Step 3: Monitor the scan progress and log output
        monitor_scan(scan_id, cybersense_api_url)

    except Exception as e:
        logging.error(f"An error occurred during the SUSE scan process: {e}")
    finally:
        ssh.close()
