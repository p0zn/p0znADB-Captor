import scapy.all as scapy
import subprocess
import time
from termcolor import colored
import sys

def print_banner():
    print(colored(r"""
            /$$$$$$                       /$$$$$$  /$$$$$$$  /$$$$$$$           /$$$$$$                        /$$                        
           /$$$_  $$                     /$$__  $$| $$__  $$| $$__  $$         /$$__  $$                      | $$                        
  /$$$$$$ | $$$$\ $$ /$$$$$$$$ /$$$$$$$ | $$  \ $$| $$  \ $$| $$  \ $$        | $$  \__/  /$$$$$$   /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$ 
 /$$__  $$| $$ $$ $$|____ /$$/| $$__  $$| $$$$$$$$| $$  | $$| $$$$$$$  /$$$$$$| $$       |____  $$ /$$__  $$|_  $$_/   /$$__  $$ /$$__  $$
| $$  \ $$| $$\ $$$$   /$$$$/ | $$  \ $$| $$__  $$| $$  | $$| $$__  $$|______/| $$        /$$$$$$$| $$  \ $$  | $$    | $$  \ $$| $$  \__/
| $$  | $$| $$ \ $$$  /$$__/  | $$  | $$| $$  | $$| $$  | $$| $$  \ $$        | $$    $$ /$$__  $$| $$  | $$  | $$ /$$| $$  | $$| $$      
| $$$$$$$/|  $$$$$$/ /$$$$$$$$| $$  | $$| $$  | $$| $$$$$$$/| $$$$$$$/        |  $$$$$$/|  $$$$$$$| $$$$$$$/  |  $$$$/|  $$$$$$/| $$      
| $$____/  \______/ |________/|__/  |__/|__/  |__/|_______/ |_______/          \______/  \_______/| $$____/    \___/   \______/ |__/      
| $$                                                                                              | $$                                    
| $$                                                                                              | $$                                    
|__/                                                                                              |__/        """, color="magenta"))
    
    print(colored("\n*************************************************************", color="yellow"))
    print(colored("\n* Copyright of p0zn, 2021                                   *", color="yellow"))
    print(colored("\n* Follow me on Github: /p0zn                                *", color="yellow"))
    print(colored("\n* Follow me on LinkedIn: /p0zn                              *", color="yellow"))
    print(colored("\n*************************************************************", color="yellow"))

def print_intro_message():
    message = "\nLet's hack 👁️ the world\n"
    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)
    print(colored("\nWARNING: This tool is for educational purposes only!", color="red"))
    time.sleep(1)

def check_adb_installed():
    try:
        subprocess.check_output(["adb", "version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_adb_server():
    try:
        subprocess.check_output(["adb kill-server"], shell=True)
        subprocess.check_output(["adb start-server"], shell=True)
    except subprocess.CalledProcessError as e:
        print(colored(f"\n[ERROR] Failed to execute ADB command: {e}", "red"))
        print(colored("💡 Make sure ADB is installed and in your system PATH.", "yellow"))
        sys.exit(1)
    except FileNotFoundError:
        print(colored("\n[ERROR] 'adb' command not found!", "red"))
        print(colored("💡 Please install Android Platform Tools and add 'adb' to PATH.", "yellow"))
        sys.exit(1)

def scan_network(ip):
    print(colored("\n\nInitiating ARP network scan... please wait.\n", color="blue"))
    arp_request_packet = scapy.ARP(pdst=ip)
    broadcast_packet = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    combined_packet = broadcast_packet / arp_request_packet
    answered_list = scapy.srp(combined_packet, timeout=1, verbose=False)[0]
    ip_list = []

    for element in answered_list:
        ip_list.append(str(element[1].psrc))

    revised_ip_list = list(dict.fromkeys(ip_list))
    return revised_ip_list

def connect_devices(ip_list):
    connected_list = []
    t = 1
    for ip in ip_list:
        try:
            connected = subprocess.check_output([f"adb connect {ip}:5555"], timeout=0.7, shell=True)
            if b"connected" in connected:
                connected_list.append(connected)
                print(f"Device {t}: {connected.decode('utf-8').strip()}")
                t += 1
        except subprocess.TimeoutExpired:
            print(colored(f"[TIMEOUT] {ip} did not respond.", "yellow"))
        except subprocess.CalledProcessError as e:
            print(colored(f"[ADB ERROR] Connection failed for {ip}: {e}", "red"))
    return connected_list

def save_output(connected_list):
    with open("output_file.txt", "w") as output:
        for element in connected_list:
            output.write(element.decode("utf-8") + "\n")
    print(colored("\n✔ Output successfully saved to 'output_file.txt'.", color="cyan"))

# ========== MAIN ==========
try:
    print_banner()
    print_intro_message()

    if not check_adb_installed():
        print(colored("\n❌ ADB is not installed or not found in system PATH. Exiting.", "red"))
        sys.exit(1)

    ip_range = input(colored("\nEnter target IP range (e.g., 192.168.1.1/24): ", "cyan"))
    ip_list = scan_network(ip_range)

    print(colored("\nStarting ADB service...", "cyan"))
    start_adb_server()

    print(colored("\nAttempting to connect to discovered devices...\n", "cyan"))
    time.sleep(0.5)

    connected_devices = connect_devices(ip_list)

    print(colored("\n✔ Attack process finished.", "green"))
    save_output(connected_devices)

    print(colored("\nDon't forget to follow me on GitHub 😻", "cyan"))

except KeyboardInterrupt:
    print(colored("\nExiting program due to keyboard interrupt.", "yellow"))
    time.sleep(1)
    sys.exit(0)
