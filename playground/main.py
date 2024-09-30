import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging for orchestration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_name):
    """
    Run a specified script using subprocess.
    :param script_name: Name of the script to run (e.g., 'ibm_flash.py')
    """
    try:
        logging.info(f"Starting {script_name}...")
        subprocess.run(f"python3 {script_name}", shell=True, check=True)
        logging.info(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"{script_name} failed: {e}")
        raise

if __name__ == "__main__":
    try:
        # Step 1: Run ibm_flash.py to recover and present the snapshot
        run_script("ibm_flash.py")
        
        # Step 2: Run aix_nfs.py to import the VG, mount file systems, and export NFS
        run_script("aix_nfs.py")

        # Step 3: Run suse_scan.py and backup.py simultaneously
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            futures.append(executor.submit(run_script, "suse_scan.py"))
            futures.append(executor.submit(run_script, "backup.py"))

            # Wait for both tasks to complete
            for future in futures:
                result = future.result()

        logging.info("Scan and Backup processes completed successfully.")
        
        # Step 4: Cleanup the environment after everything is done
        run_script("cleanup.py")
        logging.info("Cleanup completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the orchestration process: {e}")
