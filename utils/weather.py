try:
    from utils import worker
except:
    pass

import requests
import re
import json

class Weather(worker.WorkerSignals):
    pass

class WeatherWorker(worker.Worker):
    def __init__(self, signals):   
        super(WeatherWorker, self).__init__(signals, self._run)

    def _run(self):
        # now = datetime.now().strftime("%H:%M")
        # return(str(now))
        return startWeatherMonitor()

def startWeatherMonitor():
    # // Regex's for reading out the weather info from the yahoo page
    # TODO: python regex
    # tempRegex = r"temperature:({[^}]+})/"
    tempRegex = r"\"temperature\":({[^}]+})"
    condRegex = r"\"conditionDescription\":\"([^\"]+)\""
    rainRegex = r"\"precipitationProbability\":([^,]+),"
    # tempRegex = r'temperature:({[^}]+}),'
    # condRegex = r'conditionDescription:([^]+),'
    # rainRegex = r'precipitationProbability:([^,]+),'

    def getWeather():
        data = requests.get("https://www.yahoo.com/news/weather/united-states/boston/boston-2367105")
        # content = data.json()
        data_text = data.text
        weather = {}
        # temp = tempRegex.exec(body)
        temp = re.findall(tempRegex, data_text)
        # print('temp', temp)
        if temp and len(temp) > 1:
            weather['temp'] = json.loads(temp[1])

        # cond = condRegex.exec(body)
        cond = re.findall(condRegex, data_text)
        # print('cond', cond)
        if cond and len(cond) > 1 :
            weather['desc'] = cond[1]

        # rain = rainRegex.exec(body)
        rain = re.findall(rainRegex, data_text)
        # print('rain', rain)
        if rain and len(rain) > 1 :
            weather['rain'] = rain[1]
        # print('weather', weather)
        return weather
        
    # // Used for scrolling long weather descriptions
    lastWeather = None
    lastWeatherDescIndex = 0

    # // Just keep updating the data forever
    # while True:
    # // Get the current weather for Seattle
    weather = getWeather()
    if weather and weather['temp'] and weather['desc'] and weather['rain']:
        description = weather['desc']

        # // If we are trying to show the same weather description more than once, and it is longer than 9
        # // Which is all that will fit in our space, lets scroll it.
        if lastWeather and weather.get('desc') == lastWeather.get('desc') and len(weather.get('desc')) > 9: 
            # // Move the string one character over
            lastWeatherDescIndex += 1
            description = description[lastWeatherDescIndex, lastWeatherDescIndex + 9]
            if lastWeatherDescIndex > len(weather.get('desc')) - 9:
                # // Restart back at the beginning
                lastWeatherDescIndex = -1
                # // minus one since we increment before we show
        else:
            lastWeatherDescIndex = 0
        
        lastWeather = weather

        # // Create the new screen
        # screen = f"desc: {description}${' '.repeat(max(0, 9 - ('' + description).length))} |  {title(0, 2)} " + \
        #     f"temp: {weather.temp.now}{' '.repeat(max(0, 9 - ('' + weather.temp.now).length))} |  {title(1, 2)} " + \
        #     f"high: {weather.temp.high}{' '.repeat(max(0, 9 - ('' + weather.temp.high).length))} |  {title(2, 2)} " + \
        #     f"rain: {weather.rain}%{' '.repeat(max(0, 8 - ('' + weather.rain).length))} |  {title(3, 2)} "

        screen = f"desc: {description} " + \
            f"temp: {weather.get('temp').get('now')}" + \
            f"high: {weather.get('temp').get('high')}" + \
            f"rain: {weather.get('rain')}"

        screen = f"{weather.get('temp').get('now')}\n\n" + \
            f"{description}"

        # // Set this to be the latest weather info
        return screen
        

        # // Pause a bit before requesting more info
        # wait(KEYBOARD_UPDATE_TIME)