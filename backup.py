import subprocess
import logging
import time

# Set up logging to track backup progress
logging.basicConfig(filename='backup_log.out', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def start_backup(backup_paths):
    """
    Starts the backup using IBM Spectrum Protect (TSM) and returns the session ID.
    :param backup_paths: List of paths to back up (e.g., NFS mount points)
    :return: The session ID of the backup job
    """
    try:
        logging.info("Starting IBM Spectrum Protect (TSM) backup...")

        # Start the backup for each path
        for path in backup_paths:
            backup_command = f"dsmc incr {path}"
            logging.info(f"Running backup command: {backup_command}")
            subprocess.run(backup_command, shell=True, check=True)

        logging.info("Backup initiated successfully for all paths.")
        
        # Retrieve the session ID
        session_id = get_backup_session_id()
        if session_id:
            logging.info(f"Backup session ID: {session_id}")
        else:
            logging.error("Failed to retrieve backup session ID")
            raise Exception("Backup session ID could not be retrieved")
        
        return session_id
    except subprocess.CalledProcessError as e:
        logging.error(f"Backup failed: {e}")
        raise

def get_backup_session_id():
    """
    Queries the IBM Spectrum Protect server for the active session ID.
    :return: The session ID of the current backup job
    """
    try:
        query_command = "dsmadmc -id=admin -password=admin query session"
        logging.info("Querying for active session ID...")
        result = subprocess.run(query_command, shell=True, capture_output=True, text=True, check=True)
        
        # Parse the session ID from the command output
        session_id = parse_session_id(result.stdout)
        return session_id
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to query session ID: {e}")
        return None

def parse_session_id(output):
    """
    Parses the session ID from the output of the query session command.
    :param output: The command output that contains session details
    :return: Parsed session ID
    """
    # This is a placeholder for the parsing logic.
    # Adjust this based on your environment's TSM output format.
    for line in output.splitlines():
        if "Session ID" in line:  # Adjust based on actual output format
            session_id = line.split()[-1]  # Extract the session ID
            return session_id
    return None

def monitor_backup(session_id):
    """
    Monitors the progress of the IBM Spectrum Protect (TSM) backup by querying session status.
    :param session_id: The session ID of the ongoing backup process.
    """
    logging.info(f"Monitoring IBM Spectrum Protect (TSM) backup with session ID {session_id}...")

    while True:
        try:
            # Query the backup session status
            query_command = f"dsmadmc -id=admin -password=admin query session {session_id}"
            result = subprocess.run(query_command, shell=True, check=True, capture_output=True, text=True)
            
            # Process the output to check the status
            output = result.stdout
            logging.info(f"Backup session {session_id} status: {output}")

            if "Completed" in output:
                logging.info(f"Backup session {session_id} completed successfully.")
                break
            elif "Failed" in output:
                logging.error(f"Backup session {session_id} failed.")
                break
            else:
                logging.info(f"Backup session {session_id} is still in progress...")
            
            time.sleep(30)  # Adjust the interval as needed

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to query backup session: {e}")
            raise

def cancel_backup():
    """
    Cancels the ongoing backup session.
    """
    try:
        logging.info("Cancelling IBM Spectrum Protect (TSM) backup...")
        cancel_command = "dsmadmc -id=admin -password=admin halt session"
        subprocess.run(cancel_command, shell=True, check=True)
        logging.info("Backup cancelled successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to cancel backup: {e}")
        raise

if __name__ == "__main__":
    # Example backup paths (NFS mount points)
    backup_paths = ["/mnt/data1", "/mnt/data2", "/mnt/data3"]

    try:
        # Step 1: Start the backup process and retrieve the session ID
        session_id = start_backup(backup_paths)
        
        # Step 2: Monitor the backup progress using the session ID
        if session_id:
            monitor_backup(session_id)

        # If needed, you can call cancel_backup() based on conditions (e.g., a failed scan or external trigger)
        # cancel_backup()

    except Exception as e:
        logging.error(f"An error occurred during the backup process: {e}")
