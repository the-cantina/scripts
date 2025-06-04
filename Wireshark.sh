#Blue Team Wireshark Config
sshpass -p labadmin ssh admin@192.168.0.1 -o StrictHostKeyChecking=no "tcpdump -ni em3 -U -w -" | wireshark -k -i -