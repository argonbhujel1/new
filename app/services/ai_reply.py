"""
AI Smart Auto Reply System
Monitors Admission Enquiries and Contact Messages.
If no admin reply within configured wait time (default 3 hours),
sends personalized acknowledgement email and logs the action.
"""
import threading
import time
from datetime import datetime, timedelta
# AI uses UTC for consistency; wait_hours supports fractions (e.g. 0.083 = 5 min)
from flask import current_app
from flask_mail import Message
from app.models import (
    db, AdmissionEnquiry, ContactMessage, EnquiryReply, ContactReply,
    AIReplyLog, AISetting, EmailLog
)

_scheduler_started = False
_app = None

def start_ai_scheduler(app):
    global _scheduler_started, _app
    if _scheduler_started:
        return
    _app = app
    _scheduler_started = True
    t = threading.Thread(target=_ai_worker, daemon=True)
    t.start()
    print("AI Auto-Reply scheduler started.")

def _ai_worker():
    while True:
        try:
            with _app.app_context():
                process_pending_replies()
        except Exception as e:
            print(f"AI worker error: {e}")
        time.sleep(30)  # Check every 30 seconds

def process_pending_replies():
    setting = AISetting.query.first()
    if not setting or not setting.is_enabled:
        return
    
    wait_hours = setting.wait_hours or 3.0
    cutoff = datetime.utcnow() - timedelta(minutes=max(1, int(float(wait_hours) * 60)))
    
    # Process Admission Enquiries
    enquiries = AdmissionEnquiry.query.filter(
        AdmissionEnquiry.ai_replied == False,
        AdmissionEnquiry.status == 'new',
        AdmissionEnquiry.created_at <= cutoff
    ).all()
    
    for enq in enquiries:
        # Check if any human reply exists
        human_reply = EnquiryReply.query.filter_by(enquiry_id=enq.id, is_ai=False).first()
        if human_reply:
            continue
        
        send_admission_ai_reply(enq, setting)
    
    # Process Contact Messages
    contacts = ContactMessage.query.filter(
        ContactMessage.ai_replied == False,
        ContactMessage.status == 'new',
        ContactMessage.created_at <= cutoff
    ).all()
    
    for contact in contacts:
        human_reply = ContactReply.query.filter_by(contact_id=contact.id, is_ai=False).first()
        if human_reply:
            continue
        
        send_contact_ai_reply(contact, setting)

def detect_intent(message_text):
    """Simple keyword-based intent detection"""
    if not message_text:
        return 'general'
    text = message_text.lower()
    if any(w in text for w in ['fee', 'fees', 'tuition', 'payment', 'cost']):
        return 'fee'
    if any(w in text for w in ['result', 'exam', 'marksheet', 'grade']):
        return 'result'
    if any(w in text for w in ['scholarship', 'discount', 'concession']):
        return 'scholarship'
    if any(w in text for w in ['hello', 'hi', 'namaste', 'good morning']):
        return 'greeting'
    if any(w in text for w in ['admission', 'admit', 'enroll', 'join']):
        return 'admission'
    return 'general'

def send_admission_ai_reply(enquiry, setting):
    template = setting.admission_template or ''
    body = template.format(
        guardian_name=enquiry.guardian_name or 'Parent/Guardian',
        grade=enquiry.interested_grade or 'the selected grade',
        student_name=enquiry.student_name or '',
        phone=enquiry.phone or ''
    )
    
    # Log reply
    reply = EnquiryReply(
        enquiry_id=enquiry.id,
        message=body,
        is_ai=True,
        is_email_sent=False
    )
    db.session.add(reply)
    
    enquiry.ai_replied = True
    enquiry.ai_replied_at = datetime.utcnow()
    enquiry.status = 'contacted'
    note = (enquiry.internal_notes or '') + '\n[AI Auto-Reply sent at ' + str(datetime.utcnow()) + ']'
    enquiry.internal_notes = note.strip()
    
    # Send email if email exists
    email_sent = False
    if enquiry.email:
        email_sent = _send_email(
            to=enquiry.email,
            subject=f"Acknowledgement - Admission Enquiry | New Vision Academy",
            body=body
        )
        reply.is_email_sent = email_sent
    
    # AI Log
    log = AIReplyLog(
        source_type='admission',
        source_id=enquiry.id,
        recipient_email=enquiry.email,
        recipient_name=enquiry.guardian_name,
        message_sent=body,
        wait_hours=setting.wait_hours
    )
    db.session.add(log)
    db.session.commit()
    print(f"AI replied to admission enquiry #{enquiry.id}")

def send_contact_ai_reply(contact, setting):
    intent = detect_intent(contact.message)
    
    if intent == 'fee':
        template = setting.fee_template or setting.general_template
    else:
        template = setting.contact_template or setting.general_template
    
    body = (template or '').format(
        name=contact.name or 'Sir/Madam',
        subject=contact.subject or 'your enquiry',
        message=contact.message or ''
    )
    
    reply = ContactReply(
        contact_id=contact.id,
        message=body,
        is_ai=True,
        is_email_sent=False
    )
    db.session.add(reply)
    
    contact.ai_replied = True
    contact.ai_replied_at = datetime.utcnow()
    contact.status = 'replied'
    
    email_sent = False
    if contact.email:
        email_sent = _send_email(
            to=contact.email,
            subject=f"Re: {contact.subject or 'Your Message'} | New Vision Academy",
            body=body
        )
        reply.is_email_sent = email_sent
    
    log = AIReplyLog(
        source_type='contact',
        source_id=contact.id,
        recipient_email=contact.email,
        recipient_name=contact.name,
        message_sent=body,
        wait_hours=setting.wait_hours
    )
    db.session.add(log)
    db.session.commit()
    print(f"AI replied to contact message #{contact.id}")

def _send_email(to, subject, body):
    if not to or '@' not in str(to):
        print('AI email skip: no valid recipient')
        return False
    try:
        from flask import current_app
        from app import mail
        # Ensure mail username is set
        if not current_app.config.get('MAIL_USERNAME'):
            print('AI email fail: MAIL_USERNAME not configured')
            log = EmailLog(to_email=to, subject=subject, body=body, status='failed', error_message='MAIL_USERNAME empty')
            db.session.add(log)
            db.session.commit()
            return False
        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        )
        mail.send(msg)
        log = EmailLog(to_email=to, subject=subject, body=body, status='sent', sent_at=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
        print(f'AI email SENT to {to}')
        return True
    except Exception as e:
        try:
            log = EmailLog(to_email=to, subject=subject, body=body, status='failed', error_message=str(e)[:500])
            db.session.add(log)
            db.session.commit()
        except Exception:
            pass
        print(f'Email send failed: {e}')
        return False
