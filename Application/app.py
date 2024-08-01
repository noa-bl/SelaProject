from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from pymongo import MongoClient
import secrets
from bson import ObjectId

app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(16)

# Initialize MongoDB client
client = MongoClient("mongodb://myUserAdmin:changeme@mongo:27017/?authSource=admin")
db = client.Project
Users = db.Users
Posts = db.Posts


@app.route(rule='/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('home.html')
    elif request.method == 'POST':
        session['username'] = request.form.get('username')
        username = session['username']
        password = request.form.get('password')
        try:
            result = Users.find_one({'username': username, 'password': password})
            if result:
                postsNum = Posts.count_documents({'username': username})
                user_posts = Posts.find({'username': username}, {'title': 1, 'content': 1, 'likes': 1, '_id': 1})
                user_posts_list = list(user_posts)
                return render_template('userPage.html', postsNum=postsNum, user_posts_list=user_posts_list, username=username), 200
            else:
                return "Failed Login", 200
        except Exception as e:
            app.logger.error(f"Can't connect to MongoDB: {e}")
            return f"Can't connect to MongoDB: {e}", 500

@app.route(rule='/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html'), 200
    elif request.method == 'POST':
        session['username'] = request.form.get('username')
        username = session['username']
        password = request.form.get('password')
        try:
            if Users.find_one({'username': username}):
                return "Username already exists", 200
            else:
                Users.insert_one({'username': username, 'password': password})
                return render_template('userPage.html', username=username, postsNum=0, user_posts_list=[]), 200
        except Exception as e:
            app.logger.error(f"Error: {e}")
            return f"Error: {e}", 500

@app.route(rule='/newPost', methods=['GET', 'POST'])
def newPost():
    if request.method == 'GET':
        return render_template('newPost.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        username = session.get('username')

        if not title or not content or not username:
            app.logger.error("Title, content, or username not provided")
            return "Title, content, or username not provided", 400

        existing_post = Posts.find_one({'username': username, 'title': title})
        if existing_post:
            app.logger.info(f"Post already exists for user {username} with title {title}")
            return "Post already exists", 400

        try:
            Posts.insert_one({'username': username, 'title': title, 'content': content, 'likes': []})
            user_posts = Posts.find({'username': username}, {'title': 1, 'content': 1, 'likes': 1, '_id': 1})
            postsNum = Posts.count_documents({'username': username})
            user_posts_list = list(user_posts)
            return redirect(url_for('userPage'))
        except Exception as e:
            app.logger.error(f"Error creating post: {e}")
            return f"Error: {e}", 500

@app.route(rule='/likePost', methods=['POST'])
def likePost():
    post_id = request.form.get('post_id')
    username = session.get('username')
    if not post_id or not username:
        return "Invalid request", 404
    else:
        post = Posts.find_one({'_id': ObjectId(post_id)})
        if post:
            if username not in post['likes']:
                Posts.update_one({'_id': ObjectId(post_id)}, {'$addToSet': {'likes': username}})
                action = 'liked'
            else:
                Posts.update_one({'_id': ObjectId(post_id)}, {'$pull': {'likes': username}})
                action = 'unliked'
            return 'success'
        else:
            return 'invalid request', 400

@app.route('/userPage')
def userPage():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))
    user_posts = list(Posts.find({'username': username}, {'title': 1, 'content': 1, 'likes': 1, '_id': 1}))
    postsNum = len(user_posts)
    return render_template('userPage.html', username=username, postsNum=postsNum, user_posts_list=user_posts)

@app.route('/allPosts')
def allPosts():
    try:
        posts = list(Posts.find())
        return render_template('allPosts.html', posts_list=posts)
    except Exception as e:
        app.logger.error(f"Error fetching posts: {e}")
        return f"Error fetching posts: {e}", 500

@app.route('/getUpdatedPosts')
def getUpdatedPosts():
    username = session.get('username')
    user_posts = list(Posts.find({'username': username}, {'title': 1, 'content': 1, 'likes': 1, '_id': 1}))
    for post in user_posts:
        post['_id'] = str(post['_id'])
        post['likes'] = list(post['likes'])   
    posts_num = len(user_posts)
    return jsonify({
        'postsNum': posts_num,
        'user_posts_list': user_posts
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
