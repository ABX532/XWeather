# XWeather 🌤️

**XWeather** is a modern Python desktop application built with `CustomTkinter` that provides real-time weather information using the free Open-Meteo API and GeoPy geocoding.

---

## Features

* **Search Options**: Look up weather by geographic coordinates (Latitude/Longitude) or by City Name.
* **Dynamic Visuals**: Temperature display changes color dynamically based on weather severity (blue for cold, red for extreme heat).
* **Comprehensive Metrics**: Displays temperature (°C), weather conditions, humidity (%), wind speed (km/h), and local check time.
* **Modern GUI**: Sleek, customizable UI powered by CustomTkinter with a gold theme.

---

## Project Structure

```text
xweather/
├── main.py              # Main application entry point
├── requirements.txt     # Dependency list
└── README.md            # Project documentation
```

---

## Prerequisites & Installation

Make sure you have Python 3.8 or higher installed on your system.

### 1. Clone or Download the Repository

```bash
git clone https://github.com/your-username/xweather.git
cd xweather
```

### 2. Install Required Dependencies

Install all required dependencies via `pip`:

```bash
pip install customtkinter openmeteo-requests geopy requests-cache retry-requests tkfontchooser
```

Or using a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## How to Run

1. Download the file in 0.0.1 Beta Release as `main.py`.
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

## Temperature Color Thresholds

The application dynamically updates the temperature text color according to the current temperature:

| Temperature Range (°C) | Display Color | Visual Indication |
| :--- | :--- | :--- |
| ≤ 0°C | Dark Blue | Freezing |
| 1°C – 15°C | Blue | Cold |
| 16°C – 20°C | Light Blue | Cool |
| 21°C – 25°C | Yellow | Mild |
| 26°C – 30°C | Gold | Warm |
| 31°C – 35°C | Dark Orange | Hot |
| > 35°C | Red | Extreme Heat |

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

This project is open-source and available under the [MIT License](LICENSE).
