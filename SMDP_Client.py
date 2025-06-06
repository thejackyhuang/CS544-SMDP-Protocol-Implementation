"""
SMDP_Client.py
Simulates a smart IoT device that connects to an SMDP server to register itself and send state updates.

Usage:
    python SMDP_Client.py --host <server_host> --port <server_port> [--uuid <id>] [--fw <version>] [--state <0|1>]
"""

import socket
import argparse
import time
from SMDP_Protocol import *

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="SMDP Device Client")
    parser.add_argument('--host', required=True, help='Hostname or IP address of the server (required)')
    parser.add_argument('--port', type=int, required=True, help='Port number of the server (required)')
    parser.add_argument('--uuid', default="abc123", help='Device UUID (default: abc123)')
    parser.add_argument('--fw', default="v1.0", help='Firmware version (default: v1.0)')
    parser.add_argument('--state', type=int, default=1, help='Initial state (0=off, 1=on)')
    args = parser.parse_args()

    server_addr = (args.host, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # Set timeout for responses (2 seconds)

    # Step 1: Send registration packet to the server
    register = create_register_packet(args.uuid, args.state, args.fw)
    sock.sendto(register, server_addr)
    print(f"[CLIENT] Sent registration for {args.uuid} to {args.host}:{args.port}")

    try:
        # Wait for ACK from server
        resp, _ = sock.recvfrom(1024)
        msg_type, msg = parse_packet(resp)
        if msg_type == MSG_ACK and msg["acked_type"] == MSG_DEVICE_REGISTER:
            print(f"[CLIENT] Registration ACK received: status={msg['status']}")
    except socket.timeout:
        print("[CLIENT] No ACK received (timeout)")

    # Step 2: Simulate a device state change (e.g., turning off manually)
    time.sleep(1)
    state = create_state_packet(args.uuid, 0x00, "manual_off")
    sock.sendto(state, server_addr)
    print(f"[CLIENT] Sent state update: manual_off")

    sock.close()


if __name__ == "__main__":
    main()
