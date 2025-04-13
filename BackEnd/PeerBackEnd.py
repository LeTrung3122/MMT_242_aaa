import os
import requests
from BackEnd.Helper import chunk_SIZE


class Peer:
    def __init__(self, IP, port, peerID, local_path):
        self.IP = IP
        self.port = port
        self.peerID = peerID
        self.local_path = local_path

    def announce_to_tracker(self, tracker_url, files, group=None):
        data = {
            "ip": self.IP,
            "port": self.port,
            "files": files,
        }

        if group:
            data["group"] = group

            requests.post(
                tracker_url + "/join_group",
                json={"group": group, "ip": self.IP},
            )

        # gửi announce như cũ
        response = requests.post(tracker_url + "/announce", json=data)
        if response.status_code == 200:
            print("Successful registration with tracker")
        else:
            print(f"Error registering with tracker: {response.text}")

    def file_break(self, file_name):
        chunk_list_path = os.path.join("BackEnd", self.local_path, "Chunk_List")
        os.makedirs(chunk_list_path, exist_ok=True)
        fileR = open("./BackEnd/" + str(self.local_path) + "/" + str(file_name), "rb")

        chunk = 0
        byte = fileR.read(chunk_SIZE)
        while byte:
            fileT = open(
                "./BackEnd/"
                + str(self.local_path)
                + "/Chunk_List/chunk"
                + str(chunk)
                + ".txt",
                "wb",
            )
            fileT.write(byte)
            fileT.close()
            byte = fileR.read(chunk_SIZE)
            chunk += 1
