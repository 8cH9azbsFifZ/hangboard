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


import AudioTest from "./AudioTest.web";


import ReconnectingWebSocket from 'reconnecting-websocket';

var client = new ReconnectingWebSocket ('ws://10.101.40.81:4321/'); // FIXME
var clientBoard = new ReconnectingWebSocket ('ws://10.101.40.81:4324/'); // FIXME
var wsGyroscope = new ReconnectingWebSocket("ws://10.101.40.81:4323/");// FIXME


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


const gz1: () => Node = () => {
  return (
    <Text>Test</Text>
   )
}


const App: () => Node = () => {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {

  };

  const [myText, setMyText] = useState("My Original Text");// FIXME 
  const [myState, setMyState] = useState("");

  const ImageBoard = require("./board.png"); // FIXME 
  const ImageA1 = require("./A1.png");// FIXME 
  const ImageA7 = require("./A7.png");// FIXME 
  
  const [ImageHold1, SetImageHold1] = useState(ImageBoard);
  const [ImageHold2, SetImageHold2] = useState(ImageBoard);
  //var ImageHold2 = ImageBoard;

  const [ImageTest, SetImageTest] = useState('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAzCAYAAAA6oTAqAAAAEXRFWHRTb2Z0d2FyZQBwbmdjcnVzaEB1SfMAAABQSURBVGje7dSxCQBACARB+2/ab8BEeQNhFi6WSYzYLYudDQYGBgYGBgYGBgYGBgYGBgZmcvDqYGBgmhivGQYGBgYGBgYGBgYGBgYGBgbmQw+P/eMrC5UTVAAAAABJRU5ErkJggg=='); // Test image

  clientBoard.onmessage = function(e) {
    SetImageTest('data:image/png;base64,' + e.data);
  }

  wsGyroscope.onmessage = function(e) {
    if (typeof e.data === 'string') {
      var mydata = e.data;
      console.log("Received: '" + e.data + "'");
    }

    var parsed = JSON.parse(e.data);
    if (parsed.HangStateChanged == true)
    {
      //if (parsed.HangDetected == true) { SFXstarthang.play() ; }
      //if (parsed.HangDetected == false) { SFXstophang.play() ; }
    }
  }

  client.onmessage = function(e) {
    if (typeof e.data === 'string') {
      var mydata = e.data;
      console.log("Received: '" + e.data + "'");
    }

    var parsed = JSON.parse(e.data);
    var togo = parsed.Duration - parsed.Counter;

    setMyState(parsed);
    setMyText("Exercise: " + parsed.Exercise + " for " + parsed.Duration + "(s) and still " + togo + "(s) remaining."); 

    if (parsed.HoldsActive.includes("A1")) { SetImageHold1 (ImageA1);  } else { SetImageHold1(ImageBoard); }// FIXME 
    if (parsed.HoldsActive.includes("A7")) { SetImageHold2 (ImageA7); } else { SetImageHold2(ImageBoard); }

  
    //var array = parsed.HoldsActive; 
    //array.forEach(element => ImageHold1 = element);
    //array.forEach(element => window[element].setAttribute("display","inline") ); // FIXME 

    if (parsed.TimerStatus == false)
    {
    /*  if (togo == 10) { SFXten.play(); } 
      if (togo == 9) { SFXnine.play(); } 
      if (togo == 8) { SFXeight.play(); } 
      if (togo == 7) { SFXseven.play(); } 
      if (togo == 6) { SFXsix.play(); } 
      if (togo == 5) { SFXfive.play(); } 
      if (togo == 4) { SFXfour.play(); } 
      if (togo == 3) { SFXthree.play(); } 
      if (togo == 2) { SFXtwo.play(); } 
      if (togo == 1) { SFXone.play(); } */
      //if (togo == 0) { SFXdone.play(); } 
    }
    
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

  let audio = new Audio("./done.mp3");

  const startit = () => {
    audio.play();
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
          <ImageBackground source={require('./board.png')} style={{flex:1, height: 200, width: undefined}} resizeMode="contain"> 
               <ImageBackground source={ImageHold1} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain">
                <ImageBackground source={ImageHold2} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain"/>     
              </ImageBackground>
          </ImageBackground>

          <Section title="Backend Exercise">
            <Text onPress = {() => gz1()}>
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
