# Map Generator

This project allows to generate maps in a browser window. Map generation is randomnized and produces different maps each time.
Once the map has been generated, the user can click on two points of the map. If both points are on a connected land mass, a path is drawn between the points.
This path is found using the A* algorithm. It aims to find the path with the smallest changes in height along the way.
Paths leading through mountain or snowy peak terrain are additionally penalized.

## How to Run

1. Clone this repository to your local machine.
2. Navigate to the project directory in your terminal.
3. Optional: Create and activate a new python environment.
4. Install Python packages by running 'pip install -r requirements.txt'
5. Additionally install the noise package, e.g. via conda 'conda install -c conda-forge noise', for some reason pip install noise lead to an error for me. Hence, I excluded noise from requirements.txt
6. Navigate to the directory of app.py
7. Run 'set FLASK_APP=app.py' (for Windows) or 'export FLASK_APP=app.py' (for Linux and macOS)
8. Then run 'flask run'
9. Open 'http://127.0.0.1:5000/' in your browser
