"""
DreamCareer assistant engine.

A lightweight, dependency-free intent engine that powers the
on-site AI agent. It understands natural-language questions about
the platform and answers with text plus quick-action buttons.
"""

import re


INTENTS = [
    {
        "name": "greeting",
        "patterns": [
            r"\b(hi|hello|hey|good (morning|afternoon|evening)|ayubowan)\b"
        ],
        "reply": (
            "Hello! I'm Dreamy, your DreamCareer guide. "
            "I can help you analyze a resume, explore job listings, "
            "or explain how your career report works."
        ),
        "actions": [
            {"label": "Analyze my CV", "url": "/#analyze"},
            {"label": "Browse jobs", "url": "/jobs"},
        ],
    },
    {
        "name": "how_to_analyze",
        "patterns": [
            r"how.*(analyz|upload|use|work)",
            r"(analyz|upload).*(resume|cv|pdf)",
            r"what does this (site|app|platform) do",
        ],
        "reply": (
            "It's simple: click 'Analyze my CV' on the home page, upload a PDF "
            "resume, and within seconds you'll get AI career predictions, a "
            "skill-gap analysis, course suggestions and matched live jobs."
        ),
        "actions": [
            {"label": "Analyze my CV", "url": "/#analyze"},
        ],
    },
    {
        "name": "find_jobs",
        "patterns": [
            r"\b(job|jobs|vacanc|opening|hiring|career opportunity)",
            r"find.*(job|work)",
        ],
        "reply": (
            "We collect live vacancies from Sri Lankan job boards "
            "(TopJobs.lk and XpressJobs) every time the scraper runs. "
            "You can search by keyword or filter by field."
        ),
        "actions": [
            {"label": "Browse all jobs", "url": "/jobs"},
            {"label": "IT jobs", "url": "/jobs?category=Information+Technology"},
        ],
    },
    {
        "name": "explain_prediction",
        "patterns": [
            r"(explain|why|meaning of).*(prediction|result|report|score|percent)",
            r"how.*(accuracy|accurate|model|ai work|work)",
            r"\bshap\b",
        ],
        "reply": (
            "Your report compares your resume against thousands of real career "
            "profiles. You see which careers fit you best, and the 'What "
            "influenced your match' section shows exactly which of your skills "
            "helped or hurt each result. If we're not confident, we say so and "
            "lean on your verified skills instead."
        ),
        "actions": [
            {"label": "Try it now", "url": "/#analyze"},
        ],
    },
    {
        "name": "skills",
        "patterns": [
            r"\b(skill|skills)\b",
            r"what.*detect",
            r"missing skill",
            r"skill gap",
        ],
        "reply": (
            "We spot 290+ skills in your resume — technical, business, industry "
            "and soft skills. The report shows which required skills you already "
            "have and which ones are missing for your best-match career."
        ),
        "actions": [
            {"label": "Analyze my CV", "url": "/#analyze"},
        ],
    },
    {
        "name": "qualifications",
        "patterns": [
            r"\b(course|courses|qualification|study|learn|certificat|degree|upskill)\b",
        ],
        "reply": (
            "Based on your missing skills, the report suggests real courses and "
            "qualifications from providers so you can close the gap before applying."
        ),
        "actions": [
            {"label": "Analyze my CV", "url": "/#analyze"},
        ],
    },
    {
        "name": "account",
        "patterns": [
            r"\b(login|log in|sign ?up|register|account|password)\b",
        ],
        "reply": (
            "Creating a free account lets you log in and keep your session. "
            "Use the 'Get started' button in the top-right corner."
        ),
        "actions": [
            {"label": "Register", "url": "/register"},
            {"label": "Log in", "url": "/login"},
        ],
    },
    {
        "name": "thanks",
        "patterns": [
            r"\b(thanks|thank you|thx|great|awesome|nice)\b",
        ],
        "reply": "You're most welcome! Good luck with the career hunt.",
        "actions": [],
    },
]

FALLBACK_REPLIES = [
    "I'm not sure about that one. I can help with analyzing CVs, finding jobs, "
    "understanding your report, or skill gaps — what would you like to do?",
    "That's a bit outside my playbook! Try asking me about resume analysis, "
    "job listings, or how the AI predictions work.",
]


class CareerAssistant:
    """Rule-based conversational agent for platform navigation."""

    def __init__(self, intents=None):
        self.intents = intents or INTENTS

    def get_reply(self, message):
        """
        Returns {"reply": str, "actions": [{"label", "url"}], "intent": str}
        """

        if not isinstance(message, str) or not message.strip():
            return self._fallback()

        cleaned = message.lower().strip()[:300]

        for intent in self.intents:

            for pattern in intent["patterns"]:

                if re.search(pattern, cleaned):

                    return {
                        "reply": intent["reply"],
                        "actions": intent["actions"],
                        "intent": intent["name"],
                    }

        return self._fallback()

    def _fallback(self):

        import random

        return {
            "reply": random.choice(FALLBACK_REPLIES),
            "actions": [
                {"label": "Analyze my CV", "url": "/#analyze"},
                {"label": "Browse jobs", "url": "/jobs"},
            ],
            "intent": "fallback",
        }


ASSISTANT = CareerAssistant()
