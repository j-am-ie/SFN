import socket
import ssl
import mysql.connector
import uuid
import datetime


db2 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jamie",
    database="DevicesTestDB"
)
cursor1 = db2.cursor()


def handle_client(client_socket):
    ssl_socket = ssl_context.wrap_socket(client_socket, server_side=True)

    

    while True:
        data = ssl_socket.recv(1024)
        if not data:
            break

        input1 = (data.decode("utf-8"))

        if input1 == 'a':
            hoInput = ssl_socket.recv(1024).decode("utf-8")
            ipInput = ssl_socket.recv(1024).decode("utf-8")
            usInput = ssl_socket.recv(1024).decode("utf-8")
            paInput = ssl_socket.recv(1024).decode("utf-8")

            cursor1.execute("SELECT * FROM devices WHERE ip = %s", (ipInput,))
            existing = cursor1.fetchall()

            if existing:
                ssl_socket.send("Error: IP already in use".encode('utf-8'))
            else:
                unique = str(uuid.uuid1())
                cTime = datetime.datetime.now()
                fTime = cTime.strftime("%H:%M")
                input3 = "INSERT INTO devices (id, hostname, ip, username, password, Ctime) VALUES (%s, %s, %s, %s, %s, %s)"
                input4 = (unique, hoInput, ipInput, usInput, paInput, fTime)
                cursor1.execute(input3, input4)
                db2.commit()
                ssl_socket.send("Entry added".encode('utf-8'))

        elif input1 == 'b':
            cursor1.execute("SELECT * FROM devices")
            output2 = cursor1.fetchall()
            for r1 in output2:
                  
                ssl_socket.send(str(r1).encode("utf-8"))
                
            ssl_socket.send("END".encode("utf-8"))
            
            inputDel = ssl_socket.recv(1024).decode("utf-8")
            delFun = "DELETE FROM devices WHERE ip = %s"
            cursor1.execute(delFun, (inputDel,))
            db2.commit()

        elif input1 == 'c':

            cursor1.execute("SELECT * FROM devices")
            output1 = cursor1.fetchall()
            for r in output1:
                  
                ssl_socket.send(str(r).encode("utf-8"))
                
            ssl_socket.send("END".encode("utf-8"))

        elif input1 == 'd':
            ipreg = ssl_socket.recv(1024).decode("utf-8")
            stime = ssl_socket.recv(1024).decode("utf-8")
            backup_time = datetime.datetime.strptime(stime, "%H:%M")
            backup_time_str = backup_time.strftime("%H:%M")
            cursor1.execute("UPDATE devices SET Ctime = %s WHERE ip = %s", (backup_time_str, ipreg))
            db2.commit()

            
   
        elif input1 == 'm':
          
         ssl_socket.close()
         break
 
# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 12345))
server_socket.listen(5)

# Wrap the server socket with TLS
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="server.pem", keyfile="server.key", password="jamie")

while True:
    # Accept connections from clients
    print("Server is listening on port 12345...")
    client_socket, address = server_socket.accept()
    print(f"Connection established with {address}")
    handle_client(client_socket)

# Close the sockets
server_socket.close()