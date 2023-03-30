import streamlit as st
import datetime
from nsepython import *
import warnings
import requests
import numpy as np
import pandas as pd

from urllib.parse import urlencode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from io import StringIO
import smtplib
import time

warnings.filterwarnings('ignore')

def Get_option_chain():
    df, ltp, crontime = oi_chain_builder("BANKNIFTY","latest","full")
    df = df.loc[:,['CALLS_OI', 'CALLS_Chng in OI', 'CALLS_Volume',
          'CALLS_IV', 'CALLS_LTP', 'CALLS_Net Chng', 'CALLS_Bid Qty',
          'CALLS_Bid Price', 'CALLS_Ask Price', 'CALLS_Ask Qty', 'Strike Price',
          'PUTS_Bid Qty', 'PUTS_Bid Price', 'PUTS_Ask Price', 'PUTS_Ask Qty',
          'PUTS_Net Chng', 'PUTS_LTP', 'PUTS_IV', 'PUTS_Volume',
          'PUTS_Chng in OI', 'PUTS_OI']]

    df.insert(0, "Ticktime", crontime)
    df.insert(1, "Spot", ltp)
    return df

def Send_email(df):
    msg = MIMEMultipart()
    msg['Subject'] = "BANKNIFTY Option Chain"
    msg['From'] = "dhruv.suresh2@gmail.com"
    msg.add_header('Content-Type','text/html')

    textStream = StringIO()
    df.to_csv(textStream,index=False)
    msg.attach(MIMEApplication(textStream.getvalue(), Name = 'BANKNIFTY_Option_Chain.csv'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('dhruv.suresh2@gmail.com', 'easiwykbdojoolxt')
    server.sendmail(msg['From'], 'f20180884g@alumni.bits-pilani.ac.in' , msg.as_string())
    server.close()

st.title("BANKNIFTY Compendium Generator")

while True:
    email_df = pd.DataFrame()
    current_datetime = datetime.datetime.now()
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute
    current_second = current_datetime.second
    current_weekday = current_datetime.weekday()
    while current_weekday in range(0,5) and current_hour in range(3,11):
        if current_hour == 3:
            if current_minute > 48:
                df = Get_option_chain()
                email_df = pd.concat([email_df, df])
                time.sleep(300)
            else:
                time.sleep(60)
        else:
            df = Get_option_chain()
            email_df = pd.concat([email_df, df])
            time.sleep(300)
    if email_df.empty:
        time.sleep(60)
        continue
    else:
        Send_email(email_df)
        time.sleep(60)
        continue
