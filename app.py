#last left line 506

import streamlit as st
import mysql.connector
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import re
import hashlib

# For music.py
import asyncio
import nest_asyncio
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2 
import numpy as np 
import mediapipe as mp 
from keras.models import load_model
import webbrowser 
import os
import pygame
import time
from mutagen.mp3 import MP3

# Database Connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='newlogin'
)
cursor = conn.cursor()


if os.path.exists("emotion.npy"):
    os.remove("emotion.npy")

if 'emotion' not in st.session_state:
    st.session_state['emotion'] = None

#illintr
# Initialize Pygame mixer
pygame.mixer.init()

# Get list of MP3 files
mp3_files = [file for file in os.listdir("mp3_files") if file.endswith(".mp3")]

# Get list of playlists (subfolders inside "mp3_files")
playlist_folders = [folder for folder in os.listdir("mp3_files") if os.path.isdir(os.path.join("mp3_files", folder))]
playlist_folders.insert(0, "None")

# Initialize session state variables
if "current_song_index" not in st.session_state:
    st.session_state.current_song_index = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False
if "volume" not in st.session_state:
    st.session_state.volume = 0.5  # Default volume 50%
if "paused" not in st.session_state:
    st.session_state.paused = False
if "track_position" not in st.session_state:
    st.session_state.track_position = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "selected_playlist" not in st.session_state:
    st.session_state.selected_playlist = "None"

# Playlist Selection
# st.session_state.selected_playlist = st.selectbox("🎵 Select Playlist:", playlist_folders, key="playlist_selection")
if st.session_state['emotion'] == "Happy" or "neutral":
    st.session_state.selected_playlist = "Happy_songs"
elif st.session_state['emotion'] == "Sad" or "angry":
    st.session_state.selected_playlist = "Sad_songs"

# Load songs based on selected playlist
if st.session_state.selected_playlist == "None":
    filtered_mp3_files = [file for file in os.listdir("mp3_files") if file.endswith(".mp3")]
    song_folder = "mp3_files"
else:
    filtered_mp3_files = [file for file in os.listdir(f"mp3_files/{st.session_state.selected_playlist}") if file.endswith(".mp3")]
    song_folder = f"mp3_files/{st.session_state.selected_playlist}"


def play_song(song_path, start_position=0):
    """Play the song from a specific position."""
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play(start=start_position)
    pygame.mixer.music.set_volume(st.session_state.volume)
    st.session_state.is_playing = True
    st.session_state.paused = False
    st.session_state.track_position = start_position
    st.session_state.start_time = time.time() - start_position  # Adjust start time

def pause_song():
    """Pause the song and store the track position."""
    pygame.mixer.music.pause()
    st.session_state.is_playing = False
    st.session_state.paused = True
    st.session_state.track_position = int(time.time() - st.session_state.start_time)  # Save current position

def resume_song():
    """Resume the song from the paused position."""
    pygame.mixer.music.unpause()
    st.session_state.is_playing = True
    st.session_state.paused = False
    st.session_state.start_time = time.time() - st.session_state.track_position  # Adjust start time

def seek_song(position, song_path):
    """Seek to a new position in the song."""
    pygame.mixer.music.stop()
    play_song(song_path, start_position=position)
    st.session_state.track_position = position
    st.session_state.start_time = time.time() - position  # Adjust start time

def get_song_length(song_path):
    """Get the length of the song in seconds."""
    try:
        audio = MP3(song_path)
        return int(audio.info.length)
    except:
        return 1  # Default to 1 second if error

def get_current_position():
    """Get the current playback position."""
    if st.session_state.is_playing:
        return int(time.time() - st.session_state.start_time)  # Compute actual position
    return int(st.session_state.track_position)  # Ensure it's always an integer

if 'lang' not in st.session_state:
    st.session_state['lang'] = None

# Initialize Session State
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Login Function
def login():
    st.title("Login")
    st.toast("New to Mano-Raag? Register it fastttt..!", icon="🏃🏻‍➡️")
    username = st.text_input("Email", placeholder="Enter your Email")
    password = st.text_input("Password", type="password", placeholder="Enter your Password")
    
    if st.button("Login", icon="🔑"):
        sha = hashlib.sha256(password.encode('utf-8')).hexdigest()
        cursor.execute("SELECT * FROM passwords_backup WHERE user_id = (SELECT id FROM users WHERE email = %s);",(username,))
        user = cursor.fetchone()
        if user and sha == user[2]:  # Password check (decryption removed)
            st.session_state['user'] = username
            st.success("Login successful!")
            st.rerun() #st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Register Function
def register():

    def validate_password(pw):
        if len(pw) < 8:
            return "❌ Must be at least 8 characters."
        if not re.search(r"[A-Z]", pw):
            return "❌ Include at least one uppercase letter."
        if not re.search(r"[a-z]", pw):
            return "❌ Include at least one lowercase letter."
        if not re.search(r"\d", pw):
            return "❌ Include at least one digit."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw):
            return "❌ Include at least one special character."
        return "✅ Strong password!"

    st.title("Register")
    st.toast("Already a user? Then enjoy 'Mano-Raag' by Logging In..! 🎵", icon="⁉️")
    username = st.text_input("Username", placeholder="Enter your name")
    email = st.text_input("Email", placeholder="Enter your email")
    if (password := st.text_input("Enter Password", type="password", placeholder="Password must contain min 8 chars with a Capital, Small, Number & Special Char")):
        message = validate_password(password)
        (st.success if "✅" in message else st.error)(message)
    if(confirm_password := st.text_input("Confirm Password", type="password", placeholder="Re-enter the Password")):
        if password != confirm_password:
            st.error("Password Doesn't Match")
    #Restricting for less than 3 years old for data safety
    cur_date = datetime.now().date()
    max_date = cur_date - timedelta(days=3*365)
    dob = st.date_input("Date of Birth", max_value=max_date)
    gender = st.selectbox("Gender", ["Male", "Female", "Others"])

    if st.button("Register", icon="📝") and password == confirm_password:

        # Create a single database connection
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='newlogin'
        )

        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            email_exists = cursor.fetchone()[0]

            if email_exists:
                st.error("⚠️ Email already exists. Try another one.")
                return  # Stop execution
            
            hashed_pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            # Insert user data into users table
            cursor.execute("INSERT INTO users (username, email, dob, gender) VALUES (%s, %s, %s, %s)",
                           (username, email, dob, gender))
            conn.commit()

            # Fetch User ID from users table
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            user_id = cursor.fetchone()  # Fetch user ID

            if user_id:  # Ensure user ID is retrieved
                cursor.execute("INSERT INTO passwords_backup(user_id, hash_pwd) VALUES (%s, %s)",
                               (user_id[0], hashed_pwd))
                conn.commit()
            st.snow()
            st.toast("Now enjoy the unimaginale experince in Mano-Raag's Music World..!🎵😊")
            st.success("🎉Registration successful! Please log in.")

        except mysql.connector.Error as err:
            st.error(f"{err}")
            conn.rollback()  # Rollback in case of error

        finally:
            cursor.close()
            conn.close()

# Forgot Password Function
def forgot_password():
    st.title("Forgot Password")

    def validate_password(pw):
        if len(pw) < 8:
            return "❌ Must be at least 8 characters."
        if not re.search(r"[A-Z]", pw):
            return "❌ Include at least one uppercase letter."
        if not re.search(r"[a-z]", pw):
            return "❌ Include at least one lowercase letter."
        if not re.search(r"\d", pw):
            return "❌ Include at least one digit."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw):
            return "❌ Include at least one special character."
        return "✅ Strong password!"

    email = st.text_input("Email", placeholder="Enter the correct email")
    dob = st.date_input("Date of Birth")
    if (password := st.text_input("Enter Password", type="password", placeholder="Password must contain min 8 chars with a Capital, Small, Number & Special Char")):
        message = validate_password(password)
        (st.success if "✅" in message else st.error)(message)
    if(confirm_password := st.text_input("Confirm Password", type="password", placeholder="Re-enter the Password")):
        if password != confirm_password:
            st.error("Password Doesn't Match")

    if st.button("Reset Password"):

        dob_str = dob.strftime('%Y-%m-%d')

        cursor.execute("SELECT * FROM users WHERE email = %s AND dob = %s", (email, dob_str,))
        user = cursor.fetchone()
        uid = user[0]

        if user:
            cursor.execute("SELECT hash_pwd FROM passwords_backup WHERE user_id = %s", (uid,))
            pwd = cursor.fetchone()

            sha = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            if sha == pwd[0]:
                st.error("Password Cannot be same as previous")

            else:

                cursor.execute("UPDATE passwords_backup SET hash_pwd = %s WHERE user_id = %s", (sha, uid,))
                conn.commit()
                st.success("Password Changed..!")
        
        else:
            st.warning("Your Email or DOB doesn't match in our database..!\n Please Try Again or Register and start experiencing out Services..!")
        
# Capture Function
def capture():

    # Embedding music.py

    model  = load_model("model.h5")
    label = np.load("labels.npy")
    holistic = mp.solutions.holistic
    hands = mp.solutions.hands
    holis = holistic.Holistic()
    drawing = mp.solutions.drawing_utils


    # Apply nested asyncio fix
    nest_asyncio.apply()

    # Ensure there's an active event loop
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if "run" not in st.session_state:
        st.session_state['run'] = "true"
        
    if st.session_state['user']:
        
        mail = st.session_state['user']
        cursor.execute("SELECT username FROM users WHERE email = %s", (mail,))
        usr = cursor.fetchone()

        st.title(f"Hi {usr[0]}, This is Music Recommending Software Application")
                
        st.write("Please, Let me Capture your Emotion..!")
    
        st.write("Please give me Camera Access.")

        try:
            emotion = np.load("emotion.npy")[0]
        except:
            emotion = ""

        if not(emotion):
            st.session_state['run'] = "true"
        else:
            st.session_state['run'] = "false"

        class EmotionProcessor:
            def  recv(self, frame):
                
                frm= frame.to_ndarray(format="bgr24")

                ########################################

                frm = cv2.flip(frm, 1)

                res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

                lst = []

                if res.face_landmarks:
                    for i in res.face_landmarks.landmark:
                        lst.append(i.x - res.face_landmarks.landmark[1].x)
                        lst.append(i.y - res.face_landmarks.landmark[1].y)

                    if res.left_hand_landmarks:
                        for i in res.left_hand_landmarks.landmark:
                            lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                            lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
                    else:
                        for i in range(42):
                            lst.append(0.0)

                    if res.right_hand_landmarks:
                        for i in res.right_hand_landmarks.landmark:
                            lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                            lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
                    else:
                        for i in range(42):
                            lst.append(0.0)

                    lst = np.array(lst).reshape(1,-1)

                    pred = label[np.argmax(model.predict(lst))]

                    #prints the prediction of our emotion..!
                    print(pred)
                    cv2.putText(frm, pred, (50,50),cv2.FONT_ITALIC, 1, (255,0,0),2)

                    np.save("emotion.npy", np.array([pred]))

                    
                drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_CONTOURS)
                drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
                drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

                ########################################
                return av.VideoFrame.from_ndarray(frm, format = "bgr24")

        lang = st.selectbox("Languages", ["Select Language", "Kannada", "Hindi", "English", "Tamil", "Telugu", "Malayalam", "Marathi"])
        st.session_state['lang'] = lang

        if lang and (st.session_state['run'] == "true"):
            webrtc_streamer(key="music_stream", desired_playing_state=True, video_processor_factory=EmotionProcessor)

        btn = st.button("Let's Gooo..!")

        if btn:
            if not(emotion):
                st.warning("Please let me capture your emotion first")
                st.session_state['run'] = "true"
            else:
                st.write(f"You can go to Music Page now...") 

                np.save("emotion.npy", np.array([""]))

                st.session_state['emotion'] = emotion
            
                st.session_state['run'] = "false"
    else:
        st.warning("Please login first.")

# Music Player Function
def music():
    if st.session_state['user']:
        st.title("Music Player")
        st.write("Welcome to the music section.")
        if st.session_state['emotion']:
            st.write(f"Your current emotion is {st.session_state['emotion']}.")

            #illintr

            st.title("🎵 Mano-Raaga 🎶")

            # Ensure there are songs in the selected playlist
            if not filtered_mp3_files:
                st.warning(f"No songs found in {st.session_state.selected_playlist}.")
                return

            # Get the current song
            current_song_index = st.session_state.current_song_index
            current_song = filtered_mp3_files[current_song_index]
            song_path = os.path.join(song_folder, current_song)

            st.success(f"Now Playing: {current_song} from {st.session_state.selected_playlist}")

            # Play the song if not paused
            if not pygame.mixer.music.get_busy() and not st.session_state.paused:
                play_song(song_path)

            # Get song length
            song_length = get_song_length(song_path)

            # Update track position dynamically
            track_position = get_current_position()

            # Seek Slider
            new_position = st.slider("Seek", 0, song_length, track_position, 1)
            if new_position != track_position:
                seek_song(new_position, song_path)

            # Playback Controls
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⏮️ Previous") and current_song_index > 0:
                    st.session_state.current_song_index -= 1
                    st.session_state.paused = False
                    pygame.mixer.music.stop()
                    st.rerun()
            with col2:
                if st.session_state.is_playing:
                    if st.button("⏸ Pause"):
                        pause_song()
                        st.rerun()
                else:
                    if st.button("▶️ Play"):
                        resume_song()
                        st.rerun()
            with col3:
                if st.button("⏭️ Next") and current_song_index < len(filtered_mp3_files) - 1:
                    st.session_state.current_song_index += 1
                    st.session_state.paused = False
                    pygame.mixer.music.stop()
                    st.rerun()

            # Volume Control
            volume = st.slider("Volume", 0.0, 1.0, st.session_state.volume, 0.01)
            if volume != st.session_state.volume:
                pygame.mixer.music.set_volume(volume)
                st.session_state.volume = volume

            # Playlist Dropdown Below Volume Slider
            selected_song = st.radio("🎶 Up Next:", filtered_mp3_files, index=current_song_index, key="playlist_dropdown")

            # Play selected song if changed
            if selected_song != current_song:
                st.session_state.current_song_index = filtered_mp3_files.index(selected_song)
                pygame.mixer.music.stop()
                st.rerun()

            # Auto-refresh every second
            time.sleep(1)
            st.rerun()

            #illi mata
            
        else:
            st.write("Please be in your Capture Emotion Page until it captures your Emotion.")        
    else:
        st.warning("Please login first.")

# Dashboard Function
def dashboard():
    if st.session_state['user']:
        st.title("Dashboard")
        mail = st.session_state['user']
        cursor.execute("SELECT username FROM users WHERE email = %s", (mail,))
        usr = cursor.fetchone()
        st.write(f"Welcome, {usr[0]}!")
        st.title("About Us")
        st.write("Blah.. blah.. blahh..!")
        if st.session_state['lang'] != None:
            lang = st.session_state['lang'] #error ille irbahud 
            st.write(lang)
        if st.session_state['emotion'] == "Happy":
            st.toast(f"You seem very Happy today, without spoiling a second enjoy your favorite Music from 'Mano-Raaga🎸' in {lang} language")
    else:
        st.warning("Please login first.")

# Page Selection
if st.session_state['user']:
    if st.session_state['emotion']:
        page = st.sidebar.radio("Navigation", ["Music", "Dashboard"])

        if st.sidebar.button("Logout"):  # Logout button
            st.session_state['user'] = None  # Clear session state
            st.rerun()
            
        if page == "Music":
            music()
        elif page == "Dashboard":
            dashboard()
    
    else:
        page = st.sidebar.radio("Navigation", ["Capture Emotion", "Music", "Dashboard"])

        if st.sidebar.button("Logout"):  # Logout button
            pygame.mixer.init()
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            # Stop any playing music
            st.session_state['user'] = None  # Clear session state
            st.session_state['emotion'] = None  # Reset emotion
            st.session_state['is_playing'] = False  # Reset playing state
            st.session_state['paused'] = False  # Reset paused state
            st.session_state['track_position'] = 0  # Reset track position
            st.session_state['start_time'] = 0  # Reset start time
            st.session_state['selected_playlist'] = "None"  # Reset playlist
            st.rerun()  # Refresh app to reflect changes


        if page == "Capture Emotion":
            capture()
        elif page == "Music":
            music()
        elif page == "Dashboard":
            dashboard()
        
else:
    page = st.sidebar.radio("Navigation", ["Login", "Register", "Forgot Password"])

    if page == "Login":
        login()
    elif page == "Register":
        register()
    elif page == "Forgot Password":
        forgot_password()


st.divider()  # Adds a horizontal line
st.markdown(
"<h6 style='text-align: center;'>© Mano-Raaga 2025<br>Developed by <span style='font-weight: bolder; color: cyan'>Darshan N Hulamani</span>. <br>All rights reserved!</h6>", 
unsafe_allow_html=True
)
#st.sidebar.markdown("---")
st.sidebar.divider()  # Adds a horizontal line
st.sidebar.markdown("<h6 style='text-align: center; color: #ff746c; font-size: 14px'>© Mano-Raaga 2025<br>Developed by <span style='font-weight: bolder; color: cyan'>Darshan N Hulamani</span>. <br>All rights reserved!</h6>",unsafe_allow_html=True)

# Close database connection
conn.close()