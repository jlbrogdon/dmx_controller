#!/usr/bin/python
#######################################################
# DMX Controller
# See <TBD>
# Copyright (C) Jonathan Brogdon <jlbrogdon@gmail.com>
# This program is published under a GPLv2 license
#
# This code implements a DMX controller with UI provided
# by LCDproc
#
#######################################################
from DmxUi import DmxUi
from OpenDmxUsb import OpenDmxUsb
import Queue
import threading
import signal

# Thread lock serves as a signal to thread to terminate
termLock = threading.Lock()

# Tuple list of colors and corresponding
# Colorstrip channel value
static_color = [('RED'    ,10),
                ('GREEN'  ,20),
                ('BLUE'   ,30),
                ('YELLOW' ,40),
                ('MAGENTA',50),
                ('CYAN'   ,60),
                ('WHITE'  ,70)]

#Asynchronous signal handler.  Terminates threads.
def sig_handler(signum,frame):
    termLock.acquire()

######################
# DMX Control thread
######################
class DmxThread(threading.Thread):
    def __init__(self,dmxUsb,queue,tlock=None):
        threading.Thread.__init__(self)
        self.dmxUsb = dmxUsb #DMX/USB controller
        self.queue = queue   #DMX data queue
        self.tlock = tlock   #thread termination lock

    def run(self):
        channelVals = None
        while (False==self.tlock.locked()):
            #Check for new DMX data
            if (self.queue.empty() == False):
                #New values available
                channelVals = self.queue.get()
                self.queue.task_done()
            if channelVals != None:
                #Send the data to the devices
                self.dmxUsb.send_dmx(channelVals)

#################
# LCD UI thread
#################
class UiThread(threading.Thread):
    def __init__(self,dmx_ui,color_list,queue,tlock=None):
        threading.Thread.__init__(self)
        self.dmx_ui = dmx_ui         #DMX UI device
        self.color_list = color_list #Color list
        self.queue = queue           #DMX data queue
        self.tlock = tlock

    def run(self):
        channel_vals = bytearray([0]*513)
        channel_vals[0]=0 #dummy channel

        #Set Initial value
        channel_vals[1]=self.color_list[0][1]

        #Send the DMX data
        self.queue.put(channel_vals)

        while (False==self.tlock.locked()):
            #Check for UI input
            color_idx=self.dmx_ui.ui_process()
            if (color_idx != None):
                #New color value input
                channel_vals[1]=self.color_list[color_idx][1]
                #Send the new DMX data
                self.queue.put(channel_vals)

if __name__ == "__main__":
    #Install signal handler for SIGTERM
    signal.signal(signal.SIGTERM,sig_handler)

    #Queue for new DMX data
    channelsQueue=Queue.Queue()

    #DMX/USB controller
    dmx_usb = OpenDmxUsb()

    #UI controller
    dmx_ui = DmxUi(static_color)

    #DMX/USB controller thread
    dmx_thread = DmxThread(dmx_usb,channelsQueue,tlock=termLock)

    #UI controller thread
    ui_thread  = UiThread(dmx_ui,static_color,channelsQueue,tlock=termLock)

    #Start the DMX/USB controller thread
    dmx_thread.setDaemon(True)
    dmx_thread.start()

    #Start the UI controller thread
    ui_thread.setDaemon(True)
    ui_thread.start()

    #Wait for SIGTERM
    signal.pause()

    #Wait for threads to terminate
    dmx_thread.join()
    ui_thread.join()
