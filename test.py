#!/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import os
import sys
from datetime import datetime
from weather_renderer import WeatherRenderer

sys.path.append(r'lib')

def refresh():
    logging.info('Refresh ...')

    width = 640
    height = 384
    
    weather_api_key = os.getenv('OWM_API_KEY')
    city_id = 2643743

    renderer = WeatherRenderer(weather_api_key, city_id, height, width)

    try:
        if datetime.now().strftime("%H:%M") > '23:00':
            image = renderer.draw_moon()
        else:
            image = renderer.draw_update()

        image.save("./test.jpg")

    except IOError as io_error:
        logging.error(io_error)
        sys.exit()

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting ...')

    refresh()

if __name__ == '__main__':
    main()
