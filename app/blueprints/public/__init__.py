from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from app.models import (
    db, HeroSlide, Notice, NoticeCategory, News, NewsCategory, Blog, BlogCategory,
    Facility, WhatWeOffer, Commitment, PrincipalMessage, ChairmanMessage, Staff,
    GalleryAlbum, GalleryMedia, AdmissionEnquiry, ContactMessage, Subscriber,
    FAQ, Testimonial, Event, Download, PopupNotice, VisitorLog, SchoolSetting, TopStudent
)
from app.utils.helpers import slugify, sanitize_html, paginate_query, nepal_now
from datetime import datetime
import json

public_bp = Blueprint('public', __name__)

def log_visitor(page):
    try:
        ua = request.user_agent
        platform = (ua.platform or '').lower() if ua else ''
        log = VisitorLog(
            ip_address=request.remote_addr or '',
            user_agent=str(ua)[:500] if ua else '',
            page=page or '/',
            referrer=(request.referrer or '')[:500],
            device='mobile' if platform in ('android', 'iphone', 'ipad') else 'desktop',
            browser=(ua.browser if ua and ua.browser else 'unknown')[:100],
            session_id=(request.cookies.get('session') or '')[:100]
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

@public_bp.route('/')
def home():
    try:
        log_visitor('/')
    except Exception:
        pass
    try:
        slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.display_order).all()
    except Exception:
        slides = []
    try:
        notices = Notice.query.filter_by(is_active=True).order_by(Notice.is_pinned.desc(), Notice.publish_date.desc()).limit(6).all()
    except Exception:
        notices = []
    try:
        news_list = News.query.filter_by(status='published').order_by(News.publish_date.desc()).limit(3).all()
    except Exception:
        news_list = []
    try:
        blogs = Blog.query.filter_by(status='published').order_by(Blog.publish_date.desc()).limit(3).all()
    except Exception:
        blogs = []
    try:
        facilities = Facility.query.filter_by(is_active=True).order_by(Facility.display_order).limit(6).all()
    except Exception:
        facilities = []
    try:
        offers = WhatWeOffer.query.filter_by(is_active=True).order_by(WhatWeOffer.display_order).all()
    except Exception:
        offers = []
    try:
        commitments = Commitment.query.filter_by(is_active=True).order_by(Commitment.display_order).all()
    except Exception:
        commitments = []
    try:
        principal = PrincipalMessage.query.filter_by(is_active=True).first()
    except Exception:
        principal = None
    try:
        chairman = ChairmanMessage.query.filter_by(is_active=True).first()
    except Exception:
        chairman = None
    try:
        gallery = GalleryMedia.query.filter_by(is_active=True, media_type='image').order_by(GalleryMedia.display_order).limit(8).all()
    except Exception:
        gallery = []
    try:
        testimonials = Testimonial.query.filter_by(is_active=True).order_by(Testimonial.display_order).limit(6).all()
    except Exception:
        testimonials = []
    try:
        popup = PopupNotice.query.filter_by(is_active=True).first()
    except Exception:
        popup = None
    try:
        top_students = TopStudent.query.filter_by(is_active=True).order_by(TopStudent.display_order).all()
    except Exception:
        top_students = []
    stats = {
        'students': '228+',
        'teachers': '25+',
        'years': '10+',
        'success': '95%',
    }
    try:
        stats['students'] = SchoolSetting.get('statistics_students') or '228+'
        stats['teachers'] = SchoolSetting.get('statistics_teachers') or '25+'
        stats['years'] = SchoolSetting.get('statistics_years') or '10+'
        stats['success'] = SchoolSetting.get('statistics_success') or '95%'
    except Exception:
        pass
    try:
        return render_template('public/pages/home.html',
            slides=slides, notices=notices, news_list=news_list, blogs=blogs,
            facilities=facilities, offers=offers, commitments=commitments,
            principal=principal, chairman=chairman, gallery=gallery,
            testimonials=testimonials, popup=popup, stats=stats, top_students=top_students
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('HOME TEMPLATE ERROR:', e)
        return render_template('public/pages/500.html'), 500


@public_bp.route('/about')
def about():
    log_visitor('/about')
    principal = PrincipalMessage.query.filter_by(is_active=True).first()
    chairman = ChairmanMessage.query.filter_by(is_active=True).first()
    return render_template('public/pages/about.html', principal=principal, chairman=chairman)

@public_bp.route('/history')
def history():
    return render_template('public/pages/history.html')

@public_bp.route('/mission')
def mission():
    return render_template('public/pages/mission.html')

@public_bp.route('/vision')
def vision():
    return render_template('public/pages/vision.html')

@public_bp.route('/principal-message')
def principal_message():
    principal = PrincipalMessage.query.filter_by(is_active=True).first()
    return render_template('public/pages/principal_message.html', principal=principal)

@public_bp.route('/chairman-message')
def chairman_message():
    chairman = ChairmanMessage.query.filter_by(is_active=True).first()
    return render_template('public/pages/chairman_message.html', chairman=chairman)

@public_bp.route('/teachers')
def teachers():
    teachers = Staff.query.filter_by(is_active=True, staff_type='teacher').order_by(Staff.display_order).all()
    return render_template('public/pages/teachers.html', teachers=teachers)

@public_bp.route('/staff')
def staff():
    staff_list = Staff.query.filter(Staff.is_active==True, Staff.staff_type.in_(['staff', 'admin'])).order_by(Staff.display_order).all()
    return render_template('public/pages/staff.html', staff_list=staff_list)

@public_bp.route('/facilities')
def facilities():
    facilities = Facility.query.filter_by(is_active=True).order_by(Facility.display_order).all()
    return render_template('public/pages/facilities.html', facilities=facilities)

@public_bp.route('/what-we-offer')
def what_we_offer():
    offers = WhatWeOffer.query.filter_by(is_active=True).order_by(WhatWeOffer.display_order).all()
    return render_template('public/pages/what_we_offer.html', offers=offers)

@public_bp.route('/gallery')
def gallery():
    albums = GalleryAlbum.query.filter_by(is_active=True).order_by(GalleryAlbum.display_order).all()
    return render_template('public/pages/gallery.html', albums=albums)

@public_bp.route('/gallery/<slug>')
def gallery_album(slug):
    album = GalleryAlbum.query.filter_by(slug=slug, is_active=True).first_or_404()
    media = GalleryMedia.query.filter_by(album_id=album.id, is_active=True).order_by(GalleryMedia.display_order).all()
    return render_template('public/pages/gallery_album.html', album=album, media=media)

@public_bp.route('/notices')
def notices():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    query = Notice.query.filter_by(is_active=True)
    if category:
        cat = NoticeCategory.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    query = query.order_by(Notice.is_pinned.desc(), Notice.publish_date.desc())
    pagination = paginate_query(query, page, 12)
    categories = NoticeCategory.query.all()
    return render_template('public/pages/notices.html', notices=pagination.items, pagination=pagination, categories=categories)

@public_bp.route('/notice/<slug>')
def notice_detail(slug):
    notice = Notice.query.filter_by(slug=slug, is_active=True).first_or_404()
    notice.views = (notice.views or 0) + 1
    db.session.commit()
    related = Notice.query.filter(Notice.id != notice.id, Notice.is_active==True).order_by(Notice.publish_date.desc()).limit(5).all()
    return render_template('public/pages/notice_detail.html', notice=notice, related=related)

@public_bp.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    query = News.query.filter_by(status='published').order_by(News.publish_date.desc())
    pagination = paginate_query(query, page, 9)
    return render_template('public/pages/news.html', news_list=pagination.items, pagination=pagination)

@public_bp.route('/news/<slug>')
def news_detail(slug):
    item = News.query.filter_by(slug=slug, status='published').first_or_404()
    item.views = (item.views or 0) + 1
    db.session.commit()
    related = News.query.filter(News.id != item.id, News.status=='published').order_by(News.publish_date.desc()).limit(3).all()
    return render_template('public/pages/news_detail.html', news=item, related=related)

@public_bp.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    query = Blog.query.filter_by(status='published').order_by(Blog.publish_date.desc())
    pagination = paginate_query(query, page, 9)
    return render_template('public/pages/blog.html', blogs=pagination.items, pagination=pagination)

@public_bp.route('/blog/<slug>')
def blog_detail(slug):
    item = Blog.query.filter_by(slug=slug, status='published').first_or_404()
    item.views = (item.views or 0) + 1
    db.session.commit()
    related = Blog.query.filter(Blog.id != item.id, Blog.status=='published').order_by(Blog.publish_date.desc()).limit(3).all()
    return render_template('public/pages/blog_detail.html', blog=item, related=related)

@public_bp.route('/admission')
def admission():
    return render_template('public/pages/admission.html')

@public_bp.route('/admission/enquiry', methods=['GET', 'POST'])
def admission_enquiry():
    if request.method == 'POST':
        enquiry = AdmissionEnquiry(
            student_name=sanitize_html(request.form.get('student_name', '')),
            guardian_name=sanitize_html(request.form.get('guardian_name', '')),
            phone=request.form.get('phone', '').strip(),
            email=request.form.get('email', '').strip(),
            address=sanitize_html(request.form.get('address', '')),
            interested_grade=request.form.get('interested_grade', ''),
            previous_school=sanitize_html(request.form.get('previous_school', '')),
            message=sanitize_html(request.form.get('message', '')),
            status='new',
            priority='normal',
            created_at=nepal_now()
        )
        db.session.add(enquiry)
        db.session.commit()
        flash('Thank you! Your admission enquiry has been submitted successfully. We will contact you soon.', 'success')
        return redirect(url_for('public.admission_enquiry'))
    return render_template('public/pages/admission_enquiry.html')

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = ContactMessage(
            name=sanitize_html(request.form.get('name', '')),
            phone=request.form.get('phone', '').strip(),
            email=request.form.get('email', '').strip(),
            subject=sanitize_html(request.form.get('subject', '')),
            message=sanitize_html(request.form.get('message', '')),
            status='new',
            created_at=nepal_now()
        )
        db.session.add(msg)
        db.session.commit()
        flash('Thank you for contacting us. We will get back to you soon.', 'success')
        return redirect(url_for('public.contact'))
    return render_template('public/pages/contact.html')

@public_bp.route('/privacy-policy')
def privacy():
    return render_template('public/pages/privacy.html')

@public_bp.route('/terms')
def terms():
    return render_template('public/pages/terms.html')

@public_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = {'notices': [], 'news': [], 'blogs': [], 'teachers': [], 'facilities': []}
    if q and len(q) >= 2:
        results['notices'] = Notice.query.filter(Notice.title.ilike(f'%{q}%'), Notice.is_active==True).limit(10).all()
        results['news'] = News.query.filter(News.title.ilike(f'%{q}%'), News.status=='published').limit(10).all()
        results['blogs'] = Blog.query.filter(Blog.title.ilike(f'%{q}%'), Blog.status=='published').limit(10).all()
        results['teachers'] = Staff.query.filter(Staff.name.ilike(f'%{q}%'), Staff.is_active==True).limit(10).all()
        results['facilities'] = Facility.query.filter(Facility.title.ilike(f'%{q}%'), Facility.is_active==True).limit(10).all()
    return render_template('public/pages/search.html', q=q, results=results)

@public_bp.route('/faq')
def faq():
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.display_order).all()
    return render_template('public/pages/faq.html', faqs=faqs)

@public_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email = request.form.get('email', '').strip().lower()
    if email and '@' in email:
        existing = Subscriber.query.filter_by(email=email).first()
        if not existing:
            sub = Subscriber(email=email, name=request.form.get('name', ''))
            db.session.add(sub)
            db.session.commit()
            flash('Successfully subscribed to our newsletter!', 'success')
        else:
            flash('You are already subscribed.', 'info')
    else:
        flash('Please enter a valid email address.', 'danger')
    return redirect(request.referrer or url_for('public.home'))

@public_bp.route('/sitemap.xml')
def sitemap():
    from flask import make_response
    pages = [
        {'loc': url_for('public.home', _external=True), 'priority': '1.0'},
        {'loc': url_for('public.about', _external=True), 'priority': '0.8'},
        {'loc': url_for('public.admission', _external=True), 'priority': '0.9'},
        {'loc': url_for('public.contact', _external=True), 'priority': '0.8'},
        {'loc': url_for('public.notices', _external=True), 'priority': '0.7'},
        {'loc': url_for('public.news', _external=True), 'priority': '0.7'},
        {'loc': url_for('public.blog', _external=True), 'priority': '0.7'},
        {'loc': url_for('public.gallery', _external=True), 'priority': '0.6'},
        {'loc': url_for('public.facilities', _external=True), 'priority': '0.6'},
        {'loc': url_for('public.teachers', _external=True), 'priority': '0.6'},
    ]
    for n in Notice.query.filter_by(is_active=True).all():
        pages.append({'loc': url_for('public.notice_detail', slug=n.slug, _external=True), 'priority': '0.5'})
    for n in News.query.filter_by(status='published').all():
        pages.append({'loc': url_for('public.news_detail', slug=n.slug, _external=True), 'priority': '0.5'})
    for b in Blog.query.filter_by(status='published').all():
        pages.append({'loc': url_for('public.blog_detail', slug=b.slug, _external=True), 'priority': '0.5'})
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        xml += f'  <url><loc>{p["loc"]}</loc><priority>{p["priority"]}</priority></url>\n'
    xml += '</urlset>'
    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@public_bp.route('/robots.txt')
def robots():
    return '''User-agent: *
Allow: /
Disallow: /admin/
Disallow: /auth/
Sitemap: /sitemap.xml
'''

@public_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    import os
    folder = current_app.config['UPLOAD_FOLDER']
    # Security: prevent path traversal
    safe = os.path.normpath(filename).replace('\\', '/').lstrip('/')
    if '..' in safe:
        from flask import abort
        abort(404)
    return send_from_directory(folder, safe)
