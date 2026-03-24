from flask import Flask, render_template, request, redirect, url_for
from weather import Weather, WeatherException
import os

app = Flask(__name__)
# app.config.from_pyfile('config/config.cfg')



app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = 'http://api.openweathermap.org/data/2.5/forecast'
w = Weather(app.config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        location = request.form
        w.set_location(location.get('location'))
        try:
            return render_template('result.html', data=w.get_forecast_data())
        except WeatherException:
            return render_template('index.html', error="City not found! Please try again.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
