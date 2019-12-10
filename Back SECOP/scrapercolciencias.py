import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import smtplib

url = 'https://www.colciencias.gov.co/convocatorias/todas'
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

#Rango de 1 a 6
for x in range(1,6):
    cont = 0
    
    #De aqui saco el href para el vinculo
    pre2 = soup.findAll("tr")[x]
    lineas2 = str(pre2).split("\n")
    
    #De aqui saco los campos
    pre = soup.findAll("tr")[x].text
    lineas = str(pre).split("\n")
    
    #Numero de referencia
    num=""
    #Titulo de la convocatoria
    tit=""
    #Descripcion de la convocatoria
    des=""
    #Total de recursos
    tot=""
    #Fecha de apertura
    fec=""
    #Fecha resultados preliminares 
    fef=""
    #Fecha resultados finales
    fff=""
    
    #toma la pagina dentro del nombre de la convocatoria
    url2 = "https://www.colciencias.gov.co"+str(lineas2[4]).split("href")[1][2:12]
    lineaDentro = extracHyper(url2)
    fef = lineaDentro.split(",")[1].replace(",",";")
    fff = lineaDentro.split(",")[2].replace(",",";")
    
    for linea in lineas:
        
        if linea is not "" and cont is 0:
            num = linea.replace(',',' ')
            cont = 1
            continue
        if linea is not "" and cont is 1:
            tit = linea.replace(',',' ')
            cont = 2
            continue
        if linea is not "" and cont is 2:
            des = linea.replace(',',' ')
            cont = 3
            continue
        if linea is not "" and cont is 3:
            tot = linea.replace(',',' ')
            cont = 4
            continue
        if linea is not "" and cont is 4:
            fec = linea.replace(',',' ')
            cont = 0
            break
    
    #Enviando el correo, se guarda la ultima convocaatoria que fue enviada y cada vez que se ejecuta se verifica 
    #y envia en caso tal
    
    f = open("text.txt", "r")
    ultimo = f.read()
    ultimo = int(ultimo)
    f.close()
    
    if int(num)-ultimo > 0:
        #cantidad de convocatorias nuevas
        numerito = int(num)-ultimo
        f = open("text.txt","w")
        print(numerito)
        for x in range(1,numerito+1):
            #Actualizo la ultima convocatoria
            nuevaCon = ultimo+x
            print(nuevaCon)
            f.write(str(nuevaCon))
            
            #Eliminar espacios
            num=num.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            tit=tit.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            des=des.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            tot=tot.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            fec=fec.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            fef=fef.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            fff=fff.replace("  ","").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            
            #Envio el correo electronico con la nueva convocatoria
            subject = "Nueva convocatoria en Colciencias"
            mes = "Se encontro una nueva convocatoria en la pagina de ColCiencias\n"
            mesFul = "Subject: {}\n\n{}\nTitulo: {}\n\nDescripcion: {}\n\nRecursos: {}\n\nFecha de apertura: {}\n\n Fecha de resultados preliminares: {}\n\nFecha de resultados finales:{}\n\nURL: {}".format(subject,mes,tit,des,tot,fec,fef,fff,url2)
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            #Credenciales
            sender = "colcarvajal@gmail.com"
            password = "Carvajal123col"
            server.login(sender,password)

            destinatario = "juan.uribem@carvajal.com"
            server.sendmail(sender,destinatario,mesFul)
            server.quit()
            
        #Se cierra el server de envio de correos
        
        f.close()
        superHugo = num+","+tit+","+des+","+tot+","+fec+","+fef+","+fff+"\n"
        

def extracHyper(url2):
    response = requests.get(url2)
    soup = BeautifulSoup(response.text, "html.parser")

    info = soup.findAll('tr')
    cont=0
    otro=[]
    con2=""

    for x in range(2,4):
        lineas = info[x].text.split("\n")
        ' '.join(lineas).split()

        for linea in lineas:
            linea= linea.replace(" ","")

            if "Cierre" in linea or linea is "" or "Publicaciónderesultadospreliminares" in linea or linea is " ":
                continue
            else:
                if len(linea) > 3:
                    con2=con2+","+linea
                    
    return con2