# Pi Info Display

Simple e-ink display powered by raspberry pi showing weather 

## Requirements

Environment variables needs to be set

* OWM_API_KEY - API key for [Open Weather Map](https://openweathermap.org/)
* CITY_ID - Id of the city - see http://bulk.openweathermap.org/sample/city.list.json.gz

```bash
export OWM_API_KEY=xxxx
export CITY_ID=2643743
```

## Run

```bash
python3 -m venv .venv
pip3 install -r requirements.txt
source ./.venv/bin/activate
python3 eink_display.py
```

## With some help from the following projects

* [Waveshare epaper display](https://github.com/mendhak/waveshare-epaper-display)
* [ProtoStax Weather Station Demo](https://github.com/protostax/ProtoStax_Weather_Station_Demo)
