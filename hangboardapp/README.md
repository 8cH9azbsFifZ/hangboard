# Hangboard App
Status: WIP on iOS ...

# Running
```
yarn install
yarn start
yarn run ios
yarn run android
yarn run web
```

# Development information
## Initial setup
+ Have Xcode and HomeBrew installed
```
npx react-native init hangboardapp
brew install yarn
```

## Build
```
yarn install
cd ios && pod install && cd ..
```

## Add App Icon
projectname.xcodeproj/projectname.xcworkspace. On the root directory click on the folder named Images.xcassets.

Generate it using: https://appicon.co/

## Add sounds
iOS: Open Xcode and add your sound files to the project (Right-click the project and select Add Files to [PROJECTNAME])
TBD: Android
