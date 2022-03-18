# Startup Process
This is meant to document how to start the drone and spin motors

1. Power everything
2. Login to rpi (using vnc viewer)
3. Open a terminal
4. Open a mavproxy shell
  We can use this run commands to arm throttle (spins the motors), show params, etc
  To open a shell we want tell mavproxy to connect on an interface connected to the pixhawk.
  In out setup this should `serial0`, we also need to provide a baudrate for the serial port.
  In our setup this should be 576600. So run the following in the terminal
  ```
  mavproxy.py --master=/dev/serial0 --baudrate 576600 --aircraft <directory path where logs will be saved will default to current>
  ```

5. Test motors from mav proxy shell by typing
```
STABILIZE> arm throttle
```

If motors spin then we should be able to use our dronekit scripts to fly.



