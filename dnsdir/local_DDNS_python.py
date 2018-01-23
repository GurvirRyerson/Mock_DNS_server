import sqlite3
from socket import *


#www.hiscinema.com has port 44490
#local dns has port 44491 to talk to client
#local dns has port 44492 to talk to other dns
#ADNS for hiscinema.com has port 44493
#ADNS for herCDN has port 44494
#herCDN has port 44495



#Initializes the database with the dns records
def db_init():
    connection = sqlite3.connect('dns_records.db')
    c = connection.cursor()
    
    c.execute('DROP TABLE IF EXISTS DNS_Records')
    c.execute('''CREATE TABLE DNS_Records (Name text, Value text, Type text)''')
    
    dns_inserts = [('herCDN.com', 'NSherCDN.com', 'NS'), ('NSherCDN.com', 'localhost', 'A'),
                   ('hiscinema.com', 'NShiscinema.com', 'NS'), ('NShiscinema.com', 'localhost', 'A')]
    c.executemany('INSERT INTO DNS_Records VALUES (?,?,?)', dns_inserts)
    
    connection.commit()
    connection.close()
    


#compares hostname to Name coloumn in database, returns the Value field    
def NS_Lookup(hostname):
    connection = sqlite3.connect('dns_records.db')
    c = connection.cursor()
    for name_value_pair in c.execute('SELECT Name, Value FROM DNS_Records'):
        if (hostname == name_value_pair[0]):
            resolved_ip = name_value_pair[1]
            for value in  c.execute ('SELECT Value FROM DNS_Records WHERE Name=?', (name_value_pair[1],)):
                resolved_ip = value[0]
            

    connection.close()
    return resolved_ip
    

#Sends dns request to hiscinema authoritative dns, gets the NS record for herCDN authoritative dns then gets ip via db lookup
def resolver_hiscinema(request, socket, address):
    socket.sendto(request, address)
    query_answer, addr = socket.recvfrom(1024)
    record_value = query_answer.split(',')[0]
    record_type = query_answer.split(',')[1]
    if (record_type == 'NS'):
       ip_addr = NS_Lookup(record_value)
    else:
        print('Error1')
        exit(1)

    return ip_addr

#Sends dns request to herCDN authoritataive dns, gets the ip address of herCDN webserver
def resolver_herCDN(request, socket, ipaddr, port):
    socket.sendto(request, (ipaddr, port))
    query_answer, addr = socket.recvfrom(1024)
    record_value = query_answer.split(',')[0]
    record_type = query_answer.split(',')[1]
    if (record_type== 'A'):
        return record_value
    else:
        print(record_type)
        exit(2)



#Only handles 1 request at a time, so thats not very good
#Could possibly multi-thread this so resolver_hiscinema starts a new thread and the server is open to more dns requests from client
if __name__ == '__main__':
    db_init()    
    #socket for client dns requests
    local_ddns_socket = socket(AF_INET, SOCK_DGRAM)
    
    #socket for sending dns requests to other dns
    local_ddns_query_socket = socket(AF_INET, SOCK_DGRAM)
    
    local_ddns_socket.bind(('localhost', 44491))
    local_ddns_query_socket.bind(('localhost', 44492))

    #Sorta cheating by just getting hiscinema.com ADNS (Authoritative dns)
    auth_dns_name_hiscinema = NS_Lookup('hiscinema.com')
    auth_dns_port_hiscinema = 44493
    auth_address_hiscinema = (auth_dns_name_hiscinema, auth_dns_port_hiscinema)
                                                   
    #Always listening for dns request
    while True:
        #Get request from client
        request, address = local_ddns_socket.recvfrom(1024)
        #If there is some request sent, other just chill 
        if (request):
            #To get NS record of herCDN.com
            NSherCDN_addr = resolver_hiscinema(request, local_ddns_query_socket, auth_address_hiscinema)
            #To get IP addr of herCDN.com
            CDNip = resolver_herCDN (request, local_ddns_query_socket, NSherCDN_addr, 44494)
            #Send to the client the ip addr of herCDN.com
            local_ddns_socket.sendto(CDNip, address)
            


            

            
    
