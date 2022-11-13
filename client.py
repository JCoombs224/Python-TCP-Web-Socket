from socket import *
import pickle
import os
import codecs

clientDir = os.getcwd()

serverName = 'localhost'
serverPort = 18000
DEFAULT_MESSAGE = {'PAYLOAD_LENGTH': 0, 'TCP_SYN_FLAG': 0, 'TCP_ACK_FLAG': 0, 'TCP_FIN_FLAG': 0, 'HTTP_GET_REQUEST': 0, 'HTTP_RESPONSE_STATUS_CODE': 0, 'HTTP_CLIENT_VERSION': 0, 'HTTP_REQUEST_PATH': 0, 'HTTP_INCLUDED_OBJECT_PATH': 0}



def main():
    while True:
        print("1. Get a file from the server")
        print("2. Quit the program")
        sel = input()

        if sel == '2':
            break
        if sel != '1':
            print("Invalid selection.\n")
            continue
        
        request = DEFAULT_MESSAGE
        request['PAYLOAD_LENGTH'] = 1
        request['TCP_SYN_FLAG'] = 1

        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))
        print("Connecting to the server.")
        clientSocket.send(pickle.dumps(request))
        print("TCP SYN request has been sent to the server.")
        response = pickle.loads(clientSocket.recv(1024))
        request['TCP_ACK_FLAG'] = 1
        clientSocket.send(pickle.dumps(request))
        print("Received TCP ACK from server. Sent a TCP ACK back to the server.")
        print("Connection established.\n")

        requestedFile = input("Enter the path of the file you would like to request from the server: ")
        payloadLength = len(requestedFile)

        print("1. Use HTTP version 1.0 (non-persistent)")
        print("2. Use HTTP version 1.1 (persistent)")
        sel = input()

        if sel == '1':
            httpVersion = 1.0
        elif sel == '2':
            httpVersion = 1.1
        else:
            print("Invalid selection.\n")
            continue

        request = {'PAYLOAD_LENGTH': payloadLength, 'TCP_SYN_FLAG': 0, 'TCP_ACK_FLAG': 0, 'TCP_FIN_FLAG': 0, 'HTTP_GET_REQUEST': 1, 'HTTP_RESPONSE_STATUS_CODE': 0, 'HTTP_CLIENT_VERSION': httpVersion, 'HTTP_REQUEST_PATH': requestedFile, 'HTTP_INCLUDED_OBJECT_PATH': 0}
        clientSocket.send(pickle.dumps(request))
        print("\nSent HTTP GET request for file.")

        response = pickle.loads(clientSocket.recv(1024))
        if response['HTTP_RESPONSE_STATUS_CODE'] == 200:
            print("\nServer sent response code: 200 OK")
            requestedFile = os.path.split(requestedFile)[1]
            fileData = clientSocket.recv(1024).decode() # Get file data from response
            file = open(requestedFile, "w")
            file.write(fileData)
            print("\nFile data:", fileData, "\n")
            file.close()
        elif response['HTTP_RESPONSE_STATUS_CODE'] == 404:
            print("\nServer sent response code: 404 PAGE NOT FOUND")
        
        # This will run if the server has an included object in the file requested
        # and will send another GET message the server for that file.
        if response['HTTP_INCLUDED_OBJECT_PATH'] != 0:
            requestedFile = response['HTTP_INCLUDED_OBJECT_PATH']
            if httpVersion == 1.0:
                request = DEFAULT_MESSAGE
                request['TCP_FIN_FLAG'] = 1
                clientSocket.send(pickle.dumps(request))
                print("\nSent TCP FIN message to the server.")
                response = pickle.loads(clientSocket.recv(1024))
                print("Received TCP FIN ACK from the server.")
                request['TCP_FIN_FLAG'] = 0
                clientSocket.send(pickle.dumps(request))
                print("Sent TCP ACK to the server.")
                clientSocket.close()
                print("Closed connection to the server")
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect((serverName,serverPort))
                print("Connecting to the server.")
                clientSocket.send(pickle.dumps(request))
                print("TCP SYN request has been sent to the server.")
                response = pickle.loads(clientSocket.recv(1024))
                request['TCP_ACK_FLAG'] = 1
                clientSocket.send(pickle.dumps(request))
                print("Received TCP ACK from server. Sent a TCP ACK back to the server.")
                print("Connection established.")
            
            # Send get request for the second file
            payloadLength = len(requestedFile)
            request = {'PAYLOAD_LENGTH': payloadLength, 'TCP_SYN_FLAG': 0, 'TCP_ACK_FLAG': 0, 'TCP_FIN_FLAG': 0, 'HTTP_GET_REQUEST': 1, 'HTTP_RESPONSE_STATUS_CODE': 0, 'HTTP_CLIENT_VERSION': httpVersion, 'HTTP_REQUEST_PATH': requestedFile, 'HTTP_INCLUDED_OBJECT_PATH': 0}
            clientSocket.send(pickle.dumps(request))
            print("\nSent HTTP GET request for file.")
            
            # Retrieve file data then print that file and save it
            response = pickle.loads(clientSocket.recv(1024))
            if response['HTTP_RESPONSE_STATUS_CODE'] == 200:
                print("\nServer sent response code: 200 OK")
                requestedFile = os.path.split(requestedFile)[1]
                print(requestedFile)
                fileData = clientSocket.recv(1024).decode("utf-8", "ignore") # Get file data from response
                file = codecs.open(requestedFile, "w")
                file.write(fileData)
                print("\nFile data:", fileData, "\n")
                file.close()
            elif response['HTTP_RESPONSE_STATUS_CODE'] == 404:
                print("\nServer sent response code: 404 PAGE NOT FOUND")
        
        request = DEFAULT_MESSAGE
        request['TCP_FIN_FLAG'] = 1
        clientSocket.send(pickle.dumps(request))
        print("Sent TCP FIN message to the server.")
        response = pickle.loads(clientSocket.recv(1024))
        print("Received TCP FIN ACK from the server.")
        request['TCP_FIN_FLAG'] = 0
        clientSocket.send(pickle.dumps(request))
        print("Sent TCP ACK to the server.")
        clientSocket.close()
        print("Closed connection to the server\n")
    

if __name__ == "__main__": # run main when starting program
    main()