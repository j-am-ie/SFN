from scapy.layers.inet import IP, UDP
from scapy.all import *
import datetime
import mysql.connector

# Establish MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jamie",
    database="DevicesTestDB"
)
cursor = db.cursor()

# Create the network_data table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS network_data (id INT AUTO_INCREMENT PRIMARY KEY, date VARCHAR(255), time VARCHAR(255), router_ip VARCHAR(255), num_packets INT, source_ip VARCHAR(255), destination_ip VARCHAR(255), protocol VARCHAR(255), source_port INT, destination_port INT)")

def process_packet(packet: Packet):
    print(packet.show())  # Print packet details for debugging
    if IP in packet and UDP in packet and packet[IP].dst == '192.168.122.1' and packet[UDP].dport == 2055:
        # Extract necessary information
        date_time = datetime.datetime.now()
        date = str(date_time.date())
        time = str(date_time.time())
        router_ip = packet[IP].src
        source_ip = packet[IP].src
        destination_ip = packet[IP].dst
        protocol = packet[IP].payload.name if hasattr(packet[IP], 'payload') else 'Unknown'
        source_port = packet[UDP].sport
        destination_port = packet[UDP].dport

        try:
            # Attempt to extract the number of packets
            num_packets = int(packet.getlayer(Raw).load)
        except (AttributeError, ValueError):
            # Handle the case where num_packets is not an integer or not present
            print("Warning: Unable to extract num_packets. Setting it to 0.")
            num_packets = 0

        try:
            # Save this information to the database
            cursor.execute("""
                INSERT INTO network_data 
                (date, time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (date, time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port))
            db.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# Sniff continuously on virbr0
sniff(iface='virbr0', prn=process_packet, store=0)
