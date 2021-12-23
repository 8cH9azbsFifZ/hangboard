from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27, backlight_enabled=True)
#PCF8574, the MCP23008 and the MCP23017
lcd.write_string('Hello world')
smiley = (
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
)
lcd.create_char(0, smiley)