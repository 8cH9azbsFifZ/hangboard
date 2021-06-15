#!/bin/bash
yarn install
cd ios && pod install && cd ..
yarn run ios
