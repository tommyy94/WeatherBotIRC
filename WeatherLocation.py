import datetime
import json
import requests

import configparser
import sopel.module


@sopel.module.commands('weather')
def announce_weather(bot, trigger):
    """Announce weather in IRC channel
    :param bot: Current Sopel instance
    :param trigger: Target location
    """
    arg = trigger.split(" ")

    try:
        arg[1]  # Check if an argument was passed with command
    except IndexError:
        bot.say("Usage: .weather <location>")
    else:
        weather_loc = WeatherLocation(arg[1].encode('utf-8'))
        api_key = weather_loc.get_api_key
        weather = weather_loc.get_weather(api_key)
        if weather is None:
            bot.say("Invalid city name!")
        else:
            # Announce weather
            for x in weather:
                bot.say(x)


class WeatherLocation(object):
    def __init__(self, location):
        """:param location: Location of weather"""
        self.location = location

    @property
    def get_value(self):
        return True

    @property
    def get_api_key(self):
        """:return: Personal OpenWeatherMap API key"""
        cfg = configparser.ConfigParser()
        cfg.read('/home/tommy/.sopel/modules/config.cfg', encoding='utf-8')
        try:
            ret = cfg.get('openweathermap', 'api')
        except configparser.NoOptionError:
            ret = None
        except configparser.NoSectionError:
            ret = None
        return ret

    @staticmethod
    def get_sunrise_sunset(unix_ts):
        return datetime.datetime.fromtimestamp(int(unix_ts)).strftime('%Y-%m-%d %H:%M:%S')

    def get_weather(self, api_key):
        """
        Get forecast from the url
        :param api_key: OpenWeatherMap API Key
        :return: List of strings
        """
        url = "https://api.openweathermap.org/data/2.5/weather?q={0}&units=metric&appid={1}".format(self.location, api_key)
        req = requests.get(url)

        # Check if request return value
        if req.ok:
            data = json.loads(req.text)

            # Create list, because IRC protocol doesn't allow CR and/or LF in its message.
            # See: https://tools.ietf.org/html/rfc1459#section-2.3.1
            ret = [
                    "[Temperature: {0}] [Humidity: {1}] [Sky: {2}] [Wind speed: {3}]".format(data['main']['temp'],
                                                                                             data['main']['humidity'],
                                                                                             data['weather'][0]['main'],
                                                                                             data['wind']['speed']),
                    "[Sunrise: {0}] [Sunset: {1}]".format(self.get_sunrise_sunset(data['sys']['sunrise']),
                                                          self.get_sunrise_sunset(data['sys']['sunset'])),
            ]
        else:
            ret = None

        return ret


def main():
    """Used for manually testing the module."""
    arg = '.weather Berlin'.split(" ")  # Simulated command

    try:
        arg[1]  # Check if an argument was passed with command
    except IndexError:
        print("Usage: .weather <location>")
    else:
        weather_loc = WeatherLocation(arg[1].encode('utf-8'))
        api_key = weather_loc.get_api_key
        weather = weather_loc.get_weather(api_key)
        if weather is None:
            print("Invalid city name!")
        else:
            # Announce weather
            for x in weather:
                print(x)


if __name__ == '__main__':
    main()
