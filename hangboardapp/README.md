# Hangboard App
Status: WIP on iOS ...

# Running
+ Build pods etc `./build.sh`
+ Run the iOS app in simulator `yarn run ios`

# Development information


### Build for Testflight
+ Xcode > Product > Archive
+ go to: https://appstoreconnect.apple.com/apps

### Configure without metro
+ http://dev.diogomachado.com/how-run-your-app-react-on-iphone-without-metro-server-running/
Projet -> Release Scheme to Release (instead debug)


## Add App Icon
+ Generate it using: https://appicon.co/
+ Start Xcode `open ios/hangboardapp.xcworkspace`
+ On the root directory click on the folder named Images.xcassets.
+ Import a new IconSet 

## Add sounds
iOS: Open Xcode and add your sound files to the project (Right-click the project and select Add Files to [PROJECTNAME])
TBD: Android

## Initial setup
+ Have Xcode and HomeBrew installed
```
npx react-native init hangboardapp
brew install yarn
brew install cocoapods
```

## Stay awake? 
+ Variant Expo - Does not compile as described [here](https://docs.expo.io/bare/installing-unimodules/) and [here](https://www.npmjs.com/package/expo-keep-awake).
+ The "deprecated" [version](https://github.com/corbt/react-native-keep-awake#readme) works :) 