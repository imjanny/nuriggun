from django.core.mail import EmailMessage
import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from article.models import Article
from user.models import EmailNotificationSettings


class sendEmail:
    @staticmethod
    def send_email(subject, message, to_email):
        email = EmailMessage(
            subject=subject,
            body=message,
            to=[to_email],
        )
        EmailThread(email).start()


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

@receiver(post_save, sender=Article)
def article_post_email_send(sender, instance, created, **kwargs):
    if created:
        subject = "{}님이 새로운 게시글을 작성하였습니다.".format(instance.user.nickname)

        message = "{}님이 새로운 게시글을 작성하였습니다. \n\n확인하기 → http://127.0.0.1:5500/article/detail.html?article_id={}".format(
            instance.user.nickname, instance.pk)  # 이메일 내용 (test)

        # message = "{}님이 새로운 게시글을 작성하였습니다. \n\n확인하기 → https://teamnuri.xyz/article/detail.html?article_id={}".format(instance.user.nickname, instance.pk) # 이메일 내용 (배포용)

        author = instance.user  # 글 작성자
        subscribers = author.subscribes.all()  # 글 작성자를 구독한 유저
        email_notification_ok = EmailNotificationSettings.objects.filter(
            email_notification=True)

        for subscriber in subscribers:
            if subscriber.email in email_notification_ok.values_list('user__email', flat=True):
                to_email = subscriber.email
                sendEmail.send_email(subject, message, to_email)
