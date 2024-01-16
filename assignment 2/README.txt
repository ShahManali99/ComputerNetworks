Client and server using customized protocol on top of UDP protocol for requesting identification from server 
for access permission to the network.

1. First run the server using python3 assignment2_server.py. The server will bind to the socket and wait for any requests.
2. Now, in a new terminal window, run the client using python3 assignment2_client.py. 
The client will send the packets to the server
You can observe the output after that in both the client and the server. Following cases are covered:
a. Subscriber does not exist.
b. Subscriber exists, but technology does not match the database.
c. Subscriber has not paid.
d. Subscriber permitted access to the network.

In order to add/modify the packets in the client, you can change the contents of input.txt which contains 
the source subscriber number and technology used.
You can also edit the verification_database.txt on the server side which contains the source subscriber number,
technology used and the paid/not paid status.
