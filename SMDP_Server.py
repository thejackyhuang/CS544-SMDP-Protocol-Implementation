"""
SMDP_Server.py
Implements the Smart Device Management Protocol (SMDP) server. Acts as a central hub that listens for device messages
(register, state updates) over UDP and responds accordingly.

Usage:
    python SMDP_Server.py [--port 5555]
"""

import socket
import time
import argparse
from SMDP_Protocol import *

DEFAULT_PORT = 5555  # Default listening port

def main():
    # Parse command-line arguments for port configuration
    parser = argparse.ArgumentParser(description="SMDP Server (Hub)")
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to listen on (default: 5555)')
    args = parser.parse_args()

    # Dictionary to store device info keyed by UUID
    devices = {}

    # Create UDP socket and bind to all interfaces on specified port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', args.port))
    print(f"[SMDP Server] Listening on port {args.port}...")

    # Main server loop: waits for and processes incoming messages
    while True:
        data, addr = sock.recvfrom(1024)  # Receive packet from any client

        try:
            msg_type, msg = parse_packet(data)
        except Exception as e:
            print(f"[ERROR] Could not parse message from {addr}: {e}")
            continue

        if msg_type == MSG_DEVICE_REGISTER:
            # Handle device registration
            uuid = msg["device_uuid"]
            print(f"[REGISTER] Device {uuid} (fw {msg['firmware']}) state={msg['state']}")
            devices[uuid] = {
                "firmware": msg["firmware"],
                "state": msg["state"],
                "last_seen": time.time()
            }
            # Send ACK back to device
            ack = create_ack_packet(MSG_DEVICE_REGISTER, uuid, 0x00)
            sock.sendto(ack, addr)

        elif msg_type == MSG_DEVICE_STATE:
            # Handle device state update
            uuid = msg["device_id"]
            print(f"[STATE] {uuid} → code={msg['state_code']} data='{msg['state_data']}'")
            if uuid in devices:
                devices[uuid]["state"] = msg["state_code"]
                devices[uuid]["last_seen"] = time.time()

        elif msg_type == MSG_ACK:
            # Handle receipt of an ACK from device (not typically required)
            print(f"[ACK] {msg['device_id']} for type {msg['acked_type']} status={msg['status']}")

        else:
            # Unknown or unsupported message type
            print(f"[UNKNOWN] Unknown message type {msg_type} from {addr}")


if __name__ == "__main__":
    main()
