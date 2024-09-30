import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_available_disks():
    """
    List available disks on the AIX server to ensure the snapshot volume is visible.
    """
    try:
        logging.info("Listing available disks on the AIX server")
        list_disks_command = "lsdev -Cc disk"
        result = subprocess.run(list_disks_command, shell=True, check=True, capture_output=True, text=True)
        disks = result.stdout.strip().split("\n")
        logging.info(f"Available disks: {disks}")
        return disks
    except subprocess.CalledProcessError as e:
        logging.error("Failed to list available disks: {e}")
        raise

def import_volume_group(vg_name, disk):
    """
    Import the volume group from the snapshot using the specified disk.
    """
    try:
        logging.info(f"Importing volume group {vg_name} from disk {disk}")
        import_command = f"importvg -y {vg_name} {disk}"
        subprocess.run(import_command, shell=True, check=True)
        logging.info(f"Volume group {vg_name} imported successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to import volume group {vg_name} from disk {disk}: {e}")
        raise

def activate_volume_group(vg_name):
    """
    Activate (varyon) the volume group to make it available for use.
    """
    try:
        logging.info(f"Activating volume group {vg_name}")
        activate_command = f"varyonvg {vg_name}"
        subprocess.run(activate_command, shell=True, check=True)
        logging.info(f"Volume group {vg_name} activated successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to activate volume group {vg_name}: {e}")
        raise

def mount_file_systems(fs_list):
    """
    Mount all file systems in the list.
    """
    try:
        for fs in fs_list:
            logging.info(f"Mounting file system {fs}")
            mount_command = f"mount {fs}"
            subprocess.run(mount_command, shell=True, check=True)
            logging.info(f"File system {fs} mounted successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to mount file system {fs}: {e}")
        raise

def export_nfs_shares(nfs_shares):
    """
    Export the mounted file systems as NFS shares.
    """
    try:
        for share in nfs_shares:
            logging.info(f"Exporting NFS share {share}")
            export_command = f"mknfsexp -d {share} -nfsvers 4"
            subprocess.run(export_command, shell=True, check=True)
            logging.info(f"NFS share {share} exported successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to export NFS share {share}: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    vg_name = "datavg"
    file_systems = ["/data", "/logs"]
    nfs_shares = ["/data", "/logs"]

    try:
        # Step 1: List available disks to ensure the snapshot volume is visible
        available_disks = list_available_disks()
        # Assuming the snapshot is mapped to a specific disk, update the disk variable accordingly
        snapshot_disk = "/dev/hdiskX"  # Replace with actual disk name after listing

        # Step 2: Import the volume group from the snapshot
        import_volume_group(vg_name, snapshot_disk)
        
        # Step 3: Activate the volume group
        activate_volume_group(vg_name)
        
        # Step 4: Mount the file systems
        mount_file_systems(file_systems)
        
        # Step 5: Export the file systems as NFS shares
        export_nfs_shares(nfs_shares)
        
    except Exception as e:
        logging.error(f"An error occurred during AIX NFS operations: {e}")
