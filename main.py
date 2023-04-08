import sys

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")
from keras.layers import LSTM, Dropout, Dense

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import matplotlib.pyplot as plt

from matplotlib.pylab import rcParams
from sklearn.preprocessing import MinMaxScaler

rcParams['figure.figsize'] = 20, 10

import sklearn

scaler = MinMaxScaler(feature_range=(0, 1))

from keras import *
choice = int(input(print("Enter a stock to predict:1.Tata 2:Reliance 3.Dmart:")))
if choice == 1:
    df = pd.read_csv("NSE-Tata-Global-Beverages-Limited.csv")
    df["Date"] = pd.to_datetime(df.Date, format="%Y-%m-%d")
    df.index = df['Date']
elif choice == 2:
    df = pd.read_csv("Reliance-limited.csv")
    df["Date"] = pd.to_datetime(df.Date, format="%m/%d/%Y")
    df.index = df['Date']
elif choice == 3:
    df = pd.read_csv("d_spy_GOOGL.csv")
    df["Date"] = pd.to_datetime(df.Date, format="%m/%d/%Y")
    df.index = df['Date']
else:
    sys.exit("invalid choice")
plt.figure(figsize=(10, 5))
plt.plot(df["Close"], label='Close Price history')
data = df.sort_index(ascending=True, axis=0)
new_dataset = pd.DataFrame(index=range(0, len(df)), columns=['Date', 'Close'])

for i in range(0, len(data)):
    new_dataset["Date"][i] = data['Date'][i]
    new_dataset["Close"][i] = data["Close"][i]

new_dataset.index = new_dataset.Date
new_dataset.drop("Date", axis=1, inplace=True)

final_dataset = new_dataset.values

train_data = final_dataset[0:987, :]
valid_data = final_dataset[987:, :]

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(final_dataset)

x_train_data, y_train_data = [], []

for i in range(60, len(train_data)):
    x_train_data.append(scaled_data[i - 60:i, 0])
    y_train_data.append(scaled_data[i, 0])

x_train_data, y_train_data = np.array(x_train_data), np.array(y_train_data)

x_train_data = np.reshape(x_train_data, (x_train_data.shape[0], x_train_data.shape[1], 1))
lstm_model = Sequential()
lstm_model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train_data.shape[1], 1)))
lstm_model.add(Dropout(0.2))
lstm_model.add(LSTM(units=50))
lstm_model.add(Dropout(0.2))
lstm_model.add(Dense(1))

lstm_model.compile(loss='mean_squared_error', optimizer='adam')
lstm_model.fit(x_train_data, y_train_data, epochs=10, batch_size=16, verbose=2)
inputs_data = new_dataset[len(new_dataset) - len(valid_data) - 60:].values
inputs_data = inputs_data.reshape(-1, 1)
inputs_data = scaler.transform(inputs_data)

X_test = []
for i in range(60, inputs_data.shape[0]):
    X_test.append(inputs_data[i - 60:i, 0])
X_test = np.array(X_test)

X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

closing_price = lstm_model.predict(X_test)
closing_price = scaler.inverse_transform(closing_price)

lstm_model.save("saved_lstm_model.h5")

train_data = new_dataset[:987]
valid_data = new_dataset[987:]
valid_data['Predictions'] = closing_price
plt.plot(train_data[["Close"]])
plt.show()
plt.plot(valid_data[['Close', "Predictions"]])
plt.show()
