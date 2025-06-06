"""
K-Pop Sentiment Analysis Labels

Based on research into K-Pop fan discourse patterns, these 10 sentiment labels
capture the emotional and rhetorical stances within K-Pop communities.
"""

SENTIMENT_LABELS = {
    1: {
        "name": "ENTHUSIASTIC_SUPPORT",
        "description": "Highly positive, energetic support for idols/groups",
        "keywords": ["love", "amazing", "perfect", "queen", "king", "talent", "slay", "iconic"],
        "risk_level": "low",
        "examples": [
            "OMG they absolutely SLAYED this performance! 🔥",
            "This is why they're the best group ever! Pure talent!",
            "I'm so proud of them, they deserve all the success!"
        ]
    },
    
    2: {
        "name": "NOSTALGIC_APPRECIATION", 
        "description": "Warm, reflective sentiment about past eras or memories",
        "keywords": ["remember", "miss", "throwback", "classic", "golden era", "memories"],
        "risk_level": "low",
        "examples": [
            "I miss their debut era so much, those were simpler times",
            "This song brings back so many memories from 2018",
            "Remember when they used to do variety shows together?"
        ]
    },
    
    3: {
        "name": "ANTICIPATORY_EXCITEMENT",
        "description": "Forward-looking excitement about comebacks, releases, events",
        "keywords": ["comeback", "excited", "can't wait", "soon", "teaser", "announcement"],
        "risk_level": "low", 
        "examples": [
            "I can't wait for their comeback next month!",
            "The teaser looks incredible, this era will be amazing",
            "Counting down the days until the concert!"
        ]
    },
    
    4: {
        "name": "PROTECTIVE_DEFENSIVE",
        "description": "Defensive stance protecting idols from criticism or hate",
        "keywords": ["protect", "defend", "leave them alone", "haters", "jealous", "unfair"],
        "risk_level": "medium",
        "examples": [
            "Stop spreading hate about them, they work so hard",
            "These comments are so unfair, they don't deserve this",
            "We need to protect them from all this negativity"
        ]
    },
    
    5: {
        "name": "CRITICAL_DISAPPOINTMENT",
        "description": "Constructive criticism or disappointment from fans",
        "keywords": ["disappointed", "expected better", "not their best", "constructive", "feedback"],
        "risk_level": "medium",
        "examples": [
            "I love them but this song isn't their best work",
            "The styling choices were questionable this time",
            "I expected more from this comeback honestly"
        ]
    },
    
    6: {
        "name": "NEUTRAL_FACTUAL",
        "description": "Objective, informational content without emotional bias",
        "keywords": ["announced", "released", "scheduled", "confirmed", "reported", "according to"],
        "risk_level": "low",
        "examples": [
            "The album will be released on March 15th",
            "According to the company, the tour dates are confirmed",
            "The music video has reached 10 million views"
        ]
    },
    
    7: {
        "name": "COMPETITIVE_RIVALRY",
        "description": "Inter-fandom competition and comparison rhetoric",
        "keywords": ["better than", "outsold", "flop", "comparison", "charts", "numbers"],
        "risk_level": "high",
        "examples": [
            "They outsold your faves again, stay pressed",
            "The charts don't lie, we know who's really winning",
            "Your group could never reach these numbers"
        ]
    },
    
    8: {
        "name": "SARCASTIC_MOCKERY",
        "description": "Sarcastic or mocking tone, often passive-aggressive",
        "keywords": ["sure", "right", "okay", "imagine", "not", "literally"],
        "risk_level": "high",
        "examples": [
            "Sure, that performance was 'amazing' 🙄",
            "Imagine thinking they have talent lol",
            "Right, because lip-syncing is so impressive"
        ]
    },
    
    9: {
        "name": "MALICIOUS_COORDINATED",
        "description": "Coordinated attacks, smear campaigns, or malicious content",
        "keywords": ["expose", "thread", "receipts", "problematic", "cancel", "boycott"],
        "risk_level": "very_high",
        "examples": [
            "THREAD: Why [group] is problematic and needs to be cancelled",
            "Here are all the receipts proving they're fake",
            "Time to expose the truth about this overrated group"
        ]
    },
    
    10: {
        "name": "MIXED_CONFLICTED",
        "description": "Complex emotions showing internal conflict or mixed feelings",
        "keywords": ["but", "however", "mixed feelings", "conflicted", "on one hand"],
        "risk_level": "medium",
        "examples": [
            "I love the song but the music video was disappointing",
            "They're talented but I don't like their recent direction",
            "Mixed feelings about this comeback, some parts are great"
        ]
    }
}

def get_sentiment_label_info(label_id):
    """Get information about a specific sentiment label"""
    return SENTIMENT_LABELS.get(label_id, None)

def get_all_labels():
    """Get all sentiment labels"""
    return SENTIMENT_LABELS

def get_risk_levels():
    """Get unique risk levels"""
    return list(set(label["risk_level"] for label in SENTIMENT_LABELS.values()))