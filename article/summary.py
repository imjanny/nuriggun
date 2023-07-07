import threading

import openai
import os
from dotenv import load_dotenv

from article.models import Article


class SummaryThread(threading.Thread):
    '''비동기전송 : 게시글 작성 시 요약 기능으로 인한 지연현상이 없어짐'''
    def __init__(self, content):
        self.content = content
        threading.Thread.__init__(self)

    def run(self):
        summary(self.content)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def summary(content):
    if content:
        queryset = Article.objects.all()
        if queryset.exists():
            summary_content = queryset.order_by("-id").first()
            response = openai.Completion.create(
            engine='text-davinci-003',
            prompt="Summarize the content in Korean, but keep it simple so that it does not exceed max_tokens=500. No greetings or reporter information is required."+content,
            max_tokens=500,
            temperature=0.3,
            n=1,
            stop=None,
        )

            answer = response.choices[0].text.strip()

            summary_content.summary = answer
            summary_content.save()
