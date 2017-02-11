import math

def temperature_to_rgb(temp):
    """
    Convert a given color temperature within the range [1000, 40000] kelvin, 
    convert it to an RGB approximation.

    Based upon work by Tanner Helland.
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
    """

    temp = temp / 100.0
    red, green, blue = 0, 0, 0

    if temp <= 66:
        red = 255
    else:
        red = temp - 60
        red = 329.698727446 * (red ** -0.1332047592)
        if red < 0:
            red = 0
        if red > 255:
            red = 255

    if temp <= 66:
        green = temp
        green = 99.4708025861 * math.log(green) - 161.1195681661
        if green < 0:
            green = 0
        if green > 255:
            green = 255
    else:
        green = temp - 60
        green = 288.1221695283 * (green ** -0.0755148492)
        if green < 0:
            green = 0
        if green > 255:
            green = 255

    if temp >= 66:
        blue = 255
    else:
        if temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
            if blue < 0:
                blue = 0
            if blue > 255:
                blue = 255

    return (round(red), round(green), round(blue))
