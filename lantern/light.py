import re

from bluepy import btle

from lantern import color


class Light(object):

    LOCAL_NAME_MATCHER = re.compile("^YONGNUO.+")
    TRANSMIT_UUID = "f000aa61-0451-4000-B000-000000000000"
    PACKET_TYPES = {
        'set_color': 0xa1,
        'set_white': 0xaa,
        'power_off': 0xa3,
    }
    COLOR_TYPES = {
        'temperature': 0,
        'rgb': 1
    }

    @classmethod
    def discover(cls, timeout=3.0):
        """
        Perform a scan for all Yongnuo lights within range, returning Light 
        instances awaiting connection.
        """
        lights =  []
        scanner = btle.Scanner()
        for dev in scanner.scan(timeout):
            if cls.LOCAL_NAME_MATCHER.match(str(dev.getValueText(0x09))):
                lights.append(cls(dev.addr))
        return lights

    def __init__(self, addr):
        """
        Given the MAC address of a specific Yongnuo bluetooth-enabled video 
        light, create a new instance of the Light class.
        """
        self._mac = addr
        self._intensity = 1.0
        self._color = None
        self._p = None
        self._p_transmit = None

    def connect(self):
        """
        Connect to the light.
        """
        self._p = btle.Peripheral(self._mac, btle.ADDR_TYPE_RANDOM)
        self._p_transmit = self._p.getCharacteristics(uuid=self.TRANSMIT_UUID)[0]

    def disconnect(self):
        """
        Disconnect from the light.
        """
        self._p.disconnect()
        self._p = None
        self._p_transmit = None

    def _send_packet(self, cmd, v1, v2, v3):
        packet = struct.pack(">BBBBBB",
            0xAE, # start of packet
            cmd, # command
            v1, v2, v3,
            0x56  # suffix
        )
        if self._p_transmit is None:
            raise Exception("attempted to send command to disconnected light")
        return self._p_transmit.write(packet)

    def update(self):
        """
        Update the light with any changes made to color or intensity. This may 
        be safely called repeatedly with no ill effect, and is called 
        implicitly on all changes to intensity, color, or color temperature.
        """
        if self._color is None:
            raise Exception("color or temperature must be set before updating")
        typ, target = self._color
        if typ == self.COLOR_TYPES['rgb']:
            # take the HLS value, scale by intensity, and push an update packet
            r, g, b = target
            return self._send_packet(
                self.PACKET_TYPES['set_color'], 
                round(r * self.intensity), 
                round(g * self.intensity), 
                round(b * self.intensity))
        elif typ == self.COLOR_TYPES['temperature']:
            # whenever possible, use high-CRI LEDs to render temperature
            if target >= 3200 and target <= 5500:
                percent_k55 = (target - 3200)/(5500 - 3200)
                k5500 = percent_k55 * 100 * self.intensity
                k3200 = (1.0 - percent_k55) * 100 * self.intensity
                return self._send_packet(self.PACKET_TYPES['set_white'], 
                    0x01, 
                    round(k5500), 
                    round(k3200))
            # otherwise, attempt to render using RGB LEDs
            r, g, b = color.temperature_to_rgb(target)
            return self._send_packet(
                self.PACKET_TYPES['set_color'],
                round(r * self.intensity),
                round(g * self.intensity),
                round(b * self.intensity))
        else:
            raise ValueError("unknown color type")

    @property
    def intensity(self):
        """
        Return the current intensity of the light from 0 to 1. A value of None 
        will be returned if the intensity has not yet been set.
        """
        return self._intensity

    @intensity.setter
    def intensity(self, new_intensity):
        """
        Set the intensity of the light as a percentage represented by a value 
        from 0 to 1.
        """
        if new_intensity > 1.0 or new_intensity < 0:
            raise ValueError("intensity must be gte 0 and lte 1")
        self._intensity = new_intensity
        self.update()

    @property
    def color(self):
        """
        Get the current color of the light, or None if a color temperature is 
        set, instead.
        """
        if self._color is not None and \
            self._color[0] == self.COLOR_TYPES['rgb']:
            return self._color[1]
        return None

    @color.setter
    def color(self, value):
        """
        Given either a 3-tuple of RGB values from 0 to 255, or a packed 24-bit 
        RGB color representation, set the color of the light.
        """
        if isinstance(value, int):
            r = (value & 0xff0000) >> 16
            g = (value & 0x00ff00) >> 8
            b = (value & 0x0000ff)
            self._color = (self.COLOR_TYPES['rgb'], (r, g, b))
        elif isinstance(value, [list, tuple]):
            for component in value:
                if component < 0 or component > 255:
                    raise ValueError('values must be within range [0, 255]')    
            self._color = (self.COLOR_TYPES['rgb'], value)
        else:
            raise ValueError("value must be integer or 3-tuple")
        self.update()

    @property
    def color_temperature(self):
        """
        Get the current color temperature of the light, if set, or None if 
        not set.
        """
        if self._color is not None and \
            self._color[0] == self.COLOR_TYPES['temperature']:
            return self._color[1]
        return None

    @color_temperature.setter
    def color_temperature(self, value):
        """
        Set the color temperature of the light in Kelvin. Values from 1000 to 
        40000 are acceptable; however, values outside the range of 3200 to 5500 
        Kelvin will be rendered using the RGB LEDs, and no CRI can be 
        guaranteed.
        """
        self._color = (self.COLOR_TYPES['temperature'], value)
        self.update()

    def power_off(self):
        """
        Power off the light. Changing the intensity, color, or color 
        temperature will power the light back on.
        """
        self._send_packet(self.PACKET_TYPES['power_off'], 0x00, 0x00, 0x00)
        
    def __repr__(self):
        return "<Light({}) at {:x}>".format(self._mac, id(self))