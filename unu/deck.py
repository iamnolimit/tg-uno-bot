import random

from unu.card import cards


class Deck:
    def __init__(self, theme) -> None:
        self.theme = theme
        self.cards = [
            (color, value)
            for _ in range(2)
            for color in cards[theme]["CARDS"]["COLORS"]
            for value in cards[theme]["CARDS"]["VALUES"]
        ]
        self.cards += [
            ("x", car)
            for car in cards[theme]["CARDS"]["SPECIALS"]
            for _ in range(cards[theme]["CARDS"]["SPECIALS_INFO"][car][0])
        ]
        self._graveyard = []

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, amount):
        drawn = []
        for _ in range(amount):
            if not self.cards:
                # Deck is exhausted — reshuffle graveyard cards back in
                if self._graveyard:
                    self.cards = list(self._graveyard)
                    self._graveyard.clear()
                    self.shuffle()
                else:
                    break  # Truly no cards left anywhere
            if self.cards:
                drawn.append(self.cards.pop(0))
        return drawn

    def discard(self, card):
        """Put a played card into the graveyard for later reshuffling."""
        self._graveyard.append(card)
