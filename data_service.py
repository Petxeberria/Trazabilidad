"""Servicios de acceso y transformación de datos para la app Flask."""

from __future__ import annotations

from typing import Any

import pyodbc

from config import SQL_SERVER_CONFIG


def build_connection_string(config: dict[str, str]) -> str:
    """Construye cadena de conexión para SQL Server según tipo de autenticación."""
    base = (
        f"DRIVER={config['driver']};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
    )

    if not config["username"]:
        return f"{base}Trusted_Connection=yes;"

    return (
        f"{base}"
        f"UID={config['username']};"
        f"PWD={config['password']}"
    )


def get_db_connection() -> pyodbc.Connection | None:
    """Intenta abrir conexión a SQL Server."""
    try:
        return pyodbc.connect(build_connection_string(SQL_SERVER_CONFIG), timeout=5)
    except Exception as exc:  # noqa: BLE001
        print(f"Error connecting to SQL Server: {exc}")
        return None


def fetch_amasadora_rows(
    limit: int = 1000,
    start_date: str | None = None,
    end_date: str | None = None,
    recipe_id: str | None = None,
) -> tuple[list[str], list[list[Any]], bool]:
    """Obtiene filas de Amasadora1 con filtros opcionales."""
    conn = get_db_connection()
    if not conn:
        return [], [], False

    try:
        cursor = conn.cursor()
        
        # Construcción dinámica de la cláusula WHERE
        where_clauses = []
        params = []
        
        if start_date:
            where_clauses.append("[Datetime] >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("[Datetime] <= ?")
            params.append(end_date)
        if recipe_id:
            where_clauses.append("[RecipeID] = ?")
            params.append(recipe_id)
            
        where_stmt = ""
        if where_clauses:
            where_stmt = "WHERE " + " AND ".join(where_clauses)

        query = f"""
        SELECT TOP ({limit}) [Datetime], [IngredienteID], [BatchID], [RecipeID], [Value]
        FROM [gashor].[dbo].[Amasadora1]
        {where_stmt}
        ORDER BY [Datetime] DESC
        """
        
        cursor.execute(query, params)
        column_names = [column[0] for column in cursor.description]
        data = [list(row) for row in cursor.fetchall()]
        return column_names, data, True
    except Exception as exc:  # noqa: BLE001
        print(f"Error fetching data: {exc}")
        return [], [], False
    finally:
        conn.close()


def to_chart_series(rows: list[list[Any]]) -> tuple[list[str], list[float]]:
    """Transforma filas de DB en etiquetas y valores para Chart.js."""
    if not rows:
        return [], []

    ordered_rows = rows[::-1]
    labels = [
        str(row[0].strftime("%H:%M:%S")) if hasattr(row[0], "strftime") else str(row[0])
        for row in ordered_rows
    ]
    values = [float(row[4]) if row[4] is not None else 0 for row in ordered_rows]
    return labels, values


def fetch_distinct_recipes() -> list[str]:
    """Obtiene la lista de IDs de receta únicos."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = "SELECT DISTINCT [RecipeID] FROM [gashor].[dbo].[Amasadora1] WHERE [RecipeID] IS NOT NULL"
        cursor.execute(query)
        recipes = [str(row[0]) for row in cursor.fetchall()]
        return recipes
    except Exception as exc:  # noqa: BLE001
        print(f"Error fetching recipes: {exc}")
        return []
    finally:
        conn.close()


def demo_payload() -> tuple[list[str], list[list[Any]], list[str], list[float]]:
    """Datos de fallback cuando no hay conexión a SQL Server."""
    column_names = ["ID", "Categoría", "Valor", "Fecha"]
    data: list[list[Any]] = [
        [1, "Electrónica", 1500, "2024-03-01"],
        [2, "Hogar", 800, "2024-03-02"],
        [3, "Moda", 1200, "2024-03-03"],
        [4, "Deportes", 950, "2024-03-04"],
        [5, "Juguetes", 600, "2024-03-05"],
    ]
    labels = [str(row[1]) for row in data]
    values = [float(row[2]) for row in data]
    return column_names, data, labels, values
