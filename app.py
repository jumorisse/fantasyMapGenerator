from flask import Flask, render_template, send_file, request
import io

app = Flask(__name__)

import subprocess

@app.route('/')
def index():
    return render_template('mapGenerator.html')

@app.route('/generate-map')
def generate_map():
    result = subprocess.run(['python', 'mapGenerator.py'], capture_output=True)
    return result.stdout

@app.route('/generate-route', methods=['POST'])
def generate_route():
    x1 = request.form['x1']
    y1 = request.form['y1']
    x2 = request.form['x2']
    y2 = request.form['y2']
    result = subprocess.run(['python', 'routeGenerator.py', x1, y1, x2, y2], capture_output=True)
    print('First click coordinates: '+str(x1)+','+str(y1)+'  second ones:'+str(x2)+','+str(y2))
    return result.stdout
    

