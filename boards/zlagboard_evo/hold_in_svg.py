#! /usr/bin/python3
import xml.etree.ElementTree as ET
import os
import sys

def Hold2SVG(left="A1", right="A7", filename="board.svg", outfile="./test.svg"):
	tree = ET.parse(filename)
	root = tree.getroot()
		
	for g in root.findall('{http://www.w3.org/2000/svg}g'):
		name = g.get('{http://www.inkscape.org/namespaces/inkscape}label')
		style = g.get('style')
		#print (name)
		if (name == left):
			style = style.replace( 'display:none', 'display:inline;' )
			for h in g.findall('{http://www.w3.org/2000/svg}path'):
				style1 = h.get ("style")
				style1 = style1.replace("fill:#d8d8d8", "fill:#00ff00")
				h.set("style", style1)
			for h in g.findall('{http://www.w3.org/2000/svg}rect'):
				style1 = h.get ("style")
				style1 = style1.replace("fill:#d8d8d8", "fill:#00ff00")
				h.set("style", style1)
		elif (name == right):
			style = style.replace( 'display:none', 'display:inline' )
			for h in g.findall('{http://www.w3.org/2000/svg}path'):
				style1 = h.get ("style")
				style1 = style1.replace("fill:#d8d8d8", "fill:#ff0000")
				h.set("style", style1)		
			for h in g.findall('{http://www.w3.org/2000/svg}rect'):
				style1 = h.get ("style")
				style1 = style1.replace("fill:#d8d8d8", "fill:#ff0000")
				h.set("style", style1)	
		elif (name == "Board_Shape"):
			style = style.replace( 'display:none', 'display:inline' )
		else:
			style = style.replace( 'display:inline', 'display:inline' )
			#print (h.get("style"))
		g.set('style', style)

	tree.write( outfile )

Hold2SVG(left="B2",right="C2")