from flask import Flask, send_from_directory, abort, session, request, redirect, url_for, render_template_string
from functools import wraps
import os
import mimetypes
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Pincode voor preview toegang (kan via environment variable worden ingesteld)
PREVIEW_PINCODE = os.environ.get('PREVIEW_PINCODE', '432165')

# Ensure correct MIME type for SVG files on minimal images
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('image/svg+xml', '.svgz')


def require_auth(f):
    """Decorator om routes te beveiligen met pincode authenticatie"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login pagina voor pincode authenticatie"""
    error = None
    next_url = request.args.get('next', '/')
    
    if request.method == 'POST':
        pincode = request.form.get('pincode', '')
        if pincode == PREVIEW_PINCODE:
            session['authenticated'] = True
            return redirect(next_url)
        else:
            error = 'Invalid pincode. Please try again.'
    
    login_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview Access - Brain Innovation</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: radial-gradient(circle at top, #edf2ff 0, #f7fafc 45%, #edf2f7 100%);
                color: #1a202c;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .login-container {
                background: rgba(255, 255, 255, 0.96);
                border-radius: 18px;
                padding: 40px;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
                border: 1px solid rgba(226, 232, 240, 0.9);
                max-width: 400px;
                width: 100%;
            }
            h1 {
                font-size: 1.5rem;
                color: #2b6cb0;
                margin-bottom: 8px;
            }
            p {
                font-size: 0.9rem;
                color: #4a5568;
                margin-bottom: 24px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                font-size: 0.9rem;
                font-weight: 600;
                color: #1a365d;
                margin-bottom: 8px;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px 16px;
                border: 1px solid rgba(226, 232, 240, 0.9);
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.15s ease, box-shadow 0.15s ease;
            }
            input[type="text"]:focus {
                outline: none;
                border-color: #2b6cb0;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
            }
            .btn {
                width: 100%;
                padding: 12px 18px;
                background: linear-gradient(135deg, #3182ce, #805ad5);
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 0.95rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 8px 20px rgba(66, 153, 225, 0.35);
            }
            .error {
                background: #fed7d7;
                color: #c53030;
                padding: 12px;
                border-radius: 8px;
                font-size: 0.9rem;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>Preview Access</h1>
            <p>Enter the pincode to access the preview.</p>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            <form method="POST">
                <div class="form-group">
                    <label for="pincode">Pincode</label>
                    <input type="text" id="pincode" name="pincode" autocomplete="off" autofocus required>
                </div>
                <button type="submit" class="btn">Get Access</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(login_html, error=error)


@app.route('/logout')
def logout():
    """Logout route"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))


@app.route('/')
@require_auth
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/<path:requested_path>')
@require_auth
def serve_file(requested_path: str):
    safe_path = os.path.normpath(requested_path)
    if safe_path.startswith('..'):
        abort(404)
    return send_from_directory(BASE_DIR, safe_path)


@app.route('/download/<path:requested_path>')
@require_auth
def download_file(requested_path: str):
    safe_path = os.path.normpath(requested_path)
    if safe_path.startswith('..'):
        abort(404)
    return send_from_directory(BASE_DIR, safe_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


