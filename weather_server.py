import smbus
import time
import threading
import csv  

import datetime

import dash
from dash import dcc, html
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# pip install pyorbital
import pandas as pd
import numpy as np

dT = 30 # seconds

def sensor_reader():
    global time_buffer
    global data_buffer

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
        dataIN = sensorIn.read_i2c_block_data(0x44, 0x00, 6)

        # Convert the data
        cTempIN = ((((dataIN[0] * 256.0) + dataIN[1]) * 175) / 65535.0) - 45
        humidityIN = 100 * (dataIN[3] * 256 + dataIN[4]) / 65535.0
        
        # --------- Get data from Sensor OUT ---------

        # SHT30 address, 0x44(68)
        # Read data back from 0x00(00), 6 bytes
        # cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        dataOUT = sensorOut.read_i2c_block_data(0x44, 0x00, 6)

        # Convert the data
        cTempOUT = ((((dataOUT[0] * 256.0) + dataOUT[1]) * 175) / 65535.0) - 45
        humidityOUT = 100 * (dataOUT[3] * 256 + dataOUT[4]) / 65535.0

        # Reconstruct updated data history
        time_buffer.append(datetime.datetime.now().strftime('%r'))
        data_buffer.append(np.array([ cTempIN, cTempOUT, humidityIN, humidityOUT]))

        if time.time() - time_zero > 24*3600:
            time_buffer.pop(0)
            data_buffer.pop(0)

        # ---------- Log data ---------- #
        with open('/home/pi/Documents/projects/weather_station/data.csv', 'a', encoding='UTF8', newline='') as data_file:
            data_writer = csv.writer(data_file)

            # write the data
            data_writer.writerow([time_buffer[-1]] + data_buffer[-1].tolist())

        time.sleep(dT-0.5)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Temperature and humidity live measurement'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=dT*1e3, # in milliseconds
            n_intervals=0
        )
    ])
)




# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Temperature [°C]", "Humidity[%]") )

    if len(time_buffer) > 1:

        data_buffer_plot = np.array(data_buffer).T

        # Temperature data
        fig.add_trace(go.Scatter(x=time_buffer, y=data_buffer_plot[0, :], line_color="blue", name="Inside"), row=1, col=1)
        fig.add_trace(go.Scatter(x=time_buffer, y=data_buffer_plot[1, :], line_color="orange", name="Outside"), row=1, col=1)
        
        # Humidity data
        fig.add_trace(go.Scatter(x=time_buffer, y=data_buffer_plot[2, :], line_color="blue", showlegend=False), row=1, col=2)
        fig.add_trace(go.Scatter(x=time_buffer, y=data_buffer_plot[3, :], line_color="orange", showlegend=False), row=1, col=2)

    return fig

if __name__ == '__main__':

    # Get I2C bus
    sensorIn = smbus.SMBus(1)
    sensorOut = smbus.SMBus(3)

    # Data
    time_buffer = []
    data_buffer = []

    time_zero = time.time()

    with open('/home/pi/Documents/projects/weather_station/data.csv', 'w', encoding='UTF8', newline='') as data_file:
        data_writer = csv.writer(data_file)
        data_writer.writerow(['time', 'temperatureIN', 'temperatureOUT', 'humidityIN', 'humidityOUT'])

    sensor_reader_thread = threading.Thread(target=sensor_reader, daemon=True)
    sensor_reader_thread.start()

    app.run_server(host='0.0.0.0', debug=False)
    
