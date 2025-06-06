"""
SMDP_Protocol.py
Defines the message types and binary encoding/decoding functions for the Smart Device Management Protocol (SMDP).
Each message is transmitted using a fixed binary format consisting of a 4-byte header and a structured payload.

Author: Jacky Huang
Date: 06/02/25
"""

import struct

# Message type constants (2 bytes each)
MSG_DEVICE_REGISTER = 0x0001
MSG_DEVICE_STATE    = 0x0002
MSG_COMMAND_EXEC    = 0x0003
MSG_ACK             = 0x0004

# Header format: 2-byte message type + 2-byte payload length
HEADER_FORMAT = "!HH"  # Network byte order

# Payload formats for each message type
REGISTER_FORMAT = "!16sB8s"   # UUID (16 bytes), state (1 byte), firmware (8 bytes)
STATE_FORMAT    = "!16sB8s"   # UUID (16 bytes), state code (1 byte), state data (8 bytes)
ACK_FORMAT      = "!B16sB"    # Acknowledged msg type (1 byte), UUID (16 bytes), status (1 byte)

# ----------------------
# Message Creation APIs
# ----------------------

def create_register_packet(uuid, state, firmware):
    """
    Create a MSG_DEVICE_REGISTER packet.

    Args:
        uuid (str): Device UUID.
        state (int): Device state (0 or 1).
        firmware (str): Firmware version (max 8 characters).

    Returns:
        bytes: Encoded register message packet.
    """
    payload = create_payload(REGISTER_FORMAT, uuid, state, firmware)
    return create_packet(MSG_DEVICE_REGISTER, payload)

def create_state_packet(uuid, state_code, state_data):
    """
    Create a MSG_DEVICE_STATE packet.

    Args:
        uuid (str): Device UUID.
        state_code (int): State code (0 or 1).
        state_data (str): Description of state data.

    Returns:
        bytes: Encoded state message packet.
    """
    payload = create_payload(STATE_FORMAT, uuid, state_code, state_data)
    return create_packet(MSG_DEVICE_STATE, payload)

def create_ack_packet(acked_type, uuid, status):
    """
    Create a MSG_ACK packet.

    Args:
        acked_type (int): Message type being acknowledged.
        uuid (str): Device UUID.
        status (int): Acknowledgment status (0x00 = success, 0xFF = failure).

    Returns:
        bytes: Encoded acknowledgment packet.
    """
    payload = create_payload(ACK_FORMAT, acked_type, uuid, status)
    return create_packet(MSG_ACK, payload)

# ---------------------
# Message Parsing Logic
# ---------------------

def parse_packet(packet):
    """
    Parse an incoming packet into a structured dictionary.

    Args:
        packet (bytes): Full UDP packet received.

    Returns:
        tuple: (message_type, parsed_dict)
    """
    msg_type, length = struct.unpack(HEADER_FORMAT, packet[:4])
    payload = packet[4:]

    if msg_type == MSG_DEVICE_REGISTER:
        uuid, state, fw = struct.unpack(REGISTER_FORMAT, payload)
        return msg_type, {
            "device_uuid": uuid.decode().strip('\x00'),
            "state": state,
            "firmware": fw.decode().strip('\x00')
        }

    elif msg_type == MSG_DEVICE_STATE:
        uuid, code, data = struct.unpack(STATE_FORMAT, payload)
        return msg_type, {
            "device_id": uuid.decode().strip('\x00'),
            "state_code": code,
            "state_data": data.decode(errors="ignore").strip('\x00')
        }

    elif msg_type == MSG_ACK:
        acked_type, uuid, status = struct.unpack(ACK_FORMAT, payload)
        return msg_type, {
            "acked_type": acked_type,
            "device_id": uuid.decode().strip('\x00'),
            "status": status
        }

    return msg_type, { "raw_payload": payload }

# -----------------------
# Internal Helpers
# -----------------------

def create_packet(msg_type, payload_bytes):
    """
    Assemble a packet from message type and payload.

    Args:
        msg_type (int): Message type identifier.
        payload_bytes (bytes): Binary payload.

    Returns:
        bytes: Full packet including header.
    """
    header = struct.pack(HEADER_FORMAT, msg_type, len(payload_bytes))
    return header + payload_bytes

def create_payload(fmt, *args):
    """
    Encode payload fields according to struct format.

    Args:
        fmt (str): Struct format string.
        *args: Payload field values (strings are auto-padded).

    Returns:
        bytes: Packed payload.
    """
    encoded_args = []
    for arg in args:
        if isinstance(arg, str):
            size = int(fmt[fmt.find('s') - 1])  # Extract size from format
            encoded_args.append(arg.ljust(size, '\x00').encode())  # Pad with nulls
        else:
            encoded_args.append(arg)
    return struct.pack(fmt, *encoded_args)
