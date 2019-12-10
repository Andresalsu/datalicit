from flask_cors import CORS
import os
import datalicit as prime
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

@app.route('/')
def hola():
    return "hola mundo"

# Recibe los parametros para el filtrado de las licitaciones  
@app.route('/enviar', methods=['POST'])
def enviar():
    content= request.json
    entidad = content['entidad']
    ref_proc = content['ref_proc']
    
    return jsonify(prime.filterLicit(entidad,ref_proc))
    
if __name__ == '__main__':
    app.run(threaded=True,host='0.0.0.0',debug=True,port=int("4500"))