import subprocess
import logging
import paramiko

# Set up logging
logging.basicConfig(filename='cleanup_log.out', level=logging.INFO, 
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

def check_and_kill_open_files(fs):
    """
    Check for open files on the file system using fuser and kill them.
    """
    try:
        logging.info(f"Checking for open files on {fs}")
        check_command = f"sudo fuser -km {fs}"
        subprocess.run(check_command, shell=True, check=True)
        logging.info(f"Open files on {fs} have been closed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to close open files on {fs}: {e}")
        raise

def unmount_nfs_on_suse(suse_ip, suse_user, nfs_mounts):
    """
    Unmounts NFS shares on the SUSE server.
    """
    try:
        logging.info("Connecting to SUSE server to unmount NFS shares...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(suse_ip, username=suse_user)

        for mount_point in nfs_mounts:
            logging.info(f"Running fuser check on {mount_point} to close open files.")
            check_and_kill_open_files(mount_point)

            unmount_command = f"sudo umount {mount_point}"
            logging.info(f"Unmounting NFS share at {mount_point}")
            ssh_execute_command(ssh, unmount_command)

        ssh.close()
        logging.info("All NFS shares unmounted successfully on SUSE server.")
    except Exception as e:
        logging.error(f"Error during NFS unmounting on SUSE: {e}")
        raise

def unmount_file_systems_on_aix(file_systems):
    """
    Unmount file systems on the AIX server.
    """
    try:
        for fs in file_systems:
            logging.info(f"Running fuser check on {fs} to close open files.")
            check_and_kill_open_files(fs)

            logging.info(f"Unmounting file system {fs}")
            unmount_command = f"umount {fs}"
            subprocess.run(unmount_command, shell=True, check=True)
        logging.info("All file systems unmounted successfully on AIX server.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error unmounting file system: {e}")
        raise

def deactivate_and_export_vg(vg_name):
    """
    Deactivate and export the volume group on the AIX server.
    """
    try:
        logging.info(f"Deactivating volume group {vg_name}")
        deactivate_command = f"varyoffvg {vg_name}"
        subprocess.run(deactivate_command, shell=True, check=True)

        logging.info(f"Exporting volume group {vg_name}")
        export_command = f"exportvg {vg_name}"
        subprocess.run(export_command, shell=True, check=True)

        logging.info(f"Volume group {vg_name} deactivated and exported successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error deactivating or exporting volume group: {e}")
        raise

if __name__ == "__main__":
    # Example NFS mount points on the SUSE server
    nfs_mounts = ["/mnt/data1", "/mnt/data2", "/mnt/data3"]

    # SUSE server connection details
    suse_ip = "suse_ip_address"
    suse_user = "suse_user"

    # File systems and volume group on the AIX server
    file_systems = ["/data", "/logs"]
    vg_name = "datavg"

    try:
        # Step 1: Unmount NFS shares on SUSE
        unmount_nfs_on_suse(suse_ip, suse_user, nfs_mounts)

        # Step 2: Unmount file systems on AIX
        unmount_file_systems_on_aix(file_systems)

        # Step 3: Deactivate and export the volume group on AIX
        deactivate_and_export_vg(vg_name)

        logging.info("Cleanup completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the cleanup process: {e}")
