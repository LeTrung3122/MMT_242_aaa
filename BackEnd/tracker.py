import os
import hashlib
import bencodepy
from Helper import chunk_SIZE, tracker_url, calculate_number_of_chunk


class Tracker():
    def __init__(self, upload_folder="./Share_File", torrent_folder="./Torrent_File", tracker_url=tracker_url):
        self.upload_folder = upload_folder
        self.torrent_folder = torrent_folder
        self.tracker_url = tracker_url
        self.magnet_links = {}

        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.torrent_folder, exist_ok=True)

    def create_torrent_data(self, file_name, file_size):
        num_chunks = calculate_number_of_chunk(file_size)
        torrent_data = {
            'announce': self.tracker_url.encode('utf-8'),
            'hashinfo': {
                'file_name': file_name,
                'num_chunks': num_chunks,
                'chunk_size': chunk_SIZE,
                'file_size': file_size
            }
        }
        return torrent_data

    def create_magnet_link(self, torrent_data):
        tracker_url = torrent_data['announce'].decode('utf-8')
        file_name = torrent_data['hashinfo']['file_name']
        num_chunks = torrent_data['hashinfo']['num_chunks']
        chunk_size = torrent_data['hashinfo']['chunk_size']
        file_size = torrent_data['hashinfo']['file_size']
        hashinfo_str = f"{file_name}{chunk_size}{num_chunks}"
        info_hash = hashlib.sha1(hashinfo_str.encode('utf-8')).hexdigest()
        magnet_link = (
            f"magnet:?xt=urn:btih:{info_hash}"
            f"&dn={file_name}"
            f"&tr={tracker_url}"
            f"&x.n={num_chunks}"
            f"&x.c={chunk_size}"
            f"&x.s={file_size}"
        )

        return magnet_link

    def create_torrent_file(self, torrent_data):
        torrent_file_content = bencodepy.encode(torrent_data)
        file_name = torrent_data['hashinfo']['file_name']
        torrent_file_path = os.path.join(
            self.torrent_folder, f"{file_name}.torrent")
        with open(torrent_file_path, 'wb') as f:
            f.write(torrent_file_content)
