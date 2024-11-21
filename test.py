from flask import Flask, request, render_template_string, redirect, url_for, session, Response
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for signing session cookies

# Simulated token storage for logged-in users
active_tokens = set()

# Credentials for access
USERNAME = "admin"
PASSWORD = "secret"

def check_auth(username, password):
    """Check if the username and password are correct."""
    return username == USERNAME and password == PASSWORD

@app.route('/')
def home():
    """Home page."""
    return render_template_string(index_html)

@app.route('/login', methods=['POST'])
def login():
    """Log in a user and issue a token."""
    auth = request.form.get('username'), request.form.get('password')
    if not auth or not check_auth(auth[0], auth[1]):
        return render_template_string(login_html, error="Invalid credentials")
    
    # Issue a token and add it to active tokens
    token = str(uuid.uuid4())
    active_tokens.add(token)

    # Store the token in the session
    session['token'] = token

    # Redirect to protected page after successful login
    return redirect(url_for('protected'))

@app.route('/protected', methods=['GET'])
def protected():
    """Protected route requiring a valid token."""
    token = session.get('token')
    if token not in active_tokens:
        return redirect(url_for('login_page', error="You must log in first"))
    
    return render_template_string(protected_html, token=token)

@app.route('/logout', methods=['POST'])
def logout():
    """Log out all users by clearing all active tokens."""
    global active_tokens
    active_tokens.clear()

    # Clear session token
    session.pop('token', None)

    return redirect(url_for('home', message="All users have been logged out."))

@app.route('/login_page')
def login_page():
    """Render login page."""
    return render_template_string(login_html)


# HTML templates
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
</head>
<body>
    <h1>Welcome to the Website</h1>
    <p><a href="{{ url_for('login_page') }}">Login</a></p>
    <p><a href="{{ url_for('logout') }}">Logout All Users</a></p>
</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
    <form method="POST" action="{{ url_for('login') }}">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

protected_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Protected Page</title>
</head>
<body>
    <h1>Protected Page</h1>
    <p>Welcome, your session token is: {{ token }}</p>
    <p><a href="{{ url_for('home') }}">Go Home</a></p>
    <form action="{{ url_for('logout') }}" method="post">
        <button type="submit">Logout All Users</button>
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
