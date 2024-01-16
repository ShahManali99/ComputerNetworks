import socket
import time

START_OF_PACKET_ID = 0xFFFF
END_OF_PACKET_ID = 0xFFFF
CLIENT_ID = 0x01
LENGTH = 0x05

PACKET_TYPE_DATA = 0xFFF1
PACKET_TYPE_ACK = 0xFFF2
PACKET_TYPE_REJECT = 0xFFF3

REJECT_OUT_OF_SEQUENCE = 0xFFF4
REJECT_LENGTH_MISMATCH = 0xFFF5
REJECT_END_OF_PACKET_MISSING = 0xFFF6
REJECT_DUPLICATE_PACKET = 0xFFF7

ACK_WAIT_TIME_SECONDS = 3
MAX_RETRIES = 3

serverAddressPort = ("127.0.0.1",20001)
bufferSize = 1024

# Function to send a packet
def send_packet(UDPClientSocket, packet, serverAddressPort):
    UDPClientSocket.sendto(packet, serverAddressPort)

# Function to receive a packet
def receive_packet(UDPClientSocket, bufferSize):
    packet, address = UDPClientSocket.recvfrom(bufferSize)
    return packet

def build_packet(start, clientId, packetType, sequenceNumber, end, payload):
    packet = bytearray()
    packet.extend(start.to_bytes(2, 'big'))
    packet.extend(clientId.to_bytes(1, 'big'))
    packet.extend(packetType.to_bytes(2, 'big'))
    packet.extend(sequenceNumber.to_bytes(1, 'big'))
    packet.extend(len(payload).to_bytes(1, 'big'))
    packet.extend(payload.encode())
    packet.extend(end.to_bytes(2, 'big'))

    print("-----")
    print("Start of packet identifier: ", hex(start))
    print("Client id: ", hex(clientId))
    print("Packet type: ", hex(packetType))
    print("Sequence number: ", sequence_number)
    print("Length: ", len(payload))
    print("Payload: ", payload)
    
    print("End of packet identifier: ", hex(end))
    print("----- \n")

    return packet

print("Create UDP Client")
# Create a UDP socket
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Packet sequence number
sequence_number = 0

# Send five correct packets to the server
for i in range(1, 6):
    # Construct the packet
    print('Sending packet ' + str(i))
    packet = build_packet(
        START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_DATA, sequence_number, END_OF_PACKET_ID,
        payload=('This is packet ' + str(i)))    

    # Send the packet
    send_packet(UDPClientSocket, packet, serverAddressPort)
    
    # Start the ACK timer
    ACK_TIMER = time.time()
    
    # Retry counter
    RETRY_CTR = 0

    while True:
        # Receive the ACK packet
        ack_packet = receive_packet(UDPClientSocket, bufferSize)
        
        # Check if the received packet is an ACK
        if len(ack_packet) == 9 and int.from_bytes(ack_packet[3:5], 'big') == PACKET_TYPE_ACK:
            received_sequence_number = int.from_bytes(ack_packet[5:6], 'big')
            
            # Check if the received ACK is for the current packet
            if received_sequence_number == sequence_number:
                print(f"Received ACK for packet {i} \n")
                sequence_number += 1
                break
        elif time.time() - ACK_TIMER > ACK_WAIT_TIME_SECONDS:
            RETRY_CTR += 1
            if RETRY_CTR > MAX_RETRIES:
                print("Server does not respond")
                break
            print(f"Timeout: Resending packet {i} (Retry {RETRY_CTR})")
            send_packet(UDPClientSocket, packet, serverAddressPort)
            ACK_TIMER = time.time()

# Now send one correct packet to server
print('Sending correct packet')
packet = build_packet(
        START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_DATA, sequence_number, END_OF_PACKET_ID,
        payload='This is correct packet.')
send_packet(UDPClientSocket, packet, serverAddressPort)
while True:
    # Receive the ACK packet
    ack_packet = receive_packet(UDPClientSocket, bufferSize)
    if len(ack_packet) == 9 and int.from_bytes(ack_packet[3:5], 'big') == PACKET_TYPE_ACK:
        received_sequence_number = int.from_bytes(ack_packet[5:6], 'big')
        
        # Check if the received ACK is for the current packet
        if received_sequence_number == sequence_number:
            print(f"Received ACK for correct packet \n")
            sequence_number += 1
            break

# Now send out of sequence error packet to server
print('Sending out of sequence packet')
error_sequence_number = 100
packet = build_packet(
    START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_DATA, error_sequence_number, END_OF_PACKET_ID,
    payload='This is out of sequence packet.')
send_packet(UDPClientSocket, packet, serverAddressPort)
while True:
    # Receive the REJECT packet
    reject_packet = receive_packet(UDPClientSocket, bufferSize)
    if len(reject_packet) == 10 and int.from_bytes(reject_packet[3:5], 'big') == PACKET_TYPE_REJECT:
        reject_reason = int.from_bytes(reject_packet[5:7], 'big')
        if (reject_reason == REJECT_OUT_OF_SEQUENCE):
            print("Received reject out of sequence error packet from server \n")
            break

# Now send the length mismatch packet to server
print('Sending packet with length mismatch')
packet = build_packet(
        START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_DATA, sequence_number, END_OF_PACKET_ID,
        payload='This is a packet with length mismatch.')
invalid_length = 100
packet[6:7] = invalid_length.to_bytes(1, 'big')
print("Invalid length: ", invalid_length)
send_packet(UDPClientSocket, packet, serverAddressPort)
while True:
    # Receive the REJECT packet
    reject_packet = receive_packet(UDPClientSocket, bufferSize)
    if len(reject_packet) == 10 and int.from_bytes(reject_packet[3:5], 'big') == PACKET_TYPE_REJECT:
        reject_reason = int.from_bytes(reject_packet[5:7], 'big')
        if (reject_reason == REJECT_LENGTH_MISMATCH):
            print("Received reject packet with length mismatch error \n")
            break
 
 
# Now send the unexpected end of packet identifier packet to server
print('Sending packet with unexpected end of packet identifier')
unexpected_end_of_packet_id = 0xFFF0
packet = build_packet(
    START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_DATA, sequence_number, unexpected_end_of_packet_id,
    payload='This is a packet with unexpected end of packet identifier.')
send_packet(UDPClientSocket, packet, serverAddressPort)
while True:
    # Receive the REJECT packet
    reject_packet = receive_packet(UDPClientSocket, bufferSize)
    if len(reject_packet) == 10 and int.from_bytes(reject_packet[3:5], 'big') == PACKET_TYPE_REJECT:
        reject_reason = int.from_bytes(reject_packet[5:7], 'big')
        if (reject_reason == REJECT_END_OF_PACKET_MISSING):
            print("Received reject packet with end of packet missing from server \n")
            break

# Now send the packet with duplicate sequence number to server
print('Sending packet with duplicate sequence number')
duplicate_sequence_number = sequence_number - 1
packet = build_packet(
    START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_DATA, duplicate_sequence_number, END_OF_PACKET_ID,
    payload='This is a packet with duplicate sequence number.')
send_packet(UDPClientSocket, packet, serverAddressPort)
while True:
    # Receive the REJECT packet
    new_reject_packet = receive_packet(UDPClientSocket, bufferSize)
    if len(new_reject_packet) == 10 and int.from_bytes(new_reject_packet[3:5], 'big') == PACKET_TYPE_REJECT:
        new_reject_reason = int.from_bytes(new_reject_packet[5:7], 'big')
        if (new_reject_reason == REJECT_DUPLICATE_PACKET):
            print("Received reject packet with duplicate sequence number error from server \n")
            break

# Close the socket
UDPClientSocket.close()

