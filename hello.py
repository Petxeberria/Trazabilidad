from flask import Flask, render_template

from data_service import demo_payload, fetch_amasadora_rows, to_chart_series

app = Flask(__name__, template_folder='Templates')


@app.route('/')
def index():
    column_names, data = fetch_amasadora_rows(limit=100)

    if data:
        labels, values = to_chart_series(data)
        connection_success = True
    else:
        column_names, data, labels, values = demo_payload()
        connection_success = False

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
