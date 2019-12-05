from PIL import Image
from os import listdir
from os.path import isfile, join
import os, unidecode, shutil, pytesseract, re, imagehash, cv2, numpy as np
from pdf2image import convert_from_path
from spellchecker import SpellChecker
from detectTables import buscarTablas
from fpdf import FPDF
from PyPDF2 import PdfFileMerger

#Se ingresa la ruta de la carpeta con los archivos de la licitacion y se registran los archivos encontrados en ella

global path
path = "/Users/andalval/Desktop/prueba datalicit/2. SENA DIRECCIÓN GENERAL Dirección Jurídica DG-LP-001-2019/"
archivos = [f for f in listdir(path) if isfile(join(path, f))]
#Se especifica un idioma para realizar una correccion ortografica del texto extraido de los archivos mas adelante

spell = SpellChecker(language='es')
i=1
#Se transforman los archivos con extension PDF a imagen para extraer su contenido. Solo se transforman los archivos en
#cuyo nombre este la palabra 'PLIEGO' o 'Pliego', el resultado es guardado en una imagen con el mismo nombre del archivo original

for x in archivos:
    ruta = path + x
    try:
        os.stat(path+"/Imagenes para analizar")
    except:
        os.mkdir(path+"/Imagenes para analizar")
    rutanueva=path+"/Imagenes para analizar"
    if x.endswith('.pdf') and "PLIEGO" in x or "Pliego" in x:
        pages = convert_from_path(ruta, dpi=200)
        for page in pages:
            filename = x.replace(' ','_') + "-" + str(i) + '.jpg'
            page.save(os.path.join(rutanueva,filename), 'JPEG')
            i=i+1

path = path+"Imagenes para analizar/"
archivos = [f for f in listdir(path) if isfile(join(path, f))]
#cargamos la ruta donde se instala pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
for x in archivos:
    ruta = path + x
    try:
        if '.jpg' in x:
            if "PLIEGO" in x or "Pliego" in x:
                im = Image.open(ruta)
                # Utilizamos el método "image_to_string"
                # Le pasamos como argumento la imagen abierta con Pillow
                try:
                    os.stat(path+"texto"+x.replace(".jpg","")+".txt")
                except:
                    texto = pytesseract.image_to_string(im)
                    texto = unidecode.unidecode(texto)
                    datafile = ''
                    with open(path+"texto"+x.replace(".jpg","")+".txt", "w") as text_file:
                        text_file.write(texto)
        else:
            continue
    except:
        continue
#Metodo para buscar concidencias de acuerdo a palabras clave dentro de las imagenes anteriormente generadas

def buscarCoincidencias(palabra=[], extension=0):
    ocurrencias=[]
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    for x in archivos:
        ruta = path + x.replace(".jpg","")
        #Lee el texto de las imagenes y busca coincidencias con las palabras de parametro
        try:
            with open(path+"texto"+x.replace(".jpg","")+".txt", "r") as text_file:
                datafile = text_file.readlines()
            for i, line in enumerate(datafile):
                for d in palabra:
                    if d in line:
                        #Si encuentra coincidencias las guarda en un arreglo de salida
                        for l in datafile[i-2:i+extension]:
                            ocurrencias.append(l.replace('\n',''))
        except:
            continue
    #Se devuelve el arreglo con los resultados obtenidos
    return ocurrencias

def buscarPresupuesto():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["presupuesto oficial","suma de","PRESUPUESTO OFICIAL","Presupuesto oficial", "Presupuesto Oficial"]
    ocurrencias=buscarCoincidencias(palabra,4)
    results=''
    for j in ocurrencias:
        if '$' in j:
            presupuesto = re.findall(r'\d+\b', j)
            results = ''.join(presupuesto)
            return j

def buscarCodigo():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["LICITACION PUBLICA", "PROCESO CONTRACTUAL", "Licitacion publica", "Proceso contractual"]
    ocurrencias=buscarCoincidencias(palabra,2)
    p=0
    results=''
    for u in ocurrencias:
        if '-' in u:
            results=ocurrencias[p]
        p += 1
    return results

def buscarObjeto():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["OBJETO:","OBJETO","Objeto","Objeto:"]
    ocurrencias=buscarCoincidencias(palabra,9)
    results=''
    for j in ocurrencias:
        if 'CONTRATAR ' in j or 'Contratar 'in j:
            resultados=ocurrencias[ocurrencias.index(j):ocurrencias.index(j)+8]
            results=' '.join(resultados)
        elif 'PRESTAR ' in j or 'Prestar ' in j:
            resultados=ocurrencias[ocurrencias.index(j):ocurrencias.index(j)+8]
            results=' '.join(resultados)
    return results

def buscarPlazo():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["plazo de ejecuci","Plazo de ejecuci", "plazo de ejecucion", "Plazo de ejecucion", "PLAZO DE EJECUCI"]
    ocurrencias=buscarCoincidencias(palabra,3)
    p=0
    results=''
    for j in ocurrencias:
        if 'sera' in j and any(char.isdigit() for char in j):
            fecha = ocurrencias[p:p+4]
            results = ''.join(fecha)
            return results
        p += 1

def buscarUNSPSC():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["UNSPSC","CODIGO UNSPSC","SEGMENTO","Segmento","segmento", "Clasificacion UNSPSC", "CLASIFICACION UNSPSC"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    i=0
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        try:
            if 'jpg' in x:
                if "PLIEGO" in x or "Pliego" in x:
                    im = Image.open(ruta)
                    # Utilizamos el método "image_to_string"
                    # Le pasamos como argumento la imagen abierta con Pillow
                    with open(path+"texto"+x.replace(".jpg","")+".txt", "r") as text_file:
                        datafile = text_file.readlines()
                    for i, line in enumerate(datafile):
                        for d in palabra:
                            if d in line:
                                encontrados=buscarTablas(ruta)
                                for u in encontrados:
                                    texteando=pytesseract.image_to_string(u)
                                    texteando=unidecode.unidecode(texteando)
                                    if any(i.isdigit() for i in texteando) and "Servicios" in texteando or "Clasificacion" in texteando or 'FAMILIA' in texteando or 'Familia' in texteando:
                                        try:
                                            os.stat(path+"/data")
                                        except:
                                            os.mkdir(path+"/data")
                                        os.rename(u,path+r'data/UNSPSC-'+str(i)+'.png')
                                        ocurrencias.append(path+'data/UNSPSC-'+str(i)+'.png')
                                        i += 1
            else:
                continue
        except:
            continue
    dosocurrencias=[]
    for a in ocurrencias:
        for b in ocurrencias:
            try:
                if str(a) is not str(b) and os.path.exists(a) and os.path.exists(b):
                    an = cv2.imread(a)
                    bn = cv2.imread(b)
                    an = cv2.resize(an,(500,300))
                    bn = cv2.resize(bn,(500,300))
                    difference = cv2.subtract(an, bn)    
                    result = not np.any(difference)
                    if result is True:
                        ocurrencias.remove(b)
                        dosocurrencias.append(b)
                    if os.stat(a).st_size < 100000:
                        ocurrencias.remove(a)
                        dosocurrencias.append(a)
            except Exception as e:
                print(e)
                continue
    for i in dosocurrencias:
        if i in ocurrencias:
            dosocurrencias.remove(i)
    for i in dosocurrencias:
        if os.path.exists(i):
            os.remove(os.path.abspath(i))
    if not ocurrencias:
        palabra=["UNSPSC","CODIGO UNSPSC","SEGMENTO","Segmento","segmento", "Clasificacion UNSPSC", "CLASIFICACION UNSPSC", 
            "EXPERIENCIA GENERAL DEL PROPONENTE", "Experiencia general del proponente", "Experiencia del Proponente",
            "EXPERIENCIA DEL PROPONENTE"]
        ocurrencias=buscarCoincidencias(palabra,20)
        p=0
        results=''
        for j in ocurrencias:
            if 'UNSPSC' in j or 'Servicio' in j or 'CODIGO' in j or 'CODIGOS' in j:
                fecha = ocurrencias[p:p+20]
                results = fecha
                pdf = FPDF()
                pdf.add_page()
                pdf.set_xy(0, 0)
                pdf.set_font('arial', 'B', 13.0)
                for i in results:
                    pdf.write(5, str(i))
                    pdf.ln()
                pdf.output(path+'data/UNSPSC.pdf', 'F')
                return results
            p += 1
    for i in ocurrencias:
        if os.path.exists(i) == False:
            ocurrencias.remove(i)
    return ocurrencias

def buscarFinanciera():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["CAPACIDAD FINANCIERA","Capacidad financiera", "Capacidad Financiera","capacidad financiera", 
            "INDICADORES FINANCIEROS", "Indicadores financieros", "HABILITANTES FINANCIEROS", "Habilitantes financieros",
            "Habilitantes Financieros"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        try:
            if 'jpg' in x:
                if "PLIEGO" in x or "Pliego" in x:
                    im = Image.open(ruta)
                    # Utilizamos el método "image_to_string"
                    # Le pasamos como argumento la imagen abierta con Pillow
                    with open(path+"texto"+x.replace(".jpg","")+".txt", "r") as text_file:
                        datafile = text_file.readlines()
                    for i, line in enumerate(datafile):
                        for d in palabra:
                            if d in line:
                                encontrados=buscarTablas(ruta)
                                for u in encontrados:
                                    texteando=pytesseract.image_to_string(u)
                                    texteando=unidecode.unidecode(texteando)
                                    if any(i.isdigit() for i in texteando) and 'Endeudamiento' in texteando or 'ENDEUDAMIENTO' in texteando or 'endeudamiento' in texteando or '%' in texteando:
                                        try:
                                            os.stat(path+"/data")
                                        except:
                                            os.mkdir(path+"/data")
                                        os.rename(u,path+r'data/Financiero-'+str(i)+'.png')
                                        ocurrencias.append(path+'data/Financiero-'+str(i)+'.png')
                                        i += 1
            else:
                continue
        except:
            continue
    dosocurrencias=[]
    for a in ocurrencias:
        for b in ocurrencias:
            try:
                if str(a) is not str(b) and os.path.exists(a) and os.path.exists(b):
                    an = cv2.imread(a)
                    bn = cv2.imread(b)
                    an = cv2.resize(an,(500,300))
                    bn = cv2.resize(bn,(500,300))
                    difference = cv2.subtract(an, bn)    
                    result = not np.any(difference)
                    if result is True:
                        ocurrencias.remove(b)
                        dosocurrencias.append(b)
                    if os.stat(a).st_size < 100000:
                        ocurrencias.remove(a)
                        dosocurrencias.append(a)
            except Exception as e:
                print(e)
                continue
    for i in dosocurrencias:
        if (i in ocurrencias):
            dosocurrencias.remove(i)
    for i in dosocurrencias:
        if(os.path.exists(i)):
            os.remove(os.path.abspath(i))
    if not ocurrencias:
        ocurrencias=buscarCoincidencias(palabra,10)
        p=0
        results=''
        for j in ocurrencias:
            if 'INDICE DE LIQUIDEZ' in j or 'Indice de liquidez' in j or 'Indice de Liquidez' in j or 'Liquidez' in j:
                fecha = ocurrencias[p:p+20]
                results = fecha
                pdf = FPDF()
                pdf.add_page()
                pdf.set_xy(0, 0)
                pdf.set_font('arial', 'B', 13.0)
                for i in results:
                    pdf.write(5, str(i))
                    pdf.ln()
                pdf.output(path+'data/Financieros.pdf', 'F')
                return results
            p += 1
    for i in ocurrencias:
        if os.path.exists(i) == False:
            ocurrencias.remove(i)
    return ocurrencias

def buscarOrganizacional():
    archivos = [f for f in listdir(path) if isfile(join(path, f))]
    palabra=["CAPACIDAD DE ORGANIZACION","capacidad de organizacion","CAPACIDAD ORGANIZACIONAL",
            "Capacidad organizacional", "Capacidad Organizacional", 'INDICADORES DE CAPACIDAD ORGANIZACIONAL', 
            "Indicadores de capacidad organizacional", "HABILITANTES ORGANIZACIONALES", "Habilitantes Organizacionales",
            "Habilitantes organizacionales", "Indices Financieros", "INDICES FINANCIEROS", "RENTABILIDAD DEL ACTIVO",
            "Rentabilidad del Activo", "Rentabilidad Del Activo"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = path + x
        try:
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
                            encontrados=buscarTablas(ruta)
                            for u in encontrados:
                                texteando=pytesseract.image_to_string(u)
                                texteando=unidecode.unidecode(texteando)
                                if any(i.isdigit() for i in texteando) and "RENTABILIDAD " in texteando or "Rentabilidad " in texteando or "Rentabilidad " in texteando or 'Rentabilidad ' in texteando:
                                    try:
                                        os.stat(path+"/data")
                                    except:
                                        os.mkdir(path+"/data")
                                    os.rename(u,path+r'data/Organizacional-'+str(i)+'.png')
                                    ocurrencias.append(path+'data/Organizacional-'+str(i)+'.png')
                                    i += 1
            else:
                continue
        except:
            continue
    dosocurrencias=[]
    for a in ocurrencias:
        for b in ocurrencias:
            try:
                if str(a) is not str(b) and os.path.exists(a) and os.path.exists(b):
                    an = cv2.imread(a)
                    bn = cv2.imread(b)
                    an = cv2.resize(an,(500,300))
                    bn = cv2.resize(bn,(500,300))
                    difference = cv2.subtract(an, bn)    
                    result = not np.any(difference)
                    if result is True:
                        ocurrencias.remove(b)
                        dosocurrencias.append(b)
                    if os.stat(a).st_size < 100000:
                        ocurrencias.remove(a)
                        dosocurrencias.append(a)
            except Exception as e:
                print(e)
                continue
    for i in dosocurrencias:
        if (i in ocurrencias):
            dosocurrencias.remove(i)
    for i in dosocurrencias:
        if(os.path.exists(i)):
            os.remove(os.path.abspath(i))
    if not ocurrencias:
        ocurrencias=buscarCoincidencias(palabra,20)
        p=0
        results=''
        for j in ocurrencias:
            if 'RENTABILIDAD' in j or 'Rentabilidad' in j or 'rentabilidad' in j:
                fecha = ocurrencias[p:p+10]
                results = fecha
                pdf = FPDF()
                pdf.add_page()
                pdf.set_xy(0, 0)
                pdf.set_font('arial', 'B', 13.0)
                for i in results:
                    pdf.write(5, str(i))
                    pdf.ln()
                pdf.output(path+'data/Organizacionales.pdf', 'F')
                return results
            p += 1
    for i in ocurrencias:
        if os.path.exists(i) == False:
            ocurrencias.remove(i)
    return ocurrencias

resultado=[]
try:
    valor = buscarPresupuesto()
    resultado.append("Presupuesto: "+valor)
    #print(valor)
except Exception as e:
    print(e)
    print("Valor no encontrado")
try:
    codigo=buscarCodigo()
    resultado.append("Codigo: "+codigo)
    #print(codigo)
except Exception as e:
    print(e)
    print("Codigo no encontrado")
try:
    objeto=buscarObjeto()
    pobjeto=objeto.split()
    h=''
    for k in pobjeto:
        h=h+' '+spell.correction(k)
    resultado.append("Objeto: "+h)
    #print(h)
except Exception as e:
    print(e)
    print("Objeto no encontrado")
try:
    h=''
    ejecucion=buscarPlazo()
    try:
        pejecucion=ejecucion.split()
        for k in pejecucion:
            h=h+' '+spell.correction(k)
        resultado.append("Plazo: "+h)
    except Exception as e:
        print(e)
        print('Plazo de ejecucion no encontrado')
    #print(h)
except Exception as e:
    print(e)
    print('Plazo de ejecucion no encontrado')

try:
    finales=buscarUNSPSC()
    unspsc=list(dict.fromkeys(finales))
    pdf = FPDF()
    pdf.set_auto_page_break(0)
    for a in unspsc:
        pdf.add_page('L')
        pdf.image(a,0,0,300,200)
    pdf.output(path+'data/UNSPSC.pdf')
    resultado.append(path+'data/UNSPSC.pdf')
    #print(unspsc)
except Exception as e:
        print(e)
        print("Clasificacion UNSPSC no encontrada")
try:
    finales=buscarFinanciera()
    financieros=list(dict.fromkeys(finales))
    if not financieros:
        print('Datos financieros no encontrados')
    else:
        try:
            pdf = FPDF()
            for a in financieros:
                pdf.add_page('L')
                pdf.image(a,0,0,300,200)
            pdf.output(path+'data/Financieros.pdf')
            resultado.append(path+'data/Financieros.pdf')
        except Exception as e:
            print(e)
            resultado.append(financieros)
        #print(financieros)
except Exception as e:
    print(e)
    print("Datos financieros no encontrados")
try:
    finales=buscarOrganizacional()
    organizacionales=list(dict.fromkeys(finales))
    if not organizacionales:
        print('Datos organizacionales no encontrados')
    else:
        try:
            pdf = FPDF()
            for a in organizacionales:
                pdf.add_page('L')
                pdf.image(a,0,0,300,200)
            pdf.output(path+'data/Organizacionales.pdf')
            resultado.append(path+'data/Organizacionales.pdf')
        except:
            resultado.append(organizacionales)
        #print(organizacionales)
except Exception as e:
    print(e)
    print("Datos organizacionales no encontrados")

merger = PdfFileMerger()

merger.append(path+'data/UNSPSC.pdf')
merger.append(path+'data/Financieros.pdf')
merger.append(path+'data/Organizacionales.pdf')

merger.write(path+'data/Finales.pdf')
merger.close()
print(resultado)