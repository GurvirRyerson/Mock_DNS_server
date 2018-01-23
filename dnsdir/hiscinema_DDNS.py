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
    connection = sqlite3.connect('hiscinema_dns_records.db')
    c = connection.cursor()
    
    c.execute('DROP TABLE IF EXISTS hiscinema_DNS_Records')
    c.execute('''CREATE TABLE hiscinema_DNS_Records (Name text, Value text, Type text)''')

    #Another way to do this would be to make each file link to a different hostname
    #Then each Video file you wanted would be located on some different site
    #That would be useful if you had multiple CDN servers for the some site
    dns_inserts = [('herCDN.com', 'NSherCDN.com', 'NS'), ('NSherCDN', 'localhost', 'A'),
                   ('hiscinema.com', 'NShiscinema.com', 'NS'), ('NShiscinema.com', 'localhost', 'A'),
                   ('hiscinema.com/File1', 'herCDN.com', 'V'), ('hiscinema.com/File2', 'herCDN.com', 'V'),
                   ('hiscinema.com/File3', 'herCDN.com', 'V'), ('hiscinema.com/File4', 'herCDN.com', 'V')]
                   
    c.executemany('INSERT INTO hiscinema_DNS_Records VALUES (?,?,?)', dns_inserts)
    
    connection.commit()
    connection.close()


#compares record_name and record_type, gets value field
#This is only really used for getting ip of authoritative dns of herCDN
#Slightly more complex than the one used in local dns
#looks up all V type record, gets the one that matches the url givens (record), stores the Value entry in row[1]
#then finds the row that has its Name column = row[1]
def Dns_Lookup(record):
    connection = sqlite3.connect('hiscinema_dns_records.db')
    record_name = record.split(",")[0]
    record_type = record.split(",")[1]
    c = connection.cursor()
    
    for row in c.execute('SELECT * FROM hiscinema_DNS_Records WHERE Type=?', record_type):
        if (record_name == row[0]):
            for value in  c.execute ('SELECT Value, Type FROM hiscinema_DNS_Records WHERE Name=?', (row[1],)):
                resolved_query = str(value[0])+ "," + str(value[1])
            

    connection.close()
    return resolved_query
    

if __name__== '__main__':
    db_init()
    #Socket to communicate with inc dns request (Only local dns in our case)
    hiscinema_ddns_socket = socket(AF_INET, SOCK_DGRAM)
    
    hiscinema_ddns_socket.bind(('localhost', 44493))
    #Listen forever
    while True:
        #Get a request from local dns
        dns_request, address = hiscinema_ddns_socket.recvfrom(1024)
        if (dns_request):
            #Do a lookup on the request
            hiscinema_ddns_socket.sendto(Dns_Lookup(dns_request), address)
        
           
