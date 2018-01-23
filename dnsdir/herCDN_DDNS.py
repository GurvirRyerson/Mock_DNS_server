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
    connection = sqlite3.connect('herCDN_dns_records.db')
    c = connection.cursor()
    
    c.execute('DROP TABLE IF EXISTS herCDN_DNS_Records')
    c.execute('''CREATE TABLE herCDN_DNS_Records (Name text, Value text, Type text)''')

    #Has one more record than hiscinema authoritative dns so we can get the ip for herCDN.com
    dns_inserts = [('herCDN.com', 'NSherCDN.com', 'NS'), ('NSherCDN', 'localhost', 'A'),
                   ('hiscinema.com', 'NShiscinema.com', 'NS'), ('NShiscinema.com', 'localhost', 'A'),
                   ('hiscinema.com/File1', 'herCDN.com', 'V'), ('hiscinema.com/File2', 'herCDN.com', 'V'),
                   ('hiscinema.com/File3', 'herCDN.com', 'V'), ('hiscinema.com/File4', 'herCDN.com', 'V'),
                   ('herCDN.com', 'localhost', 'A')]
                   
    c.executemany('INSERT INTO herCDN_DNS_Records VALUES (?,?,?)', dns_inserts)
    
    connection.commit()
    connection.close()

#Gets the type A record for herCDN.com
#pretty straight forward
def Dns_Lookup(record):
    connection = sqlite3.connect('herCDN_dns_records.db')
    c = connection.cursor()
    
    record_name = record.split(',')[0]
    record_type = record.split(',')[1]
    
    for row in c.execute('SELECT * FROM herCDN_DNS_Records WHERE Name=?', (record_name,)):
        for value in  c.execute ('SELECT Value, Type FROM herCDN_DNS_Records WHERE Name=? AND Type=?', (row[1], 'A')):
            resolved_query = str(value[0])+ "," + str(value[1])
            
    connection.close()
    return resolved_query
    

if __name__== '__main__':
    db_init()
    
    herCDN_ddns_socket = socket(AF_INET, SOCK_DGRAM)
    
    herCDN_ddns_socket.bind(('localhost', 44494))
    #listn forever
    while True:
        #Get a dns request from local dns
        dns_request, address = herCDN_ddns_socket.recvfrom(1024)
        if (dns_request):
            #Sends the ip address of the herCDN.com (where the actual vidoes are online)
            herCDN_ddns_socket.sendto(Dns_Lookup(dns_request), address)
