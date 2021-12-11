from dronekit_basics import *
import curses, os, sys, time

def drawHud(win,x,y,z):
    win.addstr("-"*15+"XYZ Position"+"-"*15+"\n")
    win.addstr(f"x: {x}  y:{y}  z:{z}\n")

def main(win):
    win.nodelay(True)
    key=""
    win.clear()
    win.addstr("Detected key:")
    x=y=z=0
    while 1:
        win.clear()
        drawHud(win,x,y,z)
        win.refresh()
        try:
            key = win.getkey()
            #  print(key)
            #  print(curses.KEY_LEFT)
            if key == "KEY_LEFT":
                y-=2
                goto(0,-2,vehicle,win)
            elif key == "KEY_RIGHT":
                y+=2
                goto(0,2,vehicle,win)
            elif key == "KEY_UP":
                x+=2
                goto(2,0,vehicle,win)
            elif key == "KEY_DOWN":
                x-=2
                goto(-2,0,vehicle,win)
            elif key == "z":
                z+=1
            elif key == "x":
                z-=1
            elif key == "q":
                return #close program wrapper should do its thing
        except Exception as e:
            # no input
            pass
        time.sleep(0.05)


if __name__ == "__main__":
    # connect to argument vehicle provided or start sitl
    vehicle = connectMyCopter()

    print(vehicle.mode)
    #takeoff to 10 metters
    arm_and_takeoff(10,vehicle)
    
    #  goto(-10,0,vehicle)

    curses.wrapper(main)


