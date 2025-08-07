from flask import Flask, render_template, request, redirect, url_for, session
import config

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

VERSION = "1.0.1"

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == config.USERNAME and password == config.PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('welcome'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('index.html', error=error, version=VERSION)

@app.route('/welcome')
def welcome():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('welcome.html', version=VERSION)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True) 