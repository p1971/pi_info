#!/usr/bin/python
# -*- coding:utf-8 -*-

# Find your own city id here: 
# http://bulk.openweathermap.org/sample/city.list.json.gz

import sys
sys.path.append(r'lib')

import os
import logging
import signal
import time
import traceback
import pyowm
import json
import requests

from datetime import datetime, timezone
from PIL import Image,ImageDraw,ImageFont
from waveshare_epd import epd7in5
from waveshare_epd import epdconfig

font_path = 'fonts/Cousine-Regular.ttf'
weather_font_path = 'fonts/meteocons-webfont.ttf'

font16 = ImageFont.truetype(font_path, 16)
font20 = ImageFont.truetype(font_path, 20)
font24 = ImageFont.truetype(font_path, 24)
font40 = ImageFont.truetype(font_path, 40)

class timetable_entry:
    def __init__(self, stop_name, transport_type, destination_name, line, departure_time):
        self.stop_name = stop_name
        self.transport_type = transport_type
        self.destination_name = destination_name
        self.line = line
        self.departure_time = departure_time
    def get_departure_time_in_minutes(self):
        return int(divmod((self.departure_time - datetime.now(timezone.utc)).total_seconds(), 60)[0])

class weather_info:
    def __init__(self, location, reftime, description, temperature, max_temperature, min_temperature, sunrise, sunset, weather_code):
        self.location = location
        self.reftime = reftime
        self.description = description
        self.temperature = temperature
        self.max_temperature = max_temperature
        self.min_temperature = min_temperature
        self.sunrise = sunrise
        self.sunset = sunset
        self.weather_code = weather_code

class timetable_service:    
    def __init__(self):
        self.stations = {
            'Albisreiden': '8591036', 
            'Albisriederdörfli' : '8591037'}
    def get_timetable(self):
      
        departures = []

        for station in self.stations:
            response = requests.get(f"https://transport.opendata.ch/v1/stationboard?id={self.stations[station]}\&limit=6")
            timetable = json.loads(response.text)

            for stop in timetable['stationboard']:
                departure_time = datetime.strptime(stop['passList'][0]['departure'], '%Y-%m-%dT%H:%M:%S%z')            
                destination = stop['to'].replace('Zürich, ', '').replace('Zürich Oerlikon, ', '').replace('Zürich Wiedikon, ', '')
                departure = timetable_entry(station, stop['category'], destination, stop['number'], departure_time)
                if departure.get_departure_time_in_minutes()>0:
                    departures.append(departure)

        return sorted(departures, key = lambda d: d.departure_time)[:6]

class weather_service:
    def __init__(self, api_key, city_id):
        self.api_key = api_key
        self.city_id = city_id
    def get_weather(self):
        owm = pyowm.OWM(self.api_key)
        
        obs = owm.weather_at_id(self.city_id)

        location = obs.get_location().get_name()
        weather = obs.get_weather()

        temperature = weather.get_temperature(unit='celsius')
        forecast = weather_info(
            location,
            weather.get_reference_time(), 
            weather.get_detailed_status(), 
            round(temperature['temp'],1), 
            round(temperature['temp_min'],1), 
            round(temperature['temp_max'],1), 
            weather.get_sunrise_time(), 
            weather.get_sunset_time(), 
            weather.get_weather_code())

        return forecast

def draw_cell(draw, font, x, y, text, width):    
    if width != None:
        text = text[:width] + (text[width:] and '...')
    w, h = font.getsize(text)
    draw.text((x, y), text, font = font, fill = 0)
    return x+w, y+h

def draw_timetable(epd, draw, y, departures):
    font_title = ImageFont.truetype('fonts/Cousine-Regular.ttf', 35)
    font = ImageFont.truetype('fonts/Cousine-Regular.ttf', 25)
    line_width = 5
    draw.line(((0,y), (epd.width, y)), fill=0, width=line_width)
    _, h1 = draw_text(draw, font_title, 5, y+line_width,  "Departures")
    y_offset = line_width+h1 
    for departure in departures:
        x_offset = 5
        x_offset, _ = draw_cell(draw, font, x_offset, y_offset, f"{departure.line:>3}", None)
        x_offset, _ = draw_cell(draw, font, x_offset+10, y_offset, departure.destination_name, 20)

        cell_contents = f"{departure.get_departure_time_in_minutes():>4}'"
        cell_width, _ = font.getsize(cell_contents)
        x_offset, y_offset = draw_cell(draw, font, epd.height - cell_width -20, y_offset, cell_contents, 10)
    draw.line(((0,y_offset+5), (epd.width, y_offset+5)), fill = 0, width=line_width)

def draw_text(draw, font, x, y, text):
    w, h = font.getsize(text)
    draw.text((x,y), text, font=font, fill=0)
    return w+x, h+y

def draw_weather_report(epd, drawblack):
    weather_api_key = os.getenv('OwM_API_KEY')
    city_id =  int(os.getenv('CITY_ID'))            
    weather_svc = weather_service(weather_api_key, city_id)       
    forecast = weather_svc.get_weather()
    fontweathersmall = ImageFont.truetype(weather_font_path, 64)
    fontweatherbig = ImageFont.truetype(weather_font_path, 128)

    local_time = time.strftime( '%H:%M', time.localtime(forecast.reftime))
    description = f"{forecast.description} at {local_time}"

    # temperature    
    w1, h1 = draw_text(drawblack, font40, 5,5,  str("{0}{1}C".format(forecast.temperature, u'\u00b0')))
    
    # min/max temperature
    w2, h2 = draw_text(drawblack, font20, w1+15, 5, str("min {0:>4}".format(forecast.min_temperature)))
    drawblack.line(((w1+25, h2+5), (w2, h2+5)), fill = 0, width=2)
    draw_text(drawblack, font20, w1+15, h2+5, str("max {0:>4}".format(forecast.max_temperature)))

    # forecast
    _, h4 = draw_text(drawblack, font20, 5, h1+45, description)
    
    # weather icon
    weather_icon_dict = {
        200 : "6", 201 : "6", 202 : "6", 210 : "6", 211 : "6", 212 : "6", 
        221 : "6", 230 : "6" , 231 : "6", 232 : "6", 
        300 : "7", 301 : "7", 302 : "8", 310 : "7", 311 : "8", 312 : "8",
        313 : "8", 314 : "8", 321 : "8", 
        500 : "7", 501 : "7", 502 : "8", 503 : "8", 504 : "8", 511 : "8", 
        520 : "7", 521 : "7", 522 : "8", 531 : "8",
        600 : "V", 601 : "V", 602 : "W", 611 : "X", 612 : "X", 613 : "X",
        615 : "V", 616 : "V", 620 : "V", 621 : "W", 622 : "W", 
        701 : "M", 711 : "M", 721 : "M", 731 : "M", 741 : "M", 751 : "M",
        761 : "M", 762 : "M", 771 : "M", 781 : "M", 
        800 : "1", 
        801 : "H", 802 : "N", 803 : "N", 804 : "Y"
    }

    weather_icon_char = weather_icon_dict[forecast.weather_code]
    w5, _ = fontweatherbig.getsize(weather_icon_char)
    drawblack.text((epd.height - w5 - 5, 5), weather_icon_char, font = fontweatherbig, fill = 0)

    # sunrise
    w6, h6 = draw_text(drawblack, fontweathersmall, 20, h4+35, "A")
    w7, _ = draw_text(drawblack, font40, 10, h6+15, time.strftime( '%H:%M', time.localtime(forecast.sunrise)))

    #sunset
    draw_text(drawblack, fontweathersmall, epd.height - (w6+20), h4+35, "J")
    draw_text(drawblack, font40, epd.height - (w7+10), h6+15, time.strftime( '%H:%M', time.localtime(forecast.sunset)))    

def main():
    logging.basicConfig(level=logging.DEBUG)

    logging.info('Starting ...')
    
    epd = epd7in5.EPD()        

    timestable_svc = timetable_service()
    departures = timestable_svc.get_timetable()

    try:
        image = Image.new('1', (epd.height, epd.width), 255)
        
        draw = ImageDraw.Draw(image)

        draw_timetable(epd, draw, 300, departures)
        draw_weather_report(epd, draw)

        epd.init()
        epd.Clear()
        epd.display(epd.getbuffer(image))
        epd.sleep()
        
    except IOError as io_error:
        logging.error(io_error)
        print ('traceback.format_exc():\n%s', traceback.format_exc())
        epdconfig.module_init()
        epdconfig.module_exit()
        exit()

if __name__ == '__main__':
    main()