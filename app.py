#Importing Libraries
from datetime import datetime
import math
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
import url
import base64
import json

user_db = {}
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {}

st.set_page_config(page_title="Laptop Price Prediction", page_icon="💻", layout="wide")


# Define the login/signup page function
def login_signup():
    # Check if we are in signup mode
    if 'signup_mode' not in st.session_state:
        st.session_state['signup_mode'] = True  # Show signup by default

    if st.session_state['signup_mode']:
        # Display the signup form
        st.subheader("Signup")
        new_username = st.text_input("Create username", key="signup_name")
        new_password = st.text_input("Create password", type="password", key="signup_password")
        if st.button("Signup"):
            signup_success = signup(new_username, new_password)
            if signup_success:
                # If signup is successful, switch to login mode
                st.session_state['signup_mode'] = False

        # Add a button to switch to login
        if st.button("Switch to Login"):
            st.session_state['signup_mode'] = False
    else:
        # Display the login form
        st.subheader("Login")
        username = st.text_input("Enter username", key="login_name")
        password = st.text_input("Enter password", type="password", key="login_password")
        if st.button("Login"):
            login(username, password)

        # Add a button to switch to signup
        if st.button("Switch to Signup"):
            st.session_state['signup_mode'] = True

# Adjust the signup function to return a success status
def signup(username, password):
    user_db = st.session_state['user_db']
    if username in user_db:
        st.error("Username already exists!")
        return False
    else:
        user_db[username] = password
        st.success("Signup successful!")
        print("Current user database:", user_db)  # Debug line to print the user database
        return True
    
# Login function
def login(username, password):
    user_db = st.session_state['user_db']
    if username in user_db and user_db[username] == password:
        st.session_state['logged_in'] = True
        st.success("Login successful!")
        print(f"User {username} logged in.")  # Debug line to confirm login
    else:
        st.error("Incorrect username or password")

def save_to_csv(data):
    with open('predicted_prices.csv', 'a+') as f:
        if f.tell() == 0:
            pd.DataFrame([data]).to_csv(f, index=False)
        else:
            pd.DataFrame([data]).to_csv(f, mode='a', index=False, header=False)

# @st.cache_data 
# def load_data():
#     return pd.read_csv('predicted_prices.csv')


def main_page():

    def get_laptop_price(company,cpu,gpu,hdd,ips,os,ram,resolution,screen_size,ssd,touchscreen,type,weight):
        data = {
            "company": company,
            "type": type,
            "ram": int(ram),
            "weight": weight,
            "touchscreen": int(touchscreen),
            "ips": int(ips),
            "ppi": int(ppi),
            "cpu": cpu,
            "hdd": int(hdd),
            "ssd": int(ssd),
            "gpu": gpu,
            "os": os,
            "resolution":resolution,
            "screen_size":screen_size
                }

        print(data)
        response = requests.post(url.getUrl(), json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to get price. Status code: {}".format(response.status_code)}

    
    
    #import model
    st.markdown("<h1 style='text-align: center;'>Laptop Price Prediction 💻</h1>", unsafe_allow_html=True)
    pipe=pickle.load(open("pipe.pkl","rb"))
    df=pickle.load(open("df.pkl","rb"))

    # making 3 cols left_column, middle_column, right_column
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
    # brand input
        company = st.selectbox("Brand", df["Company"].unique())

    with middle_column:
        # laptop type
        type = st.selectbox("Type", df["TypeName"].unique())

    with right_column:
        # Ram size
        ram = st.selectbox("Ram (in GB)", df["Ram"].unique())

    # making 3 cols left_column, middle_column, right_column
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        # Weight input
        weight = st.number_input("Weight of laptop in kg", min_value=0.5, max_value=5.0, format="%f")

    with middle_column:
        # Touchscreen
        touchscreen = st.selectbox("Touchscreen", ["No", "Yes"])

    with right_column:
        # IPS display
        ips = st.selectbox("IPS Display", ["No", "Yes"])

    # making 3 cols left_column, middle_column, right_column
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        # screen size
        screen_size = st.number_input("Screen Size (in Inches)")

    with middle_column:
        # resolution
        resolution = st.selectbox('Screen Resolution',['1920x1080', '1366x768', '1600x900', '3840x2160', '3200x1800', '2880x1800', '2560x1600','2560x1440', '2304x1440'])
    with right_column:
        # cpu input
        cpu = st.selectbox("CPU Brand", df["Cpu brand"].unique())

    # making 3 cols left_column, middle_column, right_column
    left_column,  right_column = st.columns(2)
    with left_column:
        # hdd input
        hdd = st.selectbox("HDD(in GB)", [0, 128, 256, 512, 1024, 2048])


    with right_column:
        # ssd input
        ssd = st.selectbox("SSD(in GB)", [0, 8, 128, 256, 512, 1024])

    #gpu input
    gpu=st.selectbox("GPU Brand",df["Gpu brand"].unique())

    #os input
    os=st.selectbox("OS Type",df["os"].unique())


    if st.button("Predict Price"):
        ppi = None
        if touchscreen=="Yes":
            touchscreen=1
        else:
            touchscreen=0

        if ips == "Yes":
            ips=1
        else:
            ips=0

        X_res=int(resolution.split("x")[0])
        Y_res=int(resolution.split('x')[1])
        ppi=((X_res * 2)+(Y_res * 2))**0.5/float(screen_size)
        
        result = get_laptop_price(company,cpu,gpu,hdd,ips,os,ram,resolution,screen_size,ssd,touchscreen,type,weight)
        if 'data' in result and len(result['data']) > 1:
            price = float(result['data'][1]['price'])  # Convert price to float
        final_price = price * 1.6  # Multiply by 1.6
        st.title(f"The Predicted Price of Laptop = Rs {final_price:.2f}")
        chart_data = pd.DataFrame({"Value": [result["data"][1]["MAE"], result["data"][1]["R2 Score"]]}, index=["MAE", "R2 Score"])
        st.bar_chart(chart_data)
        
        prediction_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Company": company,
        "CPU Brand": cpu,
        "GPU Brand": gpu,
        "HDD": hdd,
        "IPS": ips,
        "OS": os,
        "RAM": ram,
        "Resolution": resolution,
        "Screen Size": screen_size,
        "SSD": ssd,
        "Touchscreen": touchscreen,
        "Type": type,
        "Weight": weight,
        "Predicted Price": final_price,
        "Mean Absolute Error": result["data"][1]["MAE"],
        "R2 Score": result["data"][1]["R2 Score"]}
        save_to_csv(prediction_data)

        st.write("# Predicted Laptop Prices")
        table = pd.read_csv("predicted_prices.csv")
        st.write(table)


   

    # Function to get image in base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
    return data



if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_signup()
else:

# Since image is in the same directory as the script
    logo_base64 = get_image_as_base64("tulogo.png")


# Prepare the header HTML with the base64 string for the image
    header_html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px;">
    <h2 style="margin: 0;">Bhaktapur Multiple Campus</h2>
    <img src="data:image/png;base64,{logo_base64}" alt="Logo" height="80px">
    <h2 style="margin: 0;">Tribhuvan University</h2>
    </div>
"""
    footer_html = """
<div style="position: fixed; bottom: 10px; left: 0; width: 100%; text-align: center; font-size: 0.9em;">
    <div style="position: relative; display: flex; justify-content: space-between; align-items: center;">
        <div style="margin-left: 10px;">
            <h5>Ronit Shrestha<br>23260/076</h5>
        </div>
        <div>
            <h5>Utsav Sapkota<br>23285/076</h5>
        </div>
        <div style="margin-right: 10px;">
            <h5>Roshan Blon<br>23261/076</h5>
        </div>
    </div>
</div>
"""
    st.markdown(footer_html, unsafe_allow_html=True)

    st.markdown(header_html, unsafe_allow_html=True)

    main_page()