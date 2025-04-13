from flask import Flask, request, jsonify
from tracker import Tracker

app = Flask(__name__)

peers = dict()
files_download = dict()

MyTracker = Tracker()
groups: dict[str, set[str]] = {}


@app.route("/announce", methods=["POST"])
def announce():
    data = request.json
    ip = data.get("ip")
    port = data.get("port")
    files = data.get("files")

    for file in files:
        file_name = file["file_name"]
        file_size = file["file_size"]
        group = file.get("group")
        password = file.get("password")
        torrent_data = MyTracker.create_torrent_data(file_name, file_size)
        magnet_link = MyTracker.create_magnet_link(torrent_data)
        MyTracker.create_torrent_file(torrent_data)
        files_download[file_name] = {
            "magnet_link": magnet_link,
            "group": group,
            "password": password,
        }

    if ip and files:
        peers[ip] = {"port": port, "files": files}
        return jsonify({"message": "Peer registered successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400


@app.route("/peers", methods=["GET"])
def get_peers():
    file_name = request.args.get("file")
    group = request.args.get("group")  # NEW
    if file_name:
        matching_peers = []
        for ip, peer_info in peers.items():

            if group and ip not in groups.get(group, set()):
                continue
            for file in peer_info["files"]:
                if file["file_name"] == file_name:
                    matching_peers.append({"ip": ip, "port": peer_info["port"]})
                    break
        return jsonify({"peers": matching_peers}), 200
    return jsonify({"error": "File not specified"}), 400


@app.route("/peers_count", methods=["GET"])
def get_peers_count():
    peer_count = len(peers)
    return jsonify({"peer_count": peer_count}), 200


@app.route("/files", methods=["GET"])
def list_files():
    response = {}
    for file, info in files_download.items():
        response[file] = {
            "magnet_link": info["magnet_link"],
            "is_private": True if info.get("password") else False,
        }
    return jsonify(response), 200


@app.route("/join_group", methods=["POST"])
def join_group():
   
    data = request.json
    group = data.get("group")
    ip = data.get("ip")
    if not group or not ip:
        return jsonify({"error": "Missing field"}), 400

    groups.setdefault(group, set()).add(ip)
    return jsonify({"message": f"{ip} joined {group}"}), 200


@app.route("/verify_file_access", methods=["POST"])
def verify_file_access():
    data = request.json
    file_name = data.get("file_name")
    password = data.get("password")

    file_info = files_download.get(file_name)
    if not file_info:
        return jsonify({"error": "File not found"}), 404

    real_pass = file_info.get("password")
    if real_pass and real_pass != password:
        return jsonify({"error": "Incorrect password"}), 403

    return jsonify({"message": "Access granted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18000)
