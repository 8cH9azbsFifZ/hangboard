""" 
Class for handling all aspects of a hangboard configuration.
"""

import json

import xml.etree.ElementTree as ET
from pathlib import Path

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
        # TODO implement #65

    def get_board(self):
        """
        Get the board configuration (STUB)
        """
        # TODO implement #65

    def init_board (self):
        self.board_status = ""
        self.boardfilename = "./board_data/" + self.boardname + "/holds.json" 

        with open(self.boardfilename) as json_file:
            self.boarddata = json.load(json_file)

        self._get_all_holds()

        self.boardname_full = self.boarddata["Name"]

    def set_active_holds(self, array_holds):
        logging.debug("Set active holds")
        self.holds_active = array_holds
        self.holds_inactive = [x for x in self.all_holds if x not in array_holds]
        logging.debug (self.holds_active)
        logging.debug (self.holds_inactive)

    def _get_all_holds(self):
        self.all_holds = []
        #print (self.boarddata["Holds"])
        for hold in self.boarddata["Holds"]:
            #print (hold["ImgLayerName"])
            self.all_holds.append(hold["ImgLayerName"])

    def get_hold_for_type(self, type):
        logging.debug("Get holds for type " + str(type))
        if type == "":
            return [""]
        holds = []
        for hold in self.boarddata["Holds"]:
            if (hold["Name"] == type):
                holds.append(hold["ImgLayerName"])
        logging.debug (holds)
        return holds

    def GetTypeForHold(self, hold):
        for hold in self.boarddata["Holds"]:
            if hold["ImgLayerName"] == hold:
                return hold["Name"]
        return ""


"""
Example empty board A1 ... C7:
.......
.......
.......  
Example used holds B1, B7: 4 fingers
.......
4.....4
.......
"""
class AsciiBoard(): # TODO continue implementation #82
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
    boardname = "zlagboard_evo"
    a = Board(boardname=boardname)

    # Test: holds for JUG
    h = a.get_hold_for_type("JUG")
    print (h[0])
    print (h[-1])

    # Test: All holds
    print (a.all_holds)

   