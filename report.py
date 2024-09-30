import smtplib
from email.mime.text import MIMEText
import logging

# Set up logging
logging.basicConfig(filename='report_log.out', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def gather_scan_results():
    """
    Gather scan results from the CyberSense process.
    This function reads from run_log.out to check for scan status and details.
    """
    try:
        logging.info("Gathering CyberSense scan results...")
        with open("run_log.out", "r") as log_file:
            scan_results = log_file.read()
        logging.info("Successfully gathered scan results.")
        return scan_results
    except FileNotFoundError as e:
        logging.error(f"Scan log file not found: {e}")
        return "Scan results log file not found."
    
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
    # Gather the scan and backup results
    scan_results = gather_scan_results()
    backup_results = gather_backup_results()
    
    # Generate the report
    report = generate_report(scan_results, backup_results)
    
    # Send the report
    recipient_email = "recipient@example.com"
    send_report(report, recipient_email)
