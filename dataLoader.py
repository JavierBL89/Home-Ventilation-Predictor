import pandas as pd


def data_loader():

    # load dataset
    df=pd.read_csv("madrid_fake_temperature_data_with_lags.csv")

    #convert timestap column to datetime format
    df["timestamp"]= pd.to_datetime(df["timestamp"])

    #displaye the first rows
    print(df.head())

    return df