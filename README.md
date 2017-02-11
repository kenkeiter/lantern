# Lantern

Lantern is a library that allows for control of Yongnuo YN-series Bluetooth-enabled video lights via Python.

Currently, Lantern supports the following models:

+ [YN-360](http://www.hkyongnuo.com/e-detaily.php?ID=375) (purchase [here](http://amzn.to/2l3rBCF))

Lantern has been tested on the following operating system(s):

+ Ubuntu 16.10

## Installation

You may encounter difficulty installing `bluepy`, but in most cases, simply running the following command will install Lantern.

```bash
$ pip install yn-lantern
```

## Getting Started

Getting started with Lantern is simple. Once you've installed the library using the steps provided above, you may import and use Lantern in your code. Please keep in mind that, on some systems, `root` privileges will be required to manage the bluetooth interface.

Lantern will attempt to render color temperatures from 1,000 to 40,000 kelvin. Color temperatures between 3,200 and 5,500 kelvin will be rendered using high-intensity, high-CRI LEDs when possible.

```python
from lantern import Light

for light in Light.discover():
    # connect to the light
    light.connect()
    # set the color temperature of the light
    light.color_temperature = 4800
    # set the output of the light to 50% intensity
    light.intensity = 0.5
    # once we're done, disconnect
    light.disconnect()
```

For some types of lights (specifically, the YN-360), RGB colors can be rendered. In the following example, we connect to a specific light, and render RGB colors in two ways, pausing two seconds between each change.

```python
import time

from lantern import Light

l = Light("e8:53:aa:45:db:c6")
l.connect()

# set an RGB color using a packed hex value
l.color = 0xFF9900
# sleep two seconds, as promised
time.sleep(2)
# set red, green, and blue components of the color individually
l.color = (0xff, 0x99, 0x00)

l.disconnect()
```

## Contributing

Please fork and open a PR to contribute. Feel free to submit issues if you run into issues. I'll do my best to help.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT), and is Copyright 2017 Kenneth Keiter.