# Mavproxy Setup Process
Shell cmds for dependcies (dont forget to `sudo apt update` first).
```
sudo apt-get install python3-dev python3-opencv python3-wxgtk4.0 python3-pip python3-matplotlib python3-lxml python3-pygame
pip3 install PyYAML mavproxy --user
echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bashrc
```

### Disable serial port for OS and enable in hardware
`sudo raspi-config` to open config wizard. Go to Interfacing option->serial->
1.  select `no` to “Would you like a login shell to be accessible over serial?”.
2. select `yes` to “Would you like the serial port hardware to be enabled?”.

Wi-fi is already configured to connect to my hotspot on boot, but it would probably be a good idea to setup an hotspot
on the RPI itself so we can connect to it instead of waiting for it to connect to us.

# Connecting Pixhawk to serial int
We'll connect to pins 4,6,8, and 10 on the RPI
|PIN#|Purpose|
--|--
|2|Power 5V|
|6|Ground|
|8|TX (Transmit goes to receive on Pixhawk)|
|10|RX (Receive goes to transmit on Pixhawk)|

## Including pinout here for reference
![Pinout](imgs/pinout.png)
