import json

from flask import current_app
from google import genai
from google.genai import types


# =========================================================
# GEMINI CLIENT
# =========================================================

def get_ai_client():

    api_key = current_app.config.get("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(
        api_key=api_key
    )


# =========================================================
# DEFAULT ANALYSIS
# =========================================================

def default_analysis():

    return {
        "category": "other",
        "priority": "low",

        "summary": "",

        "needs_reply": False,
        "suggested_reply": "",

        "create_deal": False,
        "deal": None,

        "create_task": False,
        "task": None,

        "create_follow_up": False,
        "follow_up": None,

        "payment": None,
        "meeting": None
    }


# =========================================================
# EMAIL ANALYSIS
# =========================================================

def analyze_email(email_data):

    client = get_ai_client()

    if not client:
        return default_analysis()

    sender_name = email_data.get(
        "sender_name",
        ""
    )

    sender_email = email_data.get(
        "sender_email",
        ""
    )

    subject = email_data.get(
        "subject",
        ""
    )

    body = email_data.get(
        "body",
        ""
    )

    # Prevent very large emails
    body = body[:12000]

    prompt = f"""
You are the AI manager inside Manager X.

Manager X is a creator business management platform.

You manage business operations for solo creators.

You are NOT a chatbot.
You are NOT a content generator.

Your job is to understand business emails
and decide what operational work should happen.

EMAIL

Sender Name:
{sender_name}

Sender Email:
{sender_email}

Subject:
{subject}

Body:
{body}


CATEGORY

category must be exactly one of:

brand_deal
payment
collaboration
meeting
support
spam
other


PRIORITY

priority must be exactly one of:

urgent
high
medium
low
ignore


ANALYZE

Determine:

1. Email category
2. Priority
3. Short summary
4. Whether creator needs to reply
5. Whether a brand deal should be created
6. Whether a task should be created
7. Whether a follow-up should be created
8. Whether payment information exists
9. Whether meeting information exists
10. A short professional reply if useful


IMPORTANT RULES

Do not invent information.

Do not invent:

company names
money amounts
dates
deadlines
contact names
meeting times
meeting links

If information is missing,
use null.

Return JSON only.

Use exactly this structure:

{{
    "category": "brand_deal",

    "priority": "high",

    "summary": "Short summary",

    "needs_reply": true,

    "suggested_reply": "Short professional reply",

    "create_deal": true,

    "deal": {{
        "company": null,
        "contact_name": null,
        "contact_email": null,
        "deal_value": null,
        "currency": null,
        "status": "new"
    }},

    "create_task": true,

    "task": {{
        "title": null,
        "description": null,
        "priority": "high",
        "deadline": null
    }},

    "create_follow_up": false,

    "follow_up": {{
        "title": null,
        "follow_up_at": null
    }},

    "payment": {{
        "detected": false,
        "amount": null,
        "currency": null,
        "status": null,
        "due_date": null
    }},

    "meeting": {{
        "detected": false,
        "title": null,
        "start_time": null,
        "end_time": null,
        "meeting_link": null
    }}
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json"
            )
        )

        if not response.text:
            return default_analysis()

        result = json.loads(
            response.text
        )

        return result

    except Exception as error:

        print(
            "Gemini email analysis error:",
            error
        )

        return default_analysis()


# =========================================================
# REPLY GENERATOR
# =========================================================

def generate_reply(
    email_data,
    instruction=None
):

    client = get_ai_client()

    if not client:
        return None

    sender_name = email_data.get(
        "sender_name",
        ""
    )

    subject = email_data.get(
        "subject",
        ""
    )

    body = email_data.get(
        "body",
        ""
    )[:12000]

    extra_instruction = (
        instruction
        or
        "Write the most appropriate professional response."
    )

    prompt = f"""
You are writing an email reply
for a professional creator.

Original Sender:
{sender_name}

Subject:
{subject}

Original Email:
{body}

Instruction:
{extra_instruction}


RULES

Keep the reply concise.

Be professional and natural.

Do not invent facts.

Do not invent:

prices
dates
commitments
deadlines

Do not use unnecessary marketing language.

Return only the email reply.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )

        if not response.text:
            return None

        return response.text.strip()

    except Exception as error:

        print(
            "Gemini reply generation error:",
            error
        )

        return None