from board import Board, SVGBoard

if __name__ == "__main__":
    a = Board()
    svg = SVGBoard(boardname="zlagboard_evo")
    svg.generate_all_images(holds=a.all_holds) 
    # FIXME: all holds images must be genearted and put into assets directory of flutter app.. #83
