import paho.mqtt.client as mqtt
import json
import logging
import time
import pickle
import SensorMsg_pb2
import google.protobuf

from influxdb import InfluxDBClient
from datetime import datetime

MQTT_BROKER_IP = "192.168.0.103" 
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "base"

#Implementation of Callback methods
def on_connect(client, userdata, flags, rc) :
    print ("InfluxDB is connected to MQTT Broker !!")
    #client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    #print(pickle.loads(msg.payload))
    Sensor_Read = SensorMsg_pb2.SensorData()
    #`print (str(msg.payload))
    Sensor_Read.ParseFromString(msg.payload)
    #print (str(Sensor_Read.last_updated).replace("\n", " ")) 
    #time.sleep(3)
    time_stamp = str(Sensor_Read.last_updated).replace("\n", " ")
    print (time_stamp)
    print (datetime.utcnow())
    print (Sensor_Read.batteryLevel)
    print (Sensor_Read.Motion)
    print (Sensor_Read.Ultraviolet)
    print (Sensor_Read.Luminance)
    print (Sensor_Read.RelativeHumidity)
    print (Sensor_Read.Temperature)
    json_body = [
        {
            "measurement": "Isolation_Chamber",
            "tags": {
                "Room_No": "108b",
                "Doctor_Incharge":"Dr.Thomas"
                },
            "time": datetime.utcnow(),
            "fields": {
                "BatteryLevel": Sensor_Read.batteryLevel,
                "Motion": Sensor_Read.Motion,
                "Ultraviolet": Sensor_Read.Ultraviolet, 
                "Luminance": Sensor_Read.Luminance,
                "RelativeHumidity": Sensor_Read.RelativeHumidity,
                "Temperature" : Sensor_Read.Temperature
                }
        }
    ]
    print("Dinesh" + str(json_body))
    client_influx.write_points(json_body)
    print ("Wrote values to DB")

client_influx = InfluxDBClient('localhost', 8086, 'root', 'root', 'Sensor_Values')
client_influx.create_database('Sensor_Values')


#MQTT Client instantiation
mqtt_client = mqtt.Client()

# Linking the client with callback implementations
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message 

# Connecting to the MQTT Broker
mqtt_client.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT, MQTT_KEEPALIVE_INTERVAL)

mqtt_client.loop_start()
mqtt_client.subscribe(MQTT_TOPIC)
print ("Subscribed !!")

while 1:
    pass
'''
json_body = [
        {
            "measurement": "Isolation_Chamber",
            "tags": {
                "Room_No": "108b",
                "Doctor_Incharge":"Dr.Thomas"
                },
            "time": datetime.utcnow().replace(minute=0,second=0,microsecond=0),
            "fields": {
                "Temperature": 5.3,
                "Pressure": 2.5,
                "Ultraviolet":0.0, 
                "Humidity": 4.5,
                "Vibration": 0.009
                }
            }
        ]
'''

'''    
results = client_influx.query ('select * from Isolation_Chamber;') 
#print (str(results))
humidity_value = list(results.get_points(measurement='Isolation_Chamber',tags={'Room_No': '108b','Doctor_Incharge':'Dr.Thomas'}))
print("Query Result : " + str(humidity_value))


client_influx.drop_database('Sensor_Values')
    
'''
    # Commented Code for JSON 
    #payload_tmp = pickle.loads(msg.payload)
    #payload = json.loads(payload_tmp)
    #print(payload)
    
    #if __name__ == '__main__':
 #   main()
