# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import EmailMessage
# from user.models import User
# from article.models import Article


# # 내가 구독한 사람이 게시글 작성 시 이메일 알림 발송
# @receiver(post_save, sender=Article)
# def article_post_email_send(sender, instance, created, **kwargs):
#     if created:
#         email_title = "{}님이 새로운 게시글을 작성하였습니다.".format(instance.user.nickname)
#         from_email = "nuriggunstaff@gmail.com"  # 발신 이메일 주소

#         email_content = "{}님이 새로운 게시글을 작성하였습니다. \n\n확인하기 → http://127.0.0.1:5500/article/detail.html?article_id={}".format(
#             instance.user.nickname, instance.pk)  # 본문 내용 (test)

#         # message = "{}님이 새로운 게시글을 작성하였습니다. \n\n확인하기 → https://teamnuri.xyz/article/detail.html?article_id={}".format(
#         #     instance.user.nickname, instance.pk)  # 본문 내용 (배포용)

#         author = instance.user
#         subscribers = author.subscribes.all()  # 글 작성자를 구독한 유저

#         for subscriber in subscribers:
#             to = [subscriber.email]
#             EmailMessage(subject=email_title, body=email_content,
#                          to=to, from_email=from_email).send()
