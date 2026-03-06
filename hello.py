from flask import Flask, render_template
import pyodbc
import os
from config import SQL_SERVER_CONFIG

app = Flask(__name__, template_folder='Templates')

def get_db_connection():
    try:
        # Construcción de la cadena de conexión
        if not SQL_SERVER_CONFIG['username']:
            # Autenticación de Windows
            conn_str = (
                f"DRIVER={SQL_SERVER_CONFIG['driver']};"
                f"SERVER={SQL_SERVER_CONFIG['server']};"
                f"DATABASE={SQL_SERVER_CONFIG['database']};"
                f"Trusted_Connection=yes;"
            )
        else:
            # Autenticación de SQL Server
            conn_str = (
                f"DRIVER={SQL_SERVER_CONFIG['driver']};"
                f"SERVER={SQL_SERVER_CONFIG['server']};"
                f"DATABASE={SQL_SERVER_CONFIG['database']};"
                f"UID={SQL_SERVER_CONFIG['username']};"
                f"PWD={SQL_SERVER_CONFIG['password']}"
            )
        return pyodbc.connect(conn_str, timeout=5)
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    data = []
    column_names = []
    labels = []
    values = []
    connection_success = False

    if conn:
        try:
            cursor = conn.cursor()
            # Consulta específica para Amasadora1
            query = """
            SELECT TOP (100) [Datetime], [IngredienteID], [BatchID], [RecipeID], [Value]
            FROM [gashor].[dbo].[Amasadora1]
            ORDER BY [Datetime] DESC
            """
            cursor.execute(query) 
            column_names = [column[0] for column in cursor.description]
            data = [list(row) for row in cursor.fetchall()]
            
            # Preparar datos para el gráfico (Datetime vs Value)
            if len(data) > 0:
                # Invertimos los datos para que el gráfico vaya de antiguo a nuevo
                display_data = data[::-1]
                labels = [str(row[0].strftime('%H:%M:%S')) if hasattr(row[0], 'strftime') else str(row[0]) for row in display_data]
                values = [float(row[4]) if row[4] is not None else 0 for row in display_data]
            
            connection_success = True
            conn.close()
        except Exception as e:
            print(f"Error fetching data: {e}")
    
    # Datos Mock/Demo si la conexión falla o no hay datos
    if not connection_success:
        column_names = ["ID", "Categoría", "Valor", "Fecha"]
        data = [
            [1, "Electrónica", 1500, "2024-03-01"],
            [2, "Hogar", 800, "2024-03-02"],
            [3, "Moda", 1200, "2024-03-03"],
            [4, "Deportes", 950, "2024-03-04"],
            [5, "Juguetes", 600, "2024-03-05"]
        ]
        labels = [row[1] for row in data]
        values = [row[2] for row in data]

    return render_template('index.html', 
                           data=data, 
                           column_names=column_names, 
                           labels=labels, 
                           values=values,
                           connection_success=connection_success,
                           row_count=len(data))

if __name__ == '__main__':
    app.run(debug=True)