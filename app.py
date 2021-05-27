
#Importamos lo que vamos a necesitar de flask
from flask import Flask, render_template,abort,request
#Importamos la librería request
import requests
# Importamos la libreria os
import os 
# Importamos json
import json
#Importar las fechas
from datetime import datetime
#Abrimos el fichero json donde están los paises que quiero que aparezca en mi desplegable
#y lo guardamos en infoÇ_paises
with open("paises.json") as fichero:
    info_paises=json.load(fichero)

# Definimos la variable app por Flask
app = Flask(__name__)
#Guardamos la url base
url_base="https://app.ticketmaster.com/discovery/v2/"

@app.route('/',methods=["GET","POST"])
def eventos():
    #En una variable key, guardamos por el diccionario os.environ nuestra key
    key=os.environ["apikey"]
    #La palabra clave la sacamos del formulario del index.html
    palabra_clave=request.form.get("artista")
    #Cogemos el país seleccionado en el formulario
    pais=request.form.get("pais")
    #Inicializamos la paginas:
    #Creamos el diccionario con los parámetros necesarios
    payload = {'apikey':key,'keyword':palabra_clave,'countryCode':pais}
    #Guardamos la petición en una variable(urlbase + diccionario con parametros)
    r=requests.get(url_base+'events',params=payload)

    #Guardamos los paises a partir del fichero json, de forma que nos quedamos solo con los codigos de los paises
    lista_paises=[]
    for i in info_paises:
        lista_paises.append(str(i[:2]))

	#Comprobamos que la petición genera un 200
    if r.status_code == 200:
        #Guardamos el contenido de la petición1 
        contenido = r.json()
        #Si el método por el que se accede es GET devuelve la página principal con la lista de paises para el desplegable.
        if request.method=="GET":
            return render_template("index.html",paises=lista_paises)
        #Si el método por el que se accede es un POST cogemos la información dependiendo de los parametros indicados por el usuario.
        else:
            try:
                palabra_clave=request.form.get("artista")
            except:
                abort(404)

            #Recogemos los parámetros del formulario
            pais=request.form.get("pais")
            palabra_clave=request.form.get("artista")
			
	        #Si no existe contenido devuelve un mensaje
            noms=[]
            if "_embedded" not in contenido:
                mensaje=("No tenemos eventos disponibles para esa busqueda. Vuelve a intentarlo")
                return render_template("index.html",mensaje=mensaje,palabra_clave=palabra_clave,paises=lista_paises)
            else:
			    #Creamos las listas que necesitamos
                nombres=[]
                fechas=[]
                horas=[]
                salas=[]
                direccion=[]
                ciudades=[]
                paises=[]
                urls=[]
                urls_sala=[]
                fechas_cambiadas=[]
                fecha_str=[]
                identificadores=[]
                #Contabilizamos el número de coincidencias
                coincidencias=0
                pais=request.form.get("pais")
                #Guardar contenido en listas
                for elem in contenido["_embedded"]["events"]:
                    #IDENTIFICADORES
                    identificadores.append(elem["id"])
                    #NOMBRES
                    nombres.append(elem["name"])
                    #CIUDADES
                    ciudades.append(elem["_embedded"]["venues"][0]["city"]["name"])
                    #PAISES
                    paises.append(elem["_embedded"]["venues"][0]["country"]["name"])
                    #SALAS
                    if "name" in elem["_embedded"]["venues"][0]:
                        salas.append(elem["_embedded"]["venues"][0]["name"])
                    else:
                        salas.append("-")
                    #DIRECCIONES
                    if "address" in elem["_embedded"]["venues"][0]:
                        direccion.append(elem["_embedded"]["venues"][0]["address"]["line1"])
                    else:
                        direccion.append("-")
                    #FECHAS CON CAMBIO DE FORMATO
                    fechas.append(elem["dates"]["start"]["localDate"])
                    for fecha in fechas:
                        fechas_cambiadas.append(datetime.strptime(fecha, '%Y-%m-%d'))
                    for fecha in fechas_cambiadas:
                        fecha_str.append(datetime.strftime(fecha, '%d/%m/%Y'))
                    #HORAS: A veces la hora no esta especificada así que nos aseguramos de ello.
                    if "localTime" in elem["dates"]["start"]:
                        horas.append(elem["dates"]["start"]["localTime"])
                    else:
                        horas.append("-")
                    #URLS
                    urls.append(elem["url"])
                    if elem["url"]:
                        coincidencias=coincidencias+1
                    if "url" in elem["_embedded"]["venues"][0]:
                        urls_sala.append(elem["_embedded"]["venues"][0]["url"])
                    else:
                        urls_sala.append("-")
                        
                filtro=zip(nombres,paises,ciudades,salas,direccion,fecha_str,horas,urls,urls_sala,identificadores)
                
                return render_template("index.html",filtro=filtro,palabra_clave=palabra_clave,paises=lista_paises,coincidencias=coincidencias,pais=pais)
    else:
        abort(404)

#Ruta de detalle del evento
@app.route('/evento/<identificador>',methods=["GET","POST"])
def detallevento(identificador):
    #En una variable key, guardamos por el diccionario os.environ nuestra key
    key=os.environ["apikey"]
    #Creamos el diccionario con los parámetros necesarios
    payload = {'apikey':key,'id':identificador}
    #Guardamos la petición en una variable(urlbase + diccionario con parametros)
    r=requests.get(url_base+'events',params=payload)

	#Comprobamos que la petición genera un 200
    if r.status_code == 200:
        #Guardamos el contenido de la petición1 
        contenido = r.json()
        nombres=[]
        fechas=[]
        horas=[]
        salas=[]
        direccion=[]
        ciudades=[]
        paises=[]
        urls=[]
        urls_sala=[]
        fechas_cambiadas=[]
        fecha_str=[]

        #Guardar contenido en listas
        for elem in contenido["_embedded"]["events"]:
            #Nombres
            nombres.append(elem["name"])
            #Ciudades
            ciudades.append(elem["_embedded"]["venues"][0]["city"]["name"])
            #Paises
            paises.append(elem["_embedded"]["venues"][0]["country"]["name"])
            #Salas
            if "name" in elem["_embedded"]["venues"][0]:
                salas.append(elem["_embedded"]["venues"][0]["name"])
            else:
                salas.append("-")
            #Direcciones
            if "address" in elem["_embedded"]["venues"][0]:
                direccion.append(elem["_embedded"]["venues"][0]["address"]["line1"])
            else:
                direccion.append("-")
            #Fechas con cambio de formato
            fechas.append(elem["dates"]["start"]["localDate"])
            for fecha in fechas:
                fechas_cambiadas.append(datetime.strptime(fecha, '%Y-%m-%d'))
            for fecha in fechas_cambiadas:
                fecha_str.append(datetime.strftime(fecha, '%d/%m/%Y'))
            #Horas, comprobamos que esta la hora porque a veces la hora no aparece
            if "localTime" in elem["dates"]["start"]:
                horas.append(elem["dates"]["start"]["localTime"])
            else:
                horas.append("-")
            #URLS
            urls.append(elem["url"])
            if "url" in elem["_embedded"]["venues"][0]:
                urls_sala.append(elem["_embedded"]["venues"][0]["url"])
            else:
                urls_sala.append("-")

        filtro=zip(nombres,paises,ciudades,salas,direccion,fecha_str,horas,urls,urls_sala)
        return render_template("detalle_eventos.html",filtro=filtro)

 
#Probar en el entorno de desarrollo
app.run(debug=True)
