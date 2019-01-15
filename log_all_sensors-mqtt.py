#!/usr/bin/python
import interrupt_client, MCP342X, wind_direction, HTU21D, bmp085, tgs2600, ds18b20_therm
import database # requires MySQLdb python 2 library which is not ported to python 3 yet
import os
import paho.mqtt.client as mqtt 

FALSE=0

def restart_servers():
    os.system('sudo systemctl restart apache2')
    os.system('sudo systemctl restart mysql')
    os.system('sudo /usr/local/bin/weather-station/interrupt_daemon.py stop')
    os.system('sudo /usr/local/bin/weather-station/interrupt_daemon.py start &')

pressure = bmp085.BMP085()
temp_probe = ds18b20_therm.DS18B20()
air_qual = tgs2600.TGS2600(adc_channel = 0)
humidity = HTU21D.HTU21D()
wind_dir = wind_direction.wind_direction(adc_channel = 0, config_file="wind_direction.json")
try:
    interrupts = interrupt_client.interrupt_client(port = 49501)
except:
    restart_servers()

db = database.weather_database() #Local MySQL db

wind_average = wind_dir.get_value(10) #ten seconds

print (humidity.read_temperature(), temp_probe.read_temp(), air_qual.get_value(), pressure.get_pressure(), humidity.read_humidity(), wind_average, interrupts.get_wind(), interrupts.get_wind_gust(), interrupts.get_rain())

mqClient = mqtt.Client("weather")
broker = "10.1.1.11"
port = 1883
# uncomment the below line and add your username and password if the broker needs it
#username_pw_set(username, password=None)
topicPrefix = "beaufort/"

mqClient.connect(broker, port, 60)
mqClient.publish(topicPrefix+"out/humidity", str(round(humidity.read_temperature(),2)))
mqClient.publish(topicPrefix+"out/temp_probe", str(round(temp_probe.read_temp(),2)))
mqClient.publish(topicPrefix+"out/air_qual", str(round(air_qual.get_value(),2)))
mqClient.publish(topicPrefix+"out/pressure", str(round(pressure.get_pressure(),2)))
mqClient.publish(topicPrefix+"out/humidity", str(round(humidity.read_humidity(),2)))
mqClient.publish(topicPrefix+"out/wind_average", str(round(wind_average,2)))
mqClient.publish(topicPrefix+"out/wind", str(round(interrupts.get_wind(),2)))
mqClient.publish(topicPrefix+"out/wind_gust", str(round(interrupts.get_wind_gust(),2)))
mqClient.publish(topicPrefix+"out/rain", str(round(interrupts.get_rain(),2)))
mqClient.disconnect()

try:
    print("Inserting...")
    db.insert(humidity.read_temperature(), temp_probe.read_temp(), air_qual.get_value(), pressure.get_pressure(), humidity.read_humidity(), wind_average, interrupts.get_wind(), interrupts.get_wind_gust(), interrupts.get_rain())
    print("done")
except:
    restart_servers()

interrupts.reset()
