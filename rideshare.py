from os import name
import firebase_admin
from flask import *
from firebase_admin import credentials, initialize_app, storage, db
import tempfile
import requests
import urllib3
import pandas as pd
import numpy as np
import json
import fsspec
import plotly.express as px
import plotly.io as pio
from datetime import datetime as dt
from datetime import timedelta
import pytz



app = Flask(__name__)
cred = credentials.Certificate("ride-share-e3b61-firebase-adminsdk-9phyr-6bace89f40.json")
db_app = initialize_app(credential=cred)
def filter_rides(raw_data,hours_before, hours_after):
    start_time = dt.now(pytz.timezone('Asia/Dhaka')).replace(tzinfo=None)-timedelta(hours=hours_before)
    end_time = start_time + timedelta(hours=hours_before+hours_after)
    raw_data.sort_values(by=['Ride Start Time'], ascending=False)
    filter = (raw_data['Ride Start Time']>start_time) & (raw_data['Ride Start Time']<end_time) 
    filtered_rides = raw_data[filter]
    return filtered_rides
def filtered_search(raw_data,hours_before, hours_after, starting_point, ending_point):
    start_time = hours_before
    end_time = hours_after
    filter = (raw_data['Ride Start Time']>start_time) & (raw_data['Ride Start Time']<end_time) & (raw_data['Ending Point']==ending_point) & (raw_data['Starting Point']==starting_point)
    filtered_rides = raw_data[filter]
    return filtered_rides    

@app.route('/request-ride/',  methods=['GET', 'POST'])
def req_ride():
    if request.method=="POST":
        user_name = request.form['user_name']
        starting_point = request.form['starting_point']
        ending_point = request.form['end_point']
        note = request.form['special_note']
        phone_num = request.form['phone_num']
        select_date = request.form['start_date_input']
        select_time = request.form['start_time_input']
        start_date_and_time = dt.strptime(" ".join([select_date, select_time]), '%Y-%m-%d %H:%M')
        select_end_date = request.form['end_date_input']
        select_end_time = request.form['end_time_input']
        end_date_and_time = dt.strptime(" ".join([select_end_date, select_end_time]), '%Y-%m-%d %H:%M')
        ref = db.reference("/",app=db_app ,url='https://ride-share-e3b61-default-rtdb.firebaseio.com/')
        ref.push(value=
          {
              'User Name' : user_name,
              'Starting Point' : starting_point,
              'Ending Point' : ending_point,
              'Note' : note,
              'Phone Number' : phone_num,
              'Ride Start' : str(start_date_and_time),
              'Ride End' : str(end_date_and_time)
          }
        )
        return redirect('/')
    else:    
        with open('stopagelist.txt', 'r') as stopages:
            stop_list = stopages.readlines()
         
        return render_template('request_ride.html', stops=stop_list)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method=="POST":
        select_date = request.form['start_date_input']
        
        select_time = request.form['start_time_input']
        start_date_and_time = dt.strptime(" ".join([select_date, select_time]), '%Y-%m-%d %H:%M')
        select_end_date = request.form['end_date_input']
        select_end_time = request.form['end_time_input']
        end_date_and_time = dt.strptime(" ".join([select_end_date, select_end_time]), '%Y-%m-%d %H:%M')
        starting_point = request.form['starting_point']
        ending_point = request.form['end_point']
       
        ref = db.reference("/",app=db_app ,url='https://ride-share-e3b61-default-rtdb.firebaseio.com/')
        dict_rides = ref.get()
        df = pd.DataFrame.from_dict(dict_rides, orient='index')
        df['Ride Start Time'] = pd.to_datetime(df['Ride Start'])
        df['Ride End Time'] = pd.to_datetime(df['Ride End'])
        
        prefered_rides = filtered_search(raw_data=df, 
        hours_before=start_date_and_time,
        hours_after=end_date_and_time,
        starting_point=starting_point, 
        ending_point=ending_point)
        with open('stopagelist.txt', 'r') as stopages:
            stop_list = stopages.readlines()   
        return render_template('home.html', rides=prefered_rides.values.tolist(),stops=stop_list)
        
    else:    
        ref = db.reference("/",app=db_app ,url='https://ride-share-e3b61-default-rtdb.firebaseio.com/')
        dict_rides = ref.get()
        df = pd.DataFrame.from_dict(dict_rides, orient='index')
        df['Ride Start Time'] = pd.to_datetime(df['Ride Start'])
        df['Ride End Time'] = pd.to_datetime(df['Ride End'])
        prefered_rides = filter_rides(raw_data=df, hours_before=2, hours_after=3)
        with open('stopagelist.txt', 'r') as stopages:
            stop_list = stopages.readlines()
          
        return render_template('home.html',rides=prefered_rides.values.tolist(), stops=stop_list)
@app.route('/ourteam')
def team():
    return render_template('team.html') 


if __name__=='__main__':
    app.run(debug=True)




