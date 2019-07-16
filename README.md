# InfluxDB
Python script does the following tasks:

1)Subscribes to the Sensor topic and appends value to the Influx Database. These values are used by Chronograf to publish to the webserver for graphical display.

2) Executes the Real Time PDDL Problem with Planning Solver and gives the required plan. The plan publishes the required message to the MQTT broker on tpoic Actuators, which is read and executed by the actuators
