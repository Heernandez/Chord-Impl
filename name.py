'''
Author : Luis H

    Este script recibe una direccion IP y/o MAC
    la concatena a una cadena aleatorio a de 25 caracteres
    alfanumericos y saca un hash de la cadena
    posteriormente converte el valor a entero y lo retorna

    Funciona como un generador de Id's con la funcion "magica"
    de los hash para que esa generación tenga una distribucion 
    uniforme
    
'''
import hashlib
import string
import random

def hashString(s):
    # Recibe una cadena y calcula el sha256
    sha = hashlib.sha256()
    sha.update(s.encode('ascii'))
    return sha.hexdigest()

def generation(ip, size = 25):
    aleatoria = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                      for x in range(size))
    cadena = ip + aleatoria
    return cadena

cadena = generation("192.168.0.6")
hashCode = hashString(cadena)
print("el tipo es :{}".format(hashCode))