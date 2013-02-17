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
from lcdproc.server import Server

###########################################
# LCD UI controller for the DMX controller
###########################################
class DmxUi():
    def __init__(self,color_list):
        self.color_list=color_list
        self.lcd = Server("127.0.0.1", debug=False)
        self.lcd.start_session()
        self.lcd.add_key("Up",mode="exclusively")
        self.lcd.add_key("Down",mode="exclusively")
        self.lcd.add_key("Enter",mode="exclusively")

        #Allocate the screen
        self.screen = self.lcd.add_screen("DMX")
        self.screen.set_heartbeat("off")

        #Add a widget for the label
        self.label_widget = self.screen.add_string_widget("label_widget",
                                                          text="",x=1,y=1)
        #Add a widget for the color
        self.color_widget = self.screen.add_string_widget("color_widget",
                                                          text="",x=7,y=1)
        #Add a widget to display the "selected" status
        self.not_set_widget = self.screen.add_string_widget("not_set_widget",
                                                            text="",x=16,y=1)
        #Set the label text
        self.label_widget.set_text("Color:")

        self.color_idx=0
        self.current_color_idx=0
        self.color_widget.set_text(self.color_list[self.color_idx][0])    
        self.num_colors = len(self.color_list)

    # Get a key from LCDproc
    def get_key(self):
        resp = self.lcd.poll()
        if (resp == None):
            return None

        return resp[4:-1]

    # UI processing
    # -get keyinput
    # -update display
    # -return the current selection
    def ui_process(self):

        key_press = self.get_key()

        if (key_press==None):
            return None
        
        if (key_press == "Up"):
            self.color_idx -= 1

        if (key_press == "Down"):
            self.color_idx += 1

        self.color_idx %= self.num_colors

        if (key_press == "Enter"):
            self.current_color_idx = self.color_idx

        if (self.color_idx != self.current_color_idx):
            self.not_set_widget.set_text("*")
        else:
            self.not_set_widget.set_text("")

        self.color_widget.set_text(self.color_list[self.color_idx][0])

        return self.current_color_idx
        

if __name__ == "__main__":

    color = [('RED'    ,10),
             ('GREEN'  ,20),
             ('BLUE'   ,30),
             ('YELLOW' ,40),
             ('MAGENTA',50),
             ('CYAN'   ,60),
             ('WHITE'  ,70)]

    dmxUi=DmxUi(color)
    while(True):
        val=dmxUi.ui_process()
        if (val != None):
            print val
