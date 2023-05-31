# Improvement and modified RSI Communicator (python3)

## Issues solved

- IP address settings (solved)

First make sure you set the External PC's IP the SERVER_IP in settings.py. Then try to ping the controller's IP address in terminal. If everything is fine, set the SERVER_PORT to 59152, CLIENT_PORT to 5005. 
Notice that the RECEIVER_IP is the same as SERVER_IP. RECEIVER_PORT doesn't need to be changed.

- Python3 string type errors (solved)

In python3 rsi communicator there were errors raised due to the confusion between strings and bytes. Just keep in mind that the functions in scripts need the input_text to be string, but when it is going to be sent through socket, it should be converted into bytes (utf-8).

- Robot keeps getting command (solved)

Using Eren's original code, in server.py, there is this part:

```
if connection.poll():
    data_to_send = connection.recv()
    default_command = data_to_send
else:  # send the default
    data_to_send = default_command 
```
This replace the default correction with the command you send with tcp_sender. Therefore the robot will keep executing the last command. 

## Issues:

- When trying reset test, sometimes the client will say command is not valid. With 2 commands in one line. Could be that the refresh rate too high. 
```
The command is not valid.
r,0.0000,0.1000,0.0000,0.0000,0.0000,0.0000,r,0.0000,0.1000,0.0000,0.0000,0.0000,0.0000,

```

## Explanation of needed State Data

- RIst: Cartesian coordinates of TCP
- MoCur: Motor Current of Joint A1-A6
- Torque: Torque of Joint A1-A6
- MOT_Temp: Motor Temperature of Joint A1-A6 (Celcius)

- force & torque: Force and Torque from Sensor




## Arthur and acknowlegments

RSI Communicator Aurthur: Eren Sezener (erensezener@gmail.com). [Github project here](https://github.com/erensezener/kuka-rsi3-communicator).



