import gettext
import logging
import time
from modules.WeatherModule import WeatherModule, Utils


class Alerts(WeatherModule):
    def draw(self, screen, weather, updated):
        if weather is None:
            message = "Waiting data..."
        else:
            if updated:
                message = weather["alerts"][
                    "title"] if "alerts" in weather else ""
            else:
                return

        self.clear_surface()
        if message:
            logging.info("{}: {}".format(__class__.__name__, message))
            for size in ("large", "medium", "small"):
                w, h = self.text_size(message, "bold", size)
                if w <= self.rect.width and h <= self.rect.height:
                    break
            self.draw_text(message, "regular", size, "red", (0, 0), "center")
        self.update_screen(screen)


class Clock(WeatherModule):
    def draw(self, screen, weather, updated):
        timestamp = time.time()
        locale_date = Utils.strftime(timestamp, "%a, %x")
        locale_time = Utils.strftime(timestamp, "%H:%M")
        locale_second = Utils.strftime(timestamp, " %S")

        self.clear_surface()
        self.draw_text(locale_date, "regular", "small", "white", (0, 0))
        (right, bottom) = self.draw_text(locale_time, "bold", "large",
                                         "white", (0, 20))
        self.draw_text(locale_second, "bold", "medium", "gray", (right, 20))
        self.update_screen(screen)


class Location(WeatherModule):
    def draw(self, screen, weather, updated):
        if not self.location["address"]:
            return

        message = self.location["address"]

        self.clear_surface()
        for size in ("large", "medium", "small"):
            w, h = self.text_size(message, "regular", size)
            if w <= self.rect.width and h <= self.rect.height:
                break
        if w > self.rect.width:
            message = message.split(",")[0]
        self.draw_text(message, "regular", size, "white", (0, 0), "right")
        self.update_screen(screen)


class Weather(WeatherModule):
    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        currently = weather["currently"]
        daily = weather["daily"]["data"][0]

        short_summary = currently["summary"]
        icon = currently["icon"]
        temperature = currently["temperature"]
        humidity = currently["humidity"]
        apparent_temperature = currently["apparentTemperature"]
        pressure = currently["pressure"]
        uv_index = currently["uvIndex"]
        long_summary = daily["summary"]
        temperature_high = daily["temperatureHigh"]
        temperature_low = daily["temperatureLow"]

        heat_color = Utils.heat_color(temperature, humidity, self.units)
        uv_color = Utils.uv_color(uv_index)
        weather_icon = Utils.weather_icon(currently["icon"], 100)

        temperature = Utils.temparature_text(int(temperature), self.units)
        apparent_temperature = Utils.temparature_text(
            int(apparent_temperature), self.units)
        temperature_low = Utils.temparature_text(int(temperature_low),
                                                 self.units)
        temperature_high = Utils.temparature_text(int(temperature_high),
                                                  self.units)
        humidity = Utils.percentage_text(int(humidity * 100))
        uv_index = str(uv_index)
        pressure = Utils.pressure_text(int(pressure))

        text_x = weather_icon.get_size()[0]
        text_width = self.rect.width - text_x

        message1 = "{} {}".format(temperature, short_summary)
        if self.text_size(message1, "bold", "medium")[0] > text_width:
            message1 = "{}".format(temperature)
        message2 = "{} {}   {} {} {} {}".format(_("Feel Like"),
                                                apparent_temperature,
                                                _("Low"), temperature_low,
                                                _("High"), temperature_high)
        if self.text_size(message2, "bold", "small")[0] > text_width:
            message2 = "Feel {}  {} - {}".format(apparent_temperature,
                                                 temperature_low,
                                                 temperature_high)
        message3 = "{} {}  {} {}  {} {}".format(_("Humidity"), humidity,
                                                _("Pressure"), pressure,
                                                _("UVindex"), uv_index)
        if self.text_size(message3, "bold", "small")[0] > text_width:
            message3 = "{}  {}  UV {}".format(humidity, pressure, uv_index)
        max_lines = int((self.rect.height - 55) / 15)
        message4s = self.text_warp(long_summary,
                                   text_width,
                                   "bold",
                                   "small",
                                   max_lines=max_lines)

        self.clear_surface()
        self.draw_image(weather_icon, (0, 0))
        self.draw_text(message1, "bold", "medium", heat_color, (text_x, 0))
        self.draw_text(message2, "regular", "small", "white", (text_x, 25))
        i = message3.index("UV")
        (right, bottom) = self.draw_text(message3[:i], "regular", "small",
                                         "white", (text_x, 40))
        self.draw_text(message3[i:], "bold", "small", uv_color, (right, 40))
        height = 55 + (15 * (max_lines - len(message4s))) / 2
        for message in message4s:
            self.draw_text(message, "bold", "small", "white", (text_x, height))
            height += 15
        self.update_screen(screen)


class DailyWeatherForecast(WeatherModule):
    def draw(self, screen, weather, day):
        if weather is None:
            return

        daily = weather["daily"]["data"][day]
        temperature_high = daily["temperatureHigh"]
        temperature_low = daily["temperatureLow"]

        weather_icon = Utils.weather_icon(daily["icon"], 50)
        day_of_week = Utils.strftime(daily["time"], "%a")
        temperature_low = Utils.temparature_text(int(temperature_low),
                                                 self.units)
        temperature_high = Utils.temparature_text(int(temperature_high),
                                                  self.units)
        message = "{} - {}".format(temperature_low, temperature_high)

        self.clear_surface()
        self.draw_text(day_of_week, "regular", "small", "orange", (0, 0),
                       "center")
        self.draw_text(message, "regular", "small", "white", (0, 15), "center")
        self.draw_image(weather_icon, (15, 35))
        self.update_screen(screen)


class WeatherForecast(WeatherModule):
    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)

        self.forecast_days = config["forecast_days"]
        self.forecast_modules = []
        width = self.rect.width / self.forecast_days
        for i in range(self.forecast_days):
            config["rect"] = [
                self.rect.x + i * width, self.rect.y, width, self.rect.height
            ]
            self.forecast_modules.append(
                DailyWeatherForecast(fonts, location, language, units, config))

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        for i in range(self.forecast_days):
            self.forecast_modules[i].draw(screen, weather, i + 1)


class SunriseSuset(WeatherModule):
    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["daily"]["data"]

        surise = Utils.strftime(int(daily[0]["sunriseTime"]), "%H:%M")
        sunset = Utils.strftime(int(daily[0]["sunsetTime"]), "%H:%M")
        sunrise_icon = Utils.icon("sunrise.png")
        sunset_icon = Utils.icon("sunset.png")

        self.clear_surface()
        self.draw_image(sunrise_icon, (0, 20))
        self.draw_image(sunset_icon, (0, 50))
        self.draw_text(surise, "regular", "small", "white", (0, 25), "right")
        self.draw_text(sunset, "regular", "small", "white", (0, 55), "right")
        self.update_screen(screen)


class MoonPhase(WeatherModule):
    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["daily"]["data"]

        moon_phase = round((float(daily[0]["moonPhase"]) * 100 / 3.57) + 0.25,
                           1)
        moon_icon = Utils.moon_icon(moon_phase, 50)
        moon_phase = str(moon_phase)

        self.clear_surface()
        self.draw_image(moon_icon, (15, 10))
        self.draw_text(moon_phase, "regular", "small", "white", (0, 60), "center")
        self.update_screen(screen)


class Wind(WeatherModule):
    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        currently = weather["currently"]
        wind_speed = currently["windSpeed"]
        wind_bearing = currently["windBearing"]

        # The wind speed in miles per hour.
        if self.units == "si":
            wind_speed = round(float(wind_speed) * 1.609344, 1)
        wind_icon = Utils.wind_arrow_icon(wind_bearing, 30)

        wind_speed = Utils.speed_text(wind_speed, self.units)
        wind_bearing = Utils.wind_bearing_text(wind_bearing)

        self.clear_surface()
        self.draw_text(wind_bearing, "regular", "small", "white", (0, 10),
                       "center")
        self.draw_image(wind_icon, (25, 30))
        self.draw_text(wind_speed, "regular", "small", "white", (0, 60), "center")
        self.update_screen(screen)
