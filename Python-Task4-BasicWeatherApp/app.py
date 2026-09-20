import tkinter as tk
from tkinter import ttk, messagebox
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Basic Weather App - OIBSIP")
        root.geometry("760x560")
        root.resizable(False, False)

        tk.Label(root, text="Basic Weather App",
                 font=("Arial", 28, "bold")).pack(pady=(25, 5))
        tk.Label(root, text="OASIS INFOBYTE • Python Programming • Task 4",
                 font=("Arial", 12)).pack(pady=(0, 20))

        search = ttk.LabelFrame(root, text="Search Weather")
        search.pack(fill="x", padx=35, pady=10)

        ttk.Label(search, text="City:").grid(row=0, column=0, padx=15, pady=18)
        self.city_entry = ttk.Entry(search, width=42)
        self.city_entry.grid(row=0, column=1, padx=10, pady=18)
        self.city_entry.bind("<Return>", lambda event: self.get_weather())

        self.search_button = ttk.Button(search, text="Get Weather",
                                        command=self.get_weather)
        self.search_button.grid(row=0, column=2, padx=15, pady=18)

        result = ttk.LabelFrame(root, text="Weather Information")
        result.pack(fill="both", expand=True, padx=35, pady=15)

        self.location_label = tk.Label(
            result, text="Enter a city and click Get Weather",
            font=("Arial", 20, "bold"))
        self.location_label.pack(pady=(25, 10))

        self.condition_label = tk.Label(result, text="", font=("Arial", 15))
        self.condition_label.pack(pady=8)

        self.temp_label = tk.Label(result, text="", font=("Arial", 34, "bold"))
        self.temp_label.pack(pady=8)

        self.details_label = tk.Label(result, text="", font=("Arial", 13),
                                      justify="center")
        self.details_label.pack(pady=15)

        self.status_label = tk.Label(root, text="Ready", anchor="w")
        self.status_label.pack(fill="x", padx=35, pady=(0, 15))
        self.city_entry.focus_set()

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Missing City", "Please enter a city name.")
            return

        self.search_button.config(state="disabled")
        self.status_label.config(text="Fetching weather...")
        self.root.update_idletasks()

        try:
            geo = requests.get(
                GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=10)
            geo.raise_for_status()
            results = geo.json().get("results")
            if not results:
                raise ValueError("City not found. Please check the city name.")

            place = results[0]
            weather = requests.get(
                FORECAST_URL,
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": (
                        "temperature_2m,relative_humidity_2m,"
                        "apparent_temperature,weather_code,wind_speed_10m"
                    ),
                    "timezone": "auto"
                },
                timeout=10)
            weather.raise_for_status()
            current = weather.json()["current"]

            condition = WEATHER_CODES.get(
                current.get("weather_code"), "Weather information available")

            self.location_label.config(
                text=f"{place.get('name', city)}, {place.get('country', '')}")
            self.condition_label.config(text=condition)
            self.temp_label.config(text=f"{current['temperature_2m']:.1f} °C")
            self.details_label.config(
                text=(
                    f"Feels like: {current['apparent_temperature']:.1f} °C\n"
                    f"Humidity: {current['relative_humidity_2m']}%\n"
                    f"Wind speed: {current['wind_speed_10m']:.1f} km/h\n"
                    f"Updated: {current.get('time', 'Current')}"
                ))
            self.status_label.config(text="Weather updated successfully.")

        except requests.exceptions.RequestException:
            self.status_label.config(text="Unable to connect to the weather service.")
            messagebox.showerror(
                "Connection Error",
                "Could not connect to the weather service. "
                "Please check your internet connection and try again.")
        except ValueError as exc:
            self.status_label.config(text="Could not find the requested city.")
            messagebox.showwarning("Weather Search", str(exc))
        except (KeyError, TypeError):
            self.status_label.config(text="Unexpected weather data received.")
            messagebox.showerror(
                "Data Error",
                "The weather service returned unexpected data. Please try again.")
        finally:
            self.search_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
