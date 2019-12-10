from PIL import Image
from os import listdir
from os.path import isfile, join
import os, unidecode, string, shutil, pytesseract, re
from pdf2image import convert_from_path

path = "/Users/andalval/Desktop/prueba datalicit/9. MINISTERIO DE HACIENDA MHCP-LP-05-2019/"
archivos = [f for f in listdir(path) if isfile(join(path, f))]
i=1
for x in archivos:
    ruta = path + x
    try:
        os.stat(path+"/Imagenes para analizar")
    except:
        os.mkdir(path+"/Imagenes para analizar")
    rutanueva=path+"/Imagenes para analizar"
    if ruta.endswith('.pdf') and "PLIEGO" in x or "Pliego" in x:
        pages = convert_from_path(ruta, dpi=200)
        for page in pages:
            filename = x + "-" + str(i) + '.jpg'
            page.save(os.path.join(rutanueva,filename), 'JPEG')
            i=i+1

path = path+"Imagenes para analizar/"

def buscarPresupuesto():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra="presupuesto oficial"
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        if ruta.endswith('.jpg') and "PLIEGO" in x or "Pliego" in x:
            im = Image.open(ruta)
            # Utilizamos el método "image_to_string"
            # Le pasamos como argumento la imagen abierta con Pillow
            try:
                os.stat(path+"texto"+x+".txt")
            except:
                texto = pytesseract.image_to_string(im)
                texto=unidecode.unidecode(texto)
                datafile = ''
                with open(path+"texto"+x+".txt", "w") as text_file:
                    text_file.write(texto.encode().decode())
            with open(path+"texto"+x+".txt", "r") as text_file:
                datafile = text_file.readlines()
            for i, line in enumerate(datafile):
                if palabra in line:
                    for l in datafile[i:i+5]:
                        ocurrencias.append(l)
            # Mostramos el resultado
    for j in ocurrencias:
        if '$' in j:
            presupuesto = re.findall(r'\d+\b', j)
            results = ''.join(presupuesto)
            return results

def buscarCodigo():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra="LICITACION PUBLICA"
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        if ruta.endswith('.jpg') and "PLIEGO" in x or "Pliego" in x:
            im = Image.open(ruta)
            # Utilizamos el método "image_to_string"
            # Le pasamos como argumento la imagen abierta con Pillow
            try:
                os.stat(path+"texto"+x+".txt")
            except:
                texto = pytesseract.image_to_string(im)
                texto=unidecode.unidecode(texto)
                datafile = ''
                with open(path+"texto"+x+".txt", "w") as text_file:
                    text_file.write(texto.encode().decode())
            with open(path+"texto"+x+".txt", "r") as text_file:
                datafile = text_file.readlines()
            for i, line in enumerate(datafile):
                if palabra in line:
                    for l in datafile[i:i+1]:
                        ocurrencias.append(l)
    results=ocurrencias[0]
    return results

def buscarObjeto():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra="OBJETO"
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        if ruta.endswith('.jpg') and "PLIEGO" in x or "Pliego" in x:
            im = Image.open(ruta)
            # Utilizamos el método "image_to_string"
            # Le pasamos como argumento la imagen abierta con Pillow
            try:
                os.stat(path+"texto"+x+".txt")
            except:
                texto = pytesseract.image_to_string(im)
                texto=unidecode.unidecode(texto)
                datafile = ''
                with open(path+"texto"+x+".txt", "w") as text_file:
                    text_file.write(texto.encode().decode())
            with open(path+"texto"+x+".txt", "r") as text_file:
                datafile = text_file.readlines()
            for i, line in enumerate(datafile):
                if palabra in line:
                    for l in datafile[i:i+8]:
                        ocurrencias.append(l.replace('\n',''))
    resultados=ocurrencias[0:8]
    results=' '.join(resultados)
    return results

def buscarPlazo():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra="plazo de ejecuci"
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        if ruta.endswith('.jpg') and "PLIEGO" in x or "Pliego" in x:
            im = Image.open(ruta)
            # Utilizamos el método "image_to_string"
            # Le pasamos como argumento la imagen abierta con Pillow
            try:
                os.stat(path+"texto"+x+".txt")
            except:
                texto = pytesseract.image_to_string(im)
                texto=unidecode.unidecode(texto)
                datafile = ''
                with open(path+"texto"+x+".txt", "w") as text_file:
                    text_file.write(texto.encode().decode())
            with open(path+"texto"+x+".txt", "r") as text_file:
                datafile = text_file.readlines()
            for i, line in enumerate(datafile):
                if palabra in line:
                    for l in datafile[i:i+7]:
                        ocurrencias.append(l.replace('\n',''))
    p=0
    for j in ocurrencias:
        if 'sera' in j:
            fecha = ocurrencias[p:p+1]
            results = ''.join(fecha)
            return results
        p += 1

def buscarUNSPSC():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["SEGMENTO","Segmento", "UNSPSC", "Producto"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        if ruta.endswith('.jpg') and "PLIEGO" in x or "Pliego" in x:
            im = Image.open(ruta)
            # Utilizamos el método "image_to_string"
            # Le pasamos como argumento la imagen abierta con Pillow
            try:
                os.stat(path+"texto"+x+".txt")
            except:
                texto = pytesseract.image_to_string(im)
                texto=unidecode.unidecode(texto)
                datafile = ''
                with open(path+"texto"+x+".txt", "w") as text_file:
                    text_file.write(texto.encode().decode())
            with open(path+"texto"+x+".txt", "r") as text_file:
                datafile = text_file.readlines()
            for i, line in enumerate(datafile):
                for d in palabra:
                    if d in line:
                        for l in datafile[i:i+90]:
                            ocurrencias.append(l.replace('\n',''))
    results=[]
    for j in ocurrencias:
        if '81' in j:
            codigo = re.findall(r'\d+\b', ''.join(j))
            results.append(''.join(codigo))
    return results

valor = buscarPresupuesto()
print(valor)
codigo=buscarCodigo()
print(codigo)
objeto=buscarObjeto()
print(objeto)
try:
    ejecucion=buscarPlazo()
    print(ejecucion.replace('ejecucien','ejecucion'))
except:
    print('Plazo de ejecucion no encontrado')

clasificaciones=buscarUNSPSC()
mylist=list(dict.fromkeys(clasificaciones))
for q in mylist:
    if(len(q)>=8):
        print(q)
#shutil.rmtree(rutanueva, ignore_errors=True)
