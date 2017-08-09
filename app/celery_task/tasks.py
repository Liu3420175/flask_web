from .celery import celery
from app.tool import sendEmail



@celery.task(name="send_email")
def send_email(_to=(),subject="ABC",file_path=("/home/abc/efd.pdf",)):
    sendEmail(_to,subject,file_path)