import psutil
import socket
import os
import math
import requests
import platform

chunk_SIZE = 512 * 1024
# tracker_url = "http://192.168.1.4:18000" #LAN
tracker_url = "http://127.0.0.1:18000"


def get_wireless_ipv4():
    for interface, addrs in psutil.net_if_addrs().items():
        if any(
            wireless in interface.lower()
            for wireless in ["wi-fi", "wireless", "wlan", "en0", "airport"]
        ):
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.address
    return None


def list_shared_files(files_path):
    return [
        file
        for file in os.listdir(files_path)
        if os.path.isfile(os.path.join(files_path, file))
    ]


def calculate_number_of_chunk(file_size):
    return math.ceil(file_size / chunk_SIZE)


def get_peers_count(tracker_url):
    response = requests.get(tracker_url + "/peers_count")
    if response.status_code == 200:
        peer_count = response.json().get("peer_count", 0)
        return peer_count


def remove_chunk_list():
    if platform.system() == "Windows":
        os.system('cmd /c "cd BackEnd/Share_File & rmdir /s /q Chunk_List"')
    else:
        os.system("rm -rf BackEnd/Share_File/Chunk_List")
