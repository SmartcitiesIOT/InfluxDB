from influxdb import InfluxDBClient
from datetime import datetime

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
                "Humidity": 4.5,
                "Vibration": 0.009
                }
            }
        ]

def main():
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'Sensor_Values')
    
    client.create_database('Sensor_Values')
    
    client.write_points(json_body)
    
    results = client.query ('select * from Isolation_Chamber;')
    
    humidity_value = list(results.get_points(measurement='Isolation_Chamber',tags={'Room_No': '108b','Doctor_Incharge':'Dr.Thomas'}))
    print("Query Result : " + str(humidity_value))
    
    client.drop_database('Sensor_Values')
    

if __name__ == '__main__':
    main()
