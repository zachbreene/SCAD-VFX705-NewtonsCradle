<h1 align=center> Autodesk Maya Newton's Cradle Generator </h1>
<h2 align=center> A VFX705: Visual Effects Project by Zach Breene </h2>
<h4 align=center> Created at Savannah College of Art and Design, May 2026 </h4>
<h4 align=center> *NOTE: THIS PROJECT WAS CREATED IN PART UTILIZING VIBE CODING WITH GOOGLE GEMINI, IN ORDER TO CONVERT MEL (Maya Embedded Language) MODELING HISTORY CODE INTO PYTHON* </h4>

## Introduction
My task for this project was to create a Python script that automatically generates a fully functional, tech-themed Newton's Cradle. Instead of traditional metal spheres, the pendulum relies on mechanical keyboard keycaps suspended by iPhone wires, all plugged into a modeled surge protector base. This project was created utilizing Vibe Coding with Google Gemini to convert ~1,225 lines of raw MEL code from the Autodesk Maya History Logs of my own manual modeling into a unified Python script. This single script is capable of creating the entire 3D model, building and applying 13 custom Arnold shaders, animating the cradle using mathematical expressions, and deploying a GUI to dynamically change the letters on the keycaps. 

---

## Implementation + Functions
### SP26_VFX705_01_Zach_Breene_NewtonsCradle_v01.py

This is the main, 1585-line file containing all the generation methods for the scene. <br>

&emsp; ***Modeling & GUI Method***

* The modeling execution begins with `open_ui()`, which generates a custom window prompting the user to enter a 5-letter word. Once validated, the script calls a series of generation functions (e.g., `mk_table()`, `mk_surge_protector()`, `mk_KeyCap()`) that utilize the vibe-coded Python commands to programmatically build the complex geometry from scratch. 

&emsp; ***Expression Animation Method***

* The animation method is driven by the `newton_Animation()` function. Instead of manual keyframes, it uses sine wave math (`sin(time*5)`) and value clamping to dynamically simulate the physics and directional momentum transfer across the pendulums. 

&emsp; ***Lighting & Shading Method***

* The script automatically generates 13 distinct `aiStandardSurface` materials—including physical representations of silicone, glossy plastic, metal, and wood—and assigns them to the appropriate geometry. It additionally sets up an Arnold Skydome with an EXR HDRI, configures a directional light, and applies 1080p EXR batch rendering settings to the active camera.

---

## How To Run
**IMPORTANT: This program is to only be used inside of Autodesk Maya, as it won't work elsewise.** 

To run this implementation, you must open Autodesk Maya and load `SP26_VFX705_01_Zach_Breene_NewtonsCradle_v01.py` into the Python Script Editor. Before running, ensure that the `IN_PATH` variable points to the correct directory containing your `empty_play_room_4k.exr` HDRI map and `WoodTexture.png` texture files. Once executed, a GUI will appear asking for a 5-letter word. Input your chosen word (using only letters, no spaces or numbers) and click "Generate Newton's Cradle". The script will automatically wipe any existing script geometry, generate the model, apply shaders, set the animation timeline, and configure the render settings. 

---

## Contribution
As I was the sole member of this project, I contributed to the whole of the project. This contribution is as follows:
* Manual 3D Modeling and MEL Code History Logging
* Vibe Coding Conversion from MEL to Python
* Python Implementation of Arnold Shaders, Cameras, and Render Settings
* Implementation of Sine Wave Math Expressions for Physics
