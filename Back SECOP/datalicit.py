import json as json
import csv
import pandas as pd
from sodapy import Socrata

#Implementacion KMP
def KMPSearch(pat, txt):
    if pat is "":
        return True
    M = len(pat) 
    N = len(txt) 
    lps = [0]*M 
    j = 0
    computeLPSArray(pat, M, lps) 
    i = 0 
    while i < N: 
        if pat[j] == txt[i]: 
            i += 1
            j += 1
  
        if j == M: 
            j = lps[j-1] 
            return True
        elif i < N and pat[j] != txt[i]: 
            if j != 0: 
                j = lps[j-1] 
            else:
                i += 1
                if i == N:
                    return False
        
def computeLPSArray(pat, M, lps): 
    len = 0 
    lps[0] 
    i = 1
    while i < M: 
        if pat[i]== pat[len]: 
            len += 1
            lps[i] = len
            i += 1
        else: 
            if len != 0: 
                len = lps[len-1] 
            else: 
                lps[i] = 0
                i += 1


scd1="Soluciones ciudadanos digitales"
scd = ["aarpeta ciudadana", "autenticacion digital","autenticacion electronica",
      "certificados digitales","firmas digitales","firma digital",
       "servicios de certificacion digital","carpeta electronica",
      "interoperabilidad","x-road","x road","estampado cronologico"
      "sellado de tiempo","Servicios ciudadanos digitales"]

sem1= "Soluciones con enfoque misional"
sem = ["realizacion de eventos","eventos institucionales","organizacion y coordinacion integral de los eventos"]

sci1="Soluciones ciudades inteligentes"
sci = ["smartcities","semaforos inteligentes"]

sdp1="Soluciones de participacion"
sdp = ["votaciones","consultas ciudadanas"]

sgd1="Soluciones en gestion documental"
sgd = ["gestion de archivo","digitalizacion de documentos","indexacion de documentos"
      "gestion documental","documental","almacenamiento","administracion documental integral",
       "digitalizacion","sistema documental","bpo"]

oti1="Outsourcing TI"
oti = ["procesos con dos o mas componentes diversos de los numerales 6"]

dtc1="Datacenter"
dtc = ["data center, back up, centro de datos, migracion de datos"]

ntk1="Networking"
ntk = ["redes lan y/o wan, cableado", "switch", "switches", "networking",
      "servicio de canales terrestres","satelites e internet"]

cmc1="Comunicaciones"
cmc = ["videoconferencias","telecomunicaciones","voz y datos", "video y seguridad"
      "red de datos","inalambricas","seguridad perimetral"]

sgt1="Servicio de gestion de ti"
sgt = ["mesa de ayuda","help desktop","contaccenter","centro de contacto",
      "infraestructura tecnologica","plataforma tecnologica","sistemas operativos",
      "aplicacion","autentificacion y cifrado","software de monitoreo y control",
       "pruebas de infraestructura y aplicacion","bases de datos"]
eyd1="Equipos y dispositivos"
eyd = ["computadores","escritorios","mouse","equipos y perifericos"]

imi1="Impresion inteligente"
imi = ["print","impresion","fotocopiadoras"]

url_procesos = []


#Filtro primero por entidades y luego por referencia de proceso
# Retorna una tupla de 3 con el portafolio del proceso, el proceso de referecia y el link del proceso
def filterLicit(entidad, ref_proc):
    entidad=entidad.lower()
    ref_proc=ref_proc.lower()
    ruta =("/users/hugherli/Documents/GitHub/fulldatos.csv")
    with open(ruta, encoding="utf-8") as ff:
        csv_reader = csv.reader(ff, delimiter=',')
        for row in csv_reader:
            #Descripcion
            des = row[10].lower()
            #Id del proceso
            id_proc= row[28]
            #url para la descarga de los archivos
            url = row[50]
            #Entidad que publica la licitacion
            enti = row[12].lower()
            #codigo de referencia del proceso
            ref = row[44].lower()
            #presupuesto base para la licitacion
            presupuesto = row[39]
            #Modalidad de contratacion
            modalidad = row[31]
            #Duracion de la licitacion en la medida que salga en la columna 49
            duracion = row[11]+" "+row[49]
            #Contratista 
            contratatista = row[35]

            if presupuesto.split(".")[0].isdigit():
                
                if int(presupuesto.split(".")[0]) < 100000000:
                    continue
            
            if KMPSearch(entidad ,enti):
                if KMPSearch(ref_proc, ref):
                    
                    for kw in scd:
                        if KMPSearch(kw, des):
                            url_procesos.append((scd1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in sem:
                        if KMPSearch(kw, des):
                            url_procesos.append((sem1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in sci:
                        if KMPSearch(kw, des):
                            url_procesos.append((sci1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in sdp:
                        if KMPSearch(kw, des):
                            url_procesos.append((sdp1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break        
                    for kw in sgd:
                        if KMPSearch(kw, des):
                            url_procesos.append((sgd1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break  
                    for kw in oti:
                        if KMPSearch(kw, des):
                            url_procesos.append((oti1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break  
                    for kw in dtc:
                        if KMPSearch(kw, des):
                            url_procesos.append((dtc1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break  
                    for kw in ntk:
                        if KMPSearch(kw, des):
                            url_procesos.append((ntk1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in cmc:
                        if KMPSearch(kw, des):
                            url_procesos.append((cmc1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in sgt:
                        if KMPSearch(kw, des):
                            url_procesos.append((sgt1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in eyd:
                        if KMPSearch(kw, des):
                            url_procesos.append((eyd1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                            break
                    for kw in imi:
                        if KMPSearch(kw, des):
                            url_procesos.append((imi1,des,enti,modalidad,contratatista,ref,presupuesto,duracion,url))
                else:
                    continue
            else:
                continue
    
    for x in url_procesos:
        somedict = {"portafolio":[ x[0] for x in url_procesos ],
                    "descripcion":[ x[1] for x in url_procesos ],
                    "entidad":[ x[2] for x in url_procesos ],
                    "modalidad":[ x[3] for x in url_procesos ],
                    "contratista":[ x[4] for x in url_procesos ],
                   "ref_proceso":[ x[5] for x in url_procesos ],
                    "presupuesto":[ x[6] for x in url_procesos ],
                    "duracion":[ x[7] for x in url_procesos ],
                   "url_descarga":[ x[8] for x in url_procesos]}
    return somedict
