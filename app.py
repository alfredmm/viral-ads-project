from flask import Flask, render_template, jsonify, request, send_file
from main import ad_generator
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-from-prompt', methods=['POST'])
def generate_from_prompt():
    try:
        user_prompt = request.form.get('prompt', '').strip()
        ad_data = ad_generator.generate_from_prompt(user_prompt)
        return jsonify(ad_data)
    except Exception as e:
        print(f"Error generating from prompt: {e}")
        return jsonify({"error": "Failed to generate ad. Please try again."})

@app.route('/generate-from-twitter')
def generate_from_twitter():
    try:
        ad_data = ad_generator.generate_from_twitter()
        return jsonify(ad_data)
    except Exception as e:
        print(f"Error generating from Twitter: {e}")
        return jsonify({"error": "Failed to fetch viral content from Twitter."})

@app.route('/list-ads')
def list_ads():
    try:
        ads = []
        for file in os.listdir('static'):
            if file.startswith('ad_') and file.endswith('.json'):
                try:
                    with open(f'static/{file}', 'r') as f:
                        ad_data = json.load(f)
                        ads.append(ad_data)
                except:
                    continue
        
        ads.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(ads)
    except Exception as e:
        print(f"Error listing ads: {e}")
        return jsonify({"error": "Failed to load ads"})

@app.route('/video/<filename>')
def serve_video(filename):
    try:
        return send_file(f'static/videos/{filename}', mimetype='video/mp4')
    except FileNotFoundError:
        return jsonify({"error": "Video not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)