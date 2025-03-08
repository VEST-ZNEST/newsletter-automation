import os

# Create the Flask app
from app import create_app
app = create_app()

# This allows testing the app locally
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
