import os
import csv
import json 
import requests

# Opening JSON file 
f = open('yoga.json',) 
  
# returns JSON object as a dictionary 
data = json.load(f) 

#Close file
f.close() 

#Create output CVS file
mf = open("yoga.csv", "a")

#write headers row
mf.write("NAME_GARMIN"+";"+"CATEGORY_GARMIN"+";"+"Name"+";"+"Detailed"+";"+"Body parts"+";"+"Difficulty"+";"+"Equipment"+";"+"Focus"+";"+"Description"+";"+"Image1"+";"+"Image2"+";"+"URL"+";"+"\n")

# Iterating through the json list 
for category in data['categories']: 
    
    for exercise in data['categories'][category]['exercises']:
        
        #set default values (when there is no detail for exercice)
        NAME_GARMIN = exercise
        CATEGORY_GARMIN = category
        Name = exercise.replace('_',' ').title()
        Detailed = "0"
        Body_parts = ""
        Difficulty = ""
        Equipment = ""
        Focus = ""
        Description = ""
        Image1 = ""
        Image2 = ""
        URL = ""

        #URL based on known path and exercice name
        URLjson = 'https://connect.garmin.com/web-data/exercises/en-US/' + category+"/"+exercise + '.json'
        page = requests.get(URLjson)

        #if page exists (200), then there are details for the exercice
        if page.status_code == 200:

            exdata = json.loads(page.text)

            Detailed = "1"
            Body_parts = exdata['bodyParts']
            Difficulty = exdata['difficulty']
            Equipment = exdata['equipment']
            Focus = exdata['focuses']
            Description = exdata['description']
            
            #try if there are images availables (I try just 2, but when there are, there are usually more)
            try:
                Image1 = exdata['videos'][0]['thumbnail']
            except:
                Image1 = ""
            try:
                Image2 = exdata['videos'][1]['thumbnail']
            except:
                Image2 = ""

            URL = "https://connect.garmin.com/modern/exercises/"+category+"/"+exercise

        #print the name of exercice (to see what's happening while the script is running)
        print(exercise)

        #write the row data with exercice
        mf.write(NAME_GARMIN+";"+CATEGORY_GARMIN+";"+Name+";"+Detailed+";"+Body_parts+";"+Difficulty+";"+Equipment+";"+Focus+";"+Description+";"+Image1+";"+Image2+";"+URL+";"+"\n")

#close output file
mf.close()
