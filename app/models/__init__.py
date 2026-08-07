from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

# ==================== USER & AUTH ====================
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.Text, default='{}')  # JSON permissions
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def has_permission(self, perm):
        try:
            perms = json.loads(self.permissions or '{}')
            return perms.get(perm, False) or perms.get('all', False)
        except:
            return False

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')

# ==================== SCHOOL SETTINGS ====================
class SchoolSetting(db.Model):
    __tablename__ = 'school_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    type = db.Column(db.String(20), default='text')  # text, image, json, boolean
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get(key, default=None):
        setting = SchoolSetting.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default
    
    @staticmethod
    def set(key, value, type='text'):
        setting = SchoolSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.type = type
            setting.updated_at = datetime.utcnow()
        else:
            setting = SchoolSetting(key=key, value=value, type=type)
            db.session.add(setting)
        db.session.commit()
        return setting

# ==================== HERO SLIDER ====================
class HeroSlide(db.Model):
    __tablename__ = 'hero_slides'
    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(200))
    sub_heading = db.Column(db.String(300))
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    video = db.Column(db.String(255))
    button_text = db.Column(db.String(100))
    button_url = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    publish_at = db.Column(db.DateTime)
    expire_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== NOTICES ====================
class NoticeCategory(db.Model):
    __tablename__ = 'notice_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True)
    
    notices = db.relationship('Notice', backref='category', lazy='dynamic')

class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True)
    content = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('notice_categories.id'))
    is_featured = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON list
    views = db.Column(db.Integer, default=0)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='notices')

# ==================== NEWS ====================
class NewsCategory(db.Model):
    __tablename__ = 'news_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True)
    
    news_items = db.relationship('News', backref='category', lazy='dynamic')

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True)
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('news_categories.id'))
    tags = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='draft')  # draft, published
    is_featured = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.String(500))
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='news_posts')

# ==================== BLOGS ====================
class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True)
    
    blogs = db.relationship('Blog', backref='category', lazy='dynamic')

class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True)
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'))
    tags = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='draft')
    is_featured = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.String(500))
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='blog_posts')
    comments = db.relationship('BlogComment', backref='blog', lazy='dynamic', cascade='all, delete-orphan')

class BlogComment(db.Model):
    __tablename__ = 'blog_comments'
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== GALLERY ====================
class GalleryAlbum(db.Model):
    __tablename__ = 'gallery_albums'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    media = db.relationship('GalleryMedia', backref='album', lazy='dynamic', cascade='all, delete-orphan')

class GalleryMedia(db.Model):
    __tablename__ = 'gallery_media'
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('gallery_albums.id'))
    title = db.Column(db.String(200))
    media_type = db.Column(db.String(20), default='image')  # image, video
    file_path = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== STAFF ====================
class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120))
    qualification = db.Column(db.String(255))
    experience = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    biography = db.Column(db.Text)
    photo = db.Column(db.String(255))
    staff_type = db.Column(db.String(50), default='teacher')  # teacher, staff, admin
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== FACILITIES & OFFERS ====================
class Facility(db.Model):
    __tablename__ = 'facilities'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # Font Awesome class
    image = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WhatWeOffer(db.Model):
    __tablename__ = 'what_we_offer'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    image = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Commitment(db.Model):
    __tablename__ = 'commitments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

# ==================== MESSAGES ====================
class PrincipalMessage(db.Model):
    __tablename__ = 'principal_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default='Principal')
    designation = db.Column(db.String(100), default='Principal')
    message = db.Column(db.Text)
    photo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChairmanMessage(db.Model):
    __tablename__ = 'chairman_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default='Chairman')
    designation = db.Column(db.String(100), default='Chairman')
    message = db.Column(db.Text)
    photo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== ADMISSION ENQUIRY ====================
class AdmissionEnquiry(db.Model):
    __tablename__ = 'admission_enquiries'
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(120), nullable=False)
    guardian_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    interested_grade = db.Column(db.String(50))
    previous_school = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default='new')  # new, contacted, in_progress, converted, closed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    internal_notes = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_read = db.Column(db.Boolean, default=False)
    ai_replied = db.Column(db.Boolean, default=False)
    ai_replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignee = db.relationship('User', backref='assigned_enquiries')
    replies = db.relationship('EnquiryReply', backref='enquiry', lazy='dynamic', cascade='all, delete-orphan')

class EnquiryReply(db.Model):
    __tablename__ = 'enquiry_replies'
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.Integer, db.ForeignKey('admission_enquiries.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    is_ai = db.Column(db.Boolean, default=False)
    is_email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='enquiry_replies')

# ==================== CONTACT MESSAGES ====================
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(30), default='new')
    internal_notes = db.Column(db.Text)
    ai_replied = db.Column(db.Boolean, default=False)
    ai_replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    replies = db.relationship('ContactReply', backref='contact', lazy='dynamic', cascade='all, delete-orphan')

class ContactReply(db.Model):
    __tablename__ = 'contact_replies'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact_messages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    is_ai = db.Column(db.Boolean, default=False)
    is_email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='contact_replies')

# ==================== AI LOGS ====================
class AIReplyLog(db.Model):
    __tablename__ = 'ai_reply_logs'
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(30))  # admission, contact
    source_id = db.Column(db.Integer)
    recipient_email = db.Column(db.String(120))
    recipient_name = db.Column(db.String(120))
    message_sent = db.Column(db.Text)
    wait_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== SUBSCRIBERS & NEWSLETTER ====================
class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== TESTIMONIALS ====================
class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255))
    rating = db.Column(db.Integer, default=5)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== FAQ ====================
class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

# ==================== EVENTS & CALENDAR ====================
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== DOWNLOADS ====================
class Download(db.Model):
    __tablename__ = 'downloads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    category = db.Column(db.String(100))
    downloads_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== POPUP NOTICE ====================
class PopupNotice(db.Model):
    __tablename__ = 'popup_notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    image = db.Column(db.String(255))
    button_text = db.Column(db.String(100))
    button_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== ANALYTICS ====================
class VisitorLog(db.Model):
    __tablename__ = 'visitor_logs'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    page = db.Column(db.String(255))
    referrer = db.Column(db.String(500))
    country = db.Column(db.String(100))
    device = db.Column(db.String(50))
    browser = db.Column(db.String(100))
    session_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== EMAIL LOGS ====================
class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True)
    to_email = db.Column(db.String(120))
    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    status = db.Column(db.String(30), default='pending')  # pending, sent, failed
    error_message = db.Column(db.Text)
    retries = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)

# ==================== PUSH NOTIFICATIONS ====================
class PushSubscription(db.Model):
    __tablename__ = 'push_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.Text, nullable=False)
    p256dh = db.Column(db.String(255))
    auth = db.Column(db.String(255))
    user_type = db.Column(db.String(50), default='general')  # general, parent, student, teacher
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PushNotification(db.Model):
    __tablename__ = 'push_notifications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    target = db.Column(db.String(50), default='everyone')
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(30), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== AI SETTINGS ====================
class AISetting(db.Model):
    __tablename__ = 'ai_settings'
    id = db.Column(db.Integer, primary_key=True)
    is_enabled = db.Column(db.Boolean, default=True)
    wait_hours = db.Column(db.Float, default=3.0)
    admission_template = db.Column(db.Text)
    contact_template = db.Column(db.Text)
    fee_template = db.Column(db.Text)
    general_template = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== TOP STUDENTS ====================
class TopStudent(db.Model):
    __tablename__ = 'top_students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    batch_year = db.Column(db.String(50))  # e.g. "SEE 2081"
    rank = db.Column(db.Integer, default=1)  # 1, 2, 3
    percentage = db.Column(db.String(20))
    photo = db.Column(db.String(255))
    achievement = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


print("Models loaded successfully")
