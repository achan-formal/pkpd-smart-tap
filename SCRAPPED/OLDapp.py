from flask import Flask, jsonify, request

app = Flask(__name__)

# A simple endpoint that returns JSON data
@app.route('/api/data', methods=['GET'])
def get_data():
    sample_response = {"message": "Hello from Flask!", "status": "success"}
    return jsonify(sample_response)

if __name__ == "__main__":
    # Use 0.0.0.0 to make the server accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)

#ctrl + I