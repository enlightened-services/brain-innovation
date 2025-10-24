from flask import Flask, send_from_directory, abort
import os
import mimetypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

# Ensure correct MIME type for SVG files on minimal images
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('image/svg+xml', '.svgz')


@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/<path:requested_path>')
def serve_file(requested_path: str):
    safe_path = os.path.normpath(requested_path)
    if safe_path.startswith('..'):
        abort(404)
    return send_from_directory(BASE_DIR, safe_path)


@app.route('/download/<path:requested_path>')
def download_file(requested_path: str):
    safe_path = os.path.normpath(requested_path)
    if safe_path.startswith('..'):
        abort(404)
    return send_from_directory(BASE_DIR, safe_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


