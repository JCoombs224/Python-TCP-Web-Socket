from socket import *
import pickle
import os
import codecs
import time

DEFAULT_MESSAGE = {'PAYLOAD_LENGTH': 0, 'TCP_SYN_FLAG': 0, 'TCP_ACK_FLAG': 0, 'TCP_FIN_FLAG': 0, 'HTTP_GET_REQUEST': 0, 'HTTP_RESPONSE_STATUS_CODE': 0, 'HTTP_CLIENT_VERSION': 0, 'HTTP_REQUEST_PATH': 0, 'HTTP_INCLUDED_OBJECT_PATH': 0}
serverDir = os.getcwd()

serverPort = 18000

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

# Sends a requested file with a given response and connection socket
def sendFile(request, response, connectionSocket):
    httpClientVersion = request['HTTP_CLIENT_VERSION']
    try:
        file = codecs.open(request['HTTP_REQUEST_PATH'], 'r')
        fileData = file.read()
        response['HTTP_CLIENT_VERSION'] = httpClientVersion
        response['HTTP_RESPONSE_STATUS_CODE'] = 200
        connectionSocket.send(pickle.dumps(response))
        connectionSocket.send(fileData.encode())
        print("File data has been sent to the client.\n")
        file.close()

    except IOError: # File not found send a 404
        response['HTTP_CLIENT_VERSION'] = httpClientVersion
        response['HTTP_RESPONSE_STATUS_CODE'] = 404
        connectionSocket.send(pickle.dumps(response))
        print("File was not found in local directory. Sending a message with HTTP RESPONSE CODE 404.\n")

# Main Program
def main():
    print ('The server is ready to receive')
    while 1:
        # Initialize connection socket from server when client requests connection
        connectionSocket, addr = serverSocket.accept() 

        # Begin TCP SYN process
        request = pickle.loads(connectionSocket.recv(2048))
        print("TCP SYN message received from the client.")
        response = request
        response['TCP_ACK_FLAG'] = 1
        connectionSocket.send(pickle.dumps(response))
        print("TCP SYN ACK message sent to client. Waiting for TCP ACK message from the client.")

        request = pickle.loads(connectionSocket.recv(2048))
        print("Received TCP ACK from client. Connection established.\n")
        # Connection is now established after TCP SYN process

        # Wait for request from client
        request = pickle.loads(connectionSocket.recv(2048))
        response = DEFAULT_MESSAGE

        print("HTTP GET request received from the client.")
        # Check if the requested file has any included objects that would need to be sent as well
        if request['HTTP_REQUEST_PATH'] == 'attachments/file2.html': 
            response['HTTP_INCLUDED_OBJECT_PATH'] = 'attachments/file3.html' # If so add that file to the included objects flag
        else:
            response['HTTP_INCLUDED_OBJECT_PATH'] = 0
        
        # Send original file that was requested
        sendFile(request, response, connectionSocket)

        # In the future this could be made into a loop until the file sent does not have any additional included objects
        if response['HTTP_INCLUDED_OBJECT_PATH'] != 0:
            if request['HTTP_CLIENT_VERSION'] == '1.0':
                print("Received TCP FIN message from client")
                response = request
                response['TCP_ACK_FLAG'] = 1
                print("Sending TCP FIN ACK message to the client.")
                connectionSocket.send(pickle.dumps(response))
                request = pickle.loads(connectionSocket.recv(2048))
                print("TCP ACK received. Connection closed...\n")
                connectionSocket.close()

                connectionSocket, addr = serverSocket.accept()
                request = pickle.loads(connectionSocket.recv(2048))
                print("TCP SYN message received from the client.")
                response = request
                response['TCP_ACK_FLAG'] = 1
                connectionSocket.send(pickle.dumps(response))
                print("TCP ACK message sent to client. Waiting for TCP ACK message from the client.")

                request = pickle.loads(connectionSocket.recv(2048))
                print("Received TCP ACK from client. Connection established.\n")

            response = DEFAULT_MESSAGE
            request = pickle.loads(connectionSocket.recv(2048))
            print("HTTP GET request received from the client.")

            # Send additional file from HTTP_INCLUDED_OBJECT_PATH
            sendFile(request, response, connectionSocket)

        # Send final TCP FIN messages and close connection socket
        print("Received TCP FIN message from client.")
        response = request
        response['TCP_ACK_FLAG'] = 1
        print("Sending TCP FIN ACK message to the client.")
        connectionSocket.send(pickle.dumps(response))
        request = pickle.loads(connectionSocket.recv(2048))
        print("TCP ACK received. Connection closed...\n")
        connectionSocket.close()

if __name__ == "__main__": # run main when starting program
    main()