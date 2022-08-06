from board import Board
from svg_board import SVGBoard
import os

if __name__ == "__main__":
    a = Board()
    svg = SVGBoard(boardname="zlagboard_evo")
    svg.generate_all_images_garmin(holds=a.all_holds) 

    print ("ok") # FIXME: needs imagemagick
    directory = os.fsencode(svg.cachedir)    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".png"): 
            print ("Re-Export file "+svg.cachedir+"/"+filename)
            os.system('inkscape --export-type="png" '+svg.cachedir+"/"+filename)
            print ("Reduce file "+svg.cachedir+"/"+filename)
            os.system("mogrify -geometry 200 "+svg.cachedir+"/"+filename)
            continue
        else:
            continue
