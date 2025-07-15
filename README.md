#  G-loc – Global Live Observation and Camera Viewer

**G-loc** is a Python application that displays an interactive world map with clickable markers representing real-time public camera feeds from across the globe. Built with `pygame`, it allows users to visually explore live streams simply by clicking on the dots on the map.

---

##  How It Works

- A world map is displayed using `pygame`, and camera feed markers are overlaid using latitude and longitude coordinates.
- When a user clicks a marker, a **feed window** opens showing details and launches the camera feed (usually in the default web browser).
- Camera sources are pulled from organized region-based files (like `regions/europe.py`).

---

##  Features

-  Interactive world map with zoom and pan
-  Clickable markers for each camera feed
-  Public live feeds from various services (YouTube, EarthCam, Skyline, etc.)
-  Regionally organized camera lists
-  Fully written in Python using `pygame` and `Pillow`

---

##  Requirements

- Python 3.8 or newer
- Install dependencies with:
  ```bash
  pip install -r requirements.txt
