# pylint: disable=invalid-name, too-many-locals
"""Built-in modules
"""

import datetime
import logging
import time
from modules.WeatherModule import WeatherModule, Utils


class Alerts(WeatherModule):
    """Any severe weather alerts pertinent
    """

    def draw(self, screen, weather, updated):
        if weather is None:
            message = "Waiting data..."
        else:
            return

        self.clear_surface()
        if message:
            logging.info("%s: %s", __class__.__name__, message)
            for size in ("large", "medium", "small"):
                width, height = self.text_size(message, size, bold=True)
                if width <= self.rect.width and height <= self.rect.height:
                    break
            self.draw_text(message, (0, 0),
                           size,
                           "red",
                           bold=True,
                           align="center")
        self.update_screen(screen)


class Clock(WeatherModule):
    """Current Date and Time
    """

    def draw(self, screen, weather, updated):
        timestamp = time.time()
        locale_date = Utils.strftime(timestamp, "%a, %x")
        locale_time = Utils.strftime(timestamp, "%H:%M")
        locale_second = Utils.strftime(timestamp, " %S")

        self.clear_surface()
        self.draw_text(locale_date, (0, 0), "small", "white")
        (right, _bottom) = self.draw_text(locale_time, (0, 20),
                                          "large",
                                          "white",
                                          bold=True)
        self.draw_text(locale_second, (right, 20), "medium", "gray", bold=True)
        self.update_screen(screen)


class Location(WeatherModule):
    """Current Location
    """

    def draw(self, screen, weather, updated):
        if not self.location["address"]:
            return

        message = self.location["address"]

        self.clear_surface()
        for size in ("large", "medium", "small"):
            width, height = self.text_size(message, size)
            if width <= self.rect.width and height <= self.rect.height:
                break
        if width > self.rect.width:
            message = message.split(",")[0]
        self.draw_text(message, (0, 0), size, "white", align="right")
        self.update_screen(screen)


class Weather(WeatherModule):
    """Current Weather
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 100

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        current = weather["current"]
        daily = weather["daily"][0]

        short_summary = _(current["weather"][0]["main"])
        icon = current["weather"][0]["icon"]
        temperature = current["temp"]
        humidity = current["humidity"]
        feels_like = current["feels_like"]
        pressure = current["pressure"]
        uv_index = int(current["uvi"])
        long_summary = daily["weather"][0]["description"]
        temperature_high = daily["temp"]["max"]
        temperature_low = daily["temp"]["min"]

        heat_color = Utils.heat_color(temperature, humidity, self.units)
        uv_color = Utils.uv_color(uv_index)
        weather_icon = Utils.weather_icon(icon, self.icon_size)

        temperature = Utils.temperature_text(int(temperature), self.units)
        feels_like = Utils.temperature_text(int(feels_like), self.units)
        temperature_low = Utils.temperature_text(int(temperature_low),
                                                 self.units)
        temperature_high = Utils.temperature_text(int(temperature_high),
                                                  self.units)
        humidity = Utils.percentage_text(humidity)
        uv_index = str(uv_index)
        pressure = Utils.pressure_text(int(pressure))

        text_x = weather_icon.get_size()[0]
        text_width = self.rect.width - text_x

        message1 = self.text_warp("{} {}".format(temperature, short_summary),
                                  text_width,
                                  "medium",
                                  bold=True,
                                  max_lines=1)[0]
        message2 = "{} {}   {} {} {} {}".format(_("Feels Like"), feels_like,
                                                _("Low"), temperature_low,
                                                _("High"), temperature_high)
        if self.text_size(message2, "small")[0] > text_width:
            message2 = "Feel {}  {} - {}".format(feels_like, temperature_low,
                                                 temperature_high)
        message3 = "{} {}  {} {}  {} {}".format(_("Humidity"), humidity,
                                                _("Pressure"), pressure,
                                                _("UVindex"), uv_index)
        if self.text_size(message3, "small")[0] > text_width:
            message3 = "{}  {}  UV {}".format(humidity, pressure, uv_index)
        max_lines = int((self.rect.height - 55) / 15)
        message4s = self.text_warp(long_summary,
                                   text_width,
                                   "small",
                                   bold=True,
                                   max_lines=max_lines)

        self.clear_surface()
        self.draw_image(weather_icon, (0, 0))
        self.draw_text(message1, (text_x, 0), "medium", heat_color, bold=True)
        self.draw_text(message2, (text_x, 25), "small", "white")
        i = message3.index("UV")
        (right, _bottom) = self.draw_text(message3[:i], (text_x, 40), "small",
                                          "white")
        self.draw_text(message3[i:], (right, 40), "small", uv_color, bold=True)
        height = 55 + (15 * (max_lines - len(message4s))) / 2
        for message in message4s:
            self.draw_text(message, (text_x, height),
                           "small",
                           "white",
                           bold=True)
            height += 15
        self.update_screen(screen)


class DailyWeatherForecast(WeatherModule):
    """Daily weather forecast
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"]
        self.day = config["day"]

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["daily"][self.day]
        temperature_high = daily["temp"]["max"]
        temperature_low = daily["temp"]["min"]
        icon = daily["weather"][0]["icon"]

        weather_icon = Utils.weather_icon(icon, self.icon_size)
        day_of_week = Utils.strftime(daily["dt"], "%a")
        temperature_low = Utils.temperature_text(int(temperature_low),
                                                 self.units)
        temperature_high = Utils.temperature_text(int(temperature_high),
                                                  self.units)
        message = "{}-{}".format(temperature_low, temperature_high)

        self.clear_surface()
        self.draw_text(day_of_week, (0, 0), "small", "orange", align="center")
        self.draw_text(message, (0, 15), "small", "gray", align="center")
        self.draw_image(weather_icon,
                        ((self.rect.width - self.icon_size) / 2, 30 +
                         (self.rect.height - 30 - self.icon_size) / 2))
        self.update_screen(screen)


class WeatherForecast(WeatherModule):
    """Weather Forecast
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)

        self.forecast_days = config["forecast_days"]
        self.forecast_modules = []
        width = self.rect.width / self.forecast_days
        for i in range(self.forecast_days):
            if "icon_size" not in config:
                config["icon_size"] = 50
            config["day"] = i + 1
            config["rect"] = [
                self.rect.x + i * width, self.rect.y, width, self.rect.height
            ]
            self.forecast_modules.append(
                DailyWeatherForecast(fonts, location, language, units, config))

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        for i in range(self.forecast_days):
            self.forecast_modules[i].draw(screen, weather, updated)


class SunriseSuset(WeatherModule):
    """Sunrise, Sunset time
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 40

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        current = weather["current"]
        sunrise = current["sunrise"]
        sunset = current["sunset"]

        surise = "{} \u2197".format(Utils.strftime(sunrise, "%H:%M"))
        sunset = "\u2198 {}".format(Utils.strftime(sunset, "%H:%M"))
        sun_icon = Utils.weather_icon("01d", self.icon_size)

        self.clear_surface()
        self.draw_image(sun_icon, ((self.rect.width - self.icon_size) / 2,
                                   (self.rect.height - self.icon_size) / 2))
        self.draw_text(surise, (0, 5), "small", "white", align="center")
        self.draw_text(sunset, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)


class MoonPhase(WeatherModule):
    """Moon Phase
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 50

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        current = weather["current"]
        dt = datetime.datetime.fromtimestamp(int(current["dt"]))
        moon_age = (
            ((dt.year - 11) % 19) * 11 +
            [0, 2, 0, 2, 2, 4, 5, 6, 7, 8, 9, 10][dt.month - 1] + dt.day) % 30

        moon_icon = Utils.moon_icon(moon_age, self.icon_size)
        moon_age = str(moon_age)

        self.clear_surface()
        self.draw_image(moon_icon, ((self.rect.width - self.icon_size) / 2, 5))
        self.draw_text(moon_age, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)


class Wind(WeatherModule):
    """Wind direction, speed
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 30

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["current"]
        wind_speed = daily["wind_speed"]
        wind_deg = daily["wind_deg"]

        wind_icon = Utils.wind_arrow_icon(wind_deg, self.icon_size)
        wind_speed = Utils.speed_text(wind_speed, self.units)
        wind_deg = Utils.wind_bearing_text(wind_deg)

        self.clear_surface()
        self.draw_text(wind_deg, (0, 5), "small", "white", align="center")
        self.draw_image(wind_icon,
                        ((self.rect.width - self.icon_size) / 2, 20 +
                         (self.rect.height - 40 - self.icon_size) / 2))
        self.draw_text(wind_speed, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)
