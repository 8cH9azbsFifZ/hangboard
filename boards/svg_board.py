""" 
Class for handling all aspects of a hangboard configuration.
"""

import json
import base64

import xml.etree.ElementTree as ET
from pathlib import Path

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
# FIXME: raspi must not use this, but: inkscape -w 1024 -h 1024 input.svg -o output.png



import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Board(%(threadName)-10s) %(message)s',
                    )

class SVGBoard():
    def __init__(self, verbose=None, boardname = "zlagboard_evo"):
        self.boardname = boardname
        self.boardimagename = "./board_data/" + boardname + "/board.svg" 
        self.boardimagename_png = "./board_data/" + boardname + "/board.png" 
        self.cachedir = "./cache/"
        Path(self.cachedir).mkdir(parents=True, exist_ok=True)

        self.left_color = "#00ff00"
        self.right_color = "#ff0000"
 

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

    def _cache_png_filename (self, left="A1", right="A7"):
        """
        Find Image name in cache dir
        """
        filename = self.cachedir + self.boardname + "." + left + "." + right + ".png" 
        return filename

    def Hold2SVG(self, left="A1", right="A7", garmincolors=False):
        """
        Render image for hold configuration

        garmincolors parameter?
        Configure the colors of the board SVGs for a garmin watch
        Board_Name - invisible
        Board_Background - black
        Board_Border - blue
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
            
            if (garmincolors == True):
                if (name == "Board_Name"):
                    style = style.replace( 'display:inline', 'display:none' )

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

        self._svg_to_png(self.boardimagename)
        # FIXME: put board png to cache dir #83

    def _svg_to_png(self, filename): 
        outfile = filename.replace(".svg",".png")
        drawing = svg2rlg(filename)
        renderPM.drawToFile(drawing, outfile, fmt="PNG")


if __name__ == "__main__":
    svg = SVGBoard()
    #svg.Hold2SVG()    
    #svg.generate_all_images(holds=a.all_holds)

    #svg.Hold2SVG(left="C1",right="C7")

    #svg._svg_to_png(svg._cache_svg_filename("C1","C7"))
    #svg._write_image_to_db("C1","C7")   