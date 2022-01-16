# Frontend for iOS (Flutter)
** Status: works as demonstrator, no stable yet **

+ [TODO](./TODO.md)

# Software Design
+ lib/widgets/mqttView.dart - Main view
+ lib/mqtt/MQTTManager.dart
+ lib/mqtt/stat/MQTTAppState.dart

## Development

### Preparation

- Install flutter and configure correct paths

### Add App Icon
The application icon is located under `assets/icon`. The backgound source code image has been created using https://ray.so. 
- The PNG can be converted to icon sets using this tool: https://appicon.co/ .

For iOS follow these steps to configure the application icon:
- Start Xcode `open ios/hangboardapp.xcworkspace`
- On the root directory click on the folder named Images.xcassets.
- Import a new IconSet 


### Build and install
+ `flutter build ios`
+ `~/src/flutter/bin/flutter install DG6FL`