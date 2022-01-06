from board import Board
from svg_board import SVGBoard

if __name__ == "__main__":
    a = Board()
    svg = SVGBoard(boardname="zlagboard_evo")
    svg.generate_all_images(holds=a.all_holds) 
