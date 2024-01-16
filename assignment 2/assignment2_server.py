import socket
import re

# Constants
START_OF_PACKET_ID = 0xFFFF
END_OF_PACKET_ID = 0xFFFF
PACKET_TYPE_ACC_PER = 0xFFF8
PACKET_TYPE_NOT_PAID = 0xFFF9
PACKET_TYPE_NOT_EXIST = 0xFFFA
PACKET_TYPE_ACCESS_OK = 0xFFFB

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

def build_response_packet(start, clientId, packetType, segmentNumber, length, technology, sourceSubscriberNumber, end):
    reject_packet = bytearray()
    reject_packet.extend(start.to_bytes(2, 'big'))
    reject_packet.extend(clientId.to_bytes(1, 'big'))
    reject_packet.extend(packetType.to_bytes(2, 'big'))
    reject_packet.extend(segmentNumber.to_bytes(1, 'big'))
    reject_packet.extend(length.to_bytes(1, 'big'))
    reject_packet.extend(technology.to_bytes(1, 'big'))
    reject_packet.extend(sourceSubscriberNumber.to_bytes(5, 'big'))
    reject_packet.extend(end.to_bytes(2, 'big'))
    return reject_packet

# Create a UDP socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("Created UDP Server")
# Expected segment number
expected_segment_number = 0

# Read the verification database file
database = {}
with open('Verification_Database.txt', 'r') as file:
    lines = file.readlines()
    for line in lines:
        subscriber_no, technology, paid = line.strip().split()
        formatted_subscriber_no = int(re.sub("-", "", subscriber_no))
        database[formatted_subscriber_no] = {'technology': int(technology), 'paid': int(paid)}

while True:
    # Receive a packet from the client
    packet, clientAddressPort = receive_packet(UDPServerSocket, bufferSize)
    print("Packet received")
    
    # Check if it's a valid packet
    if len(packet) < 15:
        print("Received invalid packet")
        continue
    
    # Extract packet fields
    start_of_packet_id = int.from_bytes(packet[0:2], 'big')
    client_id = int.from_bytes(packet[2:3], 'big')
    packet_type = int.from_bytes(packet[3:5], 'big')
    segment_number = int.from_bytes(packet[5:6], 'big')
    length = int.from_bytes(packet[6:7], 'big')
    technology = int.from_bytes(packet[7:8], 'big')
    sourceSubscriberNumber = int.from_bytes(packet[8:13], 'big')
    end_of_packet_id= int.from_bytes(packet[len(packet)-2:len(packet)], 'big')
    
    print("--------")
    print("Start of packet id: ", hex(start_of_packet_id))
    print("Client id: ", hex(client_id))
    print("Packet type: ", hex(packet_type))
    print("Segment number:", segment_number)
    print("Length:", length)
    print("Technology: ", technology)
    print("Source Subscriber Number: ", sourceSubscriberNumber)
    print("end of packet id:", hex(end_of_packet_id))
    print("--------")

    if start_of_packet_id == START_OF_PACKET_ID and end_of_packet_id == END_OF_PACKET_ID:
        if packet_type == PACKET_TYPE_ACC_PER:
            if sourceSubscriberNumber in database:
                if technology == database[sourceSubscriberNumber]['technology']:
                    if database[sourceSubscriberNumber]['paid'] == 1:
                        print("Granting access because subscriber permitted to access the network. \n")
                        # Subscriber permitted to access the network message.
                        response_packet = build_response_packet(START_OF_PACKET_ID, client_id, PACKET_TYPE_ACCESS_OK, 
                                              segment_number, length, technology, sourceSubscriberNumber, END_OF_PACKET_ID)
                        send_packet(UDPServerSocket, response_packet, clientAddressPort)
                    else:
                        print("Denying access because subscriber has not paid. \n")
                        # Subscriber has not paid message.
                        response_packet = build_response_packet(START_OF_PACKET_ID, client_id, PACKET_TYPE_NOT_PAID, 
                                              segment_number, length, technology, sourceSubscriberNumber, END_OF_PACKET_ID)
                        send_packet(UDPServerSocket, response_packet, clientAddressPort)
                else:
                    print("Denying access because subscriber number found, but technology does not match. \n")
                    # Subscriber number found, but technology does not match.
                    response_packet = build_response_packet(
                        START_OF_PACKET_ID, client_id, PACKET_TYPE_NOT_EXIST, segment_number, length, technology, 
                        sourceSubscriberNumber, END_OF_PACKET_ID)
                    send_packet(UDPServerSocket, response_packet, clientAddressPort)
            else:
                print("Denying access because subscriber not found. \n")
                # Subscriber number not found
                response_packet = build_response_packet(
                    START_OF_PACKET_ID, client_id, PACKET_TYPE_NOT_EXIST, segment_number, length, 
                    technology, sourceSubscriberNumber, END_OF_PACKET_ID)
                send_packet(UDPServerSocket, response_packet, clientAddressPort)
        else:
            # Invalid packet type
            print("Received unknown packet type. \n")
    else:
        # Invalid packet
        print("Received invalid packet. \n")

UDPServerSocket.close()