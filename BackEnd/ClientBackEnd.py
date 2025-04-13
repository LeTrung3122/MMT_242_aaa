import os
import bencodepy
import requests
from urllib.parse import urlparse, parse_qs
from BackEnd.Helper import chunk_SIZE


class Client():

    def __init__(self, host, local_path):
        self.host = host
        self.local_path = local_path
        chunk_list_path = os.path.join('BackEnd', local_path, 'Chunk_List')
        os.makedirs(chunk_list_path, exist_ok=True)

    def get_peers_with_file(self, tracker_url, file_name, group=None):
        params = {"file": file_name}
        if group:  # nếu có nhóm riêng tư
            params["group"] = group

        response = requests.get(tracker_url + "/peers", params=params)

        if response.status_code == 200:
            peers = response.json().get("peers", [])
            resIP, resPort = [], []
            for peer in peers:
                resIP.append(peer["ip"])
                resPort.append(peer["port"])
            return resIP, resPort
        else:
            print(f"Lỗi khi lấy danh sách peer: {response.text}")
            return [], []

    def read_torrent_file(self, encoded_data):
        torrent_data = {}
        decoded_data = bencodepy.decode(encoded_data)
        for key, value in decoded_data.items():
            if isinstance(value, bytes):
                torrent_data[key.decode('utf-8')] = value.decode('utf-8')
            elif isinstance(value, dict):
                sub_dict = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, bytes):
                        sub_dict[sub_key.decode(
                            'utf-8')] = sub_value.decode('utf-8')
                    else:
                        sub_dict[sub_key.decode('utf-8')] = sub_value
                torrent_data[key.decode('utf-8')] = sub_dict
            else:
                torrent_data[key.decode('utf-8')] = value

        return torrent_data

    def parse_magnet_link(self, magnet_link):
        parsed = urlparse(magnet_link)
        if parsed.scheme != 'magnet':
            raise ValueError("This is not a valid magnet link!")

        params = parse_qs(parsed.query)
        info_hash = params.get('xt', [None])[0]
        if info_hash and info_hash.startswith('urn:btih:'):
            info_hash = info_hash[9:]

        file_name = params.get('dn', [None])[0]
        tracker_url = params.get('tr', [None])[0]
        num_chunks = int(params.get('x.n', [0])[0])
        chunk_size = int(params.get('x.c', [0])[0])
        file_size = int(params.get('x.s', [0])[0])
        torrent_data = {
            'announce': tracker_url if tracker_url else None,
            'hashinfo': {
                'file_name': file_name,
                'num_chunks': num_chunks,
                'chunk_size': chunk_size,
                'file_size': file_size,
                'info_hash': info_hash
            }
        }

        return torrent_data

    def file_make(self, file_name):
        SplitNum = 0
        dir_path = "./BackEnd/" + str(self.local_path) + "/Chunk_List"
        for path in os.listdir(dir_path):
            SplitNum += os.path.isfile(os.path.join(dir_path, path)) is True

        fileM = open("./BackEnd/" + str(self.local_path) +
                     "/" + str(file_name), "wb")
        for chunk in range(SplitNum):
            fileT = open(str(dir_path) + "/chunk" + str(chunk) + ".txt", "rb")
            byte = fileT.read(chunk_SIZE)
            fileM.write(byte)

        fileM.close()
