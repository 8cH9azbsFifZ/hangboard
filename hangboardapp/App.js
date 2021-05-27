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

  var client = new WebSocket ('ws://127.0.0.1:4321/'); // FIXME
  const [myText, setMyText] = useState("My Original Text");

  client.onmessage = function(e) {
    if (typeof e.data === 'string') {
      mydata = e.data;
      setMyText(e.data)
      console.log("Received: '" + e.data + "'");
    }
  }; 

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
          <Section title="Backend Exercise">
    
          <Text onPress = {() => SFXdone.play()}>
            {myText}
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
