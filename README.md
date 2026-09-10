XWeather 🌤️

XWeather is a simple weather application built with Python, CustomTkinter, Open-Meteo, and GeoPy.

It allows you to check the current weather using either:

Latitude and longitude
City name
Features
🌡️ Current temperature
☁️ Weather condition
💧 Humidity
💨 Wind speed
🕐 Last weather check time
📍 Coordinate-based weather search
🏙️ City-name weather search
🎨 Custom fonts and temperature colors
🖥️ Simple CustomTkinter interface
Requirements

Python 3.9 or newer is recommended.

Install the required packages:

pip install customtkinter openmeteo-requests geopy

Fonts

XWeather uses custom fonts:

Zekton
URW Gothic
Red Hat Text

The font files should be included in the fonts folder:

XWeather/
├── main.py
├── README.md
└── fonts/
    ├── Zekton.ttf
    ├── URWGothic.ttf
    └── RedHatText.ttf

Important

Having the .ttf files in the project does not automatically make Tkinter use them.

If you want XWeather to display the same fonts on computers where they are not installed, the application needs to load/register the font files when it starts.

The font files should also be distributed according to their respective font licenses.

Running XWeather

Clone or download the project, open a terminal in the project folder, and run:

python main.py

API

Weather data is provided by Open-Meteo.

City names are converted into coordinates using GeoPy's Nominatim geocoder.

No API key is required for the basic Open-Meteo usage in this project.

Project Structure
XWeather/
│
├── main.py
├── README.md
│
└── fonts/
    ├── Zekton.ttf
    ├── URWGothic.ttf
    └── RedHatText.ttf

License

This project is provided for educational/personal use.

Check the licenses of the included fonts and external services before redistributing the project.

Credits
Weather data: Open-Meteo
Geocoding: OpenStreetMap Nominatim
GUI: CustomTkinter
Programming language: Python
