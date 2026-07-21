# Random facts module for Dreamcobots content display.

import random


FACTS = [
    "A group of flamingos is called a 'flamboyance'.",
    "Honey never spoils – archaeologists have found 3000-year-old honey in Egyptian tombs.",
    "Octopuses have three hearts and blue blood.",
    "The Eiffel Tower can grow up to 15 cm taller in summer due to thermal expansion.",
    "A day on Venus is longer than a year on Venus.",
    "Crows can recognize human faces and hold grudges.",
    "The shortest war in history lasted only 38–45 minutes (Anglo-Zanzibar War, 1896).",
    "Wombat droppings are cube-shaped.",
    "There are more possible chess games than atoms in the observable universe.",
    "Bananas are berries, but strawberries are not.",
    "A bolt of lightning is five times hotter than the surface of the sun.",
    "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
    "The first computer bug was an actual bug – a moth found in a Harvard computer in 1947.",
    "Water can boil and freeze at the same time (the triple point of water).",
    "There are more stars in the universe than grains of sand on all of Earth's beaches.",
    "Robots were first introduced into automotive manufacturing in 1961.",
    "The word 'robot' comes from the Czech word 'robota', meaning forced labor.",
    "NASA's Voyager 1 is the farthest human-made object from Earth.",
    "Python programming language is named after Monty Python, not the snake.",
    "The average person walks about 100,000 miles in a lifetime.",
]

TECH_FACTS = [
    "The first iPhone was released in 2007.",
    "Wi-Fi stands for 'Wireless Fidelity'.",
    "The internet was originally called ARPANET.",
    "The first domain name ever registered was symbolics.com in 1985.",
    "More than 3.5 billion Google searches are made every day.",
    "Bluetooth is named after King Harald Bluetooth, a Danish king from the 10th century.",
    "The first computer virus was created in 1983.",
    "There are over 700 programming languages in existence.",
    "The World Wide Web was invented by Tim Berners-Lee in 1989.",
    "The first 1GB hard drive cost $40,000 in 1980.",
]


class RandomFacts:
    """Provides random general and technology facts for Dreamcobots content display."""

    def __init__(self, custom_facts=None):
        self.general_facts = list(FACTS)
        self.tech_facts = list(TECH_FACTS)
        if custom_facts:
            self.general_facts.extend(custom_facts)

    def get_random_fact(self):
        """Return a random fact from the combined pool."""
        all_facts = self.general_facts + self.tech_facts
        return random.choice(all_facts)

    def get_tech_fact(self):
        """Return a random technology fact."""
        return random.choice(self.tech_facts)

    def get_general_fact(self):
        """Return a random general knowledge fact."""
        return random.choice(self.general_facts)

    def get_multiple(self, n=3):
        """Return n unique random facts."""
        all_facts = self.general_facts + self.tech_facts
        n = min(n, len(all_facts))
        return random.sample(all_facts, n)

    def display(self, fact=None):
        """Return a formatted fact string. Picks a random fact if none given."""
        if fact is None:
            fact = self.get_random_fact()
        return f"💡 Did you know?\n   {fact}"
