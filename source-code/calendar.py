import tkinter as tk
from tkinter import simpledialog, messagebox
import calendar
from datetime import datetime
import pyttsx3
import threading
import sqlite3
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import pyttsx3
import speech_recognition as sr
import threading
import random
import serial  # For future ESP32 support
import time


stimo_callback = None  # placeholder
def set_speaker(callback):
    global stimo_callback
    stimo_callback = callback





   
# Database setup
db_path = "stimo_events.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS events (date TEXT, event TEXT)''')
conn.commit()

# Load events from database
events = {}
def load_events():
    events.clear()  # 🛠️ Clear in-memory data to prevent duplicates
    c.execute("SELECT date, event FROM events")
    rows = c.fetchall()
    for date, event in rows:
        if date in events:
            events[date].append(event)
        else:
            events[date] = [event]

            
# Save event to database
def save_event(date, event):
    c.execute("INSERT INTO events (date, event) VALUES (?, ?)", (date, event))
    conn.commit()

# Delete event from database
def delete_event_from_db(date, event):
    c.execute("DELETE FROM events WHERE date=? AND event=?", (date, event))
    conn.commit()

# Update event in database
def update_event_in_db(date, old_event, new_event):
    c.execute("UPDATE events SET event=? WHERE date=? AND event=?", (new_event, date, old_event))
    conn.commit()

# TTS setup
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# Speak with threading and STIMO gestures


# Reminder for today's events
def check_today_events():
    today = datetime.today().strftime("%Y-%m-%d")
    if today in events:
        reminders = [f"Reminder! You have an event today: {e}" for e in events[today]]
        for reminder in reminders:
            if stimo_callback:
                stimo_callback("Reminder! You have an event today...", emotion="alert")

        messagebox.showinfo("Today's Reminders", "\n".join(events[today]))








# ================= CALENDAR UI WRAPPED =================
def open_calendar_window():
    calendar_root = tk.Toplevel()
    calendar_root.title("STIMO Calendar")
    calendar_root.geometry("400x450")
    calendar_root.configure(bg="#32C1CD")
  

    is_event_window_open = False

    def add_event(day):
        nonlocal is_event_window_open
        if is_event_window_open:
            return
        is_event_window_open = True

        event = simpledialog.askstring("Add Event", f"Enter event for {day}:", parent=calendar_root)
        if event:
            if day in events:
                events[day].append(event)
            else:
                events[day] = [event]
            save_event(day, event)
            messagebox.showinfo("Event Added", f"Event for {day} added!", parent=calendar_root)
            if stimo_callback:
                stimo_callback("Event added successfully.", emotion="alert")

            
            draw_calendar(current_year, current_month)

        is_event_window_open = False

    def view_event(day):
        nonlocal is_event_window_open
        if is_event_window_open:
            return
        is_event_window_open = True

        if day in events:
            event_list = "\n".join([f"{idx + 1}. {e}" for idx, e in enumerate(events[day])])
            messagebox.showinfo("Events", f"Events on {day}:\n{event_list}", parent=calendar_root)
        else:
            messagebox.showinfo("No Events", f"No events for {day}", parent=calendar_root)

        is_event_window_open = False

    def edit_event(day):
        nonlocal is_event_window_open
        if is_event_window_open:
            return
        is_event_window_open = True

        if day in events:
            win = tk.Toplevel(calendar_root)
            win.title(f"Edit Events on {day}")
            win.configure(bg="#E1F8DC")

            tk.Label(win, text=f"Events on {day}", font=("Arial", 12, "bold"), bg="#E1F8DC", fg="#32C1CD").pack(pady=5)
            event_listbox = tk.Listbox(win, font=("Helvetica", 10), height=5, width=30, bg="#F7F7F7", selectmode=tk.SINGLE)
            event_listbox.pack(pady=5)

            for event in events[day]:
                event_listbox.insert(tk.END, event)

            def on_event_edit():
                selected_index = event_listbox.curselection()
                if selected_index:
                    selected_event = event_listbox.get(selected_index)
                    new_event = simpledialog.askstring("Edit Event", f"Edit event:\n{selected_event}", parent=win)
                    if new_event:
                        events[day][selected_index[0]] = new_event
                        update_event_in_db(day, selected_event, new_event)
                        messagebox.showinfo("Edited", f"Event updated to: {new_event}", parent=win)
           
                        if stimo_callback:
                            stimo_callback("event updated", emotion="alert")

               

                        draw_calendar(current_year, current_month)
                        event_listbox.delete(selected_index)
                        event_listbox.insert(selected_index, new_event)

            tk.Button(win, text="Edit Selected Event", command=on_event_edit, bg="#FFD580", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(pady=5)

        else:
            messagebox.showinfo("No Events", f"No events for {day}", parent=calendar_root)

        is_event_window_open = False

    def delete_event(day):
        nonlocal is_event_window_open
        if is_event_window_open:
            return
        is_event_window_open = True

        if day in events:
            win = tk.Toplevel(calendar_root)
            win.title(f"Delete Events on {day}")
            win.configure(bg="#E1F8DC")

            tk.Label(win, text=f"Events on {day}", font=("Arial", 12, "bold"), bg="#E1F8DC", fg="#32C1CD").pack(pady=5)
            event_listbox = tk.Listbox(win, font=("Helvetica", 10), height=5, width=30, bg="#F7F7F7", selectmode=tk.SINGLE)
            event_listbox.pack(pady=5)

            for event in events[day]:
                event_listbox.insert(tk.END, event)

            def on_event_delete():
                selected_index = event_listbox.curselection()
                if selected_index:
                    selected_event = event_listbox.get(selected_index)
                    events[day].remove(selected_event)
                    delete_event_from_db(day, selected_event)
                    messagebox.showinfo("Deleted", f"Deleted event: {selected_event}", parent=win)
                    if stimo_callback:
                        stimo_callback("event deleted", emotion="alert")

               

                    if not events[day]:
                        del events[day]
                    draw_calendar(current_year, current_month)
                    event_listbox.delete(selected_index)

            tk.Button(win, text="Delete Selected Event", command=on_event_delete, bg="#FF6F61", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(pady=5)
        else:
            messagebox.showinfo("No Events", f"No events for {day}", parent=calendar_root)

        is_event_window_open = False

    def open_day_menu(year, month, day):
        day_str = f"{year}-{month:02d}-{day:02d}"
        win = tk.Toplevel(calendar_root)
        win.title(f"Manage {day_str}")
        win.configure(bg="#E1F8DC")

        tk.Label(win, text=f"{day_str}", font=("Arial", 12, "bold"), bg="#E1F8DC", fg="#32C1CD").pack(pady=5)
        tk.Button(win, text="➕ Add Event", command=lambda: add_event(day_str), bg="#A4FBA6", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(pady=3)
        tk.Button(win, text="📅 View Events", command=lambda: view_event(day_str), bg="#A4FBA6", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(pady=3)
        tk.Button(win, text="✏️ Edit Event", command=lambda: edit_event(day_str), bg="#FFD580", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(pady=3)
        tk.Button(win, text="🗑️ Delete Event", command=lambda: delete_event(day_str), bg="#FF6F61", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(pady=3)

    def draw_calendar(year, month):
        nonlocal month_label, calendar_frame
        for widget in calendar_frame.winfo_children():
            widget.destroy()

        cal = calendar.monthcalendar(year, month)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for i, day in enumerate(days):
            tk.Label(calendar_frame, text=day, font=("Arial", 10, "bold"), fg="white", bg="#32C1CD", padx=5, pady=5)\
                .grid(row=0, column=i, sticky="nsew")

        for row_index, week in enumerate(cal, start=1):
            for col_index, day in enumerate(week):
                if day != 0:
                    day_str = f"{year}-{month:02d}-{day:02d}"
                    text = f"{day}"
                    if day_str in events:
                        text += "\n" + "\n".join([f"• {e[:18]}" for e in events[day_str]])
                    today = datetime.today()
                    bg_color = "#FF9F00" if (today.year == year and today.month == month and today.day == day) else "#9AEBA3"

                    btn = tk.Button(calendar_frame, text=text, font=("Helvetica", 9), fg="#333", bg=bg_color,
                                    width=12, height=4, relief="flat", bd=2,
                                    command=lambda d=day: open_day_menu(year, month, d),
                                    wraplength=90, justify="left")
                    btn.grid(row=row_index, column=col_index, sticky="nsew", padx=2, pady=2)


        month_label.config(text=f"{calendar.month_name[month]} {year}")

    def prev_month():
        nonlocal current_month, current_year
        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1
        draw_calendar(current_year, current_month)

    def next_month():
        nonlocal current_month, current_year
        current_month += 1
        if current_month == 13:
            current_month = 1
            current_year += 1
        draw_calendar(current_year, current_month)




    tk.Label(calendar_root, text="STIMO Calendar", font=("Comic Sans MS", 22, "bold"), fg="white", bg="#32C1CD").pack(pady=5)
    month_label = tk.Label(calendar_root, font=("Arial", 14, "bold"), fg="white", bg="#32C1CD")
    month_label.pack(pady=2)

    def go_back_to_stimo():
        calendar_root.destroy()




    nav_frame = tk.Frame(calendar_root, bg="#32C1CD")
    nav_frame.pack()
    tk.Button(nav_frame, text="⏪ Prev", command=prev_month, bg="#A4FBA6", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(side="left", padx=5)
    tk.Button(nav_frame, text="Next ⏩", command=next_month, bg="#A4FBA6", font=("Helvetica", 10, "bold"), relief="flat", bd=4).pack(side="left", padx=5)
    tk.Button(nav_frame, text="🏠 Go back to STIMO", command= go_back_to_stimo, bg="#FFCCCB", font=("Helvetica", 12, "bold"), relief="flat", bd=5).pack(side="right", padx=10)



    calendar_frame = tk.Frame(calendar_root, bg="#32C1CD")
    calendar_frame.pack(pady=5, expand=True, fill="both")
    for i in range(7):
        calendar_frame.grid_columnconfigure(i, weight=1)
    for i in range(7):  # Up to 7 rows for weeks
        calendar_frame.grid_rowconfigure(i, weight=1)


    now = datetime.now()
    current_year = now.year
    current_month = now.month



    load_events()
    draw_calendar(current_year, current_month)
    check_today_events()

    
def get_due_events(days_ahead=7):
    from datetime import datetime, timedelta
    load_events()  # Ensure fresh data from DB
    today = datetime.today()
    upcoming = {}

    for offset in range(0, days_ahead + 1):  # Today through the next 7 days
        date = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
        if date in events:
            upcoming[date] = events[date]

    return upcoming
