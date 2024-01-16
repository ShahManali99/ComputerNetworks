import socket

# Constants
START_OF_PACKET_ID = 0xFFFF
END_OF_PACKET_ID = 0xFFFF
PACKET_TYPE_DATA = 0xFFF1
PACKET_TYPE_ACK = 0xFFF2
PACKET_TYPE_REJECT = 0xFFF3
REJECT_OUT_OF_SEQUENCE = 0xFFF4
REJECT_LENGTH_MISMATCH = 0xFFF5
REJECT_END_OF_PACKET_MISSING = 0xFFF6
REJECT_DUPLICATE_PACKET = 0xFFF7

bufferSize  = 1024
localIP = "127.0.0.1"
localPort = 20001
clientAddressPort = (localIP, localPort)

# Function to send a packet
def send_packet(UDPServerSocket, packet, clientAddressPort):
    UDPServerSocket.sendto(packet, clientAddressPort)

# Function to receive a packet
def receive_packet(UDPServerSocket, bufferSize):
    packet, clientAddressPort = UDPServerSocket.recvfrom(bufferSize)
    return packet, clientAddressPort

def build_reject_packet(start, clientId, packetType, rejectReason, length, end):
    reject_packet = bytearray()
    reject_packet.extend(start.to_bytes(2, 'big'))
    reject_packet.extend(clientId.to_bytes(1, 'big'))
    reject_packet.extend(packetType.to_bytes(2, 'big'))
    reject_packet.extend(rejectReason.to_bytes(2, 'big'))
    reject_packet.extend(length.to_bytes(1, 'big'))
    reject_packet.extend(end.to_bytes(2, 'big'))
    return reject_packet

def build_ack_packet(start, clientId, packetType, sequenceNumber, length, end):
    ack_packet = bytearray()
    ack_packet.extend(start.to_bytes(2, 'big'))
    ack_packet.extend(clientId.to_bytes(1, 'big'))
    ack_packet.extend(packetType.to_bytes(2, 'big'))
    ack_packet.extend(sequenceNumber.to_bytes(1, 'big'))
    ack_packet.extend(length.to_bytes(1, 'big'))
    ack_packet.extend(end.to_bytes(2, 'big'))
    return ack_packet

# Create a UDP socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("Created UDP Server")
# Expected sequence number
expected_sequence_number = 0

while True:
    # Receive a packet from the client
    packet, clientAddressPort = receive_packet(UDPServerSocket, bufferSize)
    print("Packet received")
    
    # Check if it's a valid packet
    if len(packet) < 12:
        print("Received invalid packet")
        continue
    
    # Extract packet fields
    start_of_packet_id = int.from_bytes(packet[0:2], 'big')
    client_id = int.from_bytes(packet[2:3], 'big')
    packet_type = int.from_bytes(packet[3:5], 'big')
    sequence_number = int.from_bytes(packet[5:6], 'big')
    length = int.from_bytes(packet[6:7], 'big')
    payload = packet[7:len(packet)-2]
    end_of_packet_id= int.from_bytes(packet[len(packet)-2:len(packet)], 'big')
    print("------")
    print("Start of packet id: ", hex(start_of_packet_id))
    print("Client id: ", hex(client_id))
    print("Packet type: ", hex(packet_type))
    print("Seq number: ", sequence_number)
    print("Length: ", length)
    print("Payload: ", payload.decode())
    print("End of packet id: ", hex(end_of_packet_id))
    print("------ \n")
    
    # # Check start and end of packet identifiers
    # if start_of_packet_id != START_OF_PACKET_ID or end_of_packet_id != END_OF_PACKET_ID:
    #     print("Received packet with invalid start or end of packet identifier")
    #     continue
    
    # Check if the packet is in sequence
    if sequence_number > expected_sequence_number:
        print(f"Received packet out of sequence: expected {expected_sequence_number}, received {sequence_number}")
        reject_packet = build_reject_packet(
            START_OF_PACKET_ID, client_id, PACKET_TYPE_REJECT, REJECT_OUT_OF_SEQUENCE, length, END_OF_PACKET_ID)
        send_packet(UDPServerSocket,reject_packet,clientAddressPort)
        continue
    
    # Check packet length
    if len(payload) != length:
        print("Received packet with length mismatch")
        reject_packet = build_reject_packet(
            START_OF_PACKET_ID, client_id, PACKET_TYPE_REJECT, REJECT_LENGTH_MISMATCH, length, END_OF_PACKET_ID)
        send_packet(UDPServerSocket, reject_packet, clientAddressPort)
        continue
    
    # Check end of packet identifier
    if end_of_packet_id != END_OF_PACKET_ID:
        print("Received packet with missing end of packet identifier")
        reject_packet = build_reject_packet(
            START_OF_PACKET_ID, client_id, PACKET_TYPE_REJECT, REJECT_END_OF_PACKET_MISSING, length, END_OF_PACKET_ID)
        send_packet(UDPServerSocket, reject_packet, clientAddressPort)
        continue
    
    # Check for duplicate packet
    if sequence_number < expected_sequence_number:
        print(f"Received duplicate packet: sequence number {sequence_number}")
        reject_packet = build_reject_packet(
            START_OF_PACKET_ID, client_id, PACKET_TYPE_REJECT, REJECT_DUPLICATE_PACKET, length, END_OF_PACKET_ID)
        send_packet(UDPServerSocket, reject_packet, clientAddressPort)
        continue
    
    # Process the valid packet
    print(f"Received packet {sequence_number+1} from client: {payload.decode()}")
    expected_sequence_number += 1
    
    # Send ACK packet
    ack_packet = build_ack_packet(
        START_OF_PACKET_ID, client_id, PACKET_TYPE_ACK, sequence_number, length, END_OF_PACKET_ID)
    send_packet(UDPServerSocket, ack_packet, clientAddressPort)