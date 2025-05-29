import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import current_user, login_required
from app import db
from app.models.post import Post
from app.forms.post_forms import PostForm, SearchForm

posts_bp = Blueprint('posts', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)
    
    output_size = (800, 800)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@posts_bp.route('/')
@posts_bp.route('/home')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('posts/index.html', posts=posts)

# Add at the top with other imports
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Add this function after the existing imports
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment

# Modify the new_post function
@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        
        # Analyze sentiment of both title and content
        title_sentiment = analyze_sentiment(form.title.data)
        content_sentiment = analyze_sentiment(form.content.data)
        
        # Calculate average sentiment scores
        post.sentiment_pos = (title_sentiment['pos'] + content_sentiment['pos']) / 2
        post.sentiment_neg = (title_sentiment['neg'] + content_sentiment['neg']) / 2
        post.sentiment_neu = (title_sentiment['neu'] + content_sentiment['neu']) / 2
        post.sentiment_compound = (title_sentiment['compound'] + content_sentiment['compound']) / 2
        
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created with sentiment analysis!', 'success')
            return redirect(url_for('posts.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating post: {str(e)}', 'danger')
    
    return render_template('posts/create.html', title='New Post', 
                           form=form, legend='New Post')

@posts_bp.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts/view.html', title=post.title, post=post)

@posts_bp.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        # Analyze sentiment of both title and content
        title_sentiment = analyze_sentiment(form.title.data)
        content_sentiment = analyze_sentiment(form.content.data)
        
        post.sentiment_pos = (title_sentiment['pos'] + content_sentiment['pos']) / 2
        post.sentiment_neg = (title_sentiment['neg'] + content_sentiment['neg']) / 2
        post.sentiment_neu = (title_sentiment['neu'] + content_sentiment['neu']) / 2
        post.sentiment_compound = (title_sentiment['compound'] + content_sentiment['compound']) / 2
        
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        
        try:
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating post: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('posts/edit.html', title='Update Post', 
                           form=form, legend='Update Post')

@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting post: {str(e)}', 'danger')
    
    return redirect(url_for('posts.index'))

@posts_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    results = []
    
    if form.validate_on_submit() or request.args.get('q'):
        search_query = form.search_query.data if form.validate_on_submit() else request.args.get('q')
        results = Post.query.filter(
            (Post.title.contains(search_query)) | 
            (Post.content.contains(search_query))
        ).order_by(Post.created_at.desc()).all()
    
    return render_template('posts/search.html', title='Search', form=form, results=results)

@posts_bp.route('/user/<string:username>')
def user_posts(username):
    from app.models.user import User
    
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=5)
    
    return render_template('posts/user_posts.html', posts=posts, user=user)