import pandas as pd
import sys 


if __name__ == '__main__':

    ficheros = ['order_details.csv','orders.csv','pizza_types.csv','pizzas.csv']

    for elemento in ficheros:

        print('\nlimpieza de ficheros' )
        df = pd.read_csv (elemento, sep=';', encoding= 'latin1')
        #cada fichero con su analisis 
        print('\nNúmero de NaN por columna:')
        print(df.isna().sum())
 
        print('\nNúmero de nulls por columna:')
        print(df.isnull().sum())

        print("\nType of data: ")
        print(df.dtypes)
    sys.exit()