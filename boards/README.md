# Hangboard configuration

## Contents
- board_data contains the hangboard SVG images and hold setups
- lib contains svg libraries
- board_mount contains information on how to build a board mount

## List of implemented hangboards
- Beastmaker 1000
- Beastmaker 2000
- Cliffboard Mini
- Crusher 3
- Linebreaker Base
- Metolius Prime
- Metolius Project
- Metolius Simulator 3D
- Metolius Wood Grips 2 Compact
- Monster
- Mountain Rocks
- Redge Port
- Roots Baseline
- Simond Ballsy Board
- Topout Project
- Zlagboard Evo
- Zlagboard Mini

TIP: Your hangboard is not supported yet? It can be added easily. Just open a ticket: 
https://github.com/8cH9azbsFifZ/hangboard/issues/new

NOTE: Most of the boards configuration has been merged from the excellent project <<Boards>>.


# Hangboards
For every hangboard supported there is a JSON file containing the hold names and dimensions and an SVG image with all the holds.

Luckily there is a similar project and lots of configurations are already implemented <<Boards>>. These boards have been merged to this
repository.
Measuring a hangboard is lots of work, i.e. <<Beastmaker1000HoldSizes>>.


## Implement new board configurations

- Install inkscape `brew install inkscape`
- Create a new board json file 
- Use inkscape with layers for overlay image creation 
- Edit layer "id" names manually afterwards in any editor
- change all style:: display:inline => inline
- Use colors: 979797 and d8d8d8
- Export layers as svg: https://github.com/james-bird/layer-to-svg (cf. boards directory)
- Change colors of overlays to: d8d8d8 -> 979797
- Export all layers as svg and convert them to png (i.e. https://svgtopng.com/de/)
- Conversion to PNG for all permutations can be done using the `backend/generate_all_board_images.py` script.
- Put all PNG images to `flutter_hangboard/images`

# References
<a id="Beastmaker1000HoldSizes">[1]</a> Accurate measurements of the Beastmaker 1000 hold dimensions: https://rupertgatterbauer.com/beastmaker-1000/#:~:text=Speaking%20of%20design%2C%20the%20Beasmaker,slopers%20and%20pull%2Dup%20jugs.
<a id="Boards">[2]</a> Project with lots of hangboard configurations: https://github.com/gitaaron/boards
+ Universal mount for hangboards in door frames https://smartrock.de/?lang=de