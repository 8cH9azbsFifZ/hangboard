""" 
Class for handling all aspects of a hangboard configuration.
"""

import json
import time
import base64


from tabulate import tabulate 
""" 
Use tabulate for an ASCII Hanboard display for debugging purposes
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Board(%(threadName)-10s) %(message)s',
                    )

class Board():
    """
    All stuff for handling hangboard configurations.
    """
    def __init__(self, verbose=None, boardname = "zlagboard_evo"):
        self.boardname = boardname
        self.init_board()


    def list_boards(self):
        logging.debug ("List all available boards.")
        # TODO implement

    def get_board(self):
        """
        Get the board configuration (STUB)
        """
        # TODO implement

    def init_board (self):
        # TODO rework for this version
        self.board_status = ""
        self.boardimage_base64 = ""
        self.boardfilename = "../boards/" + self.boardname + "/holds.json" 

        with open(self.boardfilename) as json_file:
            self.boarddata = json.load(json_file)

        self.get_all_holds()

        self.boardname_full = self.boarddata["Name"]
        self.boardimagename = "../boards/" + self.boardname + "/board.svg" 

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
        logging.debug("Set active holds")
        # TODO rework for this version
        self.holds_active = array_holds
        self.holds_inactive = [x for x in self.all_holds if x not in array_holds]
        logging.debug (self.holds_active)
        logging.debug (self.holds_inactive)

    def get_all_holds(self):
        # TODO rework for this version
        self.all_holds = []
        #print (self.boarddata["Holds"])
        for hold in self.boarddata["Holds"]:
            #print (hold["ImgLayerName"])
            self.all_holds.append(hold["ImgLayerName"])

    def get_hold_for_type(self, type):
        logging.debug("Get holds for type " + str(type))
        holds = []
        for hold in self.boarddata["Holds"]:
            if (hold["Name"] == type):
                holds.append(hold["ImgLayerName"])
        logging.debug (holds)
        return holds


class AsciiBoard():
    """
    All stuff for handling an ASCII output of the current hangboard configuration.
    """
    def __init__(self, verbose=None):
        self.set_board_default()
        self.render_board()

    def set_board_default(self):
        self.board_row1 = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"] # FIXME
        self.board_row2 = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]
        self.board_row3 = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]

    def set_active_holds(self):
        hold1 = "A1" #FIXME 
        hold2 = "A7"
        for index, item in enumerate(self.board_row1):
            if ((item == hold1) or (item == hold2)):
                self.board_row1[index] = "**"
            
    def render_board(self):
        self.board = (tabulate([self.board_row1, self.board_row2, self.board_row3], tablefmt="grid"))
        print (self.board)



if __name__ == "__main__":
    a = Board()
    h = a.get_hold_for_type("JUG")
    print (h[0])
    print (h[-1])