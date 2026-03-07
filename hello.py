from flask import Flask, render_template, request

from data_service import (
    demo_payload, 
    fetch_amasadora_rows, 
    to_chart_series, 
    fetch_distinct_recipes,
    fetch_amasadora_grouped_by_batch
)

app = Flask(__name__, template_folder='Templates')


def get_common_filters():
    start_date = request.args.get('start_date')
    if start_date:
        start_date = start_date.replace('T', ' ')
    end_date = request.args.get('end_date')
    if end_date:
        end_date = end_date.replace('T', ' ')
    recipe_id = request.args.get('recipe_id')
    return start_date, end_date, recipe_id


@app.route('/')
def index():
    return render_template('principal.html', active_tab='principal', connection_success=True)


@app.route('/trazabilidad1')
def trazabilidad1():
    start_date, end_date, recipe_id = get_common_filters()
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
        active_tab='trazabilidad1',
        filters={
            'start_date': start_date,
            'end_date': end_date,
            'recipe_id': recipe_id
        }
    )


@app.route('/trazabilidad2')
def trazabilidad2():
    start_date, end_date, recipe_id = get_common_filters()
    recipes = fetch_distinct_recipes()
    
    column_names, data, connection_success = fetch_amasadora_grouped_by_batch(
        limit=100,
        start_date=start_date,
        end_date=end_date,
        recipe_id=recipe_id
    )
    
    return render_template(
        'trazabilidad2.html',
        data=data,
        column_names=column_names,
        connection_success=connection_success,
        row_count=len(data),
        recipes=recipes,
        active_tab='trazabilidad2',
        filters={
            'start_date': start_date,
            'end_date': end_date,
            'recipe_id': recipe_id
        }
    )


if __name__ == '__main__':
    app.run(debug=True)
