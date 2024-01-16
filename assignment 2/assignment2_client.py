import socket
import time
import re
import math

START_OF_PACKET_ID = 0xFFFF
END_OF_PACKET_ID = 0xFFFF
CLIENT_ID = 0x01

PACKET_TYPE_ACC_PER = 0xFFF8
PACKET_TYPE_NOT_PAID = 0xFFF9
PACKET_TYPE_NOT_EXIST = 0xFFFA
PACKET_TYPE_ACCESS_OK = 0xFFFB
TECHNOLOGY_2G = 0x02
TECHNOLOGY_3G = 0x03
TECHNOLOGY_4G = 0x04
TECHNOLOGY_5G = 0x05

ACK_WAIT_TIME_SECONDS = 3
MAX_RETRIES = 3

serverAddressPort = ("127.0.0.1",20001)
bufferSize = 1024
segmentNumber = 1

# Function to send a packet
def send_packet(UDPClientSocket, packet, serverAddressPort):
    UDPClientSocket.sendto(packet, serverAddressPort)

# Function to receive a packet
def receive_packet(UDPClientSocket, bufferSize):
    packet, address = UDPClientSocket.recvfrom(bufferSize)
    return packet

def build_packet(start, clientId, packetType, segmentNumber, technology, sourceSubscriberNumber, end):
    length = math.ceil(sourceSubscriberNumber.bit_length()/8.0) + math.ceil(technology.bit_length()/8.0)
    packet = bytearray()
    packet.extend(start.to_bytes(2, 'big'))
    packet.extend(clientId.to_bytes(1, 'big'))
    packet.extend(packetType.to_bytes(2, 'big'))
    packet.extend(segmentNumber.to_bytes(1, 'big'))
    packet.extend(length.to_bytes(1, 'big'))
    packet.extend(technology.to_bytes(1, 'big'))
    packet.extend(sourceSubscriberNumber.to_bytes(5, 'big'))
    packet.extend(end.to_bytes(2, 'big'))

    print("-----")
    print("Start of packet identifier: ", hex(start))
    print("Client id: ", hex(clientId))
    print("Packet type: ", hex(packetType))
    print("Segment number: ", segmentNumber)
    print("Length: ", length)
    print("Technology: ", technology)
    print("Source Subscriber Number: ", sourceSubscriberNumber)
    print("End of packet identifier: ", hex(end))
    print("----- \n")

    return packet

print("Create UDP Client")
# Create a UDP socket
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

with open('input.txt') as f:
    for line in f:
        sourceSubscriberNumber, technology = line.strip().split()
        formattedSourceSubscriberNumber = int(re.sub("-", "", sourceSubscriberNumber))
        formattedTechnology = int(technology)

        # Send access permission request packet to the server
        print('Sending access permission request packet ')
        access_request_packet = build_packet(START_OF_PACKET_ID, CLIENT_ID, PACKET_TYPE_ACC_PER, segmentNumber, 
                              formattedTechnology, formattedSourceSubscriberNumber, END_OF_PACKET_ID)
        send_packet(UDPClientSocket, access_request_packet, serverAddressPort)

        # Start the ACK timer
        ACK_TIMER = time.time()
    
        # Retry counter
        RETRY_CTR = 0

        while True:
            # Receive the response packet
            response_packet = receive_packet(UDPClientSocket, bufferSize)
            if len(response_packet) == 15 and int.from_bytes(response_packet[3:5], 'big') == PACKET_TYPE_NOT_EXIST:
                print("Status: Access not granted. Subscriber does not exist \n")
                break
            elif  len(response_packet) == 15 and int.from_bytes(response_packet[3:5], 'big') == PACKET_TYPE_NOT_PAID:
                print("Status: Access not granted. Subscriber has not paid \n")
                break
            elif  len(response_packet) == 15 and int.from_bytes(response_packet[3:5], 'big') == PACKET_TYPE_ACCESS_OK:
                print("Status: Permitted to access the network \n")
                break
            elif time.time() - ACK_TIMER > ACK_WAIT_TIME_SECONDS:
                RETRY_CTR += 1
                if RETRY_CTR > MAX_RETRIES:
                    print("Status: Server does not respond \n")
                    break
                print(f"Timeout: Resending packet {segmentNumber} (Retry {RETRY_CTR})")
                send_packet(UDPClientSocket, access_request_packet, serverAddressPort)
                ACK_TIMER = time.time()

# Close the socket
UDPClientSocket.close()

