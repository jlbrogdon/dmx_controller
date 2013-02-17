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
from pyftdi.pyftdi import ftdi

#FTDI device info
vendor=0x0403
product=0x6001

#####################
# DMX USB controller
#####################
class OpenDmxUsb():
    def __init__(self):
        self.baud_rate = 250000
        self.data_bits = 8
        self.stop_bits = 2
        self.parity = 'N'
        self.flow_ctrl = ''
        self.rts_state = 0
        self._init_dmx()

    #Initialize the controller
    def _init_dmx(self):
        self.ftdi=ftdi.Ftdi()
        self.ftdi.open(vendor,product,0)
        self.ftdi.set_baudrate(self.baud_rate)
        self.ftdi.set_line_property(self.data_bits,self.stop_bits,self.parity,break_=0)
        self.ftdi.set_flowctrl(self.flow_ctrl)
        self.ftdi.purge_rx_buffer()
        self.ftdi.purge_tx_buffer()
        self.ftdi.set_rts(self.rts_state)

    #Send DMX data
    def send_dmx(self,channelVals):
        self.ftdi.write_data(channelVals)
        # Need to generate two bits for break
        self.ftdi.set_line_property(self.data_bits,self.stop_bits,self.parity,break_=1)
        self.ftdi.set_line_property(self.data_bits,self.stop_bits,self.parity,break_=1)
        self.ftdi.set_line_property(self.data_bits,self.stop_bits,self.parity,break_=0)            

if __name__=="__main__":
    dmxUsb=OpenDmxUsb()

    channelVals=bytearray([0]*513)
    channelVals[0]=0 # dummy channel 0
    while(True):
        channelVals[1]=10
        dmxUsb.send_dmx(channelVals)
