from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from app.models import (
    db, User, Role, ActivityLog, SchoolSetting, HeroSlide, Notice, NoticeCategory,
    News, NewsCategory, Blog, BlogCategory, Facility, WhatWeOffer, Commitment,
    PrincipalMessage, ChairmanMessage, Staff, GalleryAlbum, GalleryMedia,
    AdmissionEnquiry, EnquiryReply, ContactMessage, ContactReply, Subscriber,
    FAQ, Testimonial, Event, Download, PopupNotice, VisitorLog, EmailLog,
    AISetting, AIReplyLog, BlogComment, TopStudent
)
from app.utils.helpers import save_file, slugify, sanitize_html, paginate_query, get_file_size
import os
import shutil
import csv
import io
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_active:
            flash('Account deactivated.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def log_activity(action, details=''):
    try:
        log = ActivityLog(
            user_id=current_user.id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:255] if request.user_agent else ''
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass

# ==================== DASHBOARD ====================
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    
    stats = {
        'today_visitors': VisitorLog.query.filter(db.func.date(VisitorLog.created_at) == today).count(),
        'monthly_visitors': VisitorLog.query.filter(VisitorLog.created_at >= month_start).count(),
        'total_enquiries': AdmissionEnquiry.query.count(),
        'unread_enquiries': AdmissionEnquiry.query.filter_by(is_read=False).count(),
        'unread_contacts': ContactMessage.query.filter_by(is_read=False).count(),
        'total_notices': Notice.query.count(),
        'total_news': News.query.count(),
        'total_blogs': Blog.query.count(),
        'gallery_images': GalleryMedia.query.count(),
        'subscribers': Subscriber.query.filter_by(is_active=True).count(),
        'ai_replies': AIReplyLog.query.count(),
    }
    
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    recent_enquiries = AdmissionEnquiry.query.order_by(AdmissionEnquiry.created_at.desc()).limit(5).all()
    recent_contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    # Visitor chart data (last 7 days)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%d %b'))
        chart_data.append(VisitorLog.query.filter(db.func.date(VisitorLog.created_at) == d).count())
    
    ai_setting = AISetting.query.first()
    
    return render_template('admin/dashboard/index.html',
        stats=stats, recent_activities=recent_activities,
        recent_enquiries=recent_enquiries, recent_contacts=recent_contacts,
        chart_labels=json.dumps(chart_labels), chart_data=json.dumps(chart_data),
        ai_setting=ai_setting
    )

# ==================== SCHOOL SETTINGS ====================
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        fields = [
            'school_name', 'address', 'phone', 'mobile', 'email', 'website',
            'google_map', 'latitude', 'longitude', 'opening_time', 'closing_time',
            'facebook', 'instagram', 'tiktok', 'linkedin', 'youtube', 'whatsapp',
            'footer_text', 'seo_title', 'meta_description', 'meta_keywords',
            'about_school', 'history', 'mission', 'vision', 'school_introduction',
            'statistics_students', 'statistics_teachers', 'statistics_years', 'statistics_success', 'display_email', 'theme_primary', 'theme_secondary', 'theme_accent'
        ]
        for f in fields:
            val = request.form.get(f, '')
            SchoolSetting.set(f, val)
        
        if 'logo' in request.files and request.files['logo'].filename:
            path = save_file(request.files['logo'], 'logos')
            if path:
                SchoolSetting.set('logo', path, 'image')
        if 'favicon' in request.files and request.files['favicon'].filename:
            path = save_file(request.files['favicon'], 'logos')
            if path:
                SchoolSetting.set('favicon', path, 'image')
        if 'about_image' in request.files and request.files['about_image'].filename:
            path = save_file(request.files['about_image'], 'logos')
            if path:
                SchoolSetting.set('about_image', path, 'image')
        if 'teachers_group_photo' in request.files and request.files['teachers_group_photo'].filename:
            path = save_file(request.files['teachers_group_photo'], 'staff')
            if path:
                SchoolSetting.set('teachers_group_photo', path, 'image')
        
        log_activity('update_settings', 'Updated school settings')
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
    
    settings_dict = {s.key: s.value for s in SchoolSetting.query.all()}
    return render_template('admin/settings/index.html', settings=settings_dict)

# ==================== HERO SLIDER ====================
@admin_bp.route('/slider')
@admin_required
def slider_list():
    slides = HeroSlide.query.order_by(HeroSlide.display_order).all()
    return render_template('admin/settings/slider.html', slides=slides)

@admin_bp.route('/slider/add', methods=['GET', 'POST'])
@admin_required
def slider_add():
    if request.method == 'POST':
        slide = HeroSlide(
            heading=request.form.get('heading'),
            sub_heading=request.form.get('sub_heading'),
            description=request.form.get('description'),
            button_text=request.form.get('button_text'),
            button_url=request.form.get('button_url'),
            display_order=int(request.form.get('display_order', 0)),
            is_active=bool(request.form.get('is_active'))
        )
        if 'image' in request.files and request.files['image'].filename:
            slide.image = save_file(request.files['image'], 'slider')
        db.session.add(slide)
        db.session.commit()
        log_activity('add_slide', f'Added slide: {slide.heading}')
        flash('Slide added.', 'success')
        return redirect(url_for('admin.slider_list'))
    return render_template('admin/settings/slider_form.html', slide=None)

@admin_bp.route('/slider/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def slider_edit(id):
    slide = HeroSlide.query.get_or_404(id)
    if request.method == 'POST':
        slide.heading = request.form.get('heading')
        slide.sub_heading = request.form.get('sub_heading')
        slide.description = request.form.get('description')
        slide.button_text = request.form.get('button_text')
        slide.button_url = request.form.get('button_url')
        slide.display_order = int(request.form.get('display_order', 0))
        slide.is_active = bool(request.form.get('is_active'))
        if 'image' in request.files and request.files['image'].filename:
            slide.image = save_file(request.files['image'], 'slider')
        db.session.commit()
        flash('Slide updated.', 'success')
        return redirect(url_for('admin.slider_list'))
    return render_template('admin/settings/slider_form.html', slide=slide)

@admin_bp.route('/slider/delete/<int:id>', methods=['POST'])
@admin_required
def slider_delete(id):
    slide = HeroSlide.query.get_or_404(id)
    db.session.delete(slide)
    db.session.commit()
    flash('Slide deleted.', 'success')
    return redirect(url_for('admin.slider_list'))

# ==================== NOTICES ====================
@admin_bp.route('/notices')
@admin_required
def notices_list():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    query = Notice.query
    if q:
        query = query.filter(Notice.title.ilike(f'%{q}%'))
    query = query.order_by(Notice.publish_date.desc())
    pagination = paginate_query(query, page, 20)
    return render_template('admin/notices/list.html', notices=pagination.items, pagination=pagination, q=q)

@admin_bp.route('/notices/add', methods=['GET', 'POST'])
@admin_required
def notices_add():
    if request.method == 'POST':
        title = request.form.get('title')
        notice = Notice(
            title=title,
            slug=slugify(title) + '-' + str(int(datetime.utcnow().timestamp())),
            content=sanitize_html(request.form.get('content')),
            category_id=request.form.get('category_id') or None,
            is_featured=bool(request.form.get('is_featured')),
            is_important=bool(request.form.get('is_important')),
            is_pinned=bool(request.form.get('is_pinned')),
            is_active=bool(request.form.get('is_active')),
            created_by=current_user.id
        )
        if 'attachment' in request.files and request.files['attachment'].filename:
            notice.attachment = save_file(request.files['attachment'], 'notices')
        db.session.add(notice)
        db.session.commit()
        if notice.is_active:
            try:
                from app.utils.helpers import notify_subscribers
                body = "New Notice from New Vision Academy, Urlabari-8, Morang\n\n" + (notice.title or "") + "\n\n" + ((notice.content or "")[:500])
                notify_subscribers("New Notice: " + (notice.title or "") + " | New Vision Academy", body)
            except Exception as e:
                print("Notify error:", e)

        flash('Notice created.', 'success')
        return redirect(url_for('admin.notices_list'))
    categories = NoticeCategory.query.all()
    return render_template('admin/notices/form.html', notice=None, categories=categories)

@admin_bp.route('/notices/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def notices_edit(id):
    notice = Notice.query.get_or_404(id)
    if request.method == 'POST':
        notice.title = request.form.get('title')
        notice.content = sanitize_html(request.form.get('content'))
        notice.category_id = request.form.get('category_id') or None
        notice.is_featured = bool(request.form.get('is_featured'))
        notice.is_important = bool(request.form.get('is_important'))
        notice.is_pinned = bool(request.form.get('is_pinned'))
        notice.is_active = bool(request.form.get('is_active'))
        if 'attachment' in request.files and request.files['attachment'].filename:
            notice.attachment = save_file(request.files['attachment'], 'notices')
        db.session.commit()
        flash('Notice updated.', 'success')
        return redirect(url_for('admin.notices_list'))
    categories = NoticeCategory.query.all()
    return render_template('admin/notices/form.html', notice=notice, categories=categories)

@admin_bp.route('/notices/delete/<int:id>', methods=['POST'])
@admin_required
def notices_delete(id):
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted.', 'success')
    return redirect(url_for('admin.notices_list'))

# ==================== NEWS ====================
@admin_bp.route('/news')
@admin_required
def news_list():
    page = request.args.get('page', 1, type=int)
    pagination = paginate_query(News.query.order_by(News.publish_date.desc()), page, 20)
    return render_template('admin/news/list.html', news_list=pagination.items, pagination=pagination)

@admin_bp.route('/news/add', methods=['GET', 'POST'])
@admin_required
def news_add():
    if request.method == 'POST':
        title = request.form.get('title')
        item = News(
            title=title,
            slug=slugify(title) + '-' + str(int(datetime.utcnow().timestamp())),
            content=sanitize_html(request.form.get('content')),
            excerpt=request.form.get('excerpt'),
            category_id=request.form.get('category_id') or None,
            tags=request.form.get('tags'),
            status=request.form.get('status', 'draft'),
            is_featured=bool(request.form.get('is_featured')),
            meta_title=request.form.get('meta_title'),
            meta_description=request.form.get('meta_description'),
            author_id=current_user.id
        )
        if 'featured_image' in request.files and request.files['featured_image'].filename:
            item.featured_image = save_file(request.files['featured_image'], 'news')
        db.session.add(item)
        db.session.commit()
        if item.status == 'published':
            try:
                from app.utils.helpers import notify_subscribers
                body = "Latest News from New Vision Academy, Urlabari-8, Morang\n\n" + (item.title or "") + "\n\n" + ((item.excerpt or item.content or "")[:400])
                notify_subscribers("News: " + (item.title or "") + " | New Vision Academy", body)
            except Exception as e:
                print("Notify error:", e)

        flash('News created.', 'success')
        return redirect(url_for('admin.news_list'))
    categories = NewsCategory.query.all()
    return render_template('admin/news/form.html', news=None, categories=categories)

@admin_bp.route('/news/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def news_edit(id):
    item = News.query.get_or_404(id)
    if request.method == 'POST':
        item.title = request.form.get('title')
        item.content = sanitize_html(request.form.get('content'))
        item.excerpt = request.form.get('excerpt')
        item.category_id = request.form.get('category_id') or None
        item.tags = request.form.get('tags')
        item.status = request.form.get('status', 'draft')
        item.is_featured = bool(request.form.get('is_featured'))
        item.meta_title = request.form.get('meta_title')
        item.meta_description = request.form.get('meta_description')
        if 'featured_image' in request.files and request.files['featured_image'].filename:
            item.featured_image = save_file(request.files['featured_image'], 'news')
        db.session.commit()
        flash('News updated.', 'success')
        return redirect(url_for('admin.news_list'))
    categories = NewsCategory.query.all()
    return render_template('admin/news/form.html', news=item, categories=categories)

@admin_bp.route('/news/delete/<int:id>', methods=['POST'])
@admin_required
def news_delete(id):
    item = News.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('News deleted.', 'success')
    return redirect(url_for('admin.news_list'))

# ==================== BLOGS ====================
@admin_bp.route('/blogs')
@admin_required
def blogs_list():
    page = request.args.get('page', 1, type=int)
    pagination = paginate_query(Blog.query.order_by(Blog.publish_date.desc()), page, 20)
    return render_template('admin/blogs/list.html', blogs=pagination.items, pagination=pagination)

@admin_bp.route('/blogs/add', methods=['GET', 'POST'])
@admin_required
def blogs_add():
    if request.method == 'POST':
        title = request.form.get('title')
        item = Blog(
            title=title,
            slug=slugify(title) + '-' + str(int(datetime.utcnow().timestamp())),
            content=sanitize_html(request.form.get('content')),
            excerpt=request.form.get('excerpt'),
            category_id=request.form.get('category_id') or None,
            tags=request.form.get('tags'),
            status=request.form.get('status', 'draft'),
            is_featured=bool(request.form.get('is_featured')),
            meta_title=request.form.get('meta_title'),
            meta_description=request.form.get('meta_description'),
            author_id=current_user.id
        )
        if 'featured_image' in request.files and request.files['featured_image'].filename:
            item.featured_image = save_file(request.files['featured_image'], 'blogs')
        db.session.add(item)
        db.session.commit()
        flash('Blog created.', 'success')
        return redirect(url_for('admin.blogs_list'))
    categories = BlogCategory.query.all()
    return render_template('admin/blogs/form.html', blog=None, categories=categories)

@admin_bp.route('/blogs/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def blogs_edit(id):
    item = Blog.query.get_or_404(id)
    if request.method == 'POST':
        item.title = request.form.get('title')
        item.content = sanitize_html(request.form.get('content'))
        item.excerpt = request.form.get('excerpt')
        item.category_id = request.form.get('category_id') or None
        item.tags = request.form.get('tags')
        item.status = request.form.get('status', 'draft')
        item.is_featured = bool(request.form.get('is_featured'))
        if 'featured_image' in request.files and request.files['featured_image'].filename:
            item.featured_image = save_file(request.files['featured_image'], 'blogs')
        db.session.commit()
        flash('Blog updated.', 'success')
        return redirect(url_for('admin.blogs_list'))
    categories = BlogCategory.query.all()
    return render_template('admin/blogs/form.html', blog=item, categories=categories)

@admin_bp.route('/blogs/delete/<int:id>', methods=['POST'])
@admin_required
def blogs_delete(id):
    item = Blog.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Blog deleted.', 'success')
    return redirect(url_for('admin.blogs_list'))

# ==================== STAFF ====================
@admin_bp.route('/staff')
@admin_required
def staff_list():
    staff = Staff.query.order_by(Staff.display_order).all()
    return render_template('admin/staff/list.html', staff=staff)

@admin_bp.route('/staff/add', methods=['GET', 'POST'])
@admin_required
def staff_add():
    if request.method == 'POST':
        s = Staff(
            name=request.form.get('name'),
            position=request.form.get('position'),
            qualification=request.form.get('qualification'),
            experience=request.form.get('experience'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            biography=request.form.get('biography'),
            staff_type=request.form.get('staff_type', 'teacher'),
            display_order=int(request.form.get('display_order', 0)),
            is_active=bool(request.form.get('is_active'))
        )
        if 'photo' in request.files and request.files['photo'].filename:
            s.photo = save_file(request.files['photo'], 'staff')
        db.session.add(s)
        db.session.commit()
        flash('Staff added.', 'success')
        return redirect(url_for('admin.staff_list'))
    return render_template('admin/staff/form.html', staff=None)

@admin_bp.route('/staff/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def staff_edit(id):
    s = Staff.query.get_or_404(id)
    if request.method == 'POST':
        s.name = request.form.get('name')
        s.position = request.form.get('position')
        s.qualification = request.form.get('qualification')
        s.experience = request.form.get('experience')
        s.email = request.form.get('email')
        s.phone = request.form.get('phone')
        s.biography = request.form.get('biography')
        s.staff_type = request.form.get('staff_type', 'teacher')
        s.display_order = int(request.form.get('display_order', 0))
        s.is_active = bool(request.form.get('is_active'))
        if 'photo' in request.files and request.files['photo'].filename:
            s.photo = save_file(request.files['photo'], 'staff')
        db.session.commit()
        flash('Staff updated.', 'success')
        return redirect(url_for('admin.staff_list'))
    return render_template('admin/staff/form.html', staff=s)

@admin_bp.route('/staff/delete/<int:id>', methods=['POST'])
@admin_required
def staff_delete(id):
    s = Staff.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Staff deleted.', 'success')
    return redirect(url_for('admin.staff_list'))

# ==================== FACILITIES ====================
@admin_bp.route('/facilities')
@admin_required
def facilities_list():
    items = Facility.query.order_by(Facility.display_order).all()
    return render_template('admin/facilities/list.html', facilities=items, type='facility')

@admin_bp.route('/facilities/add', methods=['GET', 'POST'])
@admin_required
def facilities_add():
    if request.method == 'POST':
        f = Facility(
            title=request.form.get('title'),
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            display_order=int(request.form.get('display_order', 0)),
            is_active=bool(request.form.get('is_active'))
        )
        if 'image' in request.files and request.files['image'].filename:
            f.image = save_file(request.files['image'], 'facilities')
        db.session.add(f)
        db.session.commit()
        flash('Facility added.', 'success')
        return redirect(url_for('admin.facilities_list'))
    return render_template('admin/facilities/form.html', item=None, type='facility')

@admin_bp.route('/facilities/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def facilities_edit(id):
    f = Facility.query.get_or_404(id)
    if request.method == 'POST':
        f.title = request.form.get('title')
        f.description = request.form.get('description')
        f.icon = request.form.get('icon')
        f.display_order = int(request.form.get('display_order', 0))
        f.is_active = bool(request.form.get('is_active'))
        if 'image' in request.files and request.files['image'].filename:
            f.image = save_file(request.files['image'], 'facilities')
        db.session.commit()
        flash('Facility updated.', 'success')
        return redirect(url_for('admin.facilities_list'))
    return render_template('admin/facilities/form.html', item=f, type='facility')

@admin_bp.route('/facilities/delete/<int:id>', methods=['POST'])
@admin_required
def facilities_delete(id):
    f = Facility.query.get_or_404(id)
    db.session.delete(f)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.facilities_list'))

# ==================== ADMISSION ENQUIRIES ====================
@admin_bp.route('/admissions')
@admin_required
def admissions_list():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    q = request.args.get('q', '')
    query = AdmissionEnquiry.query
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(db.or_(
            AdmissionEnquiry.student_name.ilike(f'%{q}%'),
            AdmissionEnquiry.guardian_name.ilike(f'%{q}%'),
            AdmissionEnquiry.phone.ilike(f'%{q}%')
        ))
    query = query.order_by(AdmissionEnquiry.created_at.desc())
    pagination = paginate_query(query, page, 20)
    return render_template('admin/admissions/list.html', enquiries=pagination.items, pagination=pagination, status=status, q=q)

@admin_bp.route('/admissions/<int:id>', methods=['GET', 'POST'])
@admin_required
def admissions_view(id):
    enq = AdmissionEnquiry.query.get_or_404(id)
    if not enq.is_read:
        enq.is_read = True
        db.session.commit()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'reply':
            reply = EnquiryReply(
                enquiry_id=enq.id,
                user_id=current_user.id,
                message=request.form.get('message'),
                is_ai=False
            )
            db.session.add(reply)
            enq.status = request.form.get('status', enq.status)
            enq.internal_notes = request.form.get('internal_notes', enq.internal_notes)
            db.session.commit()
            flash('Reply added.', 'success')
        elif action == 'update':
            enq.status = request.form.get('status', enq.status)
            enq.priority = request.form.get('priority', enq.priority)
            enq.internal_notes = request.form.get('internal_notes', enq.internal_notes)
            db.session.commit()
            flash('Updated.', 'success')
        return redirect(url_for('admin.admissions_view', id=id))
    
    return render_template('admin/admissions/view.html', enquiry=enq)

@admin_bp.route('/admissions/export')
@admin_required
def admissions_export():
    enquiries = AdmissionEnquiry.query.order_by(AdmissionEnquiry.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Student', 'Guardian', 'Phone', 'Email', 'Grade', 'Status', 'Date'])
    for e in enquiries:
        writer.writerow([e.id, e.student_name, e.guardian_name, e.phone, e.email, e.interested_grade, e.status, e.created_at])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='admissions.csv')

# ==================== CONTACT MESSAGES ====================
@admin_bp.route('/contacts')
@admin_required
def contacts_list():
    page = request.args.get('page', 1, type=int)
    query = ContactMessage.query.order_by(ContactMessage.created_at.desc())
    pagination = paginate_query(query, page, 20)
    return render_template('admin/contacts/list.html', messages=pagination.items, pagination=pagination)

@admin_bp.route('/contacts/<int:id>', methods=['GET', 'POST'])
@admin_required
def contacts_view(id):
    msg = ContactMessage.query.get_or_404(id)
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    
    if request.method == 'POST':
        reply = ContactReply(
            contact_id=msg.id,
            user_id=current_user.id,
            message=request.form.get('message'),
            is_ai=False
        )
        db.session.add(reply)
        msg.status = 'replied'
        db.session.commit()
        flash('Reply added.', 'success')
        return redirect(url_for('admin.contacts_view', id=id))
    
    return render_template('admin/contacts/view.html', message=msg)

# ==================== PRINCIPAL / CHAIRMAN ====================
@admin_bp.route('/principal', methods=['GET', 'POST'])
@admin_required
def principal_edit():
    p = PrincipalMessage.query.first()
    if not p:
        p = PrincipalMessage()
        db.session.add(p)
        db.session.commit()
    if request.method == 'POST':
        p.name = request.form.get('name')
        p.designation = request.form.get('designation')
        p.message = request.form.get('message')
        p.is_active = bool(request.form.get('is_active'))
        if 'photo' in request.files and request.files['photo'].filename:
            p.photo = save_file(request.files['photo'], 'staff')
        db.session.commit()
        flash('Principal message updated.', 'success')
        return redirect(url_for('admin.principal_edit'))
    return render_template('admin/settings/message_form.html', item=p, title='Principal Message')

@admin_bp.route('/chairman', methods=['GET', 'POST'])
@admin_required
def chairman_edit():
    p = ChairmanMessage.query.first()
    if not p:
        p = ChairmanMessage()
        db.session.add(p)
        db.session.commit()
    if request.method == 'POST':
        p.name = request.form.get('name')
        p.designation = request.form.get('designation')
        p.message = request.form.get('message')
        p.is_active = bool(request.form.get('is_active'))
        if 'photo' in request.files and request.files['photo'].filename:
            p.photo = save_file(request.files['photo'], 'staff')
        db.session.commit()
        flash('Chairman message updated.', 'success')
        return redirect(url_for('admin.chairman_edit'))
    return render_template('admin/settings/message_form.html', item=p, title='Chairman Message')

# ==================== AI SETTINGS ====================
@admin_bp.route('/ai-settings', methods=['GET', 'POST'])
@admin_required
def ai_settings():
    setting = AISetting.query.first()
    if not setting:
        setting = AISetting()
        db.session.add(setting)
        db.session.commit()
    
    if request.method == 'POST':
        setting.is_enabled = bool(request.form.get('is_enabled'))
        setting.wait_hours = float(request.form.get('wait_hours', 3))
        setting.admission_template = request.form.get('admission_template')
        setting.contact_template = request.form.get('contact_template')
        setting.fee_template = request.form.get('fee_template')
        setting.general_template = request.form.get('general_template')
        db.session.commit()
        flash('AI settings updated.', 'success')
        return redirect(url_for('admin.ai_settings'))
    
    logs = AIReplyLog.query.order_by(AIReplyLog.created_at.desc()).limit(50).all()
    return render_template('admin/settings/ai.html', setting=setting, logs=logs)

# ==================== GALLERY ====================
@admin_bp.route('/gallery')
@admin_required
def gallery_list():
    albums = GalleryAlbum.query.order_by(GalleryAlbum.display_order).all()
    return render_template('admin/gallery/list.html', albums=albums)

@admin_bp.route('/gallery/album/add', methods=['GET', 'POST'])
@admin_required
def gallery_album_add():
    if request.method == 'POST':
        title = request.form.get('title')
        album = GalleryAlbum(
            title=title,
            slug=slugify(title),
            description=request.form.get('description'),
            display_order=int(request.form.get('display_order', 0)),
            is_active=True
        )
        db.session.add(album)
        db.session.commit()
        flash('Album created.', 'success')
        return redirect(url_for('admin.gallery_list'))
    return render_template('admin/gallery/album_form.html', album=None)

@admin_bp.route('/gallery/album/<int:id>/media', methods=['GET', 'POST'])
@admin_required
def gallery_media(id):
    album = GalleryAlbum.query.get_or_404(id)
    if request.method == 'POST':
        if 'files' in request.files:
            files = request.files.getlist('files')
            for f in files:
                if f.filename:
                    path = save_file(f, 'gallery')
                    if path:
                        media = GalleryMedia(album_id=album.id, file_path=path, media_type='image', title=f.filename)
                        db.session.add(media)
            db.session.commit()
            flash('Media uploaded.', 'success')
        return redirect(url_for('admin.gallery_media', id=id))
    media = GalleryMedia.query.filter_by(album_id=id).order_by(GalleryMedia.display_order).all()
    return render_template('admin/gallery/media.html', album=album, media=media)

# ==================== SUBSCRIBERS ====================
@admin_bp.route('/subscribers')
@admin_required
def subscribers_list():
    subs = Subscriber.query.order_by(Subscriber.subscribed_at.desc()).all()
    return render_template('admin/settings/subscribers.html', subscribers=subs)

# ==================== BACKUP ====================
@admin_bp.route('/backup')
@admin_required
def backup():
    return render_template('admin/settings/backup.html')

@admin_bp.route('/backup/create', methods=['POST'])
@admin_required
def backup_create():
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    backup_dir = current_app.config.get('BACKUP_FOLDER', os.path.join(current_app.instance_path, 'backups'))
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'school_backup_{timestamp}.db')
    shutil.copy2(db_path, backup_path)
    log_activity('backup', f'Created backup: {backup_path}')
    flash(f'Backup created: school_backup_{timestamp}.db', 'success')
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/download')
@admin_required
def backup_download():
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    return send_file(db_path, as_attachment=True, download_name='school_database.db')

# ==================== ACTIVITY LOGS ====================
@admin_bp.route('/logs')
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    pagination = paginate_query(ActivityLog.query.order_by(ActivityLog.created_at.desc()), page, 50)
    return render_template('admin/settings/logs.html', logs=pagination.items, pagination=pagination)

# ==================== ANALYTICS ====================
@admin_bp.route('/analytics')
@admin_required
def analytics():
    today = datetime.utcnow().date()
    stats = {
        'total_visitors': VisitorLog.query.count(),
        'today': VisitorLog.query.filter(db.func.date(VisitorLog.created_at) == today).count(),
        'devices': db.session.query(VisitorLog.device, db.func.count(VisitorLog.id)).group_by(VisitorLog.device).all(),
        'browsers': db.session.query(VisitorLog.browser, db.func.count(VisitorLog.id)).group_by(VisitorLog.browser).limit(10).all(),
        'pages': db.session.query(VisitorLog.page, db.func.count(VisitorLog.id)).group_by(VisitorLog.page).order_by(db.func.count(VisitorLog.id).desc()).limit(10).all(),
    }
    return render_template('admin/dashboard/analytics.html', stats=stats)


# ==================== TOP STUDENTS ====================
@admin_bp.route('/top-students')
@admin_required
def top_students_list():
    students = TopStudent.query.order_by(TopStudent.display_order).all()
    return render_template('admin/staff/top_students.html', students=students)

@admin_bp.route('/top-students/add', methods=['GET', 'POST'])
@admin_required
def top_students_add():
    if request.method == 'POST':
        s = TopStudent(
            name=request.form.get('name'),
            batch_year=request.form.get('batch_year'),
            rank=int(request.form.get('rank', 1)),
            percentage=request.form.get('percentage'),
            achievement=request.form.get('achievement'),
            display_order=int(request.form.get('display_order', 0)),
            is_active=bool(request.form.get('is_active'))
        )
        if 'photo' in request.files and request.files['photo'].filename:
            s.photo = save_file(request.files['photo'], 'staff')
        db.session.add(s)
        db.session.commit()
        flash('Top student added.', 'success')
        return redirect(url_for('admin.top_students_list'))
    return render_template('admin/staff/top_student_form.html', student=None)

@admin_bp.route('/top-students/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def top_students_edit(id):
    s = TopStudent.query.get_or_404(id)
    if request.method == 'POST':
        s.name = request.form.get('name')
        s.batch_year = request.form.get('batch_year')
        s.rank = int(request.form.get('rank', 1))
        s.percentage = request.form.get('percentage')
        s.achievement = request.form.get('achievement')
        s.display_order = int(request.form.get('display_order', 0))
        s.is_active = bool(request.form.get('is_active'))
        if 'photo' in request.files and request.files['photo'].filename:
            s.photo = save_file(request.files['photo'], 'staff')
        db.session.commit()
        flash('Updated.', 'success')
        return redirect(url_for('admin.top_students_list'))
    return render_template('admin/staff/top_student_form.html', student=s)

@admin_bp.route('/top-students/delete/<int:id>', methods=['POST'])
@admin_required
def top_students_delete(id):
    s = TopStudent.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Deleted.', 'success')
    return redirect(url_for('admin.top_students_list'))


@admin_bp.route('/ai-run-now', methods=['POST'])
@admin_required
def ai_run_now():
    """Manually trigger AI auto-reply check now."""
    try:
        from app.services.ai_reply import process_pending_replies
        process_pending_replies()
        flash('AI process ran. Check AI Reply logs and Email logs below.', 'success')
    except Exception as e:
        flash(f'AI process error: {e}', 'danger')
    return redirect(url_for('admin.ai_settings'))
