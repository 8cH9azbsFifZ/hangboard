""" 
Class for handling all aspects of a hangboard configuration.
"""

import json
import threading
from pydispatch import dispatcher
import time


from tabulate import tabulate 
""" 
Use tabulate for an ASCII Hanboard display for debugging purposes
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Board(%(threadName)-10s) %(message)s',
                    )


SIGNAL_BOARD = 'Board'
SIGNAL_ASCIIBOARD = 'AsciiBoard'

class Board(threading.Thread):
    """
    All stuff for handling hangboard configurations.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, boardname = "zlagboard_evo"):
        super(Board,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_BOARD, sender=dispatcher.Any )

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):
                return
            time.sleep(1)
        return

    def list_boards(self):
        logging.debug ("List all available boards.")
        # TODO implement


    def handle_signal (self, message):
        logging.debug('Board: Signal detected with ' + str(message) )
        """
        Execute commands as received from websocket (handler)
        """
        # TODO rework for this version
        #print("Received request: %s" % message)
        #if (message == "SetHolds"): # FIXME
        #    self.set_active_holds()  # FIXME: Parameter
        #if (message == "GetBoard"):
        #    self.get_board()

    def get_board(self):
        """
        Get the board configuration (STUB)
        """
        # TODO implement

    def init_board (self):
        # TODO rework for this version
        self.board_status = ""
        self.boardimage_base64 = ""
        self.boardfilename = "./" + self.boardname + "/holds.json" 

        with open(self.boardfilename) as json_file:
            self.boarddata = json.load(json_file)

        self.get_all_holds()

        self.boardname_full = self.boarddata["Name"]
        self.boardimagename = "./" + self.boardname + "/board.png" 

        self.get_image()

    def get_image(self):
        """
        Send board image as base64 over websocket
        """
        # TODO rework for this version
        #    
        with open(self.boardimagename, "rb") as image_file:
            self.boardimage_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        self.board_status = self.boardimage_base64 


    def set_active_holds(self, array_holds):
        # TODO rework for this version
        self.holds_active = array_holds
        self.holds_inactive = [x for x in self.all_holds if x not in array_holds]
        print (self.holds_active)
        print (self.holds_inactive)

    def get_all_holds(self):
        # TODO rework for this version
        self.all_holds = []
        #print (self.boarddata["Holds"])
        for hold in self.boarddata["Holds"]:
            #print (hold["ImgLayerName"])
            self.all_holds.append(hold["ImgLayerName"])

    def get_hold_for_type(self, type):
        # TODO rework for this version
        holds = []
        for hold in self.boarddata["Holds"]:
            if (hold["Name"] == type):
                holds.append(hold["ImgLayerName"])
        print (holds)


class AsciiBoard(threading.Thread):
    """
    All stuff for handling an ASCII output of the current hangboard configuration.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(AsciiBoard,self).__init__()
        self.target = target
        self.name = name
        self.do_stop = False
        self.daemon = True
        dispatcher.connect( self.handle_signal, signal=SIGNAL_ASCIIBOARD, sender=dispatcher.Any )

        self.set_board_default()
        self.render_board()

    def stop(self):
        self.do_stop = True
        logging.debug ("Try to stop")

    def run(self):
        while True:
            if (self.do_stop == True):
                return
            time.sleep(1)
        return

    def handle_signal (self, message):
        logging.debug('Asciiboard: Signal detected with ' + str(message) )
        if (message == "Hang"):
            self.set_active_holds()
        else:
            self.set_board_default()
        self.render_board()

    def set_board_default(self):
        self.board_row1 = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
        self.board_row2 = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]
        self.board_row3 = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]

    def set_active_holds(self):
        hold1 = "A1"
        hold2 = "A7"
        for index, item in enumerate(self.board_row1):
            if ((item == hold1) or (item == hold2)):
                self.board_row1[index] = "**"
            
    def render_board(self):
        self.board = (tabulate([self.board_row1, self.board_row2, self.board_row3], tablefmt="grid"))
        print (self.board)



if __name__ == "__main__":
    a = Board()