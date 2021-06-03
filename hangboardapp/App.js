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

import {
  Colors,
  DebugInstructions,
  Header,
  LearnMoreLinks,
  ReloadInstructions,
} from 'react-native/Libraries/NewAppScreen';

import { useState } from 'react';
import 'react-native-sound';
var Sound = require('react-native-sound');

/*
 
*/
//var client = new WebSocket ('ws://127.0.0.1:4321/'); // FIXME
var client = new WebSocket ('ws://10.101.40.81:4321/'); // FIXME



Sound.setCategory('Playback');

var SFXone = new Sound('1.mp3', Sound.MAIN_BUNDLE);
var SFXtwo = new Sound('2.mp3', Sound.MAIN_BUNDLE);
var SFXthree = new Sound('3.mp3', Sound.MAIN_BUNDLE);
var SFXfour = new Sound('4.mp3', Sound.MAIN_BUNDLE);
var SFXfive = new Sound('5.mp3', Sound.MAIN_BUNDLE);
var SFXsix = new Sound('6.mp3', Sound.MAIN_BUNDLE);
var SFXseven = new Sound('7.mp3', Sound.MAIN_BUNDLE);
var SFXeight = new Sound('8.mp3', Sound.MAIN_BUNDLE);
var SFXnine = new Sound('9.mp3', Sound.MAIN_BUNDLE);
var SFXten = new Sound('10.mp3', Sound.MAIN_BUNDLE);
var SFXdone = new Sound('done.mp3', Sound.MAIN_BUNDLE);
var SFXfailed = new Sound('failed.mp3', Sound.MAIN_BUNDLE);

const Section = ({children, title}): Node => {
  const isDarkMode = useColorScheme() === 'dark';
  return (
    <View style={styles.sectionContainer}>
      <Text
        style={[
          styles.sectionTitle,
          {
            color: isDarkMode ? Colors.white : Colors.black,
          },
        ]}>
        {title}
      </Text>
      <Text
        style={[
          styles.sectionDescription,
          {
            color: isDarkMode ? Colors.light : Colors.dark,
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
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
  };

  const [myText, setMyText] = useState("My Original Text");
  const [myState, setMyState] = useState("");

  const ImageBoard = require("./board.png");
  const ImageA1 = require("./A1.png");
  const ImageA7 = require("./A7.png");
  
  const [ImageHold1, SetImageHold1] = useState(ImageBoard);
  const [ImageHold2, SetImageHold2] = useState(ImageBoard);
  //var ImageHold2 = ImageBoard;

  client.onmessage = function(e) {
    if (typeof e.data === 'string') {
      mydata = e.data;
      console.log("Received: '" + e.data + "'");
    }

    var parsed = JSON.parse(e.data);
    var togo = parsed.Duration - parsed.Counter;

    setMyState(parsed);
    setMyText("Exercise: " + parsed.Exercise + " for " + parsed.Duration + "(s) and still " + togo + "(s) remaining."); 

    if (parsed.HoldsActive.includes("A1")) { SetImageHold1 (ImageA1);  } else { SetImageHold1(ImageBoard); }
    if (parsed.HoldsActive.includes("A7")) { SetImageHold2 (ImageA7); } else { SetImageHold2(ImageBoard); }

  
    //var array = parsed.HoldsActive; 
    //array.forEach(element => ImageHold1 = element);
    //array.forEach(element => window[element].setAttribute("display","inline") );

    if (parsed.TimerStatus == false)
    {
      if (togo == 10) { SFXten.play(); } 
      if (togo == 9) { SFXnine.play(); } 
      if (togo == 8) { SFXeight.play(); } 
      if (togo == 7) { SFXseven.play(); } 
      if (togo == 6) { SFXsix.play(); } 
      if (togo == 5) { SFXfive.play(); } 
      if (togo == 4) { SFXfour.play(); } 
      if (togo == 3) { SFXthree.play(); } 
      if (togo == 2) { SFXtwo.play(); } 
      if (togo == 1) { SFXone.play(); } 
      if (togo == 0) { SFXdone.play(); } 
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

  
  return (
    
    <SafeAreaView style={backgroundStyle}>
     
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
      <ScrollView
        contentInsetAdjustmentBehavior="automatic"
        style={backgroundStyle}>

        <View
          style={{
            backgroundColor: isDarkMode ? Colors.black : Colors.white,
          }}>
          <ImageBackground source={require('./board.png')} style={{flex:1, height: 200, width: undefined}} resizeMode="contain">
               <ImageBackground source={ImageHold1} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain">
                <ImageBackground source={ImageHold2} style={{flex:1, top:0, height: 200, width: undefined}} resizeMode="contain"/>     
              </ImageBackground>
          </ImageBackground>

          <Section title="Backend Exercise">
            <Text onPress = {() => SFXdone.play()}>
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
            </Text>
          </Section>
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
