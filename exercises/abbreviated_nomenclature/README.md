# Abbreviated nomenclature for smart timer creation
Hangboard protocols should be easy to read with a simple universal (hangboard independent) notation.
The following notation is based on the work of Eva Lopez.

## Abbreviated syntax
The following entry:
```
2x 3x Hang @25mm +0kg #4;Open 7(3)s:57s
```
translates as
```
2x      3x      Hang       @18mm              4F       Crimp  0             7                    3               60
[#sets] <#reps> <Exercise> <Hold[left;right]> [Finger] [Grip] [AddedWeight] <HangTime[(Margin)]> <PauseRepTime> [PauseSetTime]
```
- #sets: [0-9]x
- #reps: [0-9]x
- Exercise: [Any Name]
- Hold: @[0-9]mm   or   if left/right different: @[0-9]mm;[0-9]mm   or   @[0-9]° for Slopers   or   @Jug
- Finger: [1-4]F
- Grip: Text
- AddedWeight: +[0-9]kg   or   -[0-9]kg
- Hangtime: [0-9]   time in seconds

## Examples:
+ 2x 3x Hang @18mm &4 §Crimp W+5kg 7:3:60s
+ 2x 7x Hang @Jug 7:3:150s
+ 2x 7x Hang @45mm &Front3 §Open 7:3:150s
+ 2x 7x Hang @45mm &4 §Open 7:3:150s
+ 3x MEDHang @18mm 7(3):180s
+ 3x MAXHang @30mm W+10kg 7(3):180s

## FIXME:  Not implemented yet: ranges...


# Eva López strength for Reference
+ 3x MEDHang @5-10mm 7(3):180s
+ 2-5x MAXHang @8-22mm W+5-55kg 5-15(1-5):180-300s


# Eva López SubHangs MED strength endurance for Reference
+ 4-8x Hang @8-22mm 20-45(30-120)s
+ 4-8x SubHangsMED @8-22mm 20-45(30-120)s
+ 4-8x SubHangsMAX @14-20mm 20-45(30-120)s

# Eva López IntHangs MED strength endurance for Reference
+ 3-5x 4-5x Hang @8-22mm 7-10(3-30)60-120s
+ 3-5x 4-5x IntHangsMED @8-22mm 7-10(3-30)60-120s
+ 3-5x 4-5x IntHangsMAX @10-18mm 7-10(3-30)60-120s


# Warmup Routine for Reference
+ 5x Hang @Jug 10:20:60s
+ 5x 4xPullup @Jug 0:20:60s
+ 5x Hang @30mm 10:20:120s
+ 5x 5xPullup @30mm 0:30s


# Beasty 5A for reference
+ 2x 7x Hang @Jug 7:3:150s
+ 2x 7x Hang @45mm &Front3 §Open 7:3:150s
+ 2x 7x Hang @45mm &4 §Open 7:3:150s
+ 2x 7x Hang @Jug 7:3:150s
+ 2x 7x Hang @45mm &Front3 §Open 7:3:150s
+ 2x 7x Hang @45mm &4 §Open 7:3:150s


# Basic Power Endurance
+ 1x 5x Hang @Jug 10:20:120s
+ 1x 5x PullUps @Jug 2x:20:120s
+ 1x 5x Hang @30mm &Front3 10:20:120s
+ 1x 5x PullUps @30mm &Front3 2x:20:120s
+ 3x 10x Hang @30mm &Front3 6:6:180s
+ 2x 5x PullUps @Jug 4x:30:120s
+ 1x Pause 3-5min
+ 2x 1x MaximumHang @30mm &Front3 AsLongAsPossible:0:180s


# Density Hangs (Nelson)
Ref: https://strengthclimbing.com/dr-tyler-nelsons-density-hangs-finger-training-for-rock-climbing/

+ 4-9x 2-3x 20-40:10-20:180-300s
+ Hang:Rest = 1:2 Ratio
+ MVC-7 load	55 - 85%
   Density hangs are ideally performed without added load, at around 75% of maximum strength (MVC-7)
+ A typical training cycle is 4 – 5 weeks.


# Debugging

## Standard
* square brackets [optional option]
* angle brackets <required argument>
* curly braces {default values}
* parenthesis (miscellaneous info)
* Reference: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html

## JSON format for reference
{ "Rest-to-Start": 5,       
"Exercise": "Hang", 			    
"Counter": 12, 	
"Pause": 180,    
"Reps": 5, 
"Left": "15mm", 
"Right": "15mm", 
"Description": "Do a 12-second hang using a feature that you can barely hold for 15 seconds with maximum effort.",
"No": 1, 
"Fingers": 4, 
"Grip": "Open", 
"Type": "Hang",
"Intensity": 0.35
}
