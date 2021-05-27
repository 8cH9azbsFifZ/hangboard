# Hangboard Web App

This directory contains the hangboard web application.

## Preparation
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Create icon
convert ../hardware/board_mount/IsometrixBoard.png -bordercolor white -border 0 \( -clone 0 -resize 16x16 \) \( -clone 0 -resize 32x32 \) \( -clone 0 -resize 48x48 \) \( -clone 0 -resize 64x64 \) -delete 0 -alpha off -colors 256 favicon.ico


# Running the application
```
./startup.sh
```





