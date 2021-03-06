""" 
Class for handling all aspects of a hangboard configuration.
"""

import json

import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Board(%(threadName)-10s) %(message)s',
                    )


class Board():
    """
    All stuff for handling hangboard configurations.
    """
    def __init__(self, verbose=None, boardname = "zlagboard_evo", basedir="./"):
        self.boardname = boardname
        self.basedir = basedir
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
        self.boardfilename = self.basedir + "board_data/" + self.boardname + "/holds.json" 
        self.cachedir = self.basedir + "cache/"
        self.boardimagename_png = self.basedir + "board_data/" + self.boardname + "/board.png" 

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

    def _cache_png_filename (self, left="A1", right="A7"):
        """
        Find Image name in cache dir
        """
        filename = self.cachedir + self.boardname + "." + left + "." + right + ".png" 
        return filename

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
        # Find perfect match
        for hold in self.boarddata["Holds"]:
            if (hold["Name"] == type):
                holds.append(hold["ImgLayerName"])
        
        # Find nearest match
        if len(holds) == 0:
            dd = [] # delta depths array (mm)
            d1 = int(type.replace("mm",""))
            for hold in self.boarddata["Holds"]:
                h = hold["Name"]
                d2 = -100# for jug etc?
                if h[-2:] == "mm": # if hold ends with mm
                    l = h[-5:]  # last 5 chars of hold contain the length
                    d2 = int(l.replace("mm",""))
                delta = abs (d2-d1)
                #print (h, d1, d2,delta)
                dd.append(delta)

            dmin = min(dd) # FIXME del
            x = np.array(dd)
            dmin1, dmin2 = np.partition(x, 1)[0:2]

            #print ("min ",dmin)
            #index_min = min(range(len(dd)), key=dd.__getitem__)
            i = 0
            for ddd in dd:
                h = self.boarddata["Holds"][i]["ImgLayerName"]
                #print (i, ddd, h)
                if ddd == dmin1 or ddd == dmin2:
                    holds.append(h)
                i = i + 1


        logging.debug (holds)
        return holds

    def GetTypeForHold(self, hold):
        for hold in self.boarddata["Holds"]:
            if hold["ImgLayerName"] == hold:
                return hold["Name"]
        return ""


if __name__ == "__main__":
    boardname = "zlagboard_evo"
    a = Board(boardname=boardname)

    # Test: holds for JUG
    #h = a.get_hold_for_type("JUG")
    h = a.get_hold_for_type("45mm")
    h = a.get_hold_for_type("23mm")

    #print (h[0])
    #print (h[-1])

    # Test: All holds
    #print (a.all_holds)

   