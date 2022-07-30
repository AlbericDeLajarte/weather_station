# Weather_station

A simple repository to read temperature and humidity sensors with a raspberryPi.

Using two SHT30 from: https://docs.m5stack.com/en/unit/envIII

## Setup

### Activate a second I2C bus:
````
sudo nano /boot/config.txt
````
add:
````
dtoverlay=i2c-gpio,bus=3,i2c_gpio_delay_us=1,i2c_gpio_sda=17,i2c_gpio_scl=27
````
