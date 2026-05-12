"""
scam_detector.py
Keyword-based scam scoring engine for job/internship descriptions.
Each category has a weight; scores accumulate and are clamped to 0-100.
"""

import re

# ---------------------------------------------------------------------------
# Red-flag keyword database  (pattern, weight, human-readable reason)
# ---------------------------------------------------------------------------
RED_FLAGS = [
    # ── Money / Payment ─────────────────────────────────────────────────────
    (r'\b(pay|fee)\b',                           10, "Mentions payment or fees"),
    (r'\bregistration\s*(fee|charge|amount)\b',  20, "Charges a registration fee"),
    (r'\bsecurity\s*deposit\b',                  18, "Requests a security deposit"),
    (r'\btraining\s*(fee|cost|charge)\b',        18, "Charges for training materials"),
    (r'\bupfront\s*(payment|cost|fee)\b',        20, "Requires upfront payment"),
    (r'\brefundable\s*deposit\b',                15, "Mentions refundable deposit (common scam hook)"),
    (r'\bwire\s*transfer\b',                     15, "Requests wire transfer payment"),
    (r'\b(bitcoin|crypto|cryptocurrency|usdt)\b',15, "Mentions cryptocurrency"),
    
    # ── Too-Good Salary ──────────────────────────────────────────────────────
    (r'\b(earn|make|get)\s+\$?\d[\d,]*\s*(per\s*(day|hour|week)|\/day|\/hr)\b', 12,
     "High pay promised for short intervals"),
    (r'\bearn\s*(up\s*to\s*)?\$?\d{4,}\s*per\s*month\b',                        10,
     "High monthly earnings claim"),
    (r'\b(easy|quick|fast)\s*(money|cash|income|earning)\b',                     14,
     "Promises easy/quick money"),
    (r'\bwork\s*from\s*home\b',                                                  4,
     "Work from home (minor flag, context dependent)"),
    (r'\b(high|huge|unlimited)\s*income\b',                                      10,
     "Unrealistic income claim"),

    # ── Urgency / Pressure ───────────────────────────────────────────────────
    (r'\bact\s*now\b',                           10, "Creates urgency with 'Act Now'"),
    (r'\b(urgent|immediate)\b',                  5,  "Pressures immediate action"),
    (r'\blimited\s*(positions|slots|seats|openings)\b', 8, "False scarcity of positions"),
    (r'\bonly\s+\d+\s*(spots?|seats?|positions?)\s*(left|remaining|available)\b', 8,
     "Artificial scarcity of open spots"),
    (r'\btoday\s*only\b',                         8, "Time-pressure tactic 'Today Only'"),

    # ── No Experience / Anyone Can Apply ─────────────────────────────────────
    (r'\bno\s*(experience|qualification|skill)\s*required\b',  10,
     "Claims no experience required"),
    (r'\banyone\s+can\s+(join|apply|do\s+this)\b',             10,
     "Open to 'anyone' — lacks professional criteria"),
    (r'\bno\s*(resume|cv|interview)\b',                        12,
     "No resume or interview required"),
    (r'\bguaranteed\s*(job|placement|hire)\b',                 14, "Guarantees a job (unrealistic)"),

    # ── Suspicious Contact / Process ─────────────────────────────────────────
    (r'\bwhatsapp\b',                                          8, "Mentions WhatsApp for contact"),
    (r'\btelegram\b',                                          8, "Mentions Telegram for contact"),
    (r'\bgmail\.com\b',                                         6,
     "Uses personal Gmail instead of corporate email"),
    (r'\byahoo\.com\b',                                         6,
     "Uses personal Yahoo mail instead of corporate email"),
    (r'\bclick\s*(this\s*)?link\b',                             8, "Suspicious link-click instruction"),
    
    # ── Vague / Misleading Job Description ───────────────────────────────────
    (r'\bdata\s*entry\b',                                       6,
     "Data entry roles are often scammed"),
    (r'\bpackaging\b',                                          5, "Packaging job offer (often scam)"),
    (r'\b(mlm|multi.?level\s*market)\b',                       18, "Mentions MLM / multi-level marketing"),
    (r'\brefer\s*(and|&)\s*earn\b',                             10, "Refer-and-earn income model"),
    (r'\bpassive\s*income\b',                                   8,  "Promises passive income"),
    (r'\bbe\s+your\s+own\s+boss\b',                             6,  "Classic MLM phrase 'be your own boss'"),

    # ── Personal Data Abuse ───────────────────────────────────────────────────
    (r'\b(aadhar|aadhaar|pan\s*card|ssn|social\s*security)\b', 14,
     "Asks for sensitive government ID"),
    (r'\bbank\s*(account|details|info|number)\b', 16,
     "Requests bank account details"),

    # ── Generic Scam Phrases ─────────────────────────────────────────────────
    (r'\b100\s*%\s*(genuine|real|authentic|legitimate)\b',     10,
     "Overemphasis on being '100% genuine'"),
    (r'\bpart[- ]time\b',                                       4, "Part-time work (minor flag)"),
    (r'\bno\s*target\b',                                        6,
     "Claims 'no target' — often misleading"),
    (r'\bfree\s*(laptop|mobile|kit|office)\b',                 12,
     "Promises free equipment — common bait"),
    (r'\binvestment\b',                                         6, "Mentions investment"),
]


def analyze_job_description(text: str) -> dict:
    """
    Analyze a job description and return:
      - scam_score  : int 0-100
      - result      : 'Safe' | 'Medium Risk' | 'High Risk'
      - reasons     : list[str]
    """
    text_lower = text.lower()
    total_score = 0
    reasons = []
    seen_reasons = set()

    for pattern, weight, reason in RED_FLAGS:
        if re.search(pattern, text_lower):
            if reason not in seen_reasons:
                total_score += weight
                reasons.append(reason)
                seen_reasons.add(reason)

    # Clamp to 0-100
    scam_score = min(max(total_score, 0), 100)

    # Determine result label
    if scam_score >= 60:
        result = 'High Risk'
    elif scam_score >= 30:
        result = 'Medium Risk'
    else:
        result = 'Safe'

    return {
        'scam_score': scam_score,
        'result': result,
        'reasons': reasons
    }
