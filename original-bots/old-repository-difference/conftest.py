import pytest

@pytest.fixture
def conversational_data():
    return {
        "contract_keywords": ["contract", "grant", "federal", "procurement", "bid"],
        "greetings": ["Hello", "Hi", "Hey", "Good morning", "Welcome"],
        "bot_commands": ["help", "start", "stop", "status", "list"],
        "affirmations": ["Yes", "Sure", "Absolutely", "Of course", "Definitely"],
        "queries": ["Help me", "How do I", "What is", "Can you", "Please help"],
        "farewells": ["Goodbye", "Bye", "See you", "Farewell", "Take care"],
    }
