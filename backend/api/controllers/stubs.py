import random

responses = [
    "I'm here to help! Could you provide a bit more detail?",
    "I'm not sure I understood that. Can you rephrase your request?",
    "Thanks for your message. Let me think about that for a moment.",
    "I don't have enough information to answer accurately. Could you clarify?"
]

def LLM_response():
    return random.choice(responses)