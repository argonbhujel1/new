import os
import re
import uuid
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import bleach

# Nepal Standard Time (UTC+5:45)
NEPAL_TZ = timezone(timedelta(hours=5, minutes=45))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def _cloudinary_configured():
    try:
        name = current_app.config.get('CLOUDINARY_CLOUD_NAME') or ''
        key = current_app.config.get('CLOUDINARY_API_KEY') or ''
        secret = current_app.config.get('CLOUDINARY_API_SECRET') or ''
        url = current_app.config.get('CLOUDINARY_URL') or ''
        if url and 'cloudinary://' in url:
            return True
        return bool(name and key and secret)
    except Exception:
        return False


def save_file(file, folder='general'):
    """Save uploaded file to Cloudinary (preferred) or local disk.
    Returns Cloudinary URL (https://...) or relative path like 'gallery/abc.jpg' or None.
    """
    if not file or not getattr(file, 'filename', None) or not file.filename.strip():
        return None
    if not allowed_file(file.filename):
        return None
    try:
        # --- Cloudinary ---
        if _cloudinary_configured():
            try:
                import cloudinary
                import cloudinary.uploader
                cfg = current_app.config
                if cfg.get('CLOUDINARY_URL'):
                    cloudinary.config(cloudinary_url=cfg['CLOUDINARY_URL'])
                else:
                    cloudinary.config(
                        cloud_name=cfg.get('CLOUDINARY_CLOUD_NAME'),
                        api_key=cfg.get('CLOUDINARY_API_KEY'),
                        api_secret=cfg.get('CLOUDINARY_API_SECRET'),
                        secure=True
                    )
                public_id = f"nva/{folder}/{uuid.uuid4().hex}"
                result = cloudinary.uploader.upload(
                    file,
                    public_id=public_id,
                    folder=None,
                    resource_type='image',
                    overwrite=False,
                    quality='auto:good',
                    fetch_format='auto'
                )
                url = result.get('secure_url') or result.get('url')
                if url:
                    print('Cloudinary upload OK:', url[:80])
                    return url
            except Exception as e:
                print('Cloudinary upload failed, falling back to local:', e)

        # --- Local fallback ---
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = uuid.uuid4().hex + '.' + ext
        upload_root = current_app.config['UPLOAD_FOLDER']
        folder_path = os.path.join(upload_root, folder)
        os.makedirs(folder_path, exist_ok=True)
        filepath = os.path.join(folder_path, filename)
        # file may have been read by cloudinary; reset if possible
        try:
            file.stream.seek(0)
        except Exception:
            pass
        file.save(filepath)
        if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
            return None
        if ext in {'png', 'jpg', 'jpeg', 'webp'}:
            try:
                img = Image.open(filepath)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                max_size = (1600, 1600)
                try:
                    img.thumbnail(max_size, Image.LANCZOS)
                except Exception:
                    img.thumbnail(max_size)
                img.save(filepath, optimize=True, quality=85)
            except Exception as e:
                print('Image compress skip:', e)
        return folder + '/' + filename
    except Exception as e:
        print('save_file error:', e)
        return None


def media_url(path):
    """Return full URL for stored media (Cloudinary URL or local uploads path)."""
    if not path:
        return ''
    path = str(path).strip()
    if path.startswith('http://') or path.startswith('https://'):
        return path
    try:
        from flask import url_for, has_request_context
        if has_request_context():
            return url_for('public.uploaded_file', filename=path)
    except Exception:
        pass
    return '/uploads/' + path.lstrip('/')


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:200]


def sanitize_html(html):
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'table', 'thead', 'tbody',
        'tr', 'th', 'td', 'div', 'span', 'iframe'
    ]
    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'allowfullscreen']
    }
    return bleach.clean(html or '', tags=allowed_tags, attributes=allowed_attrs, strip=True)


def format_datetime(dt, fmt='%d %b %Y'):
    if dt:
        return dt.strftime(fmt)
    return ''


def get_file_size(path):
    try:
        size = os.path.getsize(path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except Exception:
        return "0 B"


def paginate_query(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)


def notify_subscribers(subject, body_text):
    """Send email notification to all active subscribers about new notice/news."""
    try:
        from app.models import Subscriber, EmailLog, db
        from app import mail
        from flask_mail import Message
        subs = Subscriber.query.filter_by(is_active=True).all()
        if not subs:
            return 0
        sent = 0
        for s in subs:
            try:
                msg = Message(subject=subject, recipients=[s.email], body=body_text)
                mail.send(msg)
                log = EmailLog(
                    to_email=s.email,
                    subject=subject,
                    body=body_text,
                    status='sent',
                    sent_at=datetime.utcnow()
                )
                db.session.add(log)
                sent += 1
            except Exception as e:
                log = EmailLog(
                    to_email=s.email,
                    subject=subject,
                    body=body_text,
                    status='failed',
                    error_message=str(e)
                )
                db.session.add(log)
        db.session.commit()
        return sent
    except Exception as e:
        print('notify_subscribers error:', e)
        return 0


def nepal_now():
    """Current time in Nepal Standard Time (UTC+5:45)."""
    return datetime.now(NEPAL_TZ).replace(tzinfo=None)


def to_nepal_time(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(NEPAL_TZ).replace(tzinfo=None)
