# Version 1.2 9/13/23
import requests, os, io, yaml, functions, urllib.request, random
from flask import Flask, send_file
app = Flask(__name__)


STEAM_KEY = functions.cleanurl(os.environ.get('STEAM_KEY', 'Steam_api_key'))

@app.route('/')
def get_random_image(run=0,error=False):
    return 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug = True)
