from flask import Flask, request, render_template, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from io import BytesIO
import logging
# Flask app setup
from dotenv import load_dotenv
import os


# Load .env variables
load_dotenv()

app = Flask(__name__)

# Environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "travel_platform")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "posts")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5500")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# MongoDB setup
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=50000)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
fs = GridFS(db)

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

@app.route('/')
def home():
    return render_template('forum.html')

@app.route('/posts', methods=['GET'])
def get_all_posts():
    try:
        posts = list(collection.find({}))
        for post in posts:
            post["_id"] = str(post["_id"])
            if post.get("image_id"):
                post["image_url"] = f"/file/{post['image_id']}"
            if post.get("video_id"):
                post["video_url"] = f"/file/{post['video_id']}"
        return jsonify(posts), 200
    except Exception as e:
        logger.exception("Failed to retrieve posts")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/add_post', methods=['POST'])
def add_post():
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', "").split(",")
        
        image_file = request.files.get('images')
        video_file = request.files.get('videos')

        image_id = fs.put(image_file, filename=image_file.filename,
                          content_type=image_file.content_type) if image_file else None
        video_id = fs.put(video_file, filename=video_file.filename,
                          content_type=video_file.content_type) if video_file else None

        post = {
            "title": title,
            "content": content,
            "tags": tags,
            "image_id": str(image_id) if image_id else None,
            "video_id": str(video_id) if video_id else None,
            "upvotes": 0,
            "downvotes": 0,
            "replies": []
        }

        collection.insert_one(post)
        return jsonify({"message": "Post added successfully!"}), 201
    except Exception as e:
        logger.exception("Error while adding post")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        response = app.response_class(file.read(), content_type=file.content_type)
        response.headers["Content-Disposition"] = f"inline; filename={file.filename}"
        return response
    except Exception as e:
        logger.exception("File retrieval failed")
        return jsonify({"status": "error", "message": str(e)}), 404

@app.route('/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        fs.delete(ObjectId(file_id))
        return jsonify({"message": "File deleted successfully!"}), 200
    except Exception as e:
        logger.exception("File deletion failed")
        return jsonify({"status": "error", "message": str(e)}), 404

@app.route('/posts/<post_id>/upvote', methods=['POST'])
def upvote_post(post_id):
    try:
        collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"upvotes": 1}})
        return jsonify({"message": "Upvoted successfully!"}), 200
    except Exception as e:
        logger.exception("Upvote failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/posts/<post_id>/downvote', methods=['POST'])
def downvote_post(post_id):
    try:
        collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"downvotes": 1}})
        return jsonify({"message": "Downvoted successfully!"}), 200
    except Exception as e:
        logger.exception("Downvote failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/posts/reply/<post_id>', methods=['POST'])
def reply_post(post_id):
    try:
        data = request.get_json()
        if not data or not data.get('content', '').strip():
            return jsonify({"status": "error", "message": "Reply content cannot be empty"}), 400

        reply = {"content": data['content'].strip()}
        result = collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"replies": reply}})
        
        if result.matched_count == 0:
            return jsonify({"status": "error", "message": "Post not found."}), 404
        return jsonify({"message": "Reply added successfully!"}), 201
    except Exception as e:
        logger.exception("Reply failed")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
