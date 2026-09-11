import tkinter as tk
from datetime import datetime

import customtkinter as ctk
import openmeteo_requests
from geopy.geocoders import Nominatim
from tkinter import tkFont

custom_font = tkFont.Font(family="Zekton", size=30, weight="bold")
custom_font2 = tkFont.Font(family="URW Gothic", size=30, weight="bold")
custom_font3 = tkFont.Font(family="Red Hat Text", size=30, weight="bold")


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
    clear()

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

    current = api.weather_api(
        "https://api.open-meteo.com/v1/forecast",
        params=params
    )[0].Current()

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
            padx=10, pady=10
        )


def coordinates():
    try:
        show_weather(float(lat_entry.get()), float(lon_entry.get()))
    except ValueError:
        clear()
        ctk.CTkLabel(
            root, text="Invalid coordinates", text_color="red"
        ).pack(pady=20)


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


def city_weather(city):
    location = Nominatim(user_agent="xweather").geocode(city)

    if not location:
        clear()
        ctk.CTkLabel(
            root, text="City not found", text_color="red"
        ).pack(pady=20)
        return

    show_weather(location.latitude, location.longitude)


def title():
    ctk.CTkLabel(
        root, text="Welcome To XWeather!",
        font=("Zekton", 30, "bold"),
        text_color="gold"
    ).pack(padx=10, pady=10)


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

root.mainloop()
