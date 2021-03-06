#!/usr/bin/python
import interrupt_client, MCP342X, wind_direction, HTU21D, bmp085, tgs2600, ds18b20_therm
import database # requires MySQLdb python 2 library which is not ported to python 3 yet
import os

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

try:
    print("Inserting...")
    db.insert(humidity.read_temperature(), temp_probe.read_temp(), air_qual.get_value(), pressure.get_pressure(), humidity.read_humidity(), wind_average, interrupts.get_wind(), interrupts.get_wind_gust(), interrupts.get_rain())
    print("done")
except:
    restart_servers()

interrupts.reset()
