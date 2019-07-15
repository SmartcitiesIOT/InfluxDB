import paho.mqtt.client as mqtt
import json
import logging
import time
import pickle
import SensorMsg_pb2
import ActuatorMsg_pb2
import google.protobuf
import urllib2, sys
import re

from influxdb import InfluxDBClient
from datetime import datetime

MQTT_BROKER_IP = "192.168.0.107" 
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "base"

Sensor_Read = SensorMsg_pb2.SensorData()
Actuator = ActuatorMsg_pb2.ActuatorData()
Actuator2 = ActuatorMsg_pb2.ActuatorData()
#Implementation of Callback methods
def on_connect(client, userdata, flags, rc) :
    print ("InfluxDB is connected to MQTT Broker !!")
    #client.subscribe(MQTT_TOPIC)

def update_problem_pddl():
    problem_pddl_str=""
    with open("p01.pddl") as fin:
        problem_pddl_str = fin.read()
    temperature_str = "(= (temperature r1) " + str(Sensor_Read.Temperature) +")"
    humidity_str = "(= (humidity r1) " + str(Sensor_Read.RelativeHumidity) +")"
    luminance_str = "(= (luminance r1) " + str(Sensor_Read.Luminance) +")"
    uv_str = "(= (uv r1) " + str(Sensor_Read.Ultraviolet) +")" 
    if (Sensor_Read.Motion == "True"):
        motion_str = "(= (motion r1) " + str(1) +")"
    else:
        motion_str = "(= (motion r1) " + str(0) +")"
    problem_pddl_str =  re.sub('\(= \(temperature r1\) [0-9.]+\)', temperature_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(humidity r1\) [0-9.]+\)', humidity_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(luminance r1\) [0-9.]+\)', luminance_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(uv r1\) [0-9.]+\)', uv_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(motion r1\) [0-9.]+\)', motion_str, problem_pddl_str)
    
    with open("p01.pddl", "w") as fout:
        fout.write(problem_pddl_str)

def get_pddl_plan():
    # Get plan from online planner
    # Publish to mqtt
    data = {'domain': open("domain.pddl", 'r').read(),
        'problem': open("p01.pddl", 'r').read()}

    req = urllib2.Request('http://solver.planning.domains/solve')
    req.add_header('Content-Type', 'application/json')
    resp = json.loads(urllib2.urlopen(req, json.dumps(data)).read())

    return ('\n'.join([act['name'] for act in resp['result']['plan']]))

def publish_pddl_plan(actuator_plan):
    #if ("turn-on-hvac" in actuator_plan): 
     #   Actuator.hvac_on = 1; 
    #else: 
     #   Actuator.hvac_on = 0;

   # if ("turn-on-light" in actuator_plan):
    #    Actuator.light_on = 1;
   # else:
    #    Actuator.light_on = 0;
    
    MSG=pickle.dumps(actuator_plan) 

    #MSG = Actuator.SerializeToString()
    #print("Actuator : " , Actuator.hvac_on)
    #Actuator2.ParseFromString(MSG)
    #print("Actuator2 : " , Actuator2.hvac_on)
    mqtt_client.publish("actuate",MSG,qos=0, retain=True)
    print("Published Actuator Plan")


def on_message(client, userdata, msg):
    #print(pickle.loads(msg.payload))
    #Sensor_Read = SensorMsg_pb2.SensorData()
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
    update_problem_pddl()
    print ("Problem Updated")
    pddl_plan = get_pddl_plan()
    publish_pddl_plan(pddl_plan)
    print (pddl_plan)


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
