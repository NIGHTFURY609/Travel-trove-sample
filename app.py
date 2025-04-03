from flask import Flask, request, render_template, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from io import BytesIO
import logging
# Flask app setup
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})




# MongoDB and gridfs setup
client = MongoClient('mongodb+srv://nightanon038:wV86jTZpkYJ1K6Qo@travel-trove.sdb1i.mongodb.net/?retryWrites=true&w=majority&appName=travel-trove')  # Replace with your MongoDB URI
serverSelectionTimeoutMS=50000,
db = client['travel_platform']  # Database name
collection = db['posts']
fs = GridFS(db)  # GridFS for storing files

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust the level as needed

# Example: adding a simple console handler (in production, configure as needed)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


@app.route('/')
def home():
    return render_template('forum.html')  # Render your HTML template


@app.route('/posts', methods=['GET'])
def get_all_posts():
    try:
        posts = list(collection.find({}))
        for post in posts:
            # Convert ObjectId to string for JSON
            post["_id"] = str(post["_id"])
            if post.get("image_id"):
                post["image_url"] = f"http://localhost:5000/file/{post['image_id']}"
            if post.get("video_id"):
                post["video_url"] = f"http://localhost:5000/file/{post['video_id']}"
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/add_post', methods=['POST'])
def add_post():
    try:
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', "").split(",")  # Split tags
        upvote_post = request.form.get('upvote_post')
        downvote_post = request.form.get('downvote_post')
        

        # Handle file uploads
        image_file = request.files.get('images')
        video_file = request.files.get('videos')

        image_id = None
        video_id = None

        if image_file:
            image_id = fs.put(image_file, filename=image_file.filename,
                              content_type=image_file.content_type)
        if video_file:
            video_id = fs.put(video_file, filename=video_file.filename,
                              content_type=video_file.content_type)

        # Insert post into MongoDB
        post = {
            "_id": ObjectId(),
            "title": title,
            "content": content,
            "tags": tags,
            "image_id": str(image_id) if image_id else None,
            "video_id": str(video_id) if video_id else None,
            "upvotes": 0,   # Default upvotes to 0
            "downvotes": 0, # Default downvotes to 0
            "replies":[]
            
            
        }
        collection.insert_one(post)

        return jsonify({"message": "Post added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        # Retrieve file from GridFS
        file = fs.get(ObjectId(file_id))
        response = app.response_class(
            file.read(), content_type=file.content_type)
        response.headers["Content-Disposition"] = f"inline; filename={file.filename}"
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

@app.route('/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        # Delete file from GridFS
        fs.delete(ObjectId(file_id))
        return jsonify({"message": "File deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404
@app.route('/posts/<post_id>/upvote', methods=['POST'])
def upvote_post(post_id):
    try:
        collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"upvotes": 1}})
        return jsonify({"message": "Upvoted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/posts/<post_id>/downvote', methods=['POST'])
def downvote_post(post_id):
    try:
        collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"downvotes": 1}})
        return jsonify({"message": "Downvoted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/posts/reply/<post_id>', methods=['POST'])
def reply_post(post_id):
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON payload provided in the request.")
            return jsonify({"status": "error", "message": "No JSON payload provided."}), 400

        content = data.get('content', '').strip()
        if not content:
            logger.error("Empty reply content provided for post_id %s", post_id)
            return jsonify({"status": "error", "message": "Reply content cannot be empty"}), 400
        
        reply = {"content": content}
        result = collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"replies": reply}}
        )
        logger.info("Update result for post %s: matched_count=%s, modified_count=%s", 
                    post_id, result.matched_count, result.modified_count)
        
        if result.matched_count == 0:
            logger.error("No document found for post_id: %s", post_id)
            return jsonify({"status": "error", "message": "Reply not added. Post not found."}), 404

        logger.info("Reply added successfully to post_id: %s", post_id)
        return jsonify({"message": "Reply added successfully!"}), 201

    except Exception as e:
        logger.exception("Exception occurred while adding reply to post_id: %s", post_id)
        return jsonify({"status": "error", "message": "An error occurred on the server."}), 500

if __name__ == '__main__':
    app.run(port=5000,debug=True)