""" 
Class for handling all aspects of a hangboard configuration.
"""

import json
import time
import base64

import xml.etree.ElementTree as ET
from pathlib import Path

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from pymongo import MongoClient

from tabulate import tabulate 
""" 
Use tabulate for an ASCII Hanboard display for debugging purposes
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Board(%(threadName)-10s) %(message)s',
                    )

class SVGBoard():
    def __init__(self, verbose=None, boardname = "zlagboard_evo",
        dbhostname="hangboard", dbuser="root", dbpassword="rootpassword"):
        self.boardname = boardname
        self.boardimagename = "./board_data/" + boardname + "/board.svg" 
        self.cachedir = "./cache/"
        Path(self.cachedir).mkdir(parents=True, exist_ok=True)

        self.left_color = "#00ff00"
        self.right_color = "#ff0000"

        self._dbhostname=dbhostname
        self._dbport=27017
        self._dbuser=dbuser
        self._dbpassword=dbpassword
        self._dbname="hangboard"
        self._connect_to_db()

    def _select_image (self, left="", right=""):
        """
        Select the correct image - with or without selected holds
        """
        filename = self.boardimagename
        if ((left != "") or (right != "")):
            filename = self._cache_svg_filename(left,right)
        return filename

    def _cache_svg_filename (self, left="A1", right="A7"):
        """
        Find Image name in cache dir
        """
        filename = self.cachedir + self.boardname + "." + left + "." + right + ".svg" 
        return filename

    def Hold2SVG(self, left="A1", right="A7"):
        """
        Render image for hold configuration
        """
        print ("Create SVG image for "+left+" and "+right)

        self.tree = ET.parse(self.boardimagename)
        self.root = self.tree.getroot()

        outfile = self._cache_svg_filename(left,right)

        for g in self.root.findall('{http://www.w3.org/2000/svg}g'):
            name = g.get('{http://www.inkscape.org/namespaces/inkscape}label')
            style = g.get('style')
            if (name == left):
                style = style.replace( 'display:none', 'display:inline;' )
                for h in g.findall('{http://www.w3.org/2000/svg}path'):
                    style1 = h.get ("style")
                    style1 = style1.replace("fill:#d8d8d8", "fill:" + self.left_color)
                    h.set("style", style1)
                for h in g.findall('{http://www.w3.org/2000/svg}rect'):
                    style1 = h.get ("style")
                    style1 = style1.replace("fill:#d8d8d8", "fill:" + self.left_color)
                    h.set("style", style1)
            elif (name == right):
                style = style.replace( 'display:none', 'display:inline' )
                for h in g.findall('{http://www.w3.org/2000/svg}path'):
                    style1 = h.get ("style")
                    style1 = style1.replace("fill:#d8d8d8", "fill:" + self.right_color)
                    h.set("style", style1)		
                for h in g.findall('{http://www.w3.org/2000/svg}rect'):
                    style1 = h.get ("style")
                    style1 = style1.replace("fill:#d8d8d8", "fill:" + self.right_color)
                    h.set("style", style1)	
            elif (name == "Board_Shape"):
                style = style.replace( 'display:none', 'display:inline' )
            else:
                style = style.replace( 'display:inline', 'display:inline' )
            g.set('style', style)

        self.tree.write( outfile ) # FIXME   #83     

    def _get_image_base64(self, left="", right=""):
        """
        Get board image as base64 for storage in the database
        """
        self.current_image_filename = self._select_image(left,right)
        with open(self.current_image_filename, "rb") as image_file:
            self.current_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        return self.current_image_base64

    def _connect_to_db(self):
        """ Connect to the mongodb """
        self._db = MongoClient('mongodb://'+self._dbhostname+':'+str(self._dbport)+'/', username=self._dbuser,   password=self._dbpassword  )[self._dbname]

    def _write_image_to_db(self,left="",right=""):
        """ Write an encoded PNG to the database """
        _coll_images = self._db[self.boardname+"-images"]
        imgstring = self._get_image_base64(left=left, right=right)
        obj = {"Left" : left, "Right" : right, "PNG": imgstring}
        _coll_images.replace_one({"$and": [{"Left": left}, {"Right": right}]}, obj, upsert=True )

    def generate_all_images(self, holds=[]):
        """ Generate all images (hold combinations) for a given hangboard """
        holds.append("")
        for left in holds:
            for right in holds:
                #if (left == right):
                #    break
                self.Hold2SVG(left=left,right=right)
                self._svg_to_png(self._cache_svg_filename(left=left,right=right))
                #self._write_image_to_db(left=left,right=right) # FIXME make configurable

        self._svg_to_png(self.boardimagename)
        # FIXME: put board png to cache dir #83

    def _svg_to_png(self, filename): 
        outfile = filename.replace(".svg",".png")
        drawing = svg2rlg(filename)
        renderPM.drawToFile(drawing, outfile, fmt="PNG")




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

        self.svg = SVGBoard(boardname=self.boardname)

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

    svg = SVGBoard(boardname=boardname)
    #svg.Hold2SVG()    
    #svg.Hold2SVG(left="C1",right="C7")
    
    svg.generate_all_images(holds=a.all_holds)


    #svg._svg_to_png(svg._cache_svg_filename("C1","C7"))
    #svg._write_image_to_db("C1","C7")