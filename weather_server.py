import smbus
import time

# Get I2C bus
sensorIn = smbus.SMBus(1)
sensorOut = smbus.SMBus(3)
while True:

    # SHT30 address, 0x44(68)
    # Send measurement command, 0x2C(44)
    #		0x06(06)	High repeatability measurement
    sensorIn.write_i2c_block_data(0x44, 0x2C, [0x06])
    sensorOut.write_i2c_block_data(0x44, 0x2C, [0x06])

    time.sleep(0.5)

    # --------- Get data from Sensor IN ---------

    # SHT30 address, 0x44(68)
    # Read data back from 0x00(00), 6 bytes
    # cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
    data = sensorIn.read_i2c_block_data(0x44, 0x00, 6)

    # Convert the data
    cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

    # Output data to screen
    print("------ Sensor IN ------ ")
    print("Relative Humidity : {:.2f} RH".format(humidity))
    print("Temperature in Celsius : {:.2f} C".format(cTemp))
    
    # --------- Get data from Sensor OUT ---------

    # SHT30 address, 0x44(68)
    # Read data back from 0x00(00), 6 bytes
    # cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
    data = sensorOut.read_i2c_block_data(0x44, 0x00, 6)

    # Convert the data
    cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

    # Output data to screen
    print("------ Sensor OUT ------ ")
    print("Relative Humidity : {:.2f} RH".format(humidity))
    print("Temperature in Celsius : {:.2f} C".format(cTemp))

    print("----------------------------------------------")
    
