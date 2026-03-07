from flask import Flask, render_template

from data_service import demo_payload, fetch_amasadora_rows, to_chart_series

app = Flask(__name__, template_folder='Templates')


@app.route('/')
def index():
    column_names, data, connection_success = fetch_amasadora_rows(limit=1000)
    
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
    )


if __name__ == '__main__':
    app.run(debug=True)
