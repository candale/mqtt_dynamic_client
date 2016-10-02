### MQTT RPC

This project aims to facilitate the communication between a user and a 
wireless enabled device.

## Description

The project consists of three parts
    * device application
    * MQTT broker
    * web application

On the device there are user-defined operations that are specified like this:
```
<mqtt_topic>|<op_type (call|recv)|<op_name>|<op_description>|<arg_type:arg_name>, ...
```
or without arguments:
```
<mqtt_topic>|<op_type (call|recv)|<op_name>|<op_description>|
```

One is free to use whatever format one desires by implementing a parser that turns the specification into a standard representation (on the web app part).

The device application is responsible for intercepting and routing MQTT messages to the user-defined operations. 

When the device boots up, the specifications of all operations are published on a MQTT topic (`device/<device_id>/spec`).

The web application listens to the specification topic and stores in the database the devices with the published operations and exposes an API through which one can call the operations on any given device.


# TODO: this is just a badly written draft; improve
