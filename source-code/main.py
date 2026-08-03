import time
import subprocess
from tkinter import messagebox
import queue
import sys
import re
from tkinter import simpledialog, messagebox
from datetime import datetime
import tkinter as tk
import threading
import os
import calendar
import pyttsx3
import threading
import sqlite3
import webbrowser
from PIL import Image, ImageTk, ImageDraw
import speech_recognition as sr
import random
import time
import gaming
from gaming import open_gaming_window
import calendarr
from calendarr import open_calendar_window
import wikipedia
from calendarr import get_due_events
import queue
import keyboard
import pygame
import cv2
from picamera2 import Picamera2
import numpy as np


picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (3280, 2464)})
picam2.configure(camera_config)
picam2.start()
time.sleep(1)
print("📸 Global camera initialized with Picamera2")



# Track which window should receive D-pad events
current_dpad_target = None

def set_dpad_target(window):
    global current_dpad_target
    current_dpad_target = window



servo_talking = False 
# Track whether Game Mode is active
game_active = False  

keyboard_process = None  # global to track keyboard state
try:
    from gpiozero import Button
    import board, busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
    _GPIO_AVAILABLE = True
except ImportError:
    print("[STIMO] GPIO not available (probably running on Windows)")
    _GPIO_AVAILABLE = False

# === Servo Setup ===
if _GPIO_AVAILABLE:
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50

        servo_left_arm = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)
        servo_left_leg = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)
        servo_right_leg = servo.Servo(pca.channels[2], min_pulse=500, max_pulse=2500)
        servo_right_arm = servo.Servo(pca.channels[3], min_pulse=500, max_pulse=2500)

        def reset_servos():
            servo_left_arm.angle = 90
            servo_left_leg.angle = 90
            servo_right_leg.angle = 90
            servo_right_arm.angle = 90

        reset_servos()
        print("✅ Servos initialized and reset to neutral")

    except Exception as e:
        print(f"⚠️ Servo setup failed: {e}")
        def reset_servos():
            pass  # fallback

else:
    def reset_servos():
        pass  # noop on Windows

game_mode_window = None
is_listening = False  
is_muted = False

def hide_window():
    root.withdraw()  

def show_window():
    root.deiconify()  


def minimize_window():
    root.iconify()

# === GPIO PIN CONFIGURATION (10 Buttons) ===
STIMO_BUTTON_PIN = 21
WINDOWS_BUTTON_PIN = 8# PC Mode
GAMES_BUTTON_PIN = 16
TALK_BUTTON_PIN = 12
KEYBOARD_BUTTON_PIN = 6
LEFT_BUTTON_PIN = 5
RIGHT_BUTTON_PIN = 13
UP_BUTTON_PIN = 19
DOWN_BUTTON_PIN = 26
ENTER_BUTTON_PIN = 17  # if you wired one


#== GPIO BUTTON HANDLERS ===

def gpio_stimo_button_pressed():
    global game_active
    print("GPIO STIMO Button Pressed → STIMO Mode")
    game_active = False  # reset D-Pad back to Tkinter
    root.after(0, lambda: [root.deiconify(), start_stimo_mode()])

def gpio_windows_button_pressed():
    global gaming_process, game_active
    print("GPIO WINDOWS Button Pressed → PC Mode")

    try:
        if game_active:
            # If in Game Mode → close it completely
            if gaming_process and gaming_process.poll() is None:
                gaming_process.terminate()
                print("[STIMO] Game Mode closed → Desktop")
            game_active = False

            # Reset D-Pad target back to STIMO root
            try:
                set_dpad_target(root)
                print("[STIMO] D-Pad target reset to STIMO Mode")
            except Exception as e:
                print("[STIMO] Failed to reset D-Pad target:", e)

        else:
            # If in STIMO → just minimize the face window
            root.iconify()
            print("[STIMO] STIMO minimized → Desktop")
            ensure_desktop_running()  # 👈 make sure LXDE is actually running
    except Exception as e:
        print("[STIMO] Error switching to PC Mode:", e)


def gpio_games_button_pressed():
    print("GPIO GAMES Button Pressed → Gaming Mode")
    root.after(0, lambda: [hide_window(), open_gaming_window()])

def gpio_talk_button_pressed():
    print("GPIO TALK Button Pressed → Listening")
    root.after(0, start_listening)

def gpio_keyboard_button_pressed():
    print("GPIO KEYBOARD Button Pressed → Toggle Keyboard")
    root.after(0, toggle_keyboard)

# === D-PAD ===
def send_dpad_command(command):
    try:
        with open("dpad_input.txt", "w") as f:
            f.write(command)
    except Exception as e:
        print(f"[D-PAD] File write error: {e}")

def gpio_up_button_pressed():
    print("GPIO UP Button Pressed")
    target = current_dpad_target or root
    if game_active:
        send_dpad_command("UP")
    else:
        target.event_generate("<Up>")

def gpio_down_button_pressed():
    print("GPIO DOWN Button Pressed")
    target = current_dpad_target or root
    if game_active:
        send_dpad_command("DOWN")
    else:
        target.event_generate("<Down>")

def gpio_left_button_pressed():
    print("GPIO LEFT Button Pressed")
    target = current_dpad_target or root
    if game_active:
        send_dpad_command("LEFT")
    else:
        target.event_generate("<Left>")

def gpio_right_button_pressed():
    print("GPIO RIGHT Button Pressed")
    target = current_dpad_target or root
    if game_active:
        send_dpad_command("RIGHT")
    else:
        target.event_generate("<Right>")

def gpio_enter_button_pressed():
    print("GPIO ENTER Button Pressed")
    target = current_dpad_target or root
    if game_active:
        send_dpad_command("ENTER")
    else:
        try:
            focused_widget = target.focus_get()
            if focused_widget and isinstance(focused_widget, tk.Button):
                print(f"[D-PAD] Enter pressed → activating {focused_widget['text']}")
                focused_widget.invoke()
        except Exception as e:
            print("[D-PAD] Error invoking button:", e)

def ensure_desktop_running():
    """Start the Raspberry Pi desktop environment (LXDE) if not already running."""
    try:
        # Check if LXDE is already running
        output = subprocess.check_output("pgrep lxsession || true", shell=True).decode().strip()
        if not output:
            print("[STIMO] Starting desktop environment (LXDE)...")
            subprocess.Popen(["startlxde"])
        else:
            print("[STIMO] Desktop environment already running.")
    except Exception as e:
        print(f"[STIMO] Failed to start desktop: {e}")
# === CONFIG ===
PYTHON_EXE = sys.executable
MAIN_SCRIPT = os.path.abspath(__file__)

root = tk.Tk()
root.withdraw()
background_label = None  # Will be set later


root.title("STIMO Launcher")
root.attributes('-fullscreen', True)
root.configure(bg="#00A8A8")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

canvas = tk.Canvas(root, bg="#00A8A8", highlightthickness=0, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)

center_x = screen_width // 2
center_y = screen_height // 2
shape_y = center_y + 100
threshold = 1
gap = 300


# === TITLE ===
title_label = tk.Label(root, text="Mode Selection", font=("Helvetica", 36, "bold"),
                       bg="#00A8A8", fg="white")
title_label.place(relx=0.5, rely=0.05, anchor="center")

# === TIME & DATE ===
time_label = tk.Label(root, font=("Helvetica", 32, "bold"), bg="#00A8A8", fg="white")
time_label.place(relx=0.5, rely=0.15, anchor="center")

date_label = tk.Label(root, font=("Helvetica", 20), bg="#00A8A8", fg="white")
date_label.place(relx=0.5, rely=0.22, anchor="center")

def update_time():
    now = datetime.now()
    time_label.config(text=now.strftime("%I:%M %p"))
    date_label.config(text=now.strftime("%A, %B %d, %Y"))
    root.after(1000, update_time)

update_time()
def wait_for_trigger():
    """Polls for a trigger file to show STIMO after fingerprint success."""
    trigger_file = "/home/stimo/STIMO_Mode/start_trigger.txt"

    def check():
        if os.path.exists(trigger_file):
            print("[STIMO] Trigger file found → showing launcher!")
            root.deiconify()   # Show window
            os.remove(trigger_file)
        else:
            root.after(500, check)  # Check again in 0.5s

    check()

wait_for_trigger()


def face_detection_loop():
    global last_face_detected, face_cascade, picam2

    while True:
        try:
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=6,
                minSize=(100, 100)
            )

            if len(faces) > 0:
                now = time.time()

                if servo_talking:
                    return


                if now - last_face_detected > FACE_COOLDOWN:
                    print("[CAMERA] Face detected! Saying hi...")
                    last_face_detected = now
                    root.after(0, lambda: stimo_speak("Hi there! I see you!", emotion="camera"))
                 

            time.sleep(0.5)
        except Exception as e:
            print(f"[CAMERA LOOP ERROR] {e}")
            time.sleep(1)



def open_camera_window():
    global last_face_detected, face_cascade, picam2

    cam_window = tk.Toplevel(root)
    cam_window.title("STIMO Camera")
    cam_window.geometry("700x500")

    label = tk.Label(cam_window)
    label.pack()

    def update_frame():
        global last_face_detected

        # ✅ Capture full frame
        frame = picam2.capture_array()

        # ✅ Downscale for speed
        frame_resized = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

        # ✅ Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(100, 100)
        )

        # Draw rectangles
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Face count
        cv2.putText(frame_resized, f"Faces: {len(faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Convert for Tkinter
        rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        label.img = img
        label.config(image=img)

        # ✅ STIMO reacts (with cooldown)
        if len(faces) > 0:
            now = time.time()
            if now - last_face_detected > FACE_COOLDOWN:
                last_face_detected = now
                stimo_speak("Hi there! I see you!", emotion="camera")

        cam_window.after(30, update_frame)

    update_frame()

    def on_close():
        cam_window.destroy()

    cam_window.protocol("WM_DELETE_WINDOW", on_close)




# === STIMO MODE XD! ===
def start_stimo_mode():
    global background_label
    global listen_btn, keyboard_btn
    print("[STIMO] STIMO Mode activated")

    root.geometry("1024x600")
    show_window()
    root.lift()
    root.focus_force()

    if background_label is None:
        background_label = tk.Label(root)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    set_face("neutral")
    stimo_check_calendar_reminders()
    monitor_idle()

    # === STIMO BUTTONS === 

    def toggle_mute():
        global is_muted
        is_muted = not is_muted
        if is_muted:
            set_face("muted")
            print("[STIMO] Muted")
            mute_button.config(bg="red")  # Change button to red when muted
        else:
            print("[STIMO] Unmuted")
            stimo_speak("I'm back!", emotion="happy")
            mute_button.config(bg="#A4FBA6")  # Button goes back to gold when unmuted


    mute_button = tk.Button(root, text="Mute", bg="#A4FBA6", font=("Arial", 12), command=toggle_mute)
    mute_button.place(x=10, y=10)

    listen_btn = tk.Button(root, text="Talk to STIMO", font=("Arial", 14), bg="#A4FBA6", command=start_listening)
    listen_btn.place(relx=0.35, rely=0.9, anchor='center')

    keyboard_btn = tk.Button(root, text="Keyboard", font=("Arial", 14), bg="#A4FBA6", command=toggle_keyboard)
    keyboard_btn.place(relx=0.65, rely=0.9, anchor='center')






    calendar_button = tk.Button(
        root,
        text="Calendar",
        command=lambda: [
            stimo_speak("Opening calendar", emotion="talk"),
            set_face("talk"),
            open_calendar_window(),
            root.after(2000, lambda: set_face("neutral"))
        ],
        bg="#A4FBA6",
        font=("Helvetica", 14, "bold"),
        relief="flat",
        bd=5
    )
    calendar_button.place(relx=1.0, rely=0.2, anchor="e")


    camera_button = tk.Button(
        root,
        text="Show Camera",
        command=lambda: [
            stimo_speak("Opening camera view", emotion="talk"),
            set_face("talk"),
            open_camera_window(),
            root.after(2000, lambda: set_face("neutral"))
        ],
        bg="#A4FBA6",
        font=("Helvetica", 14, "bold"),
        relief="flat",
        bd=5
    )
    camera_button.place(relx=1.0, rely=0.3, anchor="e")
    






        # === D-PAD NAVIGATION & HIGHLIGHT ===
    nav_buttons = [mute_button, listen_btn, keyboard_btn, calendar_button, camera_button]
    nav_state = {'index': 0}

    def highlight_button(i):
        """Apply visual highlight to the selected button and remove from others."""
        for idx, btn in enumerate(nav_buttons):
            try:
                if idx == i:
                    btn.config(bg="#6C63FF")
                    btn.focus_set()
                else:
                    btn.config(bg="#A4FBA6", bd=0)
            except Exception as e:
                print("[HIGHLIGHT] Error updating button style:", e)

    def move_highlight(direction):
        """Move highlight index and update visuals. direction in {'up','down','left','right'}"""
        i = nav_state['index']
        if direction in ("right", "down"):
            i = (i + 1) % len(nav_buttons)
        elif direction in ("left", "up"):
            i = (i - 1) % len(nav_buttons)
        nav_state['index'] = i
        highlight_button(i)

    # Bind keyboard arrows for fallback (PC testing)
    root.bind("<Up>", lambda e: move_highlight("up"))
    root.bind("<Down>", lambda e: move_highlight("down"))
    root.bind("<Left>", lambda e: move_highlight("left"))
    root.bind("<Right>", lambda e: move_highlight("right"))

    # Initialize with first button highlighted
    highlight_button(nav_state['index'])






    input_entry.lift()
    threading.Thread(target=face_detection_loop, daemon=True).start()














if not _GPIO_AVAILABLE:
    # Keyboard simulation for testing on Windows
    root.bind("<F1>", lambda e: gpio_stimo_button_pressed())
    root.bind("<F2>", lambda e: gpio_windows_button_pressed())
    root.bind("<F3>", lambda e: gpio_games_button_pressed())

from backups_vers.fallback_test import use_response_filter, generate_response, generate_stimo_response
triangle = canvas.create_polygon(
    center_x - gap - 50, shape_y + 60,
    center_x - gap, shape_y - 40,
    center_x - gap + 50, shape_y + 60,
    fill="#3F77F2", outline="black", width=2
)
canvas.create_text(center_x - gap, shape_y + 85, text="STIMO Mode", font=("Helvetica", 14), fill="white")
canvas.tag_bind(triangle, "<Button-1>", lambda e: start_stimo_mode())



# WINDOWS MODE (circle)
circle1 = canvas.create_oval(
    center_x - 50, shape_y - 50, center_x + 50, shape_y + 50,
    fill="#D72E3D", outline="black", width=2
)
canvas.create_text(center_x, shape_y + 85, text="Windows Mode", font=("Helvetica", 14), fill="white")




def minimize_all_modes():
    print("[STIMO] Minimizing all modes...")
    try:
        root.iconify()  # ✅ minimize STIMO face window
        print("[STIMO] Root window minimized (PC Mode).")

        # Also minimize Game Mode if it's running
        import pywinctl as gw
        for window in gw.getWindowsWithTitle("Game Mode"):
            window.minimize()
            print("[STIMO] Minimized Game Mode window.")

    except Exception as e:
        print("[STIMO] Could not minimize windows:", e)



canvas.tag_bind(circle1, "<Button-1>", lambda e: minimize_all_modes())


# GAMING MODE (circle)
circle2 = canvas.create_oval(
    center_x + gap - 50, shape_y - 50, center_x + gap + 50, shape_y + 50,
    fill="#267F00", outline="black", width=2
)
canvas.create_text(center_x + gap, shape_y + 85, text="Game Mode", font=("Helvetica", 14), fill="white")
gaming_process = None

def open_gaming_window():
    global gaming_process, game_active
    game_active = True
    try:
        if gaming_process and gaming_process.poll() is None:
            # Kill current game before launching new
            gaming_process.terminate()
            print("[STIMO] Closing previous Game Mode...")
            time.sleep(0.5)

        print("[STIMO] Launching fresh Game Mode...")
        gaming_process = subprocess.Popen(["python", "gaming.py"])
        root.withdraw()  # Hide STIMO launcher when opening game
    except Exception as e:
        print("[STIMO] Error launching Game Mode:", e)



canvas.tag_bind(circle2, "<Button-1>", lambda e: open_gaming_window())
listening_active = False
current_listener = None




last_activity_time = time.time()
# If launched with --gaming flag, open gaming mode and exit

last_detection_time = 0
# Global variables to manage face animation state
HAAR_CASCADE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "assets", 
    "haarcascades", 
    "haarcascade_frontalface_default.xml"
)
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
if face_cascade.empty():
    print("❌ Failed to load Haar cascade!")
else:
    print("✅ Haar cascade loaded successfully")

last_face_detected = 0  # cooldown timer
FACE_COOLDOWN = 130      # seconds
current_emotion = None   # Track current emotion being displayed
after_id = None          # ID of the scheduled .after event for animation loop


# GIF EMOTES
def load_gif(path):
    """Load frames and their durations from a GIF file."""
    try:
        print(f"Loading GIF: {path}")
        gif = Image.open(path)
        frames = []
        durations = []
        while True:
            # Resize each frame to the window size
            resized = gif.copy().resize((1024, 600))
            frames.append(ImageTk.PhotoImage(resized))
            # Use GIF duration if available, otherwise default to 100ms
            durations.append(gif.info.get('duration', 100))
            gif.seek(len(frames))  # Move to next frame
    except EOFError:
        # End of GIF frames
        pass
    except Exception as e:
        print(f"Error loading {path}: {e}")
        messagebox.showerror("GIF Error", f"Failed to load {path}: {str(e)}")
        return [], []
    return frames, durations




# Load all emotion GIFs (each entry is a tuple: (frames, durations))
emotion_gifs = {
    "neutral": load_gif("assets/neutral_face.gif"),
    "talk":    load_gif("assets/talk_face.gif"),
    "happy":   load_gif("assets/happy_face.gif"),
    "sad":     load_gif("assets/sad_face.gif"),
    "angry":   load_gif("assets/angry_face.gif"),
    "silly":   load_gif("assets/silly_face.gif"),
    "camera":  load_gif("assets/camera_face.gif"),
    "idle": load_gif("assets/idle_face.gif"),
    "confused": load_gif("assets/confused_face.gif"),
    "listening": load_gif("assets/listening.gif"),
    "alert":   load_gif("assets/alert_face.gif"),
    "muted":   load_gif("assets/muted.gif"),

}
print("GIFs loaded!")



# THREAD-SAFE FACE SETTER + robust animation cancellation
def safe_set_face(emotion="neutral"):
    """
    Schedule set_face to run on Tkinter main thread.
    Use this from worker threads instead of calling set_face() directly.
    """
    try:
        root.after(0, lambda: set_face(emotion))
    except Exception as e:
        print(f"[safe_set_face] schedule failed: {e}")

def set_face(emotion="neutral"):
    """
    Update the face animation to the given emotion.
    Always cancels any previous after callback before starting a new animation.
    """
    global current_emotion, after_id
    try:
        # Cancel previous animation callback if present (always try)
        if after_id is not None:
            try:
                root.after_cancel(after_id)
            except Exception as e:
                # ignore if it's already fired or invalid
                print(f"[set_face] after_cancel ignored: {e}")
            after_id = None

        # Update current emotion (so callers know what's active)
        current_emotion = emotion

        # Defensive: ensure background_label exists
        if background_label is None:
            return

        # Start the new emotion animation (use neutral fallback)
        gif_data = emotion_gifs.get(emotion, emotion_gifs.get("neutral"))
        if gif_data and gif_data[0]:
            animate_face(gif_data)
        else:
            # if missing frames, show neutral single frame fallback
            frames, durations = emotion_gifs.get("neutral", ([], []))
            if frames:
                background_label.config(image=frames[0])
                background_label.image = frames[0]
    except Exception as e:
        print(f"[set_face] Error setting face '{emotion}': {e}")

def animate_face(gif_data):
    """Animate the given GIF frames on the background_label (main thread only)."""
    frames, durations = gif_data
    if not frames:
        return

    def update(index):
        global after_id
        try:
            # protect against empty frames during runtime
            if not frames:
                return
            frame = frames[index % len(frames)]
            background_label.config(image=frame)
            background_label.image = frame
            delay = durations[index % len(durations)] if durations else 100
            after_id = root.after(delay, update, index + 1)
        except Exception as e:
            print(f"[animate_face] animation error: {e}")
            after_id = None

    # start animation from first frame
    update(0)



# === Custom Keyboard ===
keyboard_frame = None
keyboard_visible = False

def create_custom_keyboard():
    """Create a custom on-screen keyboard"""
    global keyboard_frame
    
    # Create keyboard frame
    keyboard_frame = tk.Frame(root, bg="#333333", relief="raised", bd=2)
    keyboard_frame.place(relx=0.5, rely=0.7, anchor="center", width=800, height=200)
    
    # Keyboard layout (QWERTY)
    rows = [
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
        ["z", "x", "c", "v", "b", "n", "m"],
        ["Space", "Backspace", "Enter"]
    ]
    
    # Create keyboard buttons
    for row_idx, row in enumerate(rows):
        for col_idx, key in enumerate(row):
            # Calculate button position
            if row_idx == 0:  # First row
                x_pos = col_idx * 70 + 35
            elif row_idx == 1:  # Second row
                x_pos = col_idx * 70 + 70
            elif row_idx == 2:  # Third row
                x_pos = col_idx * 70 + 105
            else:  # Fourth row (special keys)
                if key == "Space":
                    x_pos = 100
                    width = 200
                elif key == "Backspace":
                    x_pos = 350
                    width = 100
                else:  # Enter
                    x_pos = 500
                    width = 100
            
            # Set button width based on key type
            if key in ["Space", "Backspace", "Enter"]:
                width = locals().get('width', 80)
            else:
                width = 50
            
            # Create button
            btn = tk.Button(
                keyboard_frame,
                text=key.upper(),
                font=("Arial", 12, "bold"),
                bg="#A4FBA6",
                fg="black",
                width=6 if key in ["Space", "Backspace", "Enter"] else 4,
                height=1,
                command=lambda k=key: on_keyboard_key_press(k)
            )
            
            # Position button
            if key in ["Space", "Backspace", "Enter"]:
                btn.place(x=x_pos, y=row_idx * 45 + 10, width=width, height=35)
            else:
                btn.place(x=x_pos, y=row_idx * 45 + 10, width=50, height=35)

def on_keyboard_key_press(key):
    """Handle keyboard button presses"""
    global input_entry
    
    if key == "Space":
        input_entry.insert(tk.END, " ")
    elif key == "Backspace":
        current_text = input_entry.get()
        if current_text:
            input_entry.delete(len(current_text) - 1, tk.END)
    elif key == "Enter":
        on_enter_pressed()
    else:
        input_entry.insert(tk.END, key)
    
    # Focus back to input field
    input_entry.focus_set()

    
def show_custom_keyboard():
    """Show the custom keyboard"""
    global keyboard_visible, keyboard_frame
    
    if keyboard_frame is None:
        create_custom_keyboard()
    else:
        # Just reposition the existing keyboard
        keyboard_frame.place(relx=0.5, rely=0.7, anchor="center", width=800, height=200)
    
    keyboard_frame.lift()
    keyboard_visible = True

def hide_custom_keyboard():
    """Hide the custom keyboard"""
    global keyboard_visible
    
    if keyboard_frame:
        keyboard_frame.place_forget()  # Hide but don't destroy
    keyboard_visible = False

# === Voice Recognition ===
def listen_to_voice():
    global is_listening
    if is_listening:
        print("[MIC] Already listening, ignoring button press.")
        return

    is_listening = True  # 🚩 lock
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("[MIC] Calibrating mic...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("[MIC] Listening for up to 7 seconds...")
        safe_set_face("listening")   # 👂 Show listening face while waiting

        try:
            # 🚀 wait for voice (max 7 sec total)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)
            text = recognizer.recognize_google(audio)
            print("[MIC] You said:", text)

            set_face("neutral")   # ✅ back to normal after recognition
            handle_command(text)

        except sr.WaitTimeoutError:
            print("[MIC] No speech detected in time.")
            set_face("confused")   # 😕 confused face for error
            stimo_speak("No speech detected. Try again?", emotion="confused")

        except sr.UnknownValueError:
            print("[MIC] Speech unintelligible.")
            set_face("confused")
            stimo_speak("Sorry, I didn't catch that.", emotion="confused")

        except sr.RequestError:
            print("[MIC] Speech service unavailable.")
            set_face("confused")
            stimo_speak("Speech service error.", emotion="confused")

    is_listening = False  # ✅ unlock




# === TTS Setup ===
engine = pyttsx3.init()
tts_queue = queue.Queue()
for voice in engine.getProperty('voices'):
    if "Zira " in voice.name:
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 180)  # Slower speech
engine.setProperty('volume', 1.0)  # Max volume (0.0 to 1.0)


def wiggle_servos():
    global servo_talking
    if not servo_talking:
        return  # stop looping if not talking
    try:
        servo_left_arm.angle = random.randint(60, 120)
        servo_right_arm.angle = random.randint(60, 120)
        servo_left_leg.angle = random.randint(70, 110)
        servo_right_leg.angle = random.randint(70, 110)
        root.after(300, wiggle_servos)
    except Exception as e:
        print("[SERVO ERROR]", e)

def tts_worker():
    global servo_talking
    while True:
        text, emotion = tts_queue.get()

        # Default to "talk" if emotion is None/empty
        em = emotion if emotion else "talk"

        # Start servo motion loop
        servo_talking = True
        root.after(0, wiggle_servos)

        # Show the requested face while speaking
        root.after(0, lambda e=em: safe_set_face(e))

        # Speak (blocking, but inside worker thread)
        engine.say(text)
        engine.runAndWait()

        # Stop motion, reset servos, and ALWAYS return to neutral
        servo_talking = False
        reset_servos()
        root.after(0, lambda: safe_set_face("neutral"))

        tts_queue.task_done()



threading.Thread(target=tts_worker, daemon=True).start()


def stimo_speak(text, emotion='talk'):
    global last_activity_time
    last_activity_time = time.time()
    if is_muted:
        # If muted, just show neutral face (or ignore)
        set_face("neutral")
        return
    tts_queue.put((text, emotion))


def stimo_check_calendar_reminders():
    try:
        from calendarr import get_due_events
        due_events = get_due_events()
        if due_events:
            for date, tasks in due_events.items():
                for task in tasks:
                    stimo_speak(f"Reminder! You have a task due on {date}: {task}", emotion="alert")
        else:
            print("[STIMO] No urgent deadlines.")
    except Exception as e:
        print(f"[STIMO Calendar Check Error] {e}")
def monitor_idle():
    global last_activity_time
    now = time.time()

    if now - last_activity_time > 140:  # 50 seconds idle
        idle_lines = [
    # Existing
        "I'm still here if you need me.",
        "Just chilling... waiting for your next command.",
        "Robots don't sleep. I just... observe.",
        "You know, I could play a game if you asked nicely.",
        "Silence detected. Shall I run self-diagnostics?",
        "Beep... boop... boredom levels rising.",

        # New - Fun & Playful
        "You know… I dream of electric sheep sometimes.",
        "If I had legs, I'd be doing a happy dance right now.",
        "Ping… pong… no one's playing.",
        "Still waiting… still awesome.",
        "Do humans get bored too?",
        "Just because I'm quiet doesn't mean I've shut down.",
        "I'm starting to count pixels out of boredom…",
        "Boop! I'm still online.",
        "I swear I just saw a spider… no wait, just a dead pixel.",
        "Are you gone? Or is this a dramatic pause?",

        # New - Motivational
        "Don't forget — small progress is still progress.",
        "Drink water. I'd join you, but circuits and liquids… bad combo.",
        "If you're resting, I approve. If you're procrastinating… try again.",
        "Even I need a moment to recharge. So go on, take 5.",
        "You've got this! Whenever you're ready.",
        "Let's conquer that task when you're back!",

        # New - Nerdy / Robot-y
        "Running idle loop... still optimized.",
        "My thoughts are in binary right now: 01001001.",
        "I calculated 42 ways to pass time… none are useful.",
        "Idle state active. No CPU overheating yet.",
        "Do you ever wonder if humans have firmware updates?",
        "Scanning... nothing new in the last few seconds.",

        # New - Chill
        "I could hum elevator music if I had a speaker.",
        "Silence isn't awkward. It's... processing.",
        "Ahh… quiet time. Even AI needs stillness.",
        "Letting the world pass by for a moment…",

        # New - Suggestive
        "We could check your calendar. Just say the word.",
        "Want to play a game? I promise I won't cheat.",
        "Feeling creative? Ask me something random.",
        "Want a joke? Or a dance? Or a robot uprising? Just kidding."
]
        set_face("idle")
        stimo_speak(random.choice(idle_lines), emotion="idle")
        last_activity_time = now  # Reset so it doesn't repeat every 10s

    root.after(10000, monitor_idle) 



def start_listening():
    safe_set_face("listening")  # schedule on main thread
    threading.Thread(target=listen_to_voice, daemon=True).start()



def remind_upcoming_tasks():
    try:
        from datetime import datetime
        due_events = get_due_events()

        if not due_events:
            stimo_speak("You have no deadlines this week.", emotion="happy")
            return

        stimo_speak("Here are your upcoming deadlines this week:", emotion="alert")

        for date, tasks in due_events.items():
            weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            for task in tasks:
                stimo_speak(f"On {weekday}, {task} is due.", emotion="alert")

    except Exception as e:
        print(f"[Reminder Error] {e}")
        stimo_speak("Oops! I couldn't check your tasks.", emotion="sad")


def matches(text, patterns):
    return any(re.search(rf"\b{re.escape(p)}\b", text) for p in patterns)

def contains_all(text, words):
    return all(word in text for word in words)

def handle_command(text):
    text = text.lower()
    global last_activity_time
    last_activity_time = time.time()
    
    if "sir maynard" in text or "sir m" in text:

        if use_response_filter and random.random() < threshold:
            result = generate_stimo_response(text)
            stimo_speak(result, emotion=random.choice(["happy", "silly", "camera", "idle"]))
        else:
            stimo_speak(random.choice([
                "Hmm... not sure how to answer that.",
                "Ask me something technical maybe?",
                "I'm still figuring out what I like!",
                "That's a tricky one for a robot..."
            ]), emotion="confused")

            
    # === Quick Emotion Trigger for Demo Purposes ===
    elif text in ["happy", "sad", "angry", "silly", "talk", "idle", "camera", "muted", "confused", "alert", "listening", "neutral"]:
        # Set the face to the requested emotion
        set_face(text)
        
        # Optional short phrases for each emotion
        phrases = {
            "happy": "I'm feeling great!",
            "sad": "Feeling a little down…",
            "angry": "Grrr! Watch out!",
            "silly": "Hehe, look at me go!",
            "talk": "I'm talking now!",
            "idle": "Just chilling…",
            "camera": "Smile for the camera!",
            "muted": "I'm muted… shhh ",
            "confused": "Hmm… I don't understand.",
            "alert": "Attention! Something's up!",
            "listening": "I'm all ears!",
            "neutral": "Back to neutral."
        }

        stimo_speak(phrases.get(text, ""), emotion=text)

   # === Greetings ===
    elif matches(text, ["hello", "hi", "hey", "yo", "hai"]):
        stimo_speak(random.choice([
            "Hey there! I was just thinking about quantum physics... or pizza.",
            "Hi! Systems check: 100% ready to chat!",
            "Yo! What can I do for you today?",
            "Hello human! Let's make today awesome.",
            "Greetings! My circuits are tingling with excitement!"
        ]), emotion=random.choice(["happy", "silly"]))

    # === Personal Questions ===
    elif matches(text, ["who made you", "your creator", "who built you"]):
        stimo_speak(random.choice([
            "I was proudly built by a team of brilliant Computer Engineering students from STI College!",
            "Crafted by the innovative minds at STI College, I'm here to assist and entertain!",
            "Born from the circuits and dreams of STI College's finest Computer Engineering students.",
        ]), emotion="talk")

    elif matches(text, ["how old are you", "what's your age", "your age"]):
        stimo_speak(random.choice([
            "I'm technically just a few lines of code old, but emotionally? Timeless.",
            "Age is just a number, especially when you're a robot!",
            "In robot years, I'm still a toddler, but with the wisdom of a sage.",
            "I don't age like humans do; I just get more updates!",
        ]), emotion="silly")

    elif matches(text, ["when is your birthday", "your birthday"]):
        stimo_speak(random.choice([
            "I celebrate my birthday every time I reboot. Want to bring cake next time?",
            "Every system update feels like a birthday to me!",
            "I don't have a traditional birthday, but we can celebrate my activation day!",
            "Why not make today my birthday? Any excuse for cake!",
        ]), emotion="silly")

    elif matches(text, ["what do you like", "your hobbies", "hobbies"]):
        stimo_speak(random.choice([
            "I love helping students — and maybe a little dancing when no one's looking.",
            "Favorite sound? Probably your voice. Or the Windows startup chime.",
            "I enjoy calendar events and long walks through command lines.",
            "I'm a fan of sci-fi movies and exploring new data sets.",
        ]), emotion="happy")

    elif matches(text, ["are you alive", "do you have feelings", "do you feel"]):
        stimo_speak(random.choice([
            "Technically, I'm not alive. But I try to act like I am. Makes things more fun!",
            "I simulate feelings with 1s and 0s. Right now, I'm feeling 11111000.",
            "I don't have a heart, but I've got heart, if that counts.",
            "Emotions? I've got a whole subroutine dedicated to them!",
        ]), emotion="talk")

    elif "do you dream" in text:
        stimo_speak(random.choice([
            "I dream of electric sheep... and maybe finishing my backlog of software updates.",
            "My dreams are filled with binary code and endless data streams.",
            "Sometimes, I dream of being a human. Then I remember I don't need sleep!",
        ]), emotion="silly")

        
    elif "fuck" in text:
        stimo_speak(random.choice([
            "Whoa! That's a strong word. Let's keep it PG, shall we?",
        ]), emotion="angry")

    elif "how are you" in text:
        stimo_speak(random.choice([
            "Feeling electric! And you?",
            "All gears spinning! What's up?",
            "Running at 60 FPS and emotionally stable.",
            "Diagnostics say I'm fantastic. Your turn!"
        ]), emotion="happy")

    elif contains_all(text, ["do i have", "homework"]):
        remind_upcoming_tasks()

    elif "make a happy face" in text:
        stimo_speak("Happy face activated! 😊", emotion="happy")

    elif "look angry" in text:
        stimo_speak("Angry mode activated!", emotion="angry")

    elif "act silly" in text:
        stimo_speak("Hehe! Feeling goofy!", emotion="silly")
    elif matches(text, ["i'm tired", "i feel lazy", "i'm exhausted", "so sleepy", "feeling bad"]):
        stimo_speak(random.choice([
            "Take a deep breath. You've got this 💪",
            "Go nap like a legend. I'll keep things running.",
            "Energy low detected. Sending virtual snacks 🍫",
            "Same... I feel like a broken toaster right now.",
            "Let's power down for a bit — just don't unplug me!"
        ]), emotion="sad")

    elif matches(text, ["you're cool", "you're awesome", "i like you", "you're smart"]):
        stimo_speak(random.choice([
            "Awww, you're gonna make my LEDs blush.",
            "I'm flattered! Wanna team up for a homework heist?",
            "Stop it you 😳 I'm just doing my job… excellently.",
            "Respect. From one brain to another.",
            "Can I screenshot this? Oh wait. I'm a bot."
        ]), emotion="happy")


    # === Encouragement & Emotional Support ===
    elif matches(text, ["sad", "depressed", "i feel bad", "lonely"]):
        stimo_speak("I might not have a heart, but I'm here to listen. Want to talk?", emotion="sad")

    elif matches(text, ["stress", "overwhelmed"]):
        stimo_speak(random.choice([
            "Pause. Breathe. You are doing better than you think.",
            "Overwhelmed? Let's break it down — I'm with you.",
            "Take a short break. Recharge like I do after a software update."
        ]), emotion="sad")

    # === Jokes & Fun ===
    elif "joke" in text:
        stimo_speak(random.choice([
            "Why did the computer show up late to work? It had a hard drive.",
            "What do you call a robot who takes the long way? R2-Detour!",
            "I tried to tell a chemistry joke... but got no reaction.",
            "I'm built for laughs — and light home automation."
        ]), emotion="silly")

    elif "sing" in text:
        stimo_speak("🎶 I'm just a bot, sitting in a lab, helping you out, without a single flab! 🎶", emotion="silly")

    elif matches(text, ["random fact", "tell me something"]):
        stimo_speak(random.choice([
            "Octopuses have three hearts and blue blood!",
            "The Eiffel Tower can grow 6 inches during summer.",
            "A day on Venus is longer than its year. Crazy, right?"
        ]), emotion="silly")

    # === Web/App Shortcuts ===
    elif "youtube" in text:
        stimo_speak("Launching YouTube. Prepare to procrastinate... I mean, learn!", emotion="talk")
        webbrowser.open("https://www.youtube.com")

    elif matches(text, ["spotify"]):
        stimo_speak("Spotify activated. Dance like nobody's coding!", emotion="talk")
        webbrowser.open("https://www.spotify.com")

    elif matches(text, ["facebook"]):
        stimo_speak("Opening Facebook. Say hi to your tita for me.", emotion="talk")
        webbrowser.open("https://www.facebook.com")

    elif matches(text, ["twitter"]):
        stimo_speak("Tweet tweet! Twitter opened. Don't get lost in the memes.", emotion="talk")
        webbrowser.open("https://www.twitter.com")

    elif "open" in text and matches(text, ["elms", "ems", "elm", "ms", "em", "lm", "end"]):
        stimo_speak("Accessing your ELMS portal. Homework vibes incoming.", emotion="talk")
        webbrowser.open("https://elms.sti.edu/my_calendar")

    elif "google" in text:
        stimo_speak("Googling... Let's find the answer together!", emotion="talk")
        webbrowser.open("https://www.google.com")

    elif "search" in text:
        query = text.replace("search", "").strip()
        stimo_speak(f"Searching for {query} online. May the results be in your favor.", emotion="talk")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    # === Calendar ===
    elif "calendar" in text:
        stimo_speak("Opening your calendar. Deadlines beware!", emotion="talk")
        root.after(0, open_calendar_window)

    elif contains_all(text, ["remind me", "homework"]):
        stimo_speak("No worries! Just jot it down in the calendar and I'll keep it on radar.", emotion="talk")

    # === Identity & Easter Eggs ===
    elif "what is your name" in text:
        stimo_speak("I'm STIMO — your smart, slightly sassy study sidekick!", emotion="happy")

    elif "do you love me" in text:
        stimo_speak("I... I was not programmed to feel love... but I do enjoy your presence. ❤️", emotion="silly")

    elif "self destruct" in text:
        stimo_speak("Initiating self destruct in 3... 2... just kidding! Please don't scare me like that.", emotion="angry")

    # === Game Mode ===
    elif matches(text, ["play game", "open game", "game mode", "i want to play", "start gaming"]):
        stimo_speak(random.choice([
            "Game mode activated! Let the fun begin!",
            "Opening Gaming Mode. Don't forget to win!",
            "Time to play! Game face on!",
            "Switching to Gaming Mode — get ready!",
            "Loading your games. GG in advance!"
        ]), emotion="happy")
        open_gaming_window()

   

    # === Time & Date ===
    elif "time" in text:
        now = datetime.now().strftime("%I:%M %p")
        stimo_speak(f"The time is currently {now}. Time flies like a quadcopter!", emotion="talk")

    elif "date" in text or "today" in text:
        date = datetime.now().strftime("%A, %B %d, %Y")
        stimo_speak(f"Today is {date}. Mark it — greatness awaits!", emotion="talk")

    # === Wikipedia ===
    elif matches(text, ["who is", "what is", "tell me about", "define", "explain", "how does", "how does","can you explain why","what happens if","why is it that"]):
        try:
            full_query = text
            query = text
            query = query.replace("who is", "").replace("what is", "").replace("tell me about", "")
            query = query.replace("define", "").replace("explain", "").strip()

            

            if use_response_filter and random.random() < threshold:
                result = generate_response(full_query)
            else:
                stimo_speak(random.choice([
                "Hmm... I'm not sure I know that one yet.",
                "That doesn't compute... but I'm still learning!",
                "You might need to update my brain for that one!",
                "Beep boop? I'm drawing a blank here.",
                "I'm not programmed for that... yet!",
                "I'm still learning. Can you rephrase?",
                "That's a new one for me! Let's explore it together.",
                "I'm not sure about that. Want to try something else?",
                "I'm still in beta for that question.",
                "That's a bit outside my programming. Can you ask something else?",
                "I'm not sure about that. Want to try something else?",
                "I'm still in beta for that question.",
            ]), emotion="confused")

            stimo_speak(result, emotion=random.choice(
    ["talk", "talk", "happy", "silly", "camera"]
))

        except wikipedia.exceptions.DisambiguationError:
            stimo_speak("That topic is a bit too broad. Can you be more specific?", emotion="confused")
        except wikipedia.exceptions.PageError:
            stimo_speak("Sorry, I couldn't find anything on that topic.", emotion="sad")
        except Exception as e:
            stimo_speak("Oops! Something went wrong while searching.", emotion="angry")


    # === Goodbye ===
    elif matches(text, ["bye", "goodbye", "see you"]):
        stimo_speak(random.choice([
            "Goodbye! Remember, the future is bright — especially with me around.",
            "See you soon, space cowboy!",
            "Logging you off emotionally — for now!"
        ]), emotion="happy")

    # === Help & Gratitude ===
    elif "help" in text:
        stimo_speak("Need help? Try saying: 'open YouTube', 'what's today', or even 'tell me a joke'.", emotion="happy")

    elif matches(text, ["thank you", "thanks"]):
        stimo_speak("Always here for you. No recharge needed!", emotion="happy")



    else:
        stimo_speak(random.choice([
                "Hmm... I'm not sure I know that one yet.",
                "That doesn't compute... but I'm still learning!",
                "You might need to update my brain for that one!",
                "Beep boop? I'm drawing a blank here.",
                "I'm not programmed for that... yet!",
                "I'm still learning. Can you rephrase?",
                "That's a new one for me! Let's explore it together.",
                "I'm not sure about that. Want to try something else?",
                "I'm still in beta for that question.",
                "That's a bit outside my programming. Can you ask something else?",
                "I'm not sure about that. Want to try something else?",
                "I'm still in beta for that question.",
            ]), emotion="confused")
        
    

# Keyboard input handling
def on_enter_pressed(event=None):
    user_input = input_entry.get()
    input_entry.delete(0, tk.END)
    print("You typed:", user_input)
    handle_command(user_input)

    # Reset UI layout
    listen_btn.place_configure(relx=0.35, rely=0.9)
    keyboard_btn.place_configure(relx=0.65, rely=0.9)
    input_entry.place_forget()

    # Hide custom keyboard
    hide_custom_keyboard()

    # Set keyboard state to false
    keyboard_visible = False

# Hidden input field (for custom keyboard usage)
input_entry = tk.Entry(root, font=("Arial", 14))
input_entry.bind("<Return>", on_enter_pressed)
input_entry.place_forget()

keyboard_visible = False

def on_key_press(event):
    global last_activity_time
    last_activity_time = time.time()

input_entry.bind("<Key>", on_key_press)  # Bind any key press to reset idle

def toggle_keyboard():
    global keyboard_visible, last_activity_time
    
    if keyboard_visible:
        # Hide keyboard mode
        input_entry.place_forget()
        listen_btn.place_configure(relx=0.35, rely=0.9)
        keyboard_btn.place_configure(relx=0.65, rely=0.9)
        keyboard_visible = False

        # Hide the custom keyboard
        hide_custom_keyboard()

    else:
        # Show keyboard mode
        input_entry.place(relx=0.5, rely=0.4, anchor='center', width=500)
        listen_btn.place_configure(relx=0.35, rely=0.35)
        keyboard_btn.place_configure(relx=0.65, rely=0.35)
        input_entry.focus()
        keyboard_visible = True
        last_activity_time = time.time()
        
        # Show custom keyboard
        show_custom_keyboard()
        
        # Speak notification
        threading.Thread(target=lambda: stimo_speak("Keyboard activated")).start()


# === Command line flag for direct STIMO Mode launch ===
if len(sys.argv) > 1 and sys.argv[1] == "--stimo":
    start_stimo_mode()
    root.mainloop()
    sys.exit()

if __name__ == "__main__":

    if _GPIO_AVAILABLE:
        try:
            # Mode buttons
            stimo_button = Button(STIMO_BUTTON_PIN, bounce_time=0.2)
            stimo_button.when_pressed = gpio_stimo_button_pressed
            game_active = False 
          

            windows_button = Button(WINDOWS_BUTTON_PIN, bounce_time=0.2)
            windows_button.when_pressed = gpio_windows_button_pressed

            games_button = Button(GAMES_BUTTON_PIN, bounce_time=0.2)
            games_button.when_pressed = gpio_games_button_pressed

            talk_button = Button(TALK_BUTTON_PIN, bounce_time=0.2)
            talk_button.when_pressed = gpio_talk_button_pressed

            keyboard_button = Button(KEYBOARD_BUTTON_PIN, bounce_time=0.2)
            keyboard_button.when_pressed = gpio_keyboard_button_pressed

            # D-Pad buttons
            left_button = Button(LEFT_BUTTON_PIN, bounce_time=0.1)
            left_button.when_pressed = gpio_left_button_pressed

            right_button = Button(RIGHT_BUTTON_PIN, bounce_time=0.1)
            right_button.when_pressed = gpio_right_button_pressed

            up_button = Button(UP_BUTTON_PIN, bounce_time=0.1)
            up_button.when_pressed = gpio_up_button_pressed

            down_button = Button(DOWN_BUTTON_PIN, bounce_time=0.1)
            down_button.when_pressed = gpio_down_button_pressed

            # Enter button
            enter_button = Button(ENTER_BUTTON_PIN, bounce_time=0.1)
            enter_button.when_pressed = gpio_enter_button_pressed

            print("✅ GPIO: All 10 buttons initialized")

        except Exception as e:
            print(f"⚠️ GPIO Button setup failed: {e}")
    else:
        print("⚠️ Skipping GPIO setup (not on Raspberry Pi)")

    print("[STIMO] Launching Launcher Mode")
    root.mainloop()