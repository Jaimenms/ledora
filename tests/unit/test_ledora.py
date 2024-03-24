from ledora import Ledora

class TestLedora:
    def test_analyse_words_1(self):

        words = ["atentamente", "acordaram", "olharam", "aproximaram-se"]

        positions_e = [1, 4, 6, 9], [1, 4, 6], [1, 4], [1, 4, 6, 8, 12]
        positions_c = Ledora.analyse_words(words=words, locale="pt_PT")

        for expected, calculated in zip(positions_e, positions_c):
            assert expected == calculated
