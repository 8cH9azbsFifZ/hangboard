/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow strict-local
 */

import React from 'react';
import type {Node} from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  Image,
  Button,
  ImageBackground
} from 'react-native';

import { useState } from 'react';


import AudioTest from "./AudioTest.web"; // FIXME

import ImageBoard from "./board.png"; // FIXME
import ImageA7 from "./A7.png"; 
import ImageA1 from "./A1.png"; 

import ReconnectingWebSocket from 'reconnecting-websocket';

var client = new ReconnectingWebSocket ('ws://10.101.40.81:4321/'); // FIXME


const Section = ({children, title}): Node => {
  const isDarkMode = useColorScheme() === 'dark';
  return (
    <View style={styles.sectionContainer}>
      <Text
        style={[
        ]}>
        {title}
      </Text>
      <Text
        style={[
          styles.sectionDescription,
          {
          },
        ]}>
        {children}
      </Text>
    </View>
  );
};


const App: () => Node = () => {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {

  };

  const [myText, setMyText] = useState("My Original Text");// FIXME 
  const [myState, setMyState] = useState("");
 
  const [ImageHold1, SetImageHold1] = useState(ImageBoard);
  const [ImageHold2, SetImageHold2] = useState(ImageBoard);

  const TestImage = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAzCAYAAAA6oTAqAAAAEXRFWHRTb2Z0d2FyZQBwbmdjcnVzaEB1SfMAAABQSURBVGje7dSxCQBACARB+2/ab8BEeQNhFi6WSYzYLYudDQYGBgYGBgYGBgYGBgYGBgZmcvDqYGBgmhivGQYGBgYGBgYGBgYGBgYGBgbmQw+P/eMrC5UTVAAAAABJRU5ErkJggg==';
  const [ImageTest, SetImageTest] = useState(TestImage); // Test image

  

  client.onmessage = function(e) {
    if (typeof e.data === 'string') {
      console.log("Received: '" + e.data + "'");
    }
    var parsed = JSON.parse(e.data);
    var counter = parseFloat(parsed.Counter).toFixed(2); //Counter
    var currentcounter = parseFloat(parsed.CurrentCounter).toFixed(2); // CurrentCounter
    var togo = counter - currentcounter; 
    togo.toFixed(2);

    setMyState(parsed);
    setMyText("Exercise: " + parsed.Exercise + " for " + parseInt(counter) + "(s) and still " + parseInt(togo) + "(s) remaining."); 

    if (parsed.Left.includes("A1")) { SetImageHold1 (ImageA1);  } else { SetImageHold1(ImageBoard); }// FIXME 
    if (parsed.Right.includes("A7")) { SetImageHold2 (ImageA7); } else { SetImageHold2(ImageBoard); }

  
    //var array = parsed.HoldsActive; 
    //array.forEach(element => ImageHold1 = element);
    //array.forEach(element => window[element].setAttribute("display","inline") ); // FIXME 

/*
    if (togo-1 == 10.) { SFXten.play(); } 
    if (togo-1 == 9.) { SFXnine.play(); } 
    if (togo-1 == 8.) { SFXeight.play(); } 
    if (togo-1 == 7.) { SFXseven.play(); } 
    if (togo-1 == 6.) { SFXsix.play(); } 
    if (togo-1 == 5.) { SFXfive.play(); } 
    if (togo-1 == 4.) { SFXfour.play(); } 
    if (togo-1 == 3.) { SFXthree.play(); } 
    if (togo-1 == 2.) { SFXtwo.play(); } 
    if (togo-1 == 1.) { SFXone.play(); } 
    if (togo-1 == 0.) { SFXdone.play(); } 
  
    */

   // if (parsed.HangChangeDetected == "Hang") { SFXstarthang.play() ; }
   // if (parsed.HangChangeDetected == "NoHang") { SFXstophang.play() ; }
 

  }; 

  const sendStart = () =>
  {
    //console.log("Sending");
    client.send("Start");
  }

  const sendStop = () =>
  {
    //console.log("Sending");
    client.send("Stop");
  }

 

  return (
 

    <SafeAreaView style={backgroundStyle}>
     
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
      <ScrollView
        contentInsetAdjustmentBehavior="automatic"
        style={backgroundStyle}>

        <View
          style={{
          }}>
          <ImageBackground source={ImageBoard} style={{flex:1, height: 200, width: undefined}} resizeMode="contain"> 
               <ImageBackground source={ImageHold1} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain">
                <ImageBackground source={ImageHold2} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain"/>     
              </ImageBackground>
          </ImageBackground>

          <Section title="Backend Exercise">
            <Text>
              {myText}
            </Text>
          </Section>
     
          <Section title="Controls">
            <Button title="Start" onPress = {() => sendStart()} />
            <Button title="Stop" onPress = {() => sendStop()} />
          </Section>
          <Section title="Parsed">
            <Text>
              {myState.Duration}
              <AudioTest effect="SFXone"/>
            </Text>
          </Section>        
        </View>

        <View >
          <Section title="Testing Image Transfer"> 
          </Section>
          <ImageBackground source={{ uri: ImageTest}} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain"/>     
        </View>


      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  sectionContainer: {
    marginTop: 32,
    paddingHorizontal: 24,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '600',
  },
  sectionDescription: {
    marginTop: 8,
    fontSize: 18,
    fontWeight: '400',
  },
  highlight: {
    fontWeight: '700',
  },
});

export default App;
