#  G-loc 

**G-loc** or (Project Geo-locate) is a Python application that displays an interactive world map with clickable markers representing real-time public camera feeds from across the globe. Built with `pygame`, it allows users to visually explore live streams simply by clicking on the dots on the map. However this projects initial purpose was to use live camera feeds around the globe and face recognition software to identify a person through the live cameras but because i am a hobbyist coder and code for fun I only got until here (for now).

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

---

## Contributions 

We love community contributions! Whether it's fixing bugs, adding new camera sources, improving the UI, or optimizing performance — every bit helps G-loc grow .

### How to Contribute?

Fork this repository

Create a branch for your feature or fix

bash
git checkout -b feature/my-feature
Make your changes

Commit and push

bash
git commit -m "Add: My awesome feature"
git push origin feature/my-feature
Submit a Pull Request (PR) with a clear explanation of what you changed

## Contribution Guidelines

Keep code clean and readable (use comments if needed)

Test your changes before submitting

Don’t rebrand or redistribute the project under another name

Feel free to open an issue for discussions, bugs, or ideas

--- 

## Contact me 
email adress: roody_norman@tutamail.com


