from flask import Flask, redirect, render_template
from socket import *

local_dns_ip = 'localhost'
local_dns_port = 44491


application = Flask(__name__, )

#Starts the chain to find ip of herCDN.com
def Dns_Request(record_to_request):
    UDP_IP = 'localhost'
    UDP_PORT = 44490 
    dns_request_socket = socket(AF_INET, SOCK_DGRAM)
    dns_request_socket.bind((UDP_IP, UDP_PORT))
    dns_request_socket.sendto(record_to_request, (local_dns_ip, local_dns_port))
    resolved_address_of_content, addr = dns_request_socket.recvfrom(1024)
    return resolved_address_of_content


#Does the actual downloading of the file/video
def Content_Download(address, file_name):
    content_tcp_socket = socket (AF_INET, SOCK_STREAM)
    content_tcp_socket.connect((address, 44496))
    content_tcp_socket.send(file_name)
    
    file_name = file_name+"_download.mp4"
    try:
        file_obj = open("static/"+file_name, 'wb')
    except IOError:
        return 'FNF' #File not found
    data = content_tcp_socket.recv(1024)
    
    while (data):
        file_obj.write(data)
        data = content_tcp_socket.recv(1024)

    file_obj.close()
    content_tcp_socket.close()

    return 'Success'


@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@application.errorhandler(400)
def bad_request(e):
    return "Error 400: Bad request", 400

@application.errorhandler(505)
def http_not_supported(e):
    return "Error 505: http version not supported", 505


#Main page, has 4 links to 4 files
@application.route("/")
def Landing_Page():
    return render_template('index.html')


@application.route("/File1")
def File1():
    address = Dns_Request('hiscinema.com/File1,V')
    Content_Download(address, 'File1')
    #Each file should invoke the local dns server to start looking for the file
    return render_template('video_template.html', page_title= 'File1', video_title='File1_download.mp4')


@application.route("/File2")
def File2():
    address = Dns_Request('hiscinema.com/File2,V')
    Content_Download(address, 'File2')    
    return render_template('video_template.html', page_title= 'File2', video_title='File2_download.mp4')

@application.route("/File3")
def File3():
    address = Dns_Request('hiscinema.com/File3,V')
    Content_Download(address, 'File3')    
    return render_template('video_template.html', page_title= 'File3', video_title='File3_download.mp4')
                              
@application.route("/File4")
def File4():
    address = Dns_Request('hiscinema.com/File4,V')
    Content_Download(address, 'File4')
    return render_template('video_template.html', page_title= 'File4', video_title='File4_download.mp4')


#This counts as a multithreaded server hopefully
if __name__ == "__main__":
    application.run(host='localhost', port=5000, threaded=True)
