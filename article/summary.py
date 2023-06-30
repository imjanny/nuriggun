import openai
import os
from dotenv import load_dotenv

from article.models import Article

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def summary(content):
    if content:
        queryset = Article.objects.all()
        if queryset.exists():
            summary_content = queryset.order_by("-id").first()
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt="Please summarize this news article in Korean, focusing only on the key points. Exclude any unnecessary information such as greetings or reporter information. The summary should be around 500 tokens. \n\n[News Article]"+content,
            max_tokens=500,
            temperature=0.3,
            n=1,
            stop=None,
        )
        summary = response.choices[0].text.strip()
        summary_content.summary = summary
        summary_content.save()
        return summary