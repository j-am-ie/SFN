import socket
import ssl
import datetime
import mysql.connector
import paramiko
import time
import matplotlib.pyplot as plt
import requests

db2 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jamie",
    database="DevicesTestDB"
)
cursor1 = db2.cursor()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Wrap the socket
ssl_socket = ssl_context.wrap_socket(client_socket)


while True:
    print("Menu")
    print("---------")
    print("a: Add Router")
    print("b: Delete Router")
    print("c: List Routers")
    print("d: Set Backup Time")
    print("e: Set Router Netflow Settings")
    print("f: Remove Router Netflow Settings")
    print("g: Set Router SNMP Settings")
    print("h: Remove Router SNMP Settings")
    print("i: Show Router Config")
    print ("j: Show Changes in Router Config")
    print("k: Display Router Netflow Statistics")
    print("m: Quit")

    input1 = input("Enter your choice: ")
    
    ssl_socket.send(str(input1).encode("utf-8"))

    

    if input1 == 'a':
        hoInput = input("Input hostname: ")
        ipInput = input("Input IP: ")
        usInput = input("Input username: ")
        paInput = input("Input password: ")

        ssl_socket.send(hoInput.encode("utf-8"))
        ssl_socket.send(ipInput.encode("utf-8"))
        ssl_socket.send(usInput.encode("utf-8"))
        ssl_socket.send(paInput.encode("utf-8"))

    elif input1 == 'b':
        print()
        print("ID, hostname, IP, user, password, Backup Time")
        print("--------------------------------------|----------|-----------------|---------|---------")
        while True:

            r1 = ssl_socket.recv(1024).decode("utf-8")
            if r1 == "END":
                break
            print(r1)
        inputDel = input("What is the IP of the device that you wish to delete? ") 
        ssl_socket.send(inputDel.encode("utf-8"))

    elif input1 == 'c':
        print()
        print("ID                                     hostname   IP                user      password")
        print("--------------------------------------|----------|-----------------|---------|---------")
        while True:

            r = ssl_socket.recv(1024).decode("utf-8")
            if r == "END":
                break
            print(r)

    elif input1 == 'd':
        ipreg = input("Enter the ip: ")
        stime = input("Enter the backup time: ")  
        ssl_socket.send(ipreg.encode("utf-8"))
        ssl_socket.send(stime.encode("utf-8")) 

    elif input1 == 'e':
         NTFLW = input("What is the ip of the router: ")
         queryB = f"SELECT username, password FROM devices WHERE ip = '{NTFLW}'"
         cursor1.execute(queryB)

         # Fetch the result
         resultSS = cursor1.fetchone()

            # Create an SSH client
         ssh_client = paramiko.SSHClient()

         try:
            # Automatically add the server's host key
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(NTFLW, username=resultSS[0], password=resultSS[1], timeout=10)

            # Send the commands
            commands3 = [
                "conf t",
                "ip flow-cache timeout inactive 1",
                "ip flow-cache timeout active 1",
                "ip flow-export source FastEthernet0/0",
                "ip flow-export version 9",
                "ip flow-export destination 192.168.122.1 2055",
                "interface FastEthernet0/0",
		        "ip flow ingress",
		        "ip flow egress",
                "exit",
                "write memory",
                "exit"
                
             ]
            

            shell = ssh_client.invoke_shell()

            for command3 in commands3:
             shell.send(command3 + '\n')
             while not shell.recv_ready():
              time.sleep(0.5)
             output = shell.recv(10000).decode("utf-8")
             print(output)
         except Exception as e:
             print(f"Error: {e}")

    elif input1 == 'f':
         NTFLW1= input("What is the ip of the router: ")
         queryc = f"SELECT username, password FROM devices WHERE ip = '{NTFLW1}'"
         cursor1.execute(queryc)

         
         resultSSS = cursor1.fetchone()

            # Create an SSH client
         ssh_client = paramiko.SSHClient()

         try:
            #Gets the host key
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(NTFLW1, username=resultSSS[0], password=resultSSS[1], timeout=10)

            # Send the command to get the running configuration
            commands4 = [
                "conf t",
                "no ip flow-cache timeout inactive 1",
                "no ip flow-cache timeout active 1",
                "no ip flow-export source FastEthernet0/0",
                "no ip flow-export version 9",
                "no ip flow-export destination 192.168.122.1 2055",
                "interface FastEthernet0/0",
		        "no ip flow ingress",
		        "no ip flow egress",
                "exit",
                "write memory",
                "exit"
                
             ]
            

            shell = ssh_client.invoke_shell()

            for command4 in commands4:
             shell.send(command4 + '\n')
             while not shell.recv_ready():
              time.sleep(0.5)
             output = shell.recv(10000).decode("utf-8")
             print(output)
         except Exception as e:
             print(f"Error: {e}")
       

    elif input1 == 'g':
         SNMPSN1 = input("What is the ip of the router: ")
         queryA = f"SELECT username, password FROM devices WHERE ip = '{SNMPSN1}'"
         cursor1.execute(queryA)

         # Fetch the result
         resultS = cursor1.fetchone()

            # Create an SSH client
         ssh_client = paramiko.SSHClient()

         try:
            # Automatically add the server's host key
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(SNMPSN1, username=resultS[0], password=resultS[1], timeout=10)

            # Send the command to get the running configuration
            commands = [
                "conf t",
                "logging history debugging",
                "snmp-server community SFN RO",
                "snmp-server ifindex persist",
                "snmp-server enable traps snmp linkdown linkup",
                "snmp-server enable traps syslog",
                "snmp-server host 192.168.122.1 version 2c SFN",
                "exit",
                "write memory",
                "exit"
                
             ]
            

            shell = ssh_client.invoke_shell()

            for command in commands:
             shell.send(command + '\n')
             while not shell.recv_ready():
              time.sleep(0.5)
             output = shell.recv(10000).decode("utf-8")
             print(output)
         except Exception as e:
             print(f"Error: {e}")

    elif input1 == 'h':
         SNMPSN = input("What is the ip of the router: ")


         query = f"SELECT username, password FROM devices WHERE ip = '{SNMPSN}'"
         cursor1.execute(query)

         # Fetch the result
         resultS = cursor1.fetchone()

            # Create an SSH client
         ssh_client = paramiko.SSHClient()

         try:
            # Automatically add the server's host key
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(SNMPSN, username=resultS[0], password=resultS[1], timeout=10)

            # Send the command to get the running configuration
            commands2 = [
                "conf t",
                "no logging history debugging",
                "no snmp-server community SFN RO",
                "no snmp-server ifindex persist",
                "no snmp-server enable traps snmp linkdown linkup",
                "no snmp-server enable traps syslog",
                "no snmp-server host 192.168.122.1 version 2c SFN",
                "exit",
                "write memory",
                "exit"
                
             ]
            

            shell = ssh_client.invoke_shell()

            for command1 in commands2:
             shell.send(command1 + '\n')
             while not shell.recv_ready():
              time.sleep(0.5)
             output = shell.recv(10000).decode("utf-8")
             print(output)
         except Exception as e:
            print(f"Error: {e}")
         
          

    elif input1 == 'i':
         github_username = "j-am-ie"
         ip = input("Enter the IP address: ")
         github_raw_url = f'https://raw.githubusercontent.com/{github_username}/current_backup/main/{ip}.config'

         try:
            response = requests.get(github_raw_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            config_content = response.text
            print(f"Config file for {ip}:\n")
            print(config_content)
         except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
         except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
         except requests.exceptions.RequestException as err:
            print(f"Request Exception: {err}")    

 


    elif input1 == 'k':
       
       router_ip = input("Enter the router IP: ")

       # Query to get the protocol distribution for the specified router
       query = f"SELECT protocol, COUNT(*) AS packet_count FROM network_data WHERE router_ip = '{router_ip}' GROUP BY protocol"
       cursor1.execute(query)
       result = cursor1.fetchall()

       # Check if there is any data
       if result:
            # Create a dictionary to store protocol data
            protocol_data = {row[0]: row[1] for row in result}

            # Calculate total packet count
            total_packets = sum(protocol_data.values())

            # Calculate percentages
            percentages = [(count / total_packets) * 100 for count in protocol_data.values()]

            # Labels for the pie chart
            labels = list(protocol_data.keys())

            # Colors for each segment
            colors = plt.cm.Paired(range(len(labels)))

            # Display the pie chart with percentages
            plt.pie(percentages, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)

            # Set aspect ratio to be equal, so the pie chart looks circular
            plt.axis('equal')

            # Add a title with the router IP
            plt.title(f'Packet Distribution for Router {router_ip}')

            # Show the pie chart
            plt.show()
       else:
            print(f"No data found for router with IP: {router_ip}")



    elif input1 == 'm':
        print("Quitting the client.")
        ssl_socket.close()
        break

    else:
        print("Invalid choice. Try again.")

