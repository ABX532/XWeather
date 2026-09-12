import tkinter as tk
from datetime import datetime
import customtkinter as ctk
import openmeteo_requests
from geopy.geocoders import Nominatim
from pathlib import Path
from tkinter import messagebox
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
import json

history_dir = Path.home() / ".xweather"
history_dir.mkdir(exist_ok=True)

json_path = history_dir / "data.json"

ctk.set_default_color_theme("gold")

root = ctk.CTk()
root.title("XWeather")
root.geometry("500x500")

api = openmeteo_requests.Client()


def clear():
    for widget in root.winfo_children():
        widget.destroy()


def weather_description(code):
    return {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Foggy", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain",
        65: "Heavy rain", 71: "Slight snow", 73: "Moderate snow",
        75: "Heavy snow", 77: "Snow grains", 80: "Slight rain showers",
        81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
        99: "Thunderstorm with hail"
    }.get(code, "Unknown")


def show_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "weather_code",
            "wind_speed_10m"
        ]
    }

    try:
        current = api.weather_api(
            "https://api.open-meteo.com/v1/forecast",
            params=params
        )[0].Current()
    except IndexError:
        messagebox.showerror(
            "API Error", 
            "Invalid response from weather API. Please try again."
        )
        return
    except openmeteo_requests.OpenMeteoRequestsError as e:
        error_msg = str(e).lower()
    
        if any(keyword in error_msg for keyword in ["connection", "timeout", "unreachable", "refused"]):
            messagebox.showerror(
                "Connection Error", 
                "Unable To Connect To Server, Please Check Your Internet Connection."
            )
            return
        else:
            messagebox.showerror(
                "Invalid Coordinates", 
                "Invalid Coordinates, Please Type Valid Coordinates."
            )
            return
    except requests.exceptions.HTTPError as e:
        messagebox.showerror(
            "HTTP Error", 
            f"HTTP Error Occurred: {e.response.status_code}"
        )
        return
    except requests.exceptions.RequestException as e:
        messagebox.showerror(
            "Network Error", 
            f"Network Error Occurred: {e}"
        )
        return
    except Exception as e:
        messagebox.showerror(
            "Error", 
            f"An Unexpected Error Occurred: {e}"
        )
        return

    clear()

    ctk.CTkLabel(
        root,
        text="Processing, Please Wait...",
        font=("Red Hat Text", 18)
    ).pack(padx=10, pady=10, anchor=tk.CENTER)

    def refresh_btn():
        temp = round(current.Variables(0).Value())
        humidity = round(current.Variables(1).Value())
        code = int(current.Variables(2).Value())
        wind = round(current.Variables(3).Value())
        time = datetime.fromtimestamp(current.Time()).strftime("%H:%M")

        color = (
            "darkblue" if temp <= 0 else
            "blue" if temp <= 15 else
            "lightblue" if temp <= 20 else
            "yellow" if temp <= 25 else
            "#F6BE00" if temp <= 30 else
            "darkorange" if temp <= 35 else
            "red"
        )

        clear()

        frame = ctk.CTkFrame(root, corner_radius=20)
        frame.pack(padx=10, pady=10)

        ctk.CTkLabel(
            frame, text=f"{temp}°C",
            font=("URW Gothic", 80, "bold"),
            text_color=color
        ).pack(padx=10, pady=10)

        ctk.CTkLabel(
            frame, text=weather_description(code),
            font=("Red Hat Text", 18)
        ).pack(padx=10, pady=10)

        for text in (
            f"Latitude: {lat}",
            f"Longitude: {lon}",
            f"Last Check: {time}",
            f"Humidity: {humidity}%",
            f"Wind Speed: {wind} km/h"
        ):
            ctk.CTkLabel(root, text=text, font=("Red Hat Text", 23)).pack(
                padx=5, pady=5
            )
        
        ctk.CTkButton(
            root,
            text="Refresh",
            font=("Red Hat Text", 23, "bold"),
            command=refresh_btn,
            fg_color="darkviolet",
            hover_color="purple"
        ).pack(padx=5, pady=5, anchor="n")
        
        ctk.CTkButton(
            root,
            text="Return to Main Menu",
            font=("Red Hat Text", 23, "bold"),
            command=main_menu,
            fg_color="darkviolet",
            hover_color="purple"
        ).pack(padx=5, pady=5, anchor="n")
    
    refresh_btn()


def save_location(lat, lon, city_name="Unknown"):
    """Save a location to history"""
    try:
        with open(json_path, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    
    location = {
        "lat": lat,
        "lon": lon,
        "city": city_name,
        "time": datetime.now().isoformat()
    }
    
    # Avoid duplicates
    if location not in history:
        history.insert(0, location)
        history = history[:10]  # Keep last 10 searches
    
    with open(json_path, "w") as f:
        json.dump(history, f, indent=2)


def load_history():
    """Load search history from file"""
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def show_recent_searches():
    ctk.CTkLabel(
        root, text="Recent Searches:", font=("Red Hat Text", 16, "bold")
    ).pack(padx=10, pady=(10, 2), anchor="nw")
    
    history = load_history()
    
    history_frame = ctk.CTkFrame(root, fg_color="transparent")
    history_frame.pack(padx=10, pady=5, fill="both", expand=True)
    
    if not history:
        ctk.CTkLabel(
            history_frame, text="No recent searches", font=("Red Hat Text", 14)
        ).pack(padx=10, pady=5, anchor="nw")
    else:
        buttons = []
        last_width = [0]

        def relayout(event=None):
            frame_width = history_frame.winfo_width()
            
            if frame_width <= 1 or frame_width == last_width[0]:
                return
            
            last_width[0] = frame_width

            PADX, PADY = 5, 5
            BUTTON_HEIGHT = 32
            current_x = PADX
            current_y = PADY

            for btn in buttons:
                btn_width = btn.winfo_reqwidth()
                if current_x + btn_width + PADX > frame_width and current_x > PADX:
                    current_x = PADX
                    current_y += BUTTON_HEIGHT + PADY

                btn.place(x=current_x, y=current_y)
                current_x += btn_width + PADX

        history_frame.bind("<Configure>", relayout)

        for location in history:
            city = location["city"]
            lat = location["lat"]
            lon = location["lon"]

            suggest = ctk.CTkButton(
                history_frame,
                text=city,
                font=("Red Hat Text", 14, "bold"),
                fg_color="#696969",
                hover_color="#555555",
                width=0,
                height=32,
                command=lambda lat=lat, lon=lon: show_weather(lat, lon)
            )
            buttons.append(suggest)
        
        # Trigger initial layout
        root.update_idletasks()
        relayout()


def city_weather(city):
    location = Nominatim(user_agent="xweather").geocode(city)

    if not location:
        messagebox.showerror(
            "Invalid City Name", "City Not Found, Please Type Valid City Name."
        )
        return

    # Save to history BEFORE showing weather
    save_location(location.latitude, location.longitude, city)
    
    # Then show the weather
    show_weather(location.latitude, location.longitude)


def city_entry():
    clear()
    title()

    ctk.CTkLabel(
        root, text="City Name:", font=("Red Hat Text", 23)
    ).pack(pady=10)

    entry = ctk.CTkEntry(root, font=("Red Hat Text", 18))
    entry.pack(pady=10)

    ctk.CTkButton(
        root, text="Confirm", font=("Red Hat Text", 23),
        fg_color="green", hover_color="darkgreen",
        command=lambda: city_weather(entry.get())
    ).pack(pady=10)

    ctk.CTkButton(
        root,
        text="Return to Main Menu",
        font=("Red Hat Text", 23, "bold"),
        command=main_menu,
        fg_color="darkviolet",
        hover_color="purple"
    ).pack(padx=10, pady=10, side=ctk.BOTTOM)

    ctk.CTkButton(
        root,
        text="Clear Search History",
        font=("Red Hat Text", 23, "bold"),
        command=clear_history,
        fg_color="darkviolet",
        hover_color="purple"
    ).pack(padx=10, pady=10, side=ctk.BOTTOM)

    show_recent_searches()


def title():
    ctk.CTkLabel(
        root, text="Welcome To XWeather!",
        font=("Zekton", 30, "bold"),
        text_color="gold"
    ).pack(padx=10, pady=10)


def main_menu():
    clear()
    title()

    ctk.CTkLabel(
        root, text="Latitude:", font=("Red Hat Text", 23)
    ).pack(pady=10)

    lat_entry = ctk.CTkEntry(root, font=("Red Hat Text", 18))
    lat_entry.pack(pady=10)

    ctk.CTkLabel(
        root, text="Longitude:", font=("Red Hat Text", 23)
    ).pack(pady=10)

    lon_entry = ctk.CTkEntry(root, font=("Red Hat Text", 18))
    lon_entry.pack(pady=10)

    def coordinates():
        try:
            show_weather(float(lat_entry.get()), float(lon_entry.get()))
        except ValueError:
            messagebox.showerror(
                "Invalid Coordinates", "Invalid Coordinates, Please Type Valid Coordinates."
            )
            return

    ctk.CTkButton(
        root, text="Confirm", font=("Red Hat Text", 23),
        fg_color="green", hover_color="darkgreen",
        command=coordinates
    ).pack(pady=10)

    ctk.CTkButton(
        root, text="Change To City Name", font=("Red Hat Text", 23),
        fg_color="blue", hover_color="darkblue",
        command=city_entry
    ).pack(pady=10)

    switch_var = ctk.StringVar(value="off")

    def switch_event():
        if switch_var.get() == "on":
            ctk.set_appearance_mode("light")
        elif switch_var.get() == "off":
            ctk.set_appearance_mode("dark")

    ctk.CTkSwitch(
        root,
        text="Light mode:",
        command=switch_event,
        variable=switch_var,
        onvalue="on",
        offvalue="off"
    ).pack(padx=10, pady=10, anchor="nw")

def clear_history():
    if messagebox.askyesno(title="Confirmation", message="Are You Sure You Want To Delete All Search History?"):
        clear()
        with open(json_path, "w") as n:
            json.dump([], n)
        city_entry()
    else:
        return city_entry()



main_menu()
root.mainloop()
