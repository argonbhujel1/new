from app.models import (
    db, User, Role, SchoolSetting, HeroSlide, Notice, NoticeCategory,
    News, NewsCategory, Blog, BlogCategory, Facility, WhatWeOffer,
    Commitment, PrincipalMessage, ChairmanMessage, Staff, FAQ,
    Testimonial, AISetting, GalleryAlbum, TopStudent
)
from datetime import datetime, timedelta

def seed_database():
    """Seed initial data if database is empty"""
    if User.query.first():
        return  # Already seeded
    
    print("Seeding database with sample data...")
    
    # Roles
    admin_role = Role(name='Super Admin', permissions='{"all": true}', description='Full access')
    editor_role = Role(name='Editor', permissions='{"notices": true, "news": true, "blogs": true, "gallery": true}', description='Content editor')
    db.session.add_all([admin_role, editor_role])
    db.session.flush()
    
    # Admin user
    admin = User(
        username='admin',
        email='admin@newvisionacademy.edu.np',
        full_name='System Administrator',
        role_id=admin_role.id,
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # School Settings
    settings = {
        'school_name': 'New Vision Academy',
        'logo': '',
        'favicon': '',
        'address': 'Urlabari-8, Morang, Koshi Province, Nepal',
        'phone': '+977-9841333476',
        'mobile': '+977-9841333476',
        'email': 'argonbhujel1@gmail.com',
        'website': 'https://newvisionacademy.edu.np',
        'google_map': 'https://maps.google.com/?q=26.64513162062879,87.63686430000001',
        'latitude': '26.64513162062879',
        'longitude': '87.63686430000001',
        'opening_time': '09:00 AM',
        'closing_time': '04:00 PM',
        'facebook': 'https://facebook.com/newvisionacademy',
        'instagram': 'https://instagram.com/newvisionacademy',
        'tiktok': '',
        'linkedin': '',
        'youtube': 'https://www.youtube.com/@NEWVISIONACADEMY-q2c',
        'whatsapp': '9779841333476',
        'footer_text': 'New Vision Academy, Urlabari-8, Morang — nurturing young minds with quality education from ECD to Grade 10. Building responsible and confident citizens for tomorrow.',
        'seo_title': 'New Vision Academy | Urlabari-8, Morang',
        'meta_description': 'New Vision Academy is a private co-educational day school in Urlabari-8, Morang, Koshi Province. Offering quality education from Early Childhood Development (ECD) to Grade 10 with 228+ students.',
        'meta_keywords': 'New Vision Academy, Urlabari, Morang, school Urlabari, best school Morang, admission Urlabari, private school Koshi',
        'about_school': 'New Vision Academy is a private co-educational day school located in Urlabari-8, Morang district of Koshi Province, Nepal. The school provides quality education from Early Childhood Development (ECD/Nursery) to Grade 10. With a student-centered approach, modern teaching methods, and a caring environment, we are committed to the holistic development of every child — academic excellence, character building, and life skills.',
        'history': 'New Vision Academy was established with a clear vision to bring quality private education to the Urlabari community in Morang. Over the years, the school has steadily grown and currently serves more than 220 students from ECD to Grade 10. The school continues to expand its facilities and academic programs while remaining rooted in the values of discipline, respect, and excellence.',
        'mission': 'To provide accessible, quality education from ECD to Grade 10 that develops knowledge, skills, values and confidence in every student so they can succeed in further studies and contribute positively to society.',
        'vision': 'To be recognized as one of the leading private schools in Urlabari and Morang region — known for academic excellence, caring teachers, and well-rounded students who are prepared for the future.',
        'school_introduction': 'Located in Urlabari-8, Morang, New Vision Academy is a co-educational day school offering classes from Early Childhood Development to Grade 10. We believe every child has unique potential. Through dedicated teachers, a safe learning environment, and a balance of academics and co-curricular activities, we prepare students for SEE and beyond while building strong character and confidence.',
        'statistics_students': '228+',
        'statistics_teachers': '25+',
        'statistics_years': '10+',
        'statistics_success': '95%',
        'about_image': '',
        'teachers_group_photo': '',
        'display_email': 'info@newvisionacademy.edu.np',
        'theme_primary': '#1a365d',
        'theme_secondary': '#c9a227',
        'theme_accent': '#e53e3e',
    }
    for key, value in settings.items():
        db.session.add(SchoolSetting(key=key, value=value))
    
    # Hero Slides
    slides = [
        HeroSlide(heading='Welcome to New Vision Academy', sub_heading='Shaping Tomorrow\'s Leaders', description='A place where excellence meets opportunity.', button_text='Apply Now', button_url='/admission', display_order=1, is_active=True),
        HeroSlide(heading='Quality Education for All', sub_heading='Nurturing Young Minds', description='Modern facilities and experienced faculty.', button_text='Explore Campus', button_url='/about', display_order=2, is_active=True),
        HeroSlide(heading='Admissions Open 2026', sub_heading='Join Our Family', description='Limited seats available. Apply today.', button_text='Enquire Now', button_url='/admission/enquiry', display_order=3, is_active=True),
    ]
    db.session.add_all(slides)
    
    # Categories
    nc = NoticeCategory(name='General', slug='general')
    nc2 = NoticeCategory(name='Exam', slug='exam')
    news_cat = NewsCategory(name='School News', slug='school-news')
    blog_cat = BlogCategory(name='Education', slug='education')
    db.session.add_all([nc, nc2, news_cat, blog_cat])
    db.session.flush()
    
    # Notices
    notices = [
        Notice(title='Admissions Open for Academic Year 2026-27', slug='admissions-open-2026', content='We are pleased to announce that admissions are now open for the academic year 2026-27. Limited seats available.', category_id=nc.id, is_featured=True, is_important=True, is_pinned=True, is_active=True, publish_date=datetime.utcnow()),
        Notice(title='Parent-Teacher Meeting Scheduled', slug='ptm-scheduled', content='Parent-Teacher Meeting will be held on 15th of next month. All parents are requested to attend.', category_id=nc.id, is_active=True, publish_date=datetime.utcnow() - timedelta(days=2)),
        Notice(title='Mid-Term Examination Routine', slug='midterm-routine', content='The mid-term examination routine has been published. Please check the notice board for details.', category_id=nc2.id, is_important=True, is_active=True, publish_date=datetime.utcnow() - timedelta(days=5)),
    ]
    db.session.add_all(notices)
    
    # News
    news_items = [
        News(title='New Vision Academy Wins Inter-School Science Fair', slug='science-fair-win', content='Our students secured the first position in the inter-school science fair held last week.', excerpt='Proud moment for New Vision Academy as our team bags top honors.', category_id=news_cat.id, status='published', is_featured=True, author_id=1, publish_date=datetime.utcnow()),
        News(title='Annual Sports Day Celebrated with Grandeur', slug='sports-day-2025', content='The annual sports day was celebrated with great enthusiasm and participation from all students.', excerpt='A day of sportsmanship and healthy competition.', category_id=news_cat.id, status='published', author_id=1, publish_date=datetime.utcnow() - timedelta(days=10)),
    ]
    db.session.add_all(news_items)
    
    # Blogs
    blogs = [
        Blog(title='The Importance of Holistic Education', slug='holistic-education', content='Holistic education focuses on the development of the whole child - academic, social, emotional, and physical.', excerpt='Why holistic approach matters in modern education.', category_id=blog_cat.id, status='published', is_featured=True, author_id=1, publish_date=datetime.utcnow()),
        Blog(title='Tips for Effective Parenting in Digital Age', slug='parenting-digital-age', content='In today\'s digital world, parenting comes with unique challenges. Here are some practical tips.', excerpt='Navigating parenting challenges in the digital era.', category_id=blog_cat.id, status='published', author_id=1, publish_date=datetime.utcnow() - timedelta(days=7)),
    ]
    db.session.add_all(blogs)
    
    # Facilities
    facilities = [
        Facility(title='Modern Classrooms', description='Spacious, well-ventilated classrooms equipped with smart boards and digital learning tools.', icon='fas fa-chalkboard-teacher', display_order=1),
        Facility(title='Science Laboratories', description='Fully equipped Physics, Chemistry and Biology labs for hands-on learning.', icon='fas fa-flask', display_order=2),
        Facility(title='Library & Resource Center', description='A rich collection of books, journals and digital resources for research and reading.', icon='fas fa-book-open', display_order=3),
        Facility(title='Sports Complex', description='Indoor and outdoor sports facilities including basketball, football, badminton and more.', icon='fas fa-running', display_order=4),
        Facility(title='Computer Lab', description='High-speed internet and modern computers for IT education and research.', icon='fas fa-laptop-code', display_order=5),
        Facility(title='Transportation', description='Safe and reliable school bus service covering major areas of Kathmandu valley.', icon='fas fa-bus', display_order=6),
    ]
    db.session.add_all(facilities)
    
    # What We Offer
    offers = [
        WhatWeOffer(title='Quality Academics', description='Rigorous curriculum aligned with national standards and international best practices.', icon='fas fa-graduation-cap', display_order=1),
        WhatWeOffer(title='Experienced Faculty', description='Dedicated and highly qualified teachers committed to student success.', icon='fas fa-user-tie', display_order=2),
        WhatWeOffer(title='Holistic Development', description='Focus on academics, sports, arts, and character building.', icon='fas fa-heart', display_order=3),
        WhatWeOffer(title='Safe Environment', description='Secure campus with CCTV and trained staff ensuring student safety.', icon='fas fa-shield-alt', display_order=4),
    ]
    db.session.add_all(offers)
    
    # Commitments
    commitments = [
        Commitment(title='Academic Excellence', description='We are committed to maintaining the highest standards of teaching and learning.', icon='fas fa-award', display_order=1),
        Commitment(title='Student Well-being', description='Every child\'s physical, emotional and mental well-being is our priority.', icon='fas fa-hands-helping', display_order=2),
        Commitment(title='Inclusive Education', description='We welcome and support students of all abilities and backgrounds.', icon='fas fa-users', display_order=3),
        Commitment(title='Continuous Improvement', description='We constantly innovate and improve our practices for better outcomes.', icon='fas fa-chart-line', display_order=4),
    ]
    db.session.add_all(commitments)
    
    # Principal & Chairman
    db.session.add(PrincipalMessage(
        name='Principal',
        designation='Principal',
        message='Welcome to New Vision Academy. It is my privilege to lead this institution dedicated to nurturing young minds. Our focus remains on academic excellence combined with strong values. We believe in creating an environment where every student can thrive and discover their potential. Together with our dedicated faculty and supportive parents, we strive to shape responsible future citizens.'
    ))
    db.session.add(ChairmanMessage(
        name='Chairman',
        designation='Chairman',
        message='As the Chairman of New Vision Academy, I am proud of the journey we have undertaken. Our vision is to provide world-class education that is accessible and transformative. We invest continuously in infrastructure, teacher development, and innovative teaching methodologies. I invite parents and guardians to join us in this noble mission of educating the next generation.'
    ))
    
    # Staff
    staff_list = [
        Staff(name='Ms. Anjali Rai', position='Vice Principal', qualification='M.Ed, B.Ed', experience='18 years', staff_type='admin', display_order=1, biography='Experienced educationist with a passion for student-centered learning.'),
        Staff(name='Mr. Binod Karki', position='Science Coordinator', qualification='M.Sc Physics', experience='12 years', staff_type='teacher', display_order=2),
        Staff(name='Ms. Priya Gurung', position='English Teacher', qualification='MA English', experience='10 years', staff_type='teacher', display_order=3),
        Staff(name='Mr. Suresh Adhikari', position='Mathematics Teacher', qualification='M.Sc Mathematics', experience='15 years', staff_type='teacher', display_order=4),
        Staff(name='Ms. Kabita Shrestha', position='Primary Coordinator', qualification='B.Ed', experience='14 years', staff_type='teacher', display_order=5),
        Staff(name='Mr. Deepak Poudel', position='IT Coordinator', qualification='B.Sc CSIT', experience='8 years', staff_type='staff', display_order=6),
    ]
    db.session.add_all(staff_list)
    
    # FAQs
    faqs = [
        FAQ(question='What is the admission process?', answer='Admissions are based on interaction with the child and parents, previous academic records, and availability of seats. Please fill the enquiry form or visit the school office.', category='Admission', display_order=1),
        FAQ(question='What are the school timings?', answer='School operates from 8:00 AM to 4:00 PM from Sunday to Friday. Saturday is a holiday.', category='General', display_order=2),
        FAQ(question='Is transportation available?', answer='Yes, we provide safe school bus services covering major routes in Kathmandu valley.', category='Facilities', display_order=3),
        FAQ(question='What curriculum do you follow?', answer='We follow the national curriculum prescribed by the Government of Nepal with enhanced learning modules.', category='Academics', display_order=4),
    ]
    db.session.add_all(faqs)
    
    # Testimonials
    testimonials = [
        Testimonial(name='Mrs. Sita Devi', designation='Parent of Grade 8 Student', content='New Vision Academy has been a wonderful place for my child. The teachers are caring and the environment is positive.', rating=5, display_order=1),
        Testimonial(name='Mr. Hari Bahadur', designation='Parent', content='Excellent academic results and focus on overall development. Highly recommended.', rating=5, display_order=2),
        Testimonial(name='Ms. Anita Karki', designation='Alumni Parent', content='Both my children studied here and are now successful professionals. Grateful to the school.', rating=5, display_order=3),
    ]
    db.session.add_all(testimonials)
    
    # AI Settings
    ai_setting = AISetting(
        is_enabled=True,
        wait_hours=3.0,
        admission_template='''Hello Mr./Mrs. {guardian_name},

Thank you for contacting New Vision Academy.

We have successfully received your enquiry regarding admission for Grade {grade}.

Your enquiry has been forwarded to our Admission Department.
One of our staff members will contact you shortly.

If your enquiry is urgent, please call
+977-9841333476

Thank you.
New Vision Academy
Urlabari-8, Morang
Admission Office''',
        contact_template='''Dear {name},

Thank you for reaching out to New Vision Academy.

We have received your message regarding "{subject}".
Our team will get back to you as soon as possible.

For urgent matters, please call us at +977-9841333476.

Best regards,
New Vision Academy
Urlabari-8, Morang
Admin Office''',
        fee_template='''Dear {name},

Thank you for your enquiry about fees at New Vision Academy.

Our fee structure varies by grade. Please visit the school office or call +977-9841333476 for detailed information.

We look forward to welcoming you.

Regards,
New Vision Academy''',
        general_template='''Dear {name},

Thank you for contacting New Vision Academy.

We have received your message and will respond shortly.

For immediate assistance, call +977-9841333476.

Best regards,
New Vision Academy'''
    )
    db.session.add(ai_setting)
    

    # Top Students (3 batches)
    top_students = [
        TopStudent(name='Anisha Rai', batch_year='SEE 2081', rank=1, percentage='92.5%', achievement='School Topper', display_order=1),
        TopStudent(name='Bikash Limbu', batch_year='SEE 2081', rank=2, percentage='90.2%', achievement='Second Position', display_order=2),
        TopStudent(name='Priya Karki', batch_year='SEE 2081', rank=3, percentage='88.8%', achievement='Third Position', display_order=3),
        TopStudent(name='Sagar Thapa', batch_year='SEE 2080', rank=1, percentage='91.0%', achievement='School Topper', display_order=4),
        TopStudent(name='Manisha Shrestha', batch_year='SEE 2080', rank=2, percentage='89.5%', achievement='Second Position', display_order=5),
        TopStudent(name='Rohit Dahal', batch_year='SEE 2080', rank=3, percentage='87.2%', achievement='Third Position', display_order=6),
        TopStudent(name='Kabita Gurung', batch_year='SEE 2079', rank=1, percentage='93.1%', achievement='School Topper', display_order=7),
        TopStudent(name='Dipesh Adhikari', batch_year='SEE 2079', rank=2, percentage='90.8%', achievement='Second Position', display_order=8),
        TopStudent(name='Sita Magar', batch_year='SEE 2079', rank=3, percentage='88.0%', achievement='Third Position', display_order=9),
    ]
    db.session.add_all(top_students)

    # Gallery album
    db.session.add(GalleryAlbum(title='Campus Life', slug='campus-life', description='Glimpses of our vibrant campus', is_active=True, display_order=1))
    
    db.session.commit()
    print("Database seeded successfully!")
    print("Admin login: admin / admin123")
