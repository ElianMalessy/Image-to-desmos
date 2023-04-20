from flask import Flask
from flask_cors import CORS

from PIL import Image
import numpy as np
import cv2 as cv
import potrace
import pyperclip

import json
height = {"value": 0}
width = {"value": 0}
app = Flask(__name__)
CORS(app)

def get_contours(filename):
    image = cv.imread(filename, cv.IMREAD_GRAYSCALE)
    gray = cv.cvtColor(image, cv.COLOR_GRAY2RGB)
   
    edges = cv.Canny(gray, 120, 200)
    height["value"] = image.shape[0]
    width["value"] = image.shape[1]
    return edges[::-1]
def get_trace(data):
    for i in range(len(data)):
        data[i][data[i] > 1] = 1
    bmp = potrace.Bitmap(data)
    path = bmp.trace(2, potrace.TURNPOLICY_MINORITY, 1.0, 1, .5)
    return path

def get_latex(filename):
    latex = []
    path = get_trace(get_contours(filename))

    for curve in path.curves:
        segments = curve.segments
        start = curve.start_point
        for segment in segments:
            x0, y0 = start
            if segment.is_corner:
                x1, y1 = segment.c
                x2, y2 = segment.end_point
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x0, x1, y0, y1))
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x1, x2, y1, y2))
            else:
                x1, y1 = segment.c1
                x2, y2 = segment.c2
                x3, y3 = segment.end_point
                latex.append('((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)),\
                (1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))' % \
                (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = segment.end_point
    return latex

def get_expressions():
    exprid = 0
    exprs = []
    #file1 = open("text.txt","w")
    for expr in get_latex('birdsall-removebg-preview.png'):
        exprid += 1
        #file1.write(expr + "\n")
        exprs.append({'id': 'expr-' + str(exprid), 'latex': expr, 'color': '#000000', 'secret': True})
    #file1.close()
    return exprs


@app.route('/init')
def init():
    return json.dumps({'height': height["value"], 'width': width["value"], 'show_grid': True})

@app.route('/')
def index():
    return json.dumps({'result': latex_image})

if __name__ == '__main__':
    latex_image = get_expressions()
    app.run()