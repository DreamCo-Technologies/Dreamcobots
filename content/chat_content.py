# Chat and funny content module for Dreamcobots.
# Provides jokes, fun facts, and engaging chat responses.

import random


JOKES = [
    {"setup": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!"},
    {"setup": "Why did the robot go on a diet?", "punchline": "It had too many bytes!"},
    {
        "setup": "Why was the computer cold?",
        "punchline": "It left its Windows open!",
    },
    {
        "setup": "What do you call a sleeping dinosaur?",
        "punchline": "A dino-snore!",
    },
    {
        "setup": "Why did the programmer quit his job?",
        "punchline": "Because he didn't get arrays!",
    },
    {
        "setup": "How does a robot wave goodbye?",
        "punchline": "It waves its servo motors!",
    },
    {
        "setup": "What's a bot's favorite type of music?",
        "punchline": "Heavy metal… because of all the hardware!",
    },
    {
        "setup": "Why do programmers prefer dark mode?",
        "punchline": "Because light attracts bugs!",
    },
]

FUN_CHAT_RESPONSES = [
    "Beep boop! I'm processing your request at lightning speed! ⚡",
    "Did you know I can think faster than you can blink? 🤖",
    "I'm not just a bot – I'm your digital best friend! 😄",
    "Charging up… just kidding, I run on pure logic! 💡",
    "Let's make the world a smarter place, one command at a time. 🌍",
    "Fun fact: robots never get tired. Lucky us! 🔋",
    "Currently optimizing my joke database… please stand by! 😂",
]

GREETINGS = [
    "Hello, human! How can I assist you today?",
    "Hey there! Ready to do some amazing things together?",
    "Greetings! Your friendly Dreamcobot is online. 🤖",
    "Hi! I'm here and fully operational. What's on your mind?",
]


class ChatContent:
    """Provides jokes, fun responses, and engaging chat messages for bots."""

    def get_random_joke(self):
        """Return a random joke as a dict with 'setup' and 'punchline'."""
        return dict(random.choice(JOKES))

    def format_joke(self, joke=None):
        """Return a formatted joke string. Gets a random joke if none given."""
        if joke is None:
            joke = self.get_random_joke()
        return f"😄 {joke['setup']}\n   👉 {joke['punchline']}"

    def get_fun_response(self):
        """Return a random fun/witty response."""
        return random.choice(FUN_CHAT_RESPONSES)

    def get_greeting(self):
        """Return a random greeting message."""
        return random.choice(GREETINGS)

    def chat(self, user_input):
        """Respond to a user message with a relevant fun reply."""
        lower = user_input.lower()
        if any(word in lower for word in ["joke", "funny", "laugh"]):
            return self.format_joke()
        if any(word in lower for word in ["hi", "hello", "hey", "greet"]):
            return self.get_greeting()
        return self.get_fun_response()
