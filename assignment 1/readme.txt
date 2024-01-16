Client and server using customized protocol on top of UDP protocol for sending information to the server.

1. First run the server using python3 assignment1_server.py. The server will bind to the socket and wait for any requests.
2. Now, in a new terminal window, run the client using python3 assignment1_client.py. 

The client will send the packets to the server
You can observe the output after that in both the client and the server. Following cases are covered:
1. Client sending packets 1 to 5 and server responding with ACK packet for each.
2. Client sending correct packet and server responding with ACK packet for each.
3. Client sending out of sequence packet and server responding with REJECT packet.
4. Client sending packet with length field not matching length of payload and server responding with REJECT packet.
5. Client sending packet with invalid end of packet id and server responding with REJECT packet.
6. Client sending packet with duplicate sequence number and server responding with REJECT packet.


