import smbus
import time

import datetime

import dash
from dash import dcc, html
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# pip install pyorbital
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Temperature and humidity live measurement'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*10000, # in milliseconds
            n_intervals=0
        )
    ])
)




# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global time_buffer
    global data_buffer

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
    
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Temperature [°C]", "Humidity[%]") )

    if len(time_buffer) > 1:

        if time.time() - time_zero > 3600:
            time_buffer.pop(0)
            data_buffer.pop(0)

        data_buffer_plot = np.array(data_buffer).T

        # Tempeature data
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

    app.run_server(host='0.0.0.0', debug=True)
    
