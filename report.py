import smtplib
from email.mime.text import MIMEText
import logging
import paramiko
import re
import os

# Set up logging
logging.basicConfig(filename='report_log.out', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ssh_retrieve_log(remote_host, remote_user, remote_password, remote_log_path, local_log_path):
    """
    Retrieve the run_log.out file from the remote scan engine server using SSH.
    """
    try:
        logging.info(f"Connecting to remote host {remote_host} to retrieve the log file...")
        
        # Set up SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_host, username=remote_user, password=remote_password)

        # Use SFTP to retrieve the log file
        sftp = ssh.open_sftp()
        sftp.get(remote_log_path, local_log_path)
        sftp.close()

        logging.info("Successfully retrieved the run log from the remote server.")
    except Exception as e:
        logging.error(f"Failed to retrieve log from remote server: {e}")
        raise e
    finally:
        ssh.close()

def parse_run_log(local_log_path):
    """
    Parse the run_log.out file to extract key scan details.
    """
    try:
        logging.info("Parsing CyberSense run log...")
        with open(local_log_path, "r") as log_file:
            log_contents = log_file.read()
        
        # Extract relevant details (example patterns, adjust as necessary)
        total_bytes_pattern = r"Processed\s([0-9]+)\sbytes"
        elapsed_time_pattern = r"Real=([0-9.]+)s"
        files_scanned_pattern = r"nfiles_scanned=([0-9]+)"
        warnings_pattern = r"warning: (.*)"

        total_bytes = re.search(total_bytes_pattern, log_contents)
        elapsed_time = re.search(elapsed_time_pattern, log_contents)
        files_scanned = re.search(files_scanned_pattern, log_contents)
        warnings = re.findall(warnings_pattern, log_contents)

        # Format the report from parsed details
        report = f"Processed Bytes: {total_bytes.group(1)}\n" if total_bytes else "Processed Bytes: N/A\n"
        report += f"Elapsed Time: {elapsed_time.group(1)} seconds\n" if elapsed_time else "Elapsed Time: N/A\n"
        report += f"Files Scanned: {files_scanned.group(1)}\n" if files_scanned else "Files Scanned: N/A\n"
        
        if warnings:
            report += "Warnings:\n" + "\n".join(warnings) + "\n"
        else:
            report += "Warnings: None\n"

        logging.info("Successfully parsed scan results.")
        return report

    except FileNotFoundError as e:
        logging.error(f"Run log file not found: {e}")
        return "Run log file not found."
    except Exception as e:
        logging.error(f"Error parsing run log: {e}")
        return f"Error parsing run log: {e}"

def gather_backup_results():
    """
    Gather backup results from the IBM Spectrum Protect process.
    This function reads from backup_log.out to check for backup status and details.
    """
    try:
        logging.info("Gathering backup results...")
        with open("backup_log.out", "r") as log_file:
            backup_results = log_file.read()
        logging.info("Successfully gathered backup results.")
        return backup_results
    except FileNotFoundError as e:
        logging.error(f"Backup log file not found: {e}")
        return "Backup results log file not found."

def generate_report(scan_results, backup_results):
    """
    Generate a report based on scan and backup results.
    """
    logging.info("Generating report...")
    report = f"""
    CyberSense Scan Results:
    ------------------------
    {scan_results}
    
    IBM Spectrum Protect Backup Results:
    ------------------------------------
    {backup_results}
    """
    logging.info("Report generated successfully.")
    return report

def send_report(report, recipient_email):
    """
    Send the report via email to the specified recipient.
    """
    logging.info(f"Sending report to {recipient_email}...")
    
    msg = MIMEText(report)
    msg["Subject"] = "Daily Integrity Report"
    msg["From"] = "your_email@example.com"
    msg["To"] = recipient_email
    
    try:
        with smtplib.SMTP("smtp.example.com", 587) as server:
            server.starttls()
            server.login("your_email@example.com", "your_password")
            server.sendmail("your_email@example.com", recipient_email, msg.as_string())
        logging.info("Report sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send report: {e}")

if __name__ == "__main__":
    # Define remote server credentials and paths
    remote_host = "remote_scan_engine_host"
    remote_user = "username"
    remote_password = "password"
    remote_log_path = "/remote/path/to/run_log.out"
    local_log_path = "run_log.out"
    
    # Retrieve the log file via SSH
    try:
        ssh_retrieve_log(remote_host, remote_user, remote_password, remote_log_path, local_log_path)

        # Parse the log file and gather scan results
        scan_results = parse_run_log(local_log_path)
    except Exception as e:
        scan_results = f"Error retrieving or parsing scan log: {e}"

    # Gather backup results
    backup_results = gather_backup_results()
    
    # Generate the report
    report = generate_report(scan_results, backup_results)
    
    # Send the report
    recipient_email = "recipient@example.com"
    send_report(report, recipient_email)

    # Clean up local log file if necessary
    if os.path.exists(local_log_path):
        os.remove(local_log_path)
