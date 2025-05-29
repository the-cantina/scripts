import subprocess
import os
import sys

def run_command(command, check=True):
    print(f"Running: {command}")
    subprocess.run(command, shell=True, check=check)

def main():
    # Check for root
    if os.geteuid() != 0:
        print("This script must be run as root. Use: sudo python3 script.py")
        sys.exit(1)

    try:
        # Step 1: Download Kali archive keyring
        run_command("wget https://archive.kali.org/archive-keyring.gpg -O /usr/share/keyrings/kali-archive-keyring.gpg")

        # Step 2: Update APT sources (optional — add this only if needed)
        # Example: add a Kali sources list using the new keyring
        sources_list = "/etc/apt/sources.list.d/kali.list"
        with open(sources_list, 'w') as f:
            f.write("deb [signed-by=/usr/share/keyrings/kali-archive-keyring.gpg] http://http.kali.org/kali kali-rolling main contrib non-free\n")

        # Step 3: Update and upgrade
        run_command("apt update")
        run_command("apt -y upgrade")

        print("System update and upgrade completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
