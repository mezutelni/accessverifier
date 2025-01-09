import ipaddress
import threading
import time
import logging
import sys
from flask import Flask, request, jsonify
import requests


logger = logging.getLogger(__name__)

app = Flask(__name__)

allowed_ips = []


class Config:
    # Those should be loaded from ENV
    allowed_ip_list_endpoint = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    allowed_region = "eu-central-1"
    logging_level = "debug"

    def __init__(self, **kwargs):
        # Allow overriding defaults using keyword arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Unknown configuration attribute: {key}")


def fetch_allowed_ips(list_endpoint, allowed_region):
    global allowed_ips
    allowed_ips = []
    # Main loop for background job
    while True:
        try:
            response = requests.get(list_endpoint, timeout=30)
        except requests.exceptions.Timeout:
            logger.critical(f"Target {list_endpoint} timed out")
        except requests.exceptions.RequestException as e:
            logger.critical(
                f"Couldn't fetch allowed IP list\nRequest error - {e}")
            sys.exit(1)
        try:
            response_json = response.json()
            logger.debug(
                f"Started processing prefixes from {list_endpoint} allowed region {allowed_region}")
            for block in response_json["prefixes"]:
                if allowed_region in block["region"].lower():
                    allowed_ips.append(block["ip_prefix"])
                    logger.debug(
                        f"Added {block['ip_prefix']} to allowed IPs list")
        except Exception as e:
            logger.critical(f"Error parsing data - {e}")

        logger.info(f"Allowed IPs {allowed_ips}")

        logger.info("Job finished sucessfully, sleeping for 86400 seconds")
        time.sleep(86400)


def is_allowed(client_ip):
    # Convert string to python ipaddress object
    client_ip_address = ipaddress.ip_address(client_ip)
    for ip_prefix in allowed_ips:
        # Convert current prefix into temporary ipaddress object
        allowed_ip_prefix = ipaddress.ip_network(ip_prefix)
        if client_ip_address in allowed_ip_prefix:
            return True
    return False


@app.route('/authroize', methods=['POST'])
def authorize():
    client_ip = request.headers.get(
        'X-Forwarded-For', '').split(',')[0].strip()
    logger.info(f"Received IP: {client_ip}")
    if not client_ip:
        return jsonify({'error': 'No IP provided'}), 401
    if is_allowed(client_ip):
        return jsonify({'status': 'OK'}), 200
    else:
        return jsonify({'status': 'Unauthorized'}), 401


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=Config.logging_level.upper())
    logger.info("Starting background job")
    background_thread = threading.Thread(target=fetch_allowed_ips, args=(
        Config.allowed_ip_list_endpoint, Config.allowed_region), daemon=True)
    background_thread.start()
    logger.info("Starting webserver")
    app.run(host='0.0.0.0', port=8080)
