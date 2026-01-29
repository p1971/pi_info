#!/usr/bin/python3
# -*- coding:utf-8 -*-
import logging
import os
import sys
import time

from weather_renderer import WeatherRenderer

sys.path.append(r'lib')
from waveshare_epd import epd7in5, epdconfig

logging.basicConfig(
	format='%(asctime)s %(levelname)-8s %(message)s',
	level=logging.INFO,
	datefmt='%Y-%m-%d %H:%M:%S'
)

def initialise_panel():
    epdconfig.module_init()
    epd = epd7in5.EPD()
    epd.reset()
    epd.init()
    epd.Clear()
    return epd

def refresh(weather_api_key, city_id):
    logging.info('Refresh display ...')

    try:
        epd = initialise_panel()

        image = update_weather(weather_api_key, city_id, epd.height, epd.width)
        image = w.draw_update()
        epd.display(epd.getbuffer(image))
        epd.sleep()
    except IOError as io_error:
        logging.error(io_error)
        exit()

def update_weather(weather_api_key, city_id, height, width):
    w = WeatherRenderer(weather_api_key, city_id, height, width)
    try:
       image = w.draw_update()
       return image
    except Exception as error:
       image = w.draw_error(repr(error))
    return image

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting ...')

    if "OWM_API_KEY" not in os.environ:
        logging.error('OWM_API_KEY is not defined')
        exit(-1)

    if "CITY_ID" not in os.environ:
        logging.error('CITY_ID is not defined')
        exit(-2)

    weather_api_key = os.getenv('OWM_API_KEY')
    city_id = int(os.getenv('CITY_ID'))

    refresh(weather_api_key, city_id)

if __name__ == '__main__':
    try:
    	main()
    except KeyboardInterrupt:
        sys.exit(0)
