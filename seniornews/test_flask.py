from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=['POST', 'GET'])
def test_endpoint():
    """Test endpoint to check how parameters are received"""
    print(f"Request method: {request.method}")
    print(f"Request args: {request.args}")
    print(f"Request form: {request.form}")
    print(f"Request JSON: {request.json if request.is_json else 'Not JSON'}")
    
    # Get values from multiple sources
    # First try query parameters
    start_date = request.args.get('start_date')
    
    # Then try JSON body
    if start_date is None and request.is_json and 'start_date' in request.json:
        start_date = request.json.get('start_date')
    
    # Finally try form data
    if start_date is None and 'start_date' in request.form:
        start_date = request.form.get('start_date')
    
    print(f"Final start_date: {start_date!r}")
    
    return jsonify({
        'received_start_date': start_date,
        'args': dict(request.args),
        'json': request.json if request.is_json else None,
        'form': dict(request.form)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002)
