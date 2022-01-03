from configparser import ConfigParser

config_file="hangboard.ini"
config_obj = ConfigParser()
config_obj.read(config_file)

sensor_force_info = config_obj["SENSOR-FORCE"]
pin_dout1   = sensor_force_info["pin_dout1"] 
pin_pd_sck1 = sensor_force_info["pin_pd_sck1"] 
pin_dout2   = sensor_force_info["pin_dout2"] 
pin_pd_sck2 = sensor_force_info["pin_pd_sck2"] 

referenceUnit1 = sensor_force_info["referenceUnit1"] 
referenceUnit2 = sensor_force_info["referenceUnit2"] 

print (referenceUnit1)
print (referenceUnit2)