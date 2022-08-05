# Information was retrieved from Samsara's databases by their API according to the documentation found here:
# https://developers.samsara.com/reference/overview
# https://developers.samsara.com/docs/telematics
# https://developers.samsara.com/reference/getvehiclestats

import requests
import json
import time
import pandas as pd
import matplotlib.pyplot as plt

# API Token has been removed for security reasons
token = 'SAMSARA_SENSOR_TOKEN'  # token only has access to reading and writing sensor data
params = {'sensors': 'id'}
headers = {'Authorization': 'Bearer ' + token}


# Testing if current sensor data is reachable by printing out the most recent values for the Temperature,
# Humidity and Door Status attributes, as well as printing out information about the sensor
def initial_connection():
    for urlValue in ['temperature', 'humidity', 'door', 'list']:
        url = 'https://api.samsara.com/v1/sensors/' + urlValue
        response = requests.request('GET', url=url, headers=headers, params=params).json()
        print("-- Printing data for sensor: " + urlValue + "\n" + str(response))


initial_connection()


# Retrieving dates in Year-Month-Date format for each day between 2022-06-26 00:00 and 2022-07-25 00:00 for
# temperature and humidity graphs
dateHistoryContainer = []
for x in range(1656198000, 1658790000, 86400):
    convertedTime = time.strftime('%Y-%m-%d', time.localtime(x))
    dateHistoryContainer.append(convertedTime)


# Retrieving the temperature and humidity data for each day between 2022-06-26 00:00 and 2022-07-25 00:00
sensorHistoryUrl = 'https://api.samsara.com/v1/sensors/history'
sensorHistoryParams = {
                 'endMS': 1658793600000,
                 'fillMissing': 'withNull',
                 'series': [{'field': 'ambientTemperature',
                             'widgetId': 278018084739635}],
                 'startMs': 1656198000000,
                 'stepMS': 3600000
                 }
tempHistoryData = []
humidHistoryData = []
valueSum = 0  # For summing up the 24 values per day, so average can be calculated and appended to list
for i in ['ambientTemperature', 'humidity']:
    sensorHistoryParams['series'][0]['field'] = i  # Changing the parameters for the API request to retrieve humidity and temperature data
    tempHistoryResponse = requests.post(url=sensorHistoryUrl, headers=headers, data=json.dumps(sensorHistoryParams)).json()
    for y in range(1, 721):  # There are 720 values in the request for every hour of 30 days (30 * 24)
        if i == 'ambientTemperature':
            valueSum += round((tempHistoryResponse['results'][y]['series'][0] / 1000), 1)  # Temperature data is retrieved in millicelcius therefore dividing by 1000 and rounding to 1 decimal place
        elif i == 'humidity':
            valueSum += tempHistoryResponse['results'][y]['series'][0]
        if y % 24 == 0 and y != 0:  # Take the average of the 24 data values extracted for every day and append it to final data list
            valueSum /= 24
            if i == 'ambientTemperature':
                tempHistoryData.append(round(valueSum, 1))
            elif i == 'humidity':
                humidHistoryData.append(round(valueSum, 1))
            tempSum = 0  # Zero the integer holding the sum of values when data for a new day gets extracted


# Plotting the graphs for humidity and temperature data side by side
dateHistoryContainer = pd.to_datetime(dateHistoryContainer)
DF = pd.DataFrame()
DF2 = pd.DataFrame()
DF['value'] = tempHistoryData
DF2['value'] = humidHistoryData
DF = DF.set_index(dateHistoryContainer)
DF2 = DF2.set_index(dateHistoryContainer)
fig, (ax1, ax2) = plt.subplots(1, 2)  # Plot the graphs side by side
ax1.plot(DF)
ax2.plot(DF2)
ax1.set_xlabel("Time")
ax1.set_ylabel("Temperature in Celsius")
ax2.set_xlabel("Time")
ax2.set_ylabel("Humidity in Percentage")
plt.gcf().autofmt_xdate()
plt.show()


# Retrieving door status data between 2022-06-26 00:00 and 2022-07-02 00:00 per every hour
doorHistoryParams = {
                 'endMS': 1656802800000,
                 'fillMissing': 'withNull',
                 'series': [{'field': 'doorClosed',
                             'widgetId': 278018084465093}],
                 'startMs': 1656198000000,
                 'stepMS': 3600000
                 }
doorHistoryResponse = requests.post(url=sensorHistoryUrl, headers=headers, data=json.dumps(doorHistoryParams)).json()
doorStatusList = []
for z in range(0, 168):  # Extracting the binary values of the door status indicator from the request and appending it to a list
    doorStatusList.append(doorHistoryResponse['results'][z]['series'][0])

# Converting epoch time to Year-Month-Date format per hour, between 2022-06-26 00:00:00 and 2022-07-02 23:00:00 for the Door Status dataset
doorTimeContainer = []
for w in range(1656198000, 1656802800, 3600):
    doorTime = time.strftime('%Y-%m-%d', time.localtime(w))
    doorTimeContainer.append(doorTime)


# Plotting the graph for the door status data
doorTimeContainer = pd.to_datetime(doorTimeContainer)
data3 = doorStatusList
DF3 = pd.DataFrame()
DF3['value'] = data3
DF3 = DF3.set_index(doorTimeContainer)
plt.plot(DF3)
plt.gcf().autofmt_xdate()
plt.xlabel("Time")
plt.ylabel("Door Status where 0 = Open, 1 = Closed")
plt.show()
