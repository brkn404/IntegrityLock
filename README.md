# Code Name IntegrityLock

IntegrityLock is a set of Python code designed to orchestrate the recovery, scanning, and backup of snapshots from IBM Flash Storage and AIX NFS environments. The project automates multiple tasks, including recovery of safeguarded snapshots, NFS exports, running CyberSense scans, performing backups, generating reports, and handling cleanup tasks.

## Project Structure

IntegrityLock/
├── ibm_flash.py          # For IBM Flash Storage operations
├── aix_nfs.py            # For AIX NFS/SP operations
├── suse_scan.py          # For SUSE Linux scanning
├── backup.py             # For handling backups
├── report.py             # For generating and sending reports
├── cleanup.py            # For handling cleanup operations (optional)
└── main.py               # The main orchestration script


### Descriptions

- **`ibm_flash.py`**: This script handles IBM Flash Storage operations. It recovers immutable snapshots from IBM SVC (Spectrum Virtualize) using the SVC CLI presents the snapshot to an AIX server.
  
- **`aix_nfs.py`**: This script manages AIX NFS operations. It imports a volume group, activates it, mounts file systems, and exports the file systems as NFS shares to be used by other servers.

- **`suse_scan.py`**: This script mounts NFS file systems across 4x25GB network cards and interfaces with the CyberSense API to start and monitor vulnerability scans on NFS-mounted directories. It uses a session-based authentication system to initiate the scans.

- **`backup.py`**: This script handles the backup operations after the CyberSense scan is complete or in tandom with the scan. It ensures that the critical data is safely backed up and air gapped to tape.

- **`report.py`**: Generates and sends reports summarizing the outcomes of the scans and backups. This script helps provide insights into the security and integrity of the data.

- **`cleanup.py`**: Cleans up the environment by unmounting file systems, exporting volume groups, and removing mappings. This script is executed after all other processes are complete to avoid buildup of resources.

- **`main.py`**: The main orchestration script that coordinates the execution of all other scripts. It handles the execution flow, runs the scripts in sequence or concurrently (as needed), and ensures that the entire process is executed correctly.

## Installation

To set up and run IntegrityLock, you need to install the required dependencies. You can install the dependencies by running the following command:

```bash
pip install -r requirements.txt

