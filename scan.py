import subprocess
import ipaddress
import shutil
import sys
import os
import socket

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Run a shell command
def run_command(command, check=True):
    print(f"{CYAN}[*] Running: {command}{RESET}")
    subprocess.run(command, shell=True, check=check)

# Ensure script is run as root
def ensure_root():
    if os.geteuid() != 0:
        print(f"{RED}[-] This script must be run as root. Use: sudo python3 script.py{RESET}")
        sys.exit(1)

# Kali repo setup
def setup_kali_repo():
    try:
        print(f"{CYAN}[*] Setting up Kali Linux repository and keys...{RESET}")
        run_command("wget https://archive.kali.org/archive-keyring.gpg -O /usr/share/keyrings/kali-archive-keyring.gpg")
        sources_list = "/etc/apt/sources.list.d/kali.list"
        with open(sources_list, 'w') as f:
            f.write("deb [signed-by=/usr/share/keyrings/kali-archive-keyring.gpg] http://http.kali.org/kali kali-rolling main contrib non-free\n")
        run_command("apt update")
        run_command("apt -y upgrade")
        print(f"{GREEN}[+] System update and Kali repo setup complete.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[-] Setup failed: {e}{RESET}")
        sys.exit(1)

# Check if Gobuster is installed or install it
def install_gobuster():
    if shutil.which("gobuster"):
        print(f"{GREEN}[*] Gobuster is already installed.{RESET}")
        return True
    print(f"{YELLOW}[*] Gobuster not found. Installing with apt...{RESET}")
    try:
        subprocess.run(["apt-get", "install", "-y", "gobuster"], check=True)
        print(f"{GREEN}[+] Gobuster installed successfully.{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}[-] Failed to install Gobuster. Install it manually.{RESET}")
        return False

# Check if port 80 is open
def check_port_80(ip, timeout=1.5):
    try:
        with socket.create_connection((ip, 80), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

# Run Gobuster against IP
def run_gobuster(ip):
    try:
        wordlist = "/usr/share/wordlists/dirb/common.txt"
        print(f"{CYAN}[*] Running Gobuster on http://{ip} ...{RESET}")
        subprocess.run(["gobuster", "dir", "-u", f"http://{ip}", "-w", wordlist, "-q"], check=True)
    except subprocess.CalledProcessError:
        print(f"{RED}[-] Gobuster failed on {ip}{RESET}")

# Let user pick a network from a list
def select_network():
    options = [
        "10.30.0.0/24",
        "192.168.1.0/24",
        "172.16.0.0/24"
    ]
    print(f"{CYAN}Select a target network:{RESET}")
    for i, net in enumerate(options, 1):
        print(f"  {i}. {net}")
    
    while True:
        choice = input("Enter number (1-3): ").strip()
        if choice in {"1", "2", "3"}:
            return options[int(choice) - 1]
        else:
            print(f"{RED}[!] Invalid choice. Please select 1, 2, or 3.{RESET}")

def main():
    ensure_root()
    setup_kali_repo()

    if not install_gobuster():
        sys.exit(1)

    target_network = select_network()
    print(f"{CYAN}[*] Target network selected: {target_network}{RESET}")

    network = ipaddress.IPv4Network(target_network, strict=False)
    hosts = [str(ip) for ip in network.hosts()]

    print(f"{CYAN}[*] Scanning {len(hosts)} IPs for port 80...{RESET}")

    for ip in hosts:
        if check_port_80(ip):
            print(f"{GREEN}[+] {ip} has port 80 open.{RESET}")
            run_gobuster(ip)
        else:
            print(f"{YELLOW}[-] Skipping {ip} (port 80 closed).{RESET}")

if __name__ == "__main__":
    main()
