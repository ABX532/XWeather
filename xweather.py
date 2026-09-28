import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import customtkinter as ctk
from PIL import Image, ImageTk
from io import BytesIO
import openmeteo_requests
from geopy.geocoders import Nominatim

from pathlib import Path
from requests.exceptions import RequestException, Timeout, ConnectionError
import requests
import json
import subprocess

# Paths
history_dir = Path.home() / ".xweather"
history_dir.mkdir(exist_ok=True)

clone_dir = Path.home() / "XWeather"

json_path = history_dir / "data.json"
json_path_settings = history_dir / "settings.json"

conky_path = clone_dir / "conky"
conky_file_path = conky_path / "start.sh"
conky_python_file = conky_path / "conky"

conky_settings_json = conky_path / "conky_settings.json"

# Icon location (Primary local path + system path fallback)
PRIMARY_ICON_PATH = Path("/home/abdo/XWeather/xweather_icon.png")
FALLBACK_ICON_PATH = Path("/opt/xweather/icon.png")

ICON_FILE = str(PRIMARY_ICON_PATH if PRIMARY_ICON_PATH.exists() else FALLBACK_ICON_PATH)

ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("XWeather")
root.geometry("500x520")

# Load Window Icon
try:
    icon = tk.PhotoImage(file=ICON_FILE)
    root.iconphoto(False, icon)
except Exception as e:
    print(f"Error loading window icon: {e}")

api = openmeteo_requests.Client()


def load_settings():
    default_settings = {"theme": "System", "tempunit": "Celsius (°C)", "windunit": "KM/H"}
    try:
        if json_path_settings.exists():
            with open(json_path_settings, "r") as f:
                data = json.load(f)
                default_settings.update(data)
    except Exception as e:
        print(f"Error loading settings: {e}")
    return default_settings


def save_setting(key, value):
    settings_data = load_settings()
    settings_data[key] = value
    try:
        with open(json_path_settings, "w") as f:
            json.dump(settings_data, f, indent=2)
    except Exception as e:
        print(f"Error saving setting {key}: {e}")


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


def get_weather_icon_url(code):
    icon_map = {
        0: "01d", 1: "02d", 2: "02d", 3: "04d",
        45: "50d", 48: "50d", 51: "09d", 53: "09d",
        55: "09d", 61: "10d", 63: "10d", 65: "10d",
        71: "13d", 73: "13d", 75: "13d", 77: "13d",
        80: "10d", 81: "10d", 82: "11d", 85: "13d",
        86: "13d", 95: "11d", 96: "11d", 99: "11d"
    }
    icon_code = icon_map.get(code, "01d")
    return f"https://openweathermap.org/img/wn/{icon_code}@4x.png"


def load_weather_image(url, size=(100, 100)):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def show_weather(lat, lon):
    settings = load_settings()
    is_fahrenheit = settings.get("tempunit") == "Fahrenheit (°F)"

    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    air_params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["us_aqi"],
        "timezone": "auto",
    }
    if is_fahrenheit:
        air_params["temperature_unit"] = "fahrenheit"

    try:
        air_response = api.weather_api(
            air_url,
            params=air_params
        )[0]
    except IndexError:
        messagebox.showerror("API Error", "Invalid response from weather API. Please try again.")
        return

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "hourly": ["precipitation_probability"],
        "daily": [
            "sunrise", 
            "sunset",
            "temperature_2m_max",
            "temperature_2m_min",
        ],
        "forecast_days": 7,
    }

    if is_fahrenheit:
        params["temperature_unit"] = "fahrenheit"

    try:
        response = api.weather_api(
            "https://api.open-meteo.com/v1/forecast",
            params=params
        )[0]
        current = response.Current()
        hourly = response.Hourly()
        daily = response.Daily()
    except IndexError:
        messagebox.showerror("API Error", "Invalid response from weather API. Please try again.")
        return
    except openmeteo_requests.OpenMeteoRequestsError as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ["connection", "timeout", "unreachable", "refused"]):
            messagebox.showerror("Connection Error", "Unable To Connect To Server, Please Check Your Internet Connection.")
        else:
            messagebox.showerror("Invalid Coordinates", "Invalid Coordinates, Please Type Valid Coordinates.")
        return
    except requests.exceptions.HTTPError as e:
        messagebox.showerror("HTTP Error", f"HTTP Error Occurred: {e.response.status_code}")
        return
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Network Error Occurred: {e}")
        return
    except Exception as e:
        messagebox.showerror("Error", f"An Unexpected Error Occurred: {e}")
        return

    clear()

    ctk.CTkLabel(root, text="Processing, Please Wait...", font=("Red Hat Text", 18)).pack(padx=10, pady=10, anchor=tk.CENTER)

    def refresh_btn():
        def windunitfinal():
            if settings.get("windunit") == "MPH":
                return round(current.Variables(3).Value() * 0.621371)
            elif settings.get("windunit") == "M/S":
                return round(current.Variables(3).Value() / 3.6)
            else:
                return round(current.Variables(3).Value())
        temp = round(current.Variables(0).Value())
        humidity = round(current.Variables(1).Value())
        code = int(current.Variables(2).Value())
        wind = windunitfinal()
        winddirec = round(current.Variables(4).Value())
        aqi_air = round(air_response.Current().Variables(0).Value())
        time = datetime.fromtimestamp(current.Time())
        time_str = time.strftime("%H:%M")
        current_index = time.hour
        rain_prob = round(hourly.Variables(0).ValuesAsNumpy()[current_index])
        sunrise_ts = daily.Variables(0).ValuesInt64AsNumpy()[0]
        sunset_ts = daily.Variables(1).ValuesInt64AsNumpy()[0]
        sunrise_str = datetime.fromtimestamp(sunrise_ts).strftime("%H:%M")
        sunset_str = datetime.fromtimestamp(sunset_ts).strftime("%H:%M")
        temp_max_week = [round(x) for x in daily.Variables(2).ValuesAsNumpy()]
        temp_min_week = [round(x) for x in daily.Variables(3).ValuesAsNumpy()]
        
        compass_sectors = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(winddirec / 22.5) % 16
        wind_direction_text = compass_sectors[index]

        clear()
        

        temp_c = (temp - 32) * 5 / 9 if is_fahrenheit else temp
        color = (
            "darkblue" if temp_c <= 0 else
            "blue" if temp_c <= 15 else
            "lightblue" if temp_c <= 20 else
            "yellow" if temp_c <= 25 else
            "#F6BE00" if temp_c <= 30 else
            "darkorange" if temp_c <= 35 else
            "red"
        )
        def aqi_category(aqi: float) -> str:
            if aqi <= 50:
                return "Good"
            elif aqi <= 100:
                return "Moderate"
            elif aqi <= 150:
                return "Unhealthy for Sensitive Groups"
            elif aqi <= 200:
                return "Unhealthy"
            elif aqi <= 300:
                return "Very Unhealthy"
            else:
                return "Hazardous"

        # Main Header Card (Fixed at Top)
        frame = ctk.CTkFrame(root, corner_radius=20)
        frame.pack(padx=10, pady=5)

        icon_url = get_weather_icon_url(code)
        photo = load_weather_image(icon_url, size=(70, 70))

        temp_frame = ctk.CTkFrame(frame, fg_color="transparent")
        temp_frame.pack(padx=10, pady=5)

        if photo:
            ctk.CTkLabel(temp_frame, image=photo, text="").pack(side="left", padx=5)

        unit_symbol = "°F" if is_fahrenheit else "°C"
        ctk.CTkLabel(
            temp_frame, text=f"{temp}{unit_symbol}",
            font=("URW Gothic", 65, "bold"),
            text_color=color
        ).pack(padx=10, pady=5)

        ctk.CTkLabel(
            frame, text=weather_description(code),
            font=("Red Hat Text", 16)
        ).pack(padx=10, pady=(0, 5))

        # --- SCROLLABLE CONTAINER FOR DETAILED INFO ---
        scroll_frame = ctk.CTkScrollableFrame(root, height=180, corner_radius=15, fg_color="transparent")
        scroll_frame.pack(padx=10, pady=5, fill="both", expand=True)

        maxdailyforecast = {
            "Monday": temp_max_week[0],
            "Tuesday": temp_max_week[1],
            "Wednesday": temp_max_week[2],
            "Thursday": temp_max_week[3],
            "Friday": temp_max_week[4],
            "Saturday": temp_max_week[5],
            "Sunday": temp_max_week[6],
        }

        mindailyforecast = {
            "Monday": temp_min_week[0],
            "Tuesday": temp_min_week[1],
            "Wednesday": temp_min_week[2],
            "Thursday": temp_min_week[3],
            "Friday": temp_min_week[4],
            "Saturday": temp_min_week[5],
            "Sunday": temp_min_week[6],
        }

        details = [
            f"Latitude: {lat}",
            f"Longitude: {lon}",
            f"Last Check: {time_str}",
            f"Humidity: {humidity}%",
            f"Wind: {wind} {settings.get("windunit")} ({wind_direction_text})",
            f"Rain Probability: {rain_prob}%",
            f"Sunrise: {sunrise_str}",
            f"Sunset: {sunset_str}",
            f"Air Quality: {aqi_category(aqi_air)} (US AQI: {aqi_air})",
        ]

        forecast = [
            f"Mon"
            f"\n{maxdailyforecast["Monday"]}{unit_symbol}"
            f"\n{mindailyforecast["Monday"]}{unit_symbol}",
            f"Tue"
            f"\n{maxdailyforecast["Tuesday"]}{unit_symbol}"
            f"\n{mindailyforecast["Tuesday"]}{unit_symbol}",
            f"Wed"
            f"\n{maxdailyforecast["Wednesday"]}{unit_symbol}"
            f"\n{mindailyforecast["Wednesday"]}{unit_symbol}",
            f"Fri"
            f"\n{maxdailyforecast["Friday"]}{unit_symbol}"
            f"\n{mindailyforecast["Friday"]}{unit_symbol}",
            f"Sat"
            f"\n{maxdailyforecast["Saturday"]}{unit_symbol}"
            f"\n{mindailyforecast["Saturday"]}{unit_symbol}",
            f"Sun"
            f"\n{maxdailyforecast["Sunday"]}{unit_symbol}"
            f"\n{mindailyforecast["Sunday"]}{unit_symbol}",
        ]

        for text in details:
            ctk.CTkLabel(
                scroll_frame, 
                text=text, 
                font=("Red Hat Text", 20)
            ).pack(padx=10, pady=4)

        frcastframe = ctk.CTkFrame(scroll_frame, corner_radius="20")
        frcastframe.pack(padx=10, pady=5)

        ctk.CTkLabel(frcastframe, text="Max and Min Temperature in Every Day This Week", font=("Red Hat Text", 14)).pack(padx=10, pady=10, side="top")
        for text in forecast:
                ctk.CTkLabel(
                    frcastframe, 
                    text=text, 
                    font=("Red Hat Text", 16),
                ).pack(padx=10, pady=4, side="left")
        

        # Action Buttons (Side-by-side at Bottom)
        btn_frame = ctk.CTkFrame(root, fg_color="transparent")
        btn_frame.pack(padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Refresh", font=("Red Hat Text", 25, "bold"),
            command=refresh_btn, fg_color="darkviolet", hover_color="purple",
            width=130
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Main Menu", font=("Red Hat Text", 25, "bold"),
            command=main_menu, fg_color="darkviolet", hover_color="purple",
            width=130
        ).pack(side="left", padx=5)

    refresh_btn()


def save_location(lat, lon, city_name="Unknown"):
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

    if location not in history:
        history.insert(0, location)
        history = history[:10]

    with open(json_path, "w") as f:
        json.dump(history, f, indent=2)


def load_history():
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def show_recent_searches():
    ctk.CTkLabel(root, text="Recent Searches:", font=("Red Hat Text", 16, "bold")).pack(padx=10, pady=(10, 2), anchor="nw")

    history = load_history()
    history_frame = ctk.CTkFrame(root, fg_color="transparent")
    history_frame.pack(padx=10, pady=5, fill="both", expand=True)

    if not history:
        ctk.CTkLabel(history_frame, text="No recent searches", font=("Red Hat Text", 14)).pack(padx=10, pady=5, anchor="nw")
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
            current_x, current_y = PADX, PADY

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
            lat, lon = location["lat"], location["lon"]

            suggest = ctk.CTkButton(
                history_frame, text=city, font=("Red Hat Text", 14, "bold"),
                fg_color="#696969", hover_color="#555555", width=0, height=32,
                corner_radius=30,
                command=lambda lat=lat, lon=lon: show_weather(lat, lon)
            )
            buttons.append(suggest)

        root.update_idletasks()
        relayout()


def city_weather(city):
    if not city.strip():
        return
    location = Nominatim(user_agent="xweather").geocode(city)

    if not location:
        messagebox.showerror("Invalid City Name", "City Not Found, Please Type Valid City Name.")
        return

    save_location(location.latitude, location.longitude, city)
    show_weather(location.latitude, location.longitude)


def city_entry():
    clear()
    title()

    ctk.CTkLabel(root, text="City Name:", font=("Red Hat Text", 23)).pack(pady=10)
    entry = ctk.CTkEntry(root, font=("Red Hat Text", 18))
    entry.pack(pady=10)

    ctk.CTkButton(
        root, text="Confirm", font=("Red Hat Text", 23),
        fg_color="green", hover_color="darkgreen",
        command=lambda: city_weather(entry.get())
    ).pack(pady=10)

    ctk.CTkButton(
        root, text="Return to Main Menu", font=("Red Hat Text", 23, "bold"),
        command=main_menu, fg_color="darkviolet", hover_color="purple"
    ).pack(padx=10, pady=10, side=ctk.BOTTOM)

    show_recent_searches()


def title():
    ctk.CTkLabel(
        root, text="Welcome To XWeather!",
        font=("Zekton", 30, "bold"), text_color="gold"
    ).pack(padx=10, pady=10)


def main_menu():
    clear()

    settings_data = load_settings()
    ctk.set_appearance_mode(settings_data.get("theme", "Dark"))

    title()

    ctk.CTkLabel(root, text="Latitude:", font=("Red Hat Text", 23)).pack(pady=10)
    lat_entry = ctk.CTkEntry(root, font=("Red Hat Text", 18))
    lat_entry.pack(pady=10)

    ctk.CTkLabel(root, text="Longitude:", font=("Red Hat Text", 23)).pack(pady=10)
    lon_entry = ctk.CTkEntry(root, font=("Red Hat Text", 18))
    lon_entry.pack(pady=10)

    def coordinates():
        try:
            show_weather(float(lat_entry.get()), float(lon_entry.get()))
        except ValueError:
            messagebox.showerror("Invalid Coordinates", "Invalid Coordinates, Please Type Valid Coordinates.")

    ctk.CTkButton(
        root, text="Confirm", font=("Red Hat Text", 23),
        fg_color="green", hover_color="darkgreen", command=coordinates
    ).pack(pady=10)

    ctk.CTkButton(
        root, text="Change To City Name", font=("Red Hat Text", 23),
        fg_color="blue", hover_color="darkblue", command=city_entry
    ).pack(pady=10)

    def open_settings():
        for widget in root.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                widget.lift()
                return

        settings_window = ctk.CTkToplevel(root)
        settings_window.title("XWeather Settings")
        settings_window.geometry("380x380")
        settings_window.resizable(False, False)

        tabview = ctk.CTkTabview(settings_window, width=350, height=320)
        tabview.pack(padx=10, pady=10, fill="both", expand=True)

        tab_general = tabview.add("General")
        tab_appearance = tabview.add("Appearance")
        tab_widgets = tabview.add("Widgets")
        tab_about = tabview.add("About")

        # --- TAB 1: GENERAL SETTINGS ---
        ctk.CTkLabel(tab_general, text="Temperature Unit:", font=("Red Hat Text", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
        
        current_settings = load_settings()
        unit_var = ctk.StringVar(value=current_settings.get("tempunit", "Celsius (°C)"))

        def change_unit_event(selected_unit):
            save_setting("tempunit", selected_unit)

        unit_selector = ctk.CTkSegmentedButton(
            tab_general,
            values=["Celsius (°C)", "Fahrenheit (°F)"],
            variable=unit_var,
            command=change_unit_event
        )
        unit_selector.pack(anchor="w", padx=10, pady=(0, 15))

        ctk.CTkLabel(tab_general, text="Wind Speed Unit:", font=("Red Hat Text", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
        
        current_settings = load_settings()
        wind_unit_var = ctk.StringVar(value=current_settings.get("windunit", "KM/H"))

        def change_wind_unit_event(selected_unit):
            save_setting("windunit", selected_unit)

        unit_selector = ctk.CTkSegmentedButton(
            tab_general,
            values=["KM/H", "MPH", "M/S"],
            variable=wind_unit_var,
            command=change_wind_unit_event
        )
        unit_selector.pack(anchor="w", padx=10, pady=(0, 15))

        ctk.CTkLabel(tab_general, text="Search History:", font=("Red Hat Text", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
        
        def clear_history_settings():
            if messagebox.askyesno("Confirmation", "Are You Sure You Want To Delete All Search History?"):
                with open(json_path, "w") as n:
                    json.dump([], n)

        ctk.CTkButton(
            tab_general,
            text="Clear History",
            fg_color="red",
            hover_color="darkred",
            command=clear_history_settings
        ).pack(anchor="w", padx=10, pady=5)

        # --- TAB 2: APPEARANCE ---
        ctk.CTkLabel(tab_appearance, text="Theme Mode:", font=("Red Hat Text", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        theme_var = ctk.StringVar(value=current_settings.get("theme", "Dark"))

        def change_theme_event(new_theme):
            ctk.set_appearance_mode(new_theme)
            save_setting("theme", new_theme)

        theme_menu = ctk.CTkOptionMenu(
            tab_appearance,
            values=["Dark", "Light", "System"],
            variable=theme_var,
            command=change_theme_event
        )
        theme_menu.pack(anchor="w", padx=10, pady=5)

        # --- TAB 3: ABOUT (Always loads your icon) ---
        try:
            about_icon = Image.open(ICON_FILE)
            ctk_icon = ctk.CTkImage(light_image=about_icon, dark_image=about_icon, size=(50, 50))
            ctk.CTkButton(tab_about, image=ctk_icon, text="", fg_color="transparent", hover=False).pack(padx=2, pady=2)
        except Exception as e:
            print(f"Error displaying icon in About tab: {e}")

        ctk.CTkLabel(tab_about, text="XWeather", font=("Zekton", 22, "bold"), text_color="gold").pack(pady=2)
        ctk.CTkLabel(tab_about, text="Version 1.0", font=("Red Hat Text", 12)).pack(pady=2)
        ctk.CTkLabel(tab_about, text="Data provided by Open-Meteo API", font=("Red Hat Text", 11, "italic")).pack(pady=2)
        ctk.CTkLabel(tab_about, text="© 2026 ABX. All rights reserved.", font=("Red Hat Text", 11, "italic")).pack(pady=10, side=tk.BOTTOM)

        # ---TAB 4: WIDGETS---

        def conky_widget():
            global proc
            proc = subprocess.Popen([conky_file_path])
        def conky_close():
            proc.kill()
            

        ctk.CTkLabel(tab_widgets,text="Make Conky Widget(Beta)", font=("Red Hat Text", 14, "bold")).pack(anchor="w" ,padx=10, pady=10)
        ctk.CTkButton(tab_widgets, text="Run Conky Widget", command=conky_widget).pack(anchor="w" ,padx=10, pady=2)
        ctk.CTkButton(tab_widgets, text="Close Conky Widget", command=conky_close, fg_color="red", hover_color="darkred").pack(anchor="w" ,padx=10, pady=2)
        ctk.CTkLabel(tab_widgets, text="Note: This Feature Still Under Construction", font=("Red Hat Text", 11, "italic")).pack(anchor="w" ,padx=10, pady=2)


    ctk.CTkButton(
        root, text="Settings", font=("Red Hat Text", 23),
        fg_color="red", hover_color="darkred", command=open_settings
    ).pack(padx=10, pady=10, side=tk.BOTTOM)


def clear_history():
    if messagebox.askyesno(title="Confirmation", message="Are You Sure You Want To Delete All Search History?"):
        with open(json_path, "w") as n:
            json.dump([], n)
        city_entry()


main_menu()
root.mainloop()