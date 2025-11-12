import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_PATH = 'memes.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                profile_picture TEXT DEFAULT NULL
            );
            CREATE TABLE IF NOT EXISTS memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT NOT NULL,
                filename TEXT,
                meme_text TEXT,
                meme_type TEXT NOT NULL,
                category TEXT NOT NULL,
                background_color TEXT DEFAULT '#2a2a3e',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(meme_id) REFERENCES memes(id)
            );
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                reaction TEXT NOT NULL,
                UNIQUE(meme_id, username, reaction),
                FOREIGN KEY(meme_id) REFERENCES memes(id)
            );
            CREATE TABLE IF NOT EXISTS followers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower TEXT NOT NULL,
                following TEXT NOT NULL,
                UNIQUE(follower, following)
            );
        ''')

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    with get_db() as conn:
        memes = conn.execute('SELECT * FROM memes ORDER BY created_at DESC').fetchall()
        memes_data = []
        for meme in memes:
            comments = conn.execute('SELECT username, comment FROM comments WHERE meme_id=? ORDER BY created_at ASC', (meme['id'],)).fetchall()
            reactions = conn.execute('SELECT reaction, COUNT(*) AS cnt FROM reactions WHERE meme_id=? GROUP BY reaction', (meme['id'],)).fetchall()
            reactions_counts = {r['reaction']: r['cnt'] for r in reactions}
            meme_data = dict(meme)
            meme_data['comments'] = comments
            meme_data['reactions_counts'] = reactions_counts
            memes_data.append(meme_data)
        user_profile = conn.execute('SELECT username, profile_picture FROM users WHERE username=?', (username,)).fetchone()
        followers_count = conn.execute('SELECT COUNT(*) FROM followers WHERE following=?', (username,)).fetchone()[0]
        likes_count = conn.execute('SELECT COUNT(*) FROM reactions WHERE username=?', (username,)).fetchone()[0] or 0
        total_reactions_count = likes_count
        user_memes = conn.execute('SELECT * FROM memes WHERE username=? ORDER BY created_at DESC', (username,)).fetchall()
        profile_data = {
            'username': username,
            'picture_url': user_profile['profile_picture'] if user_profile else None,
            'followers_count': followers_count,
            'likes_count': likes_count,
            'total_reactions_count': total_reactions_count,
            'memes': user_memes
        }
    return render_template('memesite.html', memes=memes_data, logged_in=True, username=username, user_profile=profile_data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form.get('password_confirm', '')
        if password != password_confirm:
            flash('Passwords do not match.')
            return render_template('signup.html')
        hash_pw = generate_password_hash(password)
        try:
            with get_db() as conn:
                conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hash_pw))
            flash('Account created! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken.')
    return render_template('signup.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        flash('You must be logged in to upload memes.')
        return redirect(url_for('login'))
    title = request.form.get('meme_title', '').strip()
    meme_type = request.form.get('meme_type')
    category = request.form.get('category')
    meme_text = request.form.get('meme_text', '').strip()
    background_color = request.form.get('background_color', '#2a2a3e').strip()
    file = request.files.get('image')
    if not title or not meme_type or not category:
        flash('Title, type and category are required.')
        return redirect(url_for('index'))
    filename = None
    if meme_type == 'Text':
        if not meme_text:
            flash('Text meme cannot be empty.')
            return redirect(url_for('index'))
    else:
        if not file or not allowed_file(file.filename):
            flash('Valid media file is required.')
            return redirect(url_for('index'))
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    with get_db() as conn:
        conn.execute('''INSERT INTO memes (title, username, filename, meme_text, meme_type, category, background_color) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (title, session['username'], filename, meme_text, meme_type, category, background_color))
    flash('Meme uploaded successfully!')
    return redirect(url_for('index'))

@app.route('/react/<int:meme_id>', methods=['POST'])
def react(meme_id):
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Login required'}), 401
    reaction = request.json.get('reaction')
    if reaction not in {'❤️', '😂', '😮', '😢', '😡'}:
        return jsonify({'status': 'error', 'message': 'Invalid reaction'}), 400
    username = session['username']
    with get_db() as conn:
        try:
            conn.execute('INSERT INTO reactions (meme_id, username, reaction) VALUES (?, ?, ?)', (meme_id, username, reaction))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({'status': 'error', 'message': 'Already reacted'}), 409
    return jsonify({'status': 'ok', 'reaction': reaction})

@app.route('/comments/<int:meme_id>', methods=['POST'])
def add_comment(meme_id):
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Login required'}), 401
    comment = request.json.get('comment', '').strip()
    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment cannot be empty'}), 400
    username = session['username']
    with get_db() as conn:
        conn.execute('INSERT INTO comments (meme_id, username, comment) VALUES (?, ?, ?)', (meme_id, username, comment))
        conn.commit()
    return jsonify({'status': 'ok', 'comment': comment, 'username': username})

@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'username' not in session:
        return redirect(url_for('login'))
    file = request.files.get('profile_pic')
    if not file or not allowed_file(file.filename):
        flash('Invalid profile picture file.')
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    with get_db() as conn:
        conn.execute('UPDATE users SET profile_picture=? WHERE username=?', (filename, session['username']))
    flash('Profile picture updated!')
    return redirect(url_for('index'))

@app.route('/follow/<string:followed_username>', methods=['POST'])
def follow_user(followed_username):
    if 'username' not in session:
        return jsonify({'status':'error', 'message':'Login required'}), 401
    follower = session['username']
    if follower == followed_username:
        return jsonify({'status':'error', 'message':'Cannot follow yourself'}), 400
    with get_db() as conn:
        try:
            conn.execute('INSERT INTO followers (follower, following) VALUES (?, ?)', (follower, followed_username))
            conn.commit()
            return jsonify({'status':'ok', 'message':'Followed successfully'})
        except sqlite3.IntegrityError:
            return jsonify({'status':'error', 'message':'Already following'})

@app.route('/unfollow/<string:followed_username>', methods=['POST'])
def unfollow_user(followed_username):
    if 'username' not in session:
        return jsonify({'status':'error', 'message':'Login required'}), 401
    follower = session['username']
    with get_db() as conn:
        conn.execute('DELETE FROM followers WHERE follower=? AND following=?', (follower, followed_username))
        conn.commit()
    return jsonify({'status':'ok', 'message':'Unfollowed successfully'})

if __name__ == '__main__':
    app.run(debug=True)
