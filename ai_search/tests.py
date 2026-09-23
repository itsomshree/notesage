import math

from django.test import SimpleTestCase

from .services import embed_text


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


class EmbedtextTests(SimpleTestCase):
    def test_returns_expected_dimension(self):
        vector = embed_text("Grocery list: eggs, milk, bread")
        self.assertEqual(len(vector), 384)

    def test_is_deterministic(self):
        text = "Meeting notes form the Q3 planning session"
        self.assertEqual(embed_text(text), embed_text(text))

    def test_similar_texts_are_closer_than_dissimilar_ones(self):
        base = embed_text("My favorite pasta recipe with garlic and olive oil")
        similar = embed_text("A simple recipe for garlic pasta")
        different = embed_text("Quarterly budget review meeting agenda")

        sim_to_similar = cosine_similarity(base, similar)
        sim_to_different = cosine_similarity(base, different)

        self.assertGreater(sim_to_similar, sim_to_different)
