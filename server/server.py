from socket import *
import pickle
import os

DEFAULT_MESSAGE = {'PAYLOAD_LENGTH': 0, 'TCP_SYN_FLAG': 0, 'TCP_ACK_FLAG': 0, 'TCP_FIN_FLAG': 0, 'HTTP_GET_REQUEST': 0, 'HTTP_RESPONSE_STATUS_CODE': 0, 'HTTP_CLIENT_VERSION': 0, 'HTTP_REQUEST_PATH': 0, 'HTTP_INCLUDED_OBJECT_PATH': 0}
serverDir = os.getcwd()

serverPort = 18000

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

print ('The server is ready to receive')
while 1:
    connectionSocket, addr = serverSocket.accept()
    request = pickle.loads(connectionSocket.recv(1024))
    response = request
    response['TCP_ACK_FLAG'] = 1
    connectionSocket.send(pickle.dumps(response))
    print("TCP ACK message sent to client. Waiting for TCP ACK message from the client.")

    request = pickle.loads(connectionSocket.recv(1024))
    print("Received TCP ACK from client. Connection established.")
    httpClientVersion = request['HTTP_CLIENT_VERSION']
    
    request = pickle.loads(connectionSocket.recv(1024))
    response = DEFAULT_MESSAGE
    try:
        file = open(request['HTTP_REQUEST_PATH'], "r")
        fileData = file.read()
        response['HTTP_CLIENT_VERSION'] = httpClientVersion
        response['HTTP_RESPONSE_STATUS_CODE'] = 200
        connectionSocket.send(pickle.dumps(response))
        connectionSocket.send(fileData.encode())


    except IOError: # File not found send a 404
        response['HTTP_CLIENT_VERSION'] = httpClientVersion
        response['HTTP_RESPONSE_STATUS_CODE'] = 404
        connectionSocket.send(pickle.dumps(response))
        response = DEFAULT_MESSAGE
        response['TCP_ACK_FLAG'] = 1
        response['TCP_FIN_FLAG'] = 1
        connectionSocket.send(pickle.dumps(response))


    connectionSocket.close()
