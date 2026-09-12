# XWeather 🌤️

A lightweight desktop weather application built with Python and **CustomTkinter**, utilizing the **Open-Meteo API** and **Geopy** for accurate real-time weather forecasting.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

* **City Search & Coordinates:** Look up weather details by city name or exact latitude and longitude.
* **Dynamic Search History:** Saves up to 10 recent searches locally to `~/.xweather/data.json` with quick-launch search tags.
* **Auto-Wrapping UI:** Search tags dynamically wrap to new lines based on window width and city name length.
* **Temperature Color-Coding:** Real-time visual status indicator changes color depending on temperature severity.
* **Dark / Light Mode:** Built-in theme toggling.
* **Offline & Connection Detection:** Displays distinct warnings for lost internet connectivity vs. invalid coordinates.

---

## Project Structure

```text
xweather/
├── main.py              # Main application entry point
├── requirements.txt     # Dependency list
└── README.md            # Project documentation
└── lICENCE.md           # Project Licence
```

---

# Notice

**Note**: For Better Experience, Consider Downloading The Following Fonts: Zekton, URW Gothic and Red Hat Text
**Another Note:** This Project is Currently in Beta Release. You May Encounder Some Bugs. Please Report Any Bug.

---

## Prerequisites & Installation

Make sure you have Python 3.8 or higher installed on your system.

### 1. Clone or Download the Repository

```bash
git clone [https://github.com/ABX532/XWeather.git](https://github.com/ABX532/XWeather.git)
cd xweather
```

### 2. Install Required Dependencies

Install all required dependencies via `pip`:

```bash
pip install customtkinter openmeteo-requests geopy requests
```

Or using a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## How to Run

1. Download the file in 0.0.2 Beta Release as `main.py`.
2. Open your terminal or command prompt and run:

```bash
python main.py
```

---

## Usage Guide

1. **By Coordinates (Default Screen)**:
   * Input the **Latitude** and **Longitude** (e.g., `40.7128` and `-74.0060` for New York).
   * Click **Confirm** to load live weather data.

2. **By City Name**:
   * Click **Change To City Name**.
   * Enter the city name (e.g., `London`, `Tokyo`, `Paris`).
   * Click **Confirm** to geocode the city and retrieve current weather metrics.

---

## Tech Stack & APIs

* **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Weather Data**: [Open-Meteo API](https://open-meteo.com/)
* **Geocoding Engine**: [GeoPy](https://geopy.readthedocs.io/) (Nominatim)
* **Python API Client**: `openmeteo-requests`

---

## Troubleshooting

* **"City not found"**: Double-check the city spelling. You can also specify the country (e.g., "Paris, France").
* **"Invalid coordinates"**: Ensure latitude is between -90 and 90, and longitude is between -180 and 180.
* **Missing Dependencies**: Ensure all required libraries are installed using `pip install -r requirements.txt`.

---

## License

This project is open-source and available under the [GPLv3 License](LICENSE).
