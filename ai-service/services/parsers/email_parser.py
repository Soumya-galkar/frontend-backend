from email import policy
from email.parser import BytesParser


def extract_text_from_email(file_path):

    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = msg["subject"] or ""
    sender = msg["from"] or ""
    receiver = msg["to"] or ""
    date = msg["date"] or ""

    body = ""

    if msg.is_multipart():

        for part in msg.walk():

            content_type = part.get_content_type()

            if content_type == "text/plain":

                try:
                    body += part.get_content()
                except:
                    pass

    else:

        body = msg.get_content()

    text = f"""
Subject: {subject}

From: {sender}

To: {receiver}

Date: {date}

Body:

{body}
"""

    return [
        {
            "page_number": 1,
            "text": text
        }
    ]