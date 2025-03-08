import os

# Create the Flask app
from app import create_app
application = create_app()

# For compatibility with WSGI servers that look for 'app'
app = application

# This allows testing the app locally
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
