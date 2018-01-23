from socket import *
import threading

#Function that is the thread for downloading files/videos
def Communication_Thread(connection_object):
    file_name = connection_object.recv(1024)
    file_name = file_name + '.mp4'
    try:
        file_obj = open("Data/"+file_name, 'rb')
        print 'here1'
    except IOError:
        connection_object.close()
        return
    
    data = file_obj.read(1024)
    while (data):
        connection_object.send(data)
        data = file_obj.read(1024)

    file_obj.close()
    connection_object.close()
    return


if __name__ == '__main__':
    #Tcp socket, max 5 requests at a time
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('localhost', 44496))
    server_socket.listen(5)
    
    while True:
        c, addr = server_socket.accept()
        #Initialize thread
        communication_thread_object = threading.Thread(target = Communication_Thread,kwargs ={'connection_object': c})
        communication_thread_object.start()

        
    server_socket.close()
