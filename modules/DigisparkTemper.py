# pylint: disable=invalid-name, broad-except, bare-except, too-many-locals
"""DigisparkTemper (usb temperature/humidity sensor) module
"""

import json
import logging
import usb

from modules.TemperatureModule import TemperatureModule
from modules.WeatherModule import Utils


def read_temperature_and_humidity(device, correction_value):
    """Read Temperature and humidity from sensor
    """

    def read(device):
        """Read byte from usb device
        """
        while True:
            try:
                response = device.ctrl_transfer(
                    bmRequestType=usb.util.build_request_type(
                        usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS,
                        usb.util.CTRL_RECIPIENT_DEVICE),
                    bRequest=0x01,  # USBRQ_HID_GET_REPORT
                    wValue=(0x03 << 8) | 0,
                    wIndex=0,  # ignored
                    data_or_wLength=1)  # length
                if response:
                    return response[0]
            except usb.core.USBError:
                pass

    def read_line(device):
        """Read line
        """
        line = ""
        while True:
            c = chr(read(device))
            if c == '\r':
                return line
            line += c

    try:
        line = read_line(device).strip()
        data = json.loads(line)

        humidity = data["Humidity"]
        celsius = round(data["Temperature"] + correction_value, 1)

        logging.info("Celsius: %s Humidity: %s", celsius, humidity)
        return celsius, humidity

    except Exception as e:
        if line:
            logging.error("DigisparkTemper: %s", line)
        logging.error(e, exc_info=True)
        return None


class DigisparkTemper(TemperatureModule):
    """
    DigisparkTemper (USB temperature/humidity sensor) module
    https://github.com/miyaichi/DigisparkTemper

    This module gets data form DigisparkTemper and display it in
    Heat Index color.

    example config:
    {
      "module": "DigisparkTemper",
      "config": {
        "rect": [x, y, width, height],
        "correction_value": -1,
        "logfile": "/var/log/sensor.csv",
        "graph_rect": [x, y, width, height]
      }
     }
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.device = None
        self.correction_value = None

        self.correction_value = float(config["correction_value"])
        self.device = usb.core.find(idVendor=0x16c0, idProduct=0x05df)
        if not self.device:
            logging.error("%s: device not found", __class__.__name__)
            raise Exception()

        # start sensor thread
        self.start_sensor_thread(20, read_temperature_and_humidity,
                                 [self.device, self.correction_value])

    def draw(self, screen, weather, updated):
        (celsius, humidity, data_changed) = self.get_sensor_value()
        if not data_changed:
            return

        color = Utils.heat_color(celsius, humidity, "metric")
        temperature = Utils.temperature_text(
            celsius if self.units == "metric" else Utils.fahrenheit(celsius),
            self.units)
        humidity = Utils.percentage_text(humidity)

        for size in ("large", "medium", "small"):
            # Horizontal
            message1 = "{}  {}".format(temperature, humidity)
            message2 = None
            w, h = self.text_size(message1, size, bold=True)
            if w <= self.rect.width and 20 + h <= self.rect.height:
                break

            # Vertical
            message1 = temperature
            message2 = humidity if humidity else None
            w1, h1 = self.text_size(message1, size, bold=True)
            w2, h2 = self.text_size(message2, size, bold=True)
            if max(w1,
                   w2) <= self.rect.width and 20 + h1 + h2 <= self.rect.height:
                break

        self.clear_surface()
        self.draw_text(_("Indoor"), (0, 0), "small", "gray")
        (w, h) = self.draw_text(message1, (0, 20), size, color, bold=True)
        if message2:
            self.draw_text(message2, (0, 20 + h), size, color, bold=True)
        self.update_screen(screen)

        # draw the graph if necessary
        self.draw_graph(screen, weather, updated)
