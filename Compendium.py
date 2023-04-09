import datetime
from datetime import time
from nsepython import *
import warnings
import requests
import numpy as np
import pandas as pd
import streamlit as st
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
    server.login('dhruv.suresh2@gmail.com', st.secrets["password"])
    server.sendmail(msg['From'], 'f20180884g@alumni.bits-pilani.ac.in' , msg.as_string())
    server.close()

def Sleeper():
    t = datetime.datetime.now().time().minute
    s = datetime.datetime.now().time().second
    upper_three_min = math.ceil(t / 3) * 3
    diff = upper_three_min - t
    if diff == 0:
        diff = 3
    else:
        pass
    sleep_time_sec = ((diff - 1) * 60) + (60 - s)
    return sleep_time_sec
    
st.title("BANKNIFTY Compendium Generator")

while True:
    current_weekday = datetime.datetime.now().weekday()
    email_df = pd.DataFrame()
    while current_weekday in range(0,5):
        current_time = datetime.datetime.now().time()
        session_start = datetime.time(3,46,00)
        session_end = datetime.time(10,3,00)
        while current_time > session_start and current_time < session_end:
            sleepy_time = Sleeper()
            time.sleep(sleepy_time)
            st.write("Sleeping for {} seconds".format(sleepy_time))
            df = Get_option_chain()
            Send_email(df)
            email_df = pd.concat([email_df, df])
            st.write("Email sent for time {}".format(str(datetime.datetime.now().time())))
        time.sleep(60)
        st.write("Not within market hours")
    if email_df.empty:
        st.write("Weeknd is here")
    else:
        st.write("Sending final Compendium email")
        Send_email(email_df)
    time.sleep(60)
