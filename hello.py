from flask import Flask, render_template, request

from data_service import demo_payload, fetch_amasadora_rows, to_chart_series, fetch_distinct_recipes

app = Flask(__name__, template_folder='Templates')


@app.route('/')
def index():
    start_date = request.args.get('start_date')
    if start_date:
        start_date = start_date.replace('T', ' ')
        
    end_date = request.args.get('end_date')
    if end_date:
        end_date = end_date.replace('T', ' ')
        
    recipe_id = request.args.get('recipe_id')

    # Obtener recetas para el dropdown
    recipes = fetch_distinct_recipes()

    column_names, data, connection_success = fetch_amasadora_rows(
        limit=1000,
        start_date=start_date,
        end_date=end_date,
        recipe_id=recipe_id
    )
    
    if connection_success and data:
        labels, values = to_chart_series(data)
    elif not connection_success:
        column_names, data, labels, values = demo_payload()
    else:
        # Conexión ok pero sin datos
        labels, values = [], []

    return render_template(
        'index.html',
        data=data,
        column_names=column_names,
        labels=labels,
        values=values,
        connection_success=connection_success,
        row_count=len(data),
        recipes=recipes,
        filters={
            'start_date': start_date,
            'end_date': end_date,
            'recipe_id': recipe_id
        }
    )


if __name__ == '__main__':
    app.run(debug=True)
