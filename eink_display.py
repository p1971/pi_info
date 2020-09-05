#!/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import os
import sys
import time
from datetime import datetime, timezone

from weather_renderer import WeatherRenderer

from waveshare_epd import epd7in5

sys.path.append(r'lib')

def refresh():
    logging.info('Refresh ...')

    try:
        epd = epd7in5.EPD()
        epd.init()

        weather_api_key = os.getenv('OWM_API_KEY')
        city_id =  int(os.getenv('CITY_ID'))

        w = WeatherRenderer(weather_api_key, epd.height, epd.width)

        if datetime.now().strftime("%H:%M") > '21:00':
            epd.Clear()
            image = w.draw_moon()
        else:
            image = w.draw_update()
        epd.display(epd.getbuffer(image))
        epd.sleep()
    except IOError as io_error:
        logging.error(io_error)
        exit()

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting ...')

    if "OWM_API_KEY" not in os.environ:
        logging.error('OWM_API_KEY is not defined')
        exit(-1)

    if "CITY_ID" not in os.environ:
        logging.error('CITY_ID is not defined')
        exit(-2)

    refresh()

if __name__ == '__main__':
    while True:
        main()
        time.sleep(300)
