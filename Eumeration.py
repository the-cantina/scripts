import subprocess
import re
import ipaddress

# Function to validate network input
def is_valid_network(network):
    try:
        # Try to create an IP network object using the input
        ipaddress.IPv4Network(network, strict=False)
        return True
    except ValueError:
        return False

# Prompt user for network input (providing an example but not defaulting)
while True:
    user_input = input("Enter target network (example: 192.168.1.0/24): ").strip()
    
    if user_input and is_valid_network(user_input):
        target_network = user_input
        break
    else:
        print("[!] Error: Invalid network. Please enter a valid network (e.g., 192.168.1.0/24).")

print(f"[*] Scanning network: {target_network}")

# Discover live hosts using nmap ping sweep
def discover_hosts(network):
    try:
        print("[*] Discovering hosts with nmap ping sweep...")
        # -sn = ping scan (host discovery only), -n disables DNS resolution, -oG - outputs grepable format to stdout
        nmap_output = subprocess.check_output([
            "nmap", "-sn", "-n", "-oG", "-", network
        ]).decode()

        # Extract IP addresses of hosts that are up
        ip_list = re.findall(r"Host: (\d+\.\d+\.\d+\.\d+) \(", nmap_output)
        return ip_list
    except subprocess.CalledProcessError:
        return []

# Scan ports 1-10000 on each host using nmap
def scan_ports(ip):
    try:
        print(f"[*] Scanning ports for {ip}...")
        # Scan ports 1-10000 only, showing open ports
        nmap_result = subprocess.check_output([ 
            "nmap", "-p1-10000", "--open", "--min-rate", "5000", "-T4", ip, "-oG", "-" 
        ]).decode()

        # Extract open ports using regex
        open_ports = re.findall(r"(\d+)/open", nmap_result)
        open_ports = list(map(int, open_ports))

        if not open_ports:  # If no open ports are found
            print(f"[!] No open ports found on {ip}")
        return ip, open_ports
    except subprocess.CalledProcessError:
        return ip, []

# Run Gobuster on hosts with port 80 open
def run_gobuster(ip):
    try:
        wordlist = "/usr/share/wordlists/dirb/common.txt"
        print(f"[*] Running Gobuster on http://{ip} ...")
        subprocess.run(["gobuster", "dir", "-u", f"http://{ip}", "-w", wordlist, "-q"], check=True)
    except subprocess.CalledProcessError:
        print(f"[-] Gobuster failed on {ip}")

# Main logic
def main():
    hosts = discover_hosts(target_network)
    if not hosts:
        print("[!] No hosts found.")
        return

    print(f"\n[+] Discovered hosts: {hosts}")

    for host in hosts:
        ip, ports = scan_ports(host)
        if ports:
            print(f"[+] {ip} has open ports: {ports}")
            if 80 in ports:
                run_gobuster(ip)

if __name__ == "__main__":
    main()
