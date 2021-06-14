# Hangboard Hold configuration
This directory contains the hold configurations for different boards

# Boards
## Zlagboard EVO

## Zlagboard Mini

## Beastmaker 1000
+ Hold sizes: https://rupertgatterbauer.com/beastmaker-1000/#:~:text=Speaking%20of%20design%2C%20the%20Beasmaker,slopers%20and%20pull%2Dup%20jugs.

## Beastmaker 2000

# Implement new board configurations

## Preparation
+ Install inkscape `brew install inkscape`

## Work
+ Create a new board json file 
+ Use inkscape with layers for overlay image creation 
+ Edit layer "id" names manually afterwards
+ change all style:: display:inline => inline
+ Use colors: 979797 and d8d8d8
+ Export layers as svg: https://github.com/james-bird/layer-to-svg (cf. current dir)
+ Change colors of overlays to: d8d8d8 -> 979797
+ Export all layers as svg and convert them to png (i.e. https://svgtopng.com/de/)
+ Converting to PNG? `brew install librsvg`




# References 
+ Excellent project with a similar idea: https://github.com/gitaaron/boards
