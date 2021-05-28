#!/bin/bash
cd ios && pod install && cd ..
yarn install
yarn run ios
