from scapy.all import sniff, SNMP, SNMPvarbind, IP
import mysql.connector
from datetime import datetime

# Replace these values with your actual database credentials
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "jamie",
    "database": "DevicesTestDB"
}

# Connect to the database
db = mysql.connector.connect(**db_config)
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS snmp_data (id INT AUTO_INCREMENT PRIMARY KEY, date VARCHAR(255), time VARCHAR(255), router_ip VARCHAR(255), trap_type INT, message_or_state VARCHAR(255), interface_name VARCHAR(255))")

def save_to_database(date, time, router_ip, trap_type, message_or_state, interface_name=None):
    # Insert data into the snmp_data table
    if trap_type == 1:  # SYSLOG trap
        query = "INSERT INTO snmp_data (date, time, router_ip, trap_type, message_or_state) VALUES (%s, %s, %s, %s, %s)"
        values = (date, time, router_ip, trap_type, message_or_state)
    elif trap_type in [2, 3]:  # LINK UP or LINK DOWN trap
        query = "INSERT INTO snmp_data (date, time, router_ip, trap_type, message_or_state, interface_name) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (date, time, router_ip, trap_type, message_or_state, interface_name)

    cursor.execute(query, values)
    db.commit()

def process_snmp_packet(packet):
    if SNMP in packet:
        trap_type = None
        message_or_state = None
        interface_name = None

        if packet[SNMP].version == 1:  # SNMPv2c
            if packet[SNMP].community:
                trap_type = 1  # SYSLOG trap
                message_or_state = str(packet[SNMP].community)

        elif packet[SNMP].version == 2:  # SNMPv2c
            if SNMPvarbind in packet:
                interface_name_oid = "1.3.6.1.2.1.2.2.1.2"  # Assuming interface name OID
                interface_name_value = None

                for varbind in packet[SNMPvarbind]:
                    oid, value = varbind.oid, varbind.value
                    if oid == "1.3.6.1.6.3.1.1.5.3":  # LINK DOWN trap
                        trap_type = 4
                        message_or_state = "LINK DOWN"
                    elif oid == "1.3.6.1.6.3.1.1.5.4":  # LINK UP trap
                        trap_type = 3
                        message_or_state = "LINK UP"
                    elif oid == interface_name_oid:  # Interface name
                        interface_name_value = value

                if interface_name_value:
                    interface_name = str(interface_name_value)

        if trap_type is not None:
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            router_ip = packet[IP].src
            save_to_database(date_time.split()[0], date_time.split()[1], router_ip, trap_type, message_or_state, interface_name)

# Sniff SNMP packets on virbr0 interface
sniff(iface="virbr0", filter="udp and port 162", prn=process_snmp_packet, store=0)