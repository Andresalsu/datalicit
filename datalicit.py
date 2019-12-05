from PIL import Image
from os import listdir
from os.path import isfile, join
import os, unidecode, pytesseract, imagehash, cv2, numpy as np
from pdf2image import convert_from_path
from detectTables import buscarTablas
from fpdf import FPDF
from PyPDF2 import PdfFileMerger, PdfFileReader

#Se declaran variables globales para la carpeta y la ruta del PDF a estudiar
global pathb
pathb=''
global folder
folder = ''
global carpeta
carpeta = ''
#Se especifica la ruta de Pytesseract, libreria utilizada para la identificacion de texto en imagenes
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'

#En el siguiente metodo se inicia la conversion del PDF por paginas. Se toma cada pagina y se convierte en imagen,
#esto con el fin de poder tomar todo el texto sin importar si el PDF es un escaner o no. Luego se usan los metodos
#de busqueda de codigos unspsc, datos financieros y datos organizacionales

def convertirPDF(path=''):
    pathb = os.path.dirname(path)+'/'+os.path.basename(path)
    folder=os.path.dirname(pathb)
    carpeta=folder+'/'+os.path.splitext(os.path.basename(pathb))[0]
    pages=convert_from_path(pathb.replace('_',' '))
    i=0
    paginas = []
    try:
        if(os.stat(carpeta+'/Finales.jpg')):
            os.remove(carpeta+'/Finales.jpg')
        if(os.stat(carpeta+'/Finales.txt')):
            os.remove(carpeta+'/Finales.txt')
        if(os.stat(carpeta+'/Finales.pdf')):
            os.remove(carpeta+'/Finales.pdf')
    except:
        pass
    #Se crea una carpeta con el nombre del archivo PDF
    try:
        os.stat(carpeta)
    except:
        os.mkdir(carpeta)
    #Se toma cada pagina del PDF y se convierte en imagen con formato .jpg usando la libreria pdf2image
    for page in pages:
        filename = carpeta.replace('_',' ') +'/'+ os.path.splitext(os.path.basename(pathb))[0].replace('_',' ')+"-" + str(i) + '.jpg'
        page.save(filename, 'JPEG')
        paginas.append(filename.replace('_',' '))
        i=i+1
    #Se toma cada imagen generada y se extrae su texto usando reconocimiento optico de caracteres OCR
    for j in paginas:
        im = Image.open(j.replace('_',' '))
        try:
            os.stat(j.replace(".jpg","")+".txt")
        except FileNotFoundError as e:
            texto = pytesseract.image_to_string(im)
            texto = unidecode.unidecode(texto)
            datafile = ''
            with open(j.replace(".jpg","").replace('_',' ')+".txt", "w") as text_file:
                text_file.write(texto)
            continue
    #Se envia la ruta de los archivos de texto generados para buscar los datos en cada metodo. Al final todos los resultados
    #se guardan en un PDF relacionado con los datos extraidos.
    finales=buscarUNSPSC(carpeta+'/')
    unspsc=list(dict.fromkeys(finales))
    pdf = FPDF()
    try:
        for a in unspsc:
            pdf.add_page('L')
            pdf.image(a,0,0,300,200)
        pdf.output(carpeta+'/UNSPSC.pdf')
    except:
        pass

    finales=buscarFinanciera(carpeta+'/')
    financieros=list(dict.fromkeys(finales))
    if not financieros:
        print('Datos financieros no encontrados')
    else:
        try:
            pdf = FPDF()
            for a in financieros:
                pdf.add_page('L')
                pdf.image(a,0,0,300,200)
            pdf.output(carpeta+'/Financieros.pdf')
        except Exception as e:
            print(e)
    try: 
        finales=buscarOrganizacional(carpeta+'/')
        organizacionales=list(dict.fromkeys(finales))
        if not organizacionales:
            print('Datos organizacionales no encontrados')
        else:
            try:
                pdf = FPDF()
                for a in organizacionales:
                    pdf.add_page('L')
                    pdf.image(a,0,0,300,200)
                pdf.output(carpeta+'/Organizacionales.pdf')
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
        print("Datos organizacionales no encontrados")

    #Una vez encontrados los datos, las tablas extraidas se concatenan en un solo archivo de imagen para ser devuelto
    try:
        onlyfiles = [f for f in listdir(carpeta) if isfile(join(carpeta, f))]
        imagenes = []
        for j in onlyfiles:
            if j.endswith('.png'):
                imagenes.append(carpeta+'/'+j)
        imgs = [Image.open(i) for i in imagenes]
        min_img_width = min(i.width for i in imgs)

        total_height = 0
        for i, img in enumerate(imgs):
            # If the image is larger than the minimum width, resize it
            if img.width > min_img_width:
                imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
            total_height += imgs[i].height

        # I have picked the mode of the first image to be generic. You may have other ideas
        # Now that we know the total height of all of the resized images, we know the height of our final image
        img_merge = Image.new(imgs[0].mode, (min_img_width, total_height))
        y = 0
        for img in imgs:
            img_merge.paste(img, (0, y))
            y += img.height
        
        img_merge.save(carpeta+'/Finales.jpg')
        #Adicionalmente, se guardan los resultados en un PDF para mejor usabilidad
        merger = PdfFileMerger()

        try:
            merger.append(PdfFileReader(carpeta+'/UNSPSC.pdf'))
        except:
            pass
        try:
            merger.append(PdfFileReader(carpeta+'/Financieros.pdf'))
        except:
            pass
        try:
            merger.append(PdfFileReader(carpeta+'/Organizacionales.pdf'))
        except:
            pass

        merger.write(carpeta+'/Finales.pdf')
        merger.close()

        #Finalmente, se devuelve la ruta del archivo de imagen con los resultados
        return os.path.abspath(carpeta+'/Finales.jpg')
    except Exception as e:
        print(e)

#Este metodo busca coincidencias en base a palabras clave y a una longitud de busqueda dentro del texto
def buscarCoincidencias(palabra=[], extension=0, folder=''):
    ocurrencias=[]
    archivos = [f for f in listdir(folder) if isfile(join(folder, f))]
    for x in archivos:
        ruta = folder + x.replace(".jpg","")
        #Lee el texto de las imagenes y busca coincidencias con las palabras de parametro
        try:
            with open(folder+x.replace(".jpg","")+".txt", "r") as text_file:
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

#Este metodo busca codigos unspsc contenidos dentro del PDF y los guarda dentro de imagenes PNG y un PDF general
def buscarUNSPSC(folder=''):
    print('Entrando a UNSPSC')
    archivos = [f for f in listdir(folder) if isfile(join(folder, f))]
    palabra=["UNSPSC","CODIGO UNSPSC","SEGMENTO","Segmento","segmento", "Clasificacion UNSPSC", "CLASIFICACION UNSPSC"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    i=0
    # Abrimos la imagen
    for x in archivos:
        ruta = folder + x
        try:
            if '.jpg' in x:
                im = Image.open(ruta)
                # Utilizamos el método "image_to_string"
                # Le pasamos como argumento la imagen abierta con Pillow
                with open(folder+x.replace('.jpg','')+".txt", "r") as text_file:
                    datafile = text_file.readlines()
                for i, line in enumerate(datafile):
                    for d in palabra:
                        if d in line:
                            #Se utiliza el script buscarTablas para encontrar y extraer las tablas relacionadas
                            encontrados=buscarTablas(ruta)
                            #Los resultados se escanean con la libreria Pytesseract y se comprueba que lo encontrado es correcto
                            for u in encontrados:
                                texteando=pytesseract.image_to_string(u)
                                texteando=unidecode.unidecode(texteando)
                                #Si hay coincidencias se guarda el resultado en una imagen
                                if any(i.isdigit() for i in texteando) and "Servicios" in texteando or "Clasificacion" in texteando or 'FAMILIA' in texteando or 'Familia' in texteando:
                                    os.rename(u,folder+r'UNSPSC-'+str(i)+'.png')
                                    ocurrencias.append(folder+'UNSPSC-'+str(i)+'.png')
                                    i += 1
        except Exception as e:
            continue
    dosocurrencias=[]
    #En caso de haber repetidos resultados o resultados no relacionados, se eliminan para ahorrar analisis y espacio
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
    #Como ultima alternativa, en caso de no encontrar cuadros con la informacion, se busca el texto y se extrae el texto relacionado
    if not ocurrencias:
        palabra=["UNSPSC","CODIGO UNSPSC","SEGMENTO","Segmento","segmento", "Clasificacion UNSPSC", "CLASIFICACION UNSPSC", 
            "EXPERIENCIA GENERAL DEL PROPONENTE", "Experiencia general del proponente", "Experiencia del Proponente",
            "EXPERIENCIA DEL PROPONENTE"]
        ocurrencias=buscarCoincidencias(palabra, 20, folder)
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
                pdf.output(folder+'UNSPSC.pdf', 'F')
                #Se toma cada pagina del PDF y se convierte en imagen con formato .jpg usando la libreria pdf2image
                pages=convert_from_path(folder+'UNSPSC.pdf')
                paginas=[]
                u=0
                for page in pages:
                    filename = "UNSPSC"+"-" + str(u) + '.png'
                    page.save(folder+filename.replace('_',' '), 'PNG')
                    results.append(folder+filename.replace('_',' '))
                    u=u+1
                return results
            p += 1
    #Se eliminan errores y se devuelve la ruta con los resultados obtenidos
    for i in ocurrencias:
        if os.path.exists(i) == False:
            ocurrencias.remove(i)
    return ocurrencias

#Este metodo busca data financiera contenidos dentro del PDF y los guarda dentro de imagenes PNG y un PDF general
def buscarFinanciera(folder=''):
    print('Entrando a Financiera')
    archivos = [f for f in listdir(folder) if isfile(join(folder, f))]
    palabra=["CAPACIDAD FINANCIERA","Capacidad financiera", "Capacidad Financiera","capacidad financiera", 
            "INDICADORES FINANCIEROS", "Indicadores financieros", "HABILITANTES FINANCIEROS", "Habilitantes financieros",
            "Habilitantes Financieros"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    for x in archivos:
        ruta = folder + x
        try:
            if x.endswith('.jpg'):
                im = Image.open(ruta)
                # Utilizamos el método "image_to_string"
                # Le pasamos como argumento la imagen abierta con Pillow
                with open(folder+x.replace('.jpg','')+".txt", "r") as text_file:
                    datafile = text_file.readlines()
                for i, line in enumerate(datafile):
                    for d in palabra:
                        if d in line:
                            #Se utiliza el script buscarTablas para encontrar y extraer las tablas relacionadas
                            encontrados=buscarTablas(ruta)
                            #Los resultados se escanean con la libreria Pytesseract y se comprueba que lo encontrado es correcto
                            for u in encontrados:
                                texteando=pytesseract.image_to_string(u)
                                texteando=unidecode.unidecode(texteando)
                                #Si hay coincidencias se guarda el resultado en una imagen
                                if any(i.isdigit() for i in texteando) and 'Endeudamiento' in texteando or 'ENDEUDAMIENTO' in texteando or 'endeudamiento' in texteando or '%' in texteando:
                                    os.rename(u,folder+r'Financiero-'+str(i)+'.png')
                                    ocurrencias.append(folder+'Financiero-'+str(i)+'.png')
                                    i += 1
            else:
                continue
        except:
            continue
    dosocurrencias=[]
    #En caso de haber repetidos resultados o resultados no relacionados, se eliminan para ahorrar analisis y espacio
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
    #Como ultima alternativa, en caso de no encontrar cuadros con la informacion, se busca el texto y se extrae el texto relacionado
    if not ocurrencias:
        ocurrencias=buscarCoincidencias(palabra,10, folder)
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
                pdf.output(folder+'Financieros.pdf', 'F')
                pages=convert_from_path(folder+'Financieros.pdf')
                paginas=[]
                u=0
                for page in pages:
                    filename = "Financieros"+"-" + str(u) + '.png'
                    page.save(folder+filename.replace('_',' '), 'PNG')
                    results.append(folder+filename.replace('_',' '))
                    u=u+1
                return results
            p += 1
    #Se eliminan errores y se devuelve la ruta con los resultados obtenidos
    for i in ocurrencias:
        if os.path.exists(i) == False:
            ocurrencias.remove(i)
    return ocurrencias

#Este metodo busca data organizacional contenidos dentro del PDF y los guarda dentro de imagenes PNG y un PDF general
def buscarOrganizacional(folder=''):
    print('Entrando a organizacional')
    archivos = [f for f in listdir(folder) if isfile(join(folder, f))]
    palabra=["CAPACIDAD DE ORGANIZACION","capacidad de organizacion","CAPACIDAD ORGANIZACIONAL",
            "Capacidad organizacional", "Capacidad Organizacional", 'INDICADORES DE CAPACIDAD ORGANIZACIONAL', 
            "Indicadores de capacidad organizacional", "HABILITANTES ORGANIZACIONALES", "Habilitantes Organizacionales",
            "Habilitantes organizacionales", "Indices Financieros", "INDICES FINANCIEROS", "RENTABILIDAD DEL ACTIVO",
            "Rentabilidad del Activo", "Rentabilidad Del Activo"]
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.0/bin/tesseract'
    ocurrencias=[]
    # Abrimos la imagen
    try:
        for x in archivos:
            ruta = folder + x
            try:
                if ruta.endswith('.jpg'):
                    im = Image.open(ruta)
                    # Utilizamos el método "image_to_string"
                    # Le pasamos como argumento la imagen abierta con Pillow
                    try:
                        os.stat(folder+x.replace('.jpg','')+".txt")
                    except Exception as e:
                        print(e)
                        texto = pytesseract.image_to_string(im)
                        texto=unidecode.unidecode(texto)
                        datafile = ''
                        with open(folder+x.replace('.jpg','')+".txt", "w") as text_file:
                            text_file.write(texto.encode().decode())
                    try:
                        with open(folder+x.replace('.jpg','')+".txt", "r") as text_file:
                            datafile = text_file.readlines()
                        for i, line in enumerate(datafile):
                            for d in palabra:
                                if d in line:
                                    #Se utiliza el script buscarTablas para encontrar y extraer las tablas relacionadas
                                    encontrados=buscarTablas(ruta)
                                    #Los resultados se escanean con la libreria Pytesseract y se comprueba que lo encontrado es correcto
                                    for u in encontrados:
                                        texteando=pytesseract.image_to_string(u)
                                        texteando=unidecode.unidecode(texteando)
                                        #Si hay coincidencias se guarda el resultado en una imagen
                                        if any(i.isdigit() for i in texteando) and "RENTABILIDAD " in texteando or "Rentabilidad " in texteando or "Rentabilidad " in texteando or 'Rentabilidad ' in texteando:
                                            os.rename(u,folder+r'Organizacional-'+str(i)+'.png')
                                            ocurrencias.append(folder+'Organizacional-'+str(i)+'.png')
                                            i += 1
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)
        pass
    dosocurrencias=[]
    #Como ultima alternativa, en caso de no encontrar cuadros con la informacion, se busca el texto y se extrae el texto relacionado
    if not ocurrencias:
        ocurrencias=buscarCoincidencias(palabra,20,folder)
        p=0
        results=''
        for j in ocurrencias:
            try:
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
                    pdf.output(folder+'Organizacionales.pdf', 'F')
                    pages=convert_from_path(folder+'Organizacionales.pdf')
                    paginas=[]
                    u=0
                    for page in pages:
                        filename = "Organizacionales"+"-" + str(u) + '.png'
                        page.save(folder+filename.replace('_',' '), 'PNG')
                        results.append(folder+filename.replace('_',' '))
                        u=u+1
                    return results
            except Exception as e:
                print(e)
                print('Aqui esta el error 2')
                continue
            p += 1
    else:
        #En caso de haber repetidos resultados o resultados no relacionados, se eliminan para ahorrar analisis y espacio
        for i in ocurrencias:
            if os.path.exists(i) == False:
                ocurrencias.remove(i)
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
    #Se eliminan errores y se devuelve la ruta con los resultados obtenidos
        for i in dosocurrencias:
            if(os.path.exists(i)):
                os.remove(os.path.abspath(i))
    return ocurrencias

#convertirPDF('/Users/andalval/Desktop/prueba datalicit/7. FONTIC FTIC-LP-03-2019/PLIEGO DEFINITIVO FTIC-LP-03-2019.pdf')