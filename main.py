import pandas as pd 
import re 
import sys 
import random
import xml.etree.ElementTree as ET


def salida_controlada():
    
    print('\nFinalizando programa\nmaven_pizzas ')
    print('\nPrograma finalizado')
    sys.exit()
    
    
def extract():
    
    ordersdetails = pd.read_csv('order_details.csv', sep=',')                   
    ingredients = pd.read_csv('pizza_types.csv', encoding='latin1')    
    pizza_price = pd.read_csv('pizzas.csv')           
    orders=pd.read_csv('orders.csv', sep=',')   
                      
    return [ingredients , orders , pizza_price , ordersdetails]


def porciones(pizzas_pedidas, cantidad_ingredientes, j, recuento, i  ) :
    # Dependiendo del tamaño tendremos que añadir una cantidad determinada de ingredientes
    k=0
    while k < len(pizzas_pedidas[i]):
        if pizzas_pedidas[i][k] == 'S':
            cantidad_ingredientes[recuento[j]]+= 1
        elif pizzas_pedidas[i][k] == 'M':
            cantidad_ingredientes[recuento[j]]+= 2
        elif pizzas_pedidas[i][k] == 'L':
            cantidad_ingredientes[recuento[j]]+= 3
        elif pizzas_pedidas[i][k] == 'X' and pizzas_pedidas[i][k+1]== 'L':
            k=k+1
            cantidad_ingredientes[recuento[j]] += 4 
        else: # tamaño xl o xxl 
            cantidad_ingredientes[recuento[j]]+= 6
            k=k+2 #tamano xxl
        k=k+1
    return cantidad_ingredientes

def porciones_al_comenzar(pizzas_pedidas,n,nombre_pizza,recuento_ingredientes,j,cantidad_ingredientes):
    
    if pizzas_pedidas[nombre_pizza][n] == 'S':
        cantidad_ingredientes[recuento_ingredientes[j]] += 1
    elif pizzas_pedidas[nombre_pizza][n] == 'M':
        cantidad_ingredientes[recuento_ingredientes[j]] += 2
    elif pizzas_pedidas[nombre_pizza][n] == 'L':
        cantidad_ingredientes[recuento_ingredientes[j]] += 3
    elif pizzas_pedidas[nombre_pizza][n]== 'X' and pizzas_pedidas[nombre_pizza][n+1]== 'L':
        cantidad_ingredientes[recuento_ingredientes[j]] += 4
        n=n+1
    else: 
        #cojo la xxl como un tamaño gigante, asumo ing= 6 
        n=n+2
        cantidad_ingredientes[recuento_ingredientes[j]] += 6 
    return n, cantidad_ingredientes

def ingredientes(ingredients, porciones_ingredientes,cantidad_ingredientes,pizzas_pedidas,nombre_pizza):
    'funcion que determina la cantidad de ingredientes a añadir a la lista de la compra'
    
    longitud_1=len(ingredients['pizza_type_id'])
    for k in range(longitud_1):
        if ingredients['pizza_type_id'][k] == nombre_pizza:
            recuento_ingredientes = ingredients['ingredients'][k].split(', ') # separamos tambien el espacio despues de la coma 
            for j in range(len(recuento_ingredientes)):
                if recuento_ingredientes[j] in porciones_ingredientes :
                    cantidad_ingredientes= porciones(pizzas_pedidas,cantidad_ingredientes,j,recuento_ingredientes, nombre_pizza)
                else:
                    # cuando tengamos 0 ingredientes le damos un valor inicial 
                    porciones_ingredientes.append(recuento_ingredientes[j])
                    n=0
                    cantidad_ingredientes[recuento_ingredientes[j]]=0
                    while n < len(pizzas_pedidas[nombre_pizza]):
                        n, cantidad= porciones_al_comenzar(pizzas_pedidas,n,nombre_pizza,
                                                           recuento_ingredientes,j,cantidad_ingredientes)
                        cantidad_ingredientes=cantidad
                        n=n+1
                        
    return cantidad_ingredientes, porciones_ingredientes


def ordenar(order__details, pizzas, pizzas_pedidos, pedidos_cantidad):
    
    ' funcion que devuelve un par clave valor de la forma (pizza: tamano) devolviendo todos los tamaños pedidos en un string '
    
    tamano= len(order__details['order_id']) # cantidad de orders id
    longitud_2=len(pizzas['pizza_id'])  # cantidad de pizzas id 
    for j in range(tamano):
        # vemos los detalles de los pedidos para empezar a trabajar con ingredientes 
        if order__details['order_id'][j] in pedidos_cantidad:
            pizza_id = order__details['pizza_id'][j]
            quantity = order__details['quantity'][j]
            for k in range(longitud_2):
                if pizzas['pizza_id'][k] == pizza_id:
                    for i in range(0,quantity):
                        # el numero de veces que se pide la pizza 
                        # añadimos clave : valor al diccionario
                        if pizzas['pizza_type_id'][k] in pizzas_pedidos != False: 
                            # si ya se ha registrado una pizza igual
                            pizzas_pedidos[pizzas['pizza_type_id'][k]] += pizzas['size'][k]
                        else: # si es la primera vez que se registra la pizza
                            pizzas_pedidos[pizzas['pizza_type_id'][k]] = pizzas['size'][k]
                        
    return pizzas_pedidos  #pedidos realizados durante 10 semanas 


def transform(ingredients, orders, pizzas, orderdetails):
    
    fechas_totales  = [] 
    longitud = len(orders.axes[0])-1
    #iniciamos valores para el bucle. 
    contador = -1
    fecha = ""
    while contador < len(orders['date']) and longitud!=-1:
        if str(orders.loc[longitud]['date']) != fecha:
            fecha = str(orders['date'][longitud])
            fechas_totales.append(fecha)           
            contador += 1
        longitud-= 1
        
    # Aqui lo que tenemos son todas las semanas en las que hemos pedido pizzas, es decir todas las fechas del fichero. 
    # claro que hacerlo con todas las semanas sería una locura, por tanto cogeremos unas cuantas semanas de forma aleatoria. 
    # despues, sobre esas semanas haremos la mediana de cada ingrediente. 
    
    longitud_fichero=len(fechas_totales)-8
    lista_randoms=[]
    for i in range(10): 
        lista_randoms.append(random.randint(1,longitud_fichero))
    # aqui seleccionamos las semanas que vamos a utilizar. 
    fichero_semanas=[]
    for i in range(0,longitud_fichero): 
        if i in lista_randoms:
            for j in range(7):
                fichero_semanas.append(fechas_totales[i+j])
    # ya tenemos el fichero con las semanas que queremos - llamado fichero semanas. 
    
    pedidos = _semana_(orders,fichero_semanas)
    encargos = {} # para tener nombre pizza: tamaño pedidos  , con esto podremos calcular los ingredientes necesarios. 
    pizzas_ordenadas_p= ordenar(orderdetails,pizzas,encargos,pedidos)
    # ojo porque este fichero puede devolver pizza: LLLLlMXL , es decir devuelve todos los tamaños en los que se ha pedido la pizza
    porciones_ingredientes = []
    nombre_ingredientes={}  # para tener ingredientes : cantidad 
    for nombre_pizza in pizzas_ordenadas_p:
        # for cada pizza tenemos que estudiar los ingredientes basandonos en los tamaños proporcionados
        nombre_ingredientes, porciones_ingredientes=ingredientes(ingredients, porciones_ingredientes,
                                                                 nombre_ingredientes,encargos,nombre_pizza)
    
    cantidad_ingredientes=nombre_ingredientes
    
    return cantidad_ingredientes


def _semana_(pedidos_en_semana,semana):
    pedidos_semanales = []
    longitud_3= len(pedidos_en_semana['order_id'])
    # pedidos en semanas que estamos buscando (10 semanas por tanto)
    for i in range(longitud_3):
        if pedidos_en_semana['date'][i] in semana:
            pedidos_semanales.append(pedidos_en_semana['order_id'][i])
    return pedidos_semanales


def load(cantidad,fichero):
    #realizamos la media de las 10 semanas , tenemos todas sumadas por lo que tenemos que dividir entre 10. 
    # Funcion que manda el diccionario a un csv 
    df = pd.DataFrame(columns =  ['Ingredientes_necesarios', 'Cantidad a comprar por semana'])
    for i in cantidad:
        df.loc[i] = (str(i), int(cantidad[i]/10))
    df.to_csv(fichero, index=False)
    #guarda la informacion en un xml

def main():
    
    dfs=extract()
    cantidades=transform(dfs[0], dfs[1], dfs[2], dfs[3])
    fichero = 'compra_necesaria.csv'
    load( cantidades,fichero) 
    # guardarlo en el csv designado en la fucnion load 
    salida_controlada()


if __name__  ==  '__main__' :
    main()