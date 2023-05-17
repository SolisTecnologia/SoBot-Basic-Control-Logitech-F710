#!/usr/bin/python3
"""
Solis Robot - SoBot

Controle_F710_Logitech.py: Programming example to control the "SoBot"
using the Logitech F710 controller once Raspberry is turned on.

Created By   : Vinicius M. Kawakami
Version      : 1.0

Company: Solis Tecnologia

Controller button functions:
BTN_START – Enables wheel motors
BTN_R1 – Configure curve mode on the same axis
BTN_L1 – Configure differential curve mode
BTN_R2 – Sets speed 8cm/s
BTN_L2 – Sets speed 4cm/s
BTN_UP – Moves the robot forward
BTN_DOWN – Moves the robot backwards
BTN_LEFT – Moves the robot to the left
BTN_RIGTH – Moves the robot to the right

"""

import inputs
import serial
from time import sleep
import threading
import signal
import sys

'''
###################################
        Global Variables
###################################
'''

flag_start = 0
flag_BT_RZ = 0
flag_BT_Z = 0
flag_vel = 1
flag_BTX_press = 0
flag_BTY_press = 0
flag_pause = 0

'''
###################################
        Auxiliary Functions
###################################
'''

def Timer_BTX_Press ():
    global flag_BTX_press
    flag_BTX_press = 0

def Timer_BTY_Press ():
    global flag_BTY_press
    flag_BTY_press = 0

def Timer_Pause ():
    global flag_pause
    global flag_BTX_press
    global flag_BTY_press
    flag_pause = 0
    if flag_BTY_press == 2:
        usb.write(b"MT0 MP")
        threading.Timer(0.1, Timer_BTY_Press).start()
    elif flag_BTX_press == 2:
        usb.write(b"MT0 MP")
        threading.Timer(0.1, Timer_BTX_Press).start()

# Function to handle script termination signal
def handle_signal(signum, frame):
    usb.write(b"MT0 ME0")   # Disable motors
    usb.write(b"LT E0")     # Turn off Led Tap
    sys.exit(0)             # Encerra o script


'''
###################################
        Funçâos Principal
###################################
'''

# Find the Logitech F710 controller ID connected to the Raspberry Pi
gamepad = inputs.devices.gamepads[0]
print(gamepad)

# Configure the serial port
usb = serial.Serial('/dev/ttyACM0', 57600, timeout=0, dsrdtr=False)
usb.flush()

# Registrar a função de tratamento de sinal para SIGTERM
signal.signal(signal.SIGTERM, handle_signal)

# Configure wheel parametres
usb.write(b"WP MT1 WD99,84")
usb.write(b"WP MT2 WD99,54")
usb.write(b"WP DW264,95")

# Set the motion proportional gain
usb.write(b"PG SO2,3 CA3,22 DF6,11 RI-6")

# Configure operating parametres in continuous mode
usb.write(b"MT0 MC MD0 AT100 DT100 V8")

usb.write(b"LT E1 RD0 GR100 BL0")   # Turn on Led Tap

while True:
    
    events = inputs.get_gamepad()   # Checks if there was any control event
    
    for event in events:
        
        # Checks if it is event of type "KEY"
        if event.ev_type == "Key":
            print(f"Evento code: {event.code}")
            print(f"Evento state: {event.state}")

            # Check if the event code is "BTN_START" in state 1
            if event.code == "BTN_START" and event.state == 1:
                print("Botão Start pressionado")
                if flag_start == 0:
                    flag_start = 1
                    usb.write(b"MT0 ME1")               # Enable motors
                    usb.write(b"LT E1 RD0 GR0 BL100")   # Turn on Led Tap

                else:
                    flag_start = 0
                    usb.write(b"MT0 ME0")               # Disable motors
                    usb.write(b"LT E1 RD0 GR100 BL0")   # Turn on Led Tap

            # Check if the event code is "BTN_SOUTH" in state 1
            if event.code == "BTN_SOUTH" and event.state == 1:
                print("Botão A pressionado")
                usb.write(b"LT E1 RD0 GR100 BL0")   # Turn on Led Tap

            # Check if the event code is "BTN_EAST" in state 1
            elif event.code == "BTN_EAST" and event.state == 1:
                print("Botão B pressionado")
                usb.write(b"LT E1 RD100 GR0 BL0")   # Turn on Led Tap

            # Check if the event code is "BTN_NORTH" in state 1
            elif event.code == "BTN_NORTH" and event.state == 1:
                print("Botão X pressionado")
                usb.write(b"LT E1 RD0 GR0 BL100")   # Turn on Led Tap

            # Check if the event code is "BTN_WEST" in state 1
            elif event.code == "BTN_WEST" and event.state == 1:
                print("Botão Y pressionado")
                usb.write(b"LT E1 RD100 GR50 BL0")   # Turn on Led Tap

            # Check if the event code is "BTN_TR" in state 1
            elif event.code == "BTN_TR" and event.state == 1:
                print("Botão RB pressionado")
                # Configure continuous mode with curve on the same axis
                if flag_vel:
                    usb.write(b"MT0 MC MD0 AT100 DT100 V8")
                else:
                    usb.write(b"MT0 MC MD0 AT100 DT100 V4")

            # Check if the event code is "BTN_TL" in state 1
            elif event.code == "BTN_TL" and event.state == 1:
                print("Botão LB pressionado")
                # Configure continuous mode with differential curve
                if flag_vel:
                    usb.write(b"MT0 MC MD1 RI100 AT100 DT100 V8")
                else:
                    usb.write(b"MT0 MC MD1 RI100 AT100 DT100 V4")

        # Checks if it is event of type "Absolute"
        if event.ev_type == "Absolute":
            print(f"Evento code: {event.code}")
            print(f"Evento state: {event.state}")

            ### Buttons to control the direction ###
            # Events with the MODE button disabled
            # Check if the event code is "ABS_HAT0X"
            if event.code == "ABS_HAT0X":
                if flag_start:                  # Check if flag_start is enable
                    if flag_BTY_press == 0 and flag_BTX_press == 0:
                        if event.state == -1:       # Check state (left direction) of the button
                            flag_BTX_press = 1
                            flag_pause = 1
                            print("Botão ESQ pressionado")
                            usb.write(b"MT0 ML")
                            threading.Timer(0.1, Timer_Pause).start()

                        elif event.state == 1:      # Check state (right direction) of the button
                            flag_BTX_press = 1
                            flag_pause = 1
                            print("Botão DIR pressionado")
                            usb.write(b"MT0 MR")
                            threading.Timer(0.1, Timer_Pause).start()

                    elif flag_BTX_press == 1:
                        if event.state == 0:
                            flag_BTX_press = 2
                            if flag_pause == 0:
                                usb.write(b"MT0 MP")
                                threading.Timer(0.1, Timer_BTX_Press).start()

            # Check if the event code is "ABS_HAT0Y"
            if event.code == "ABS_HAT0Y":
                if flag_start:                  # Check if flag_start is enable
                    if flag_BTX_press == 0 and flag_BTY_press == 0:
                        if event.state == -1:       # Check state (front direction) of the button
                            flag_BTY_press = 1
                            flag_pause = 1
                            print("Botão FRENTE pressionado")
                            usb.write(b"MT0 MF")
                            threading.Timer(0.1, Timer_Pause).start()

                        elif event.state == 1:      # Check state (back direction) of the button
                            flag_BTY_press = 1
                            flag_pause = 1
                            print("Botão TRAS pressionado")
                            usb.write(b"MT0 MB")
                            threading.Timer(0.1, Timer_Pause).start()

                    elif flag_BTY_press == 1:
                        if event.state == 0:
                            flag_BTY_press = 2
                            if flag_pause == 0:
                                usb.write(b"MT0 MP")
                                threading.Timer(0.1, Timer_BTY_Press).start()
            
            ### Buttons to control the velocity ###
            # Check if the event code is "ABS_RZ"
            if event.code == "ABS_RZ":
                if event.state >= 1:            # Check if state is greater than 1 (button pressed)
                    if flag_BT_RZ == 0:
                        flag_BT_RZ = 1
                        flag_vel = 1
                        print("Botão RZ pressionado")
                        usb.write(b"MT0 MC MD0 AT100 DT100 V8")
                elif event.state == 0:
                    print("Botão RZ solto")
                    flag_BT_RZ = 0

            # Check if the event code is "ABS_Z"
            if event.code == "ABS_Z":
                if event.state >= 1:            # Check if state is greater than 1 (button pressed)
                    if flag_BT_Z == 0:
                        flag_BT_Z = 1
                        flag_vel = 0
                        print("Botão Z pressionado")
                        usb.write(b"MT0 MC MD0 AT100 DT100 V4")
                elif event.state == 0:
                    print("Botão Z solto")
                    flag_BT_Z = 0

