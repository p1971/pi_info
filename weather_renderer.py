#!/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import sys
import textwrap

from dataclasses import dataclass
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from pyowm.owm import OWM
from pytz import timezone

from weather_service import *

class WeatherRenderer:
    def __init__(self, owm_api_key, city_id, height, width):
        if owm_api_key is None:
            logging.error('owm_api_key is not defined')
            sys.exit(-1)

        self.__font_path = 'fonts/Cousine-Regular.ttf'
        self.__weather_font_path = 'fonts/meteocons-webfont.ttf'

        self.__font20 = ImageFont.truetype(self.__font_path, 20)
        self.__font40 = ImageFont.truetype(self.__font_path, 40)
        self.__font64 = ImageFont.truetype(self.__font_path, 64)

        self.owm_api_key = owm_api_key
        self.city_id = city_id
        self.height = height
        self.width = width

    def draw_update(self):
        image = Image.new('1', (self.height, self.width), 255)
        draw = ImageDraw.Draw(image)
        self.__draw_weather_report(draw)
        return image

    def draw_moon(self):
        image = Image.new('RGBA', (self.height, self.width), 0)
        moon = Image.open('moon.jpg').convert('RGBA')
        x, y = moon.size
        image.paste(moon, (0, 0, x, y), moon)
        return image

    def __draw_weather_report(self, drawblack):
        weather_svc = WeatherService(self.owm_api_key, self.city_id)
        forecast = weather_svc.get_weather()
        fontweathersmall = ImageFont.truetype(self.__weather_font_path, 64)
        fontweatherbig = ImageFont.truetype(self.__weather_font_path, 128)

        # temperature
        _, h1 = self.__draw_text(drawblack, self.__font64, 5, 5,  str(
            "{0}\u00b0C".format(forecast.temperature)))

        # min/max temperature
        self.__draw_text(drawblack, self.__font20, 5, h1 + 15, str("min {0:>4}\u00b0C".format(forecast.min_temperature)))
        self.__draw_text(drawblack, self.__font20, 5, h1+40, str("max {0:>4}\u00b0C".format(forecast.max_temperature)))

        # forecast
        local_time = forecast.reftime.strftime('%H:%M')
        description = textwrap.fill(
            f"{forecast.description} @ {local_time}", width=55)
        _, h4 = self.__draw_multiline_text(
            drawblack, self.__font20, 5, h1+75, description)

        # weather icon
        weather_icon_dict = {
            200: "6", 201: "6", 202: "6", 210: "6", 211: "6", 212: "6",
            221: "6", 230: "6", 231: "6", 232: "6",
            300: "7", 301: "7", 302: "8", 310: "7", 311: "8", 312: "8",
            313: "8", 314: "8", 321: "8",
            500: "7", 501: "7", 502: "8", 503: "8", 504: "8", 511: "8",
            520: "7", 521: "7", 522: "8", 531: "8",
            600: "V", 601: "V", 602: "W", 611: "X", 612: "X", 613: "X",
            615: "V", 616: "V", 620: "V", 621: "W", 622: "W",
            701: "M", 711: "M", 721: "M", 731: "M", 741: "M", 751: "M",
            761: "M", 762: "M", 771: "M", 781: "M",
            800: "1",
            801: "H", 802: "N", 803: "N", 804: "Y"
        }

        weather_icon_char = weather_icon_dict[forecast.weather_code]        
        
        w5, _ = self.__get_size(fontweatherbig.getbbox(weather_icon_char))
        self.__draw_text(drawblack, fontweatherbig, self.height - w5 - 5,0,weather_icon_char )
        
        # sunrise
        w6, h6 = self.__draw_text(drawblack, fontweathersmall, 20, h4+25, "A")
        w7, h7 = self.__draw_text(
            drawblack, self.__font40, 10, h6+15, forecast.sunrise.strftime('%H:%M'))

        # sunset
        self.__draw_text(drawblack, fontweathersmall,
                         self.height - (w6+20), h4+25, "J")
        self.__draw_text(drawblack, self.__font40, self.height -
                         (w7+10), h6+15, forecast.sunset.strftime('%H:%M'))

        h7 = h7 + 30
        i = 0
        for f in forecast.forecasts:
            row_height = 80
            weather_icon_char = weather_icon_dict[f.weather_code]
            w9, _ = self.__get_size(fontweathersmall.getbbox(weather_icon_char))       
            drawblack.text((15+w9, h7 + i*row_height ), f.reftime.strftime('%H:%M'), font=self.__font20, fill=0)
            drawblack.text((240+w9, h7 + i*row_height ), str("{0}{1}C".format(f.temperature, u'\u00b0')), font=self.__font20, fill=0)
            drawblack.text((15+w9, 25+h7 + i*row_height ), f.description, font=self.__font20, fill=0)
            drawblack.text((5, (h7-12) + i*row_height ), weather_icon_char, font=fontweathersmall, fill=0)
            i = i + 1            

    def __get_size(self, box):
        return box[2]-box[0], box[3]

    def __draw_cell(self, draw, font, x, y, text, width):
        if width != None:
            text = text[:width] + (text[width:] and '...')
        w, h = self.__get_size(font.getbbox(text))
        draw.text((x, y), text, font=font, fill=0)
        return x+w, y+h

    def __draw_text(self, draw, font, x, y, text):
        w, h = self.__get_size(font.getbbox(text))
        draw.text((x, y), text, font=font, fill=0)
        return w+x, h+y

    def __draw_multiline_text(self, draw, font, x, y, text):
        w, h = self.__get_size(font.getbbox(text))
        draw.multiline_text((x, y), text, font=font, fill=0)
        return w+x, h+y