import flask
from flask import Flask, request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os, base64, datetime
from datalicit import convertirPDF
from flask import jsonify

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

#El siguiente metodo es utilizado para recibir el PDF del pliego de condiciones de la licitacion e iniciar la busqueda de
#los codigos UNSPSC, los requisitos financieros y los requisitos organizacionales que se requieren para aplicar a esta
@app.route('/analizar', methods=['GET','POST'])
def analizarPDF():

    print('Iniciando')

    #Se crea una carpeta donde se almacenaran los archivos necesarios para la busqueda
    try:
        os.stat(os.getcwd()+'/archivos')
    except:
        os.mkdir(os.getcwd()+'/archivos')
    #Se guarda el PDF dentro de la carpeta creada anteriormente y se envia al metodo convertirPDF para extraer la informacion
    target=os.getcwd()+'/archivos'
    archivo = request.files['file']
    filename=secure_filename(archivo.filename.replace('_',' '))
    destination="/".join([target, os.path.splitext(filename.replace('_',' '))[0]+'.pdf'])
    archivo.save(destination)
    analisis = convertirPDF(destination)
    #Se recibe la ruta de la imagen con los resultados obtenidos y se devuelve codificado en base64
    with open(os.path.abspath(analisis),'rb') as img_file:
        codificada=base64.b64encode(img_file.read())
    return jsonify(imagen=codificada) 
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
    app.secret_key = os.urandom(24)