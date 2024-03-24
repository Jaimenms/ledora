from ledora import Ledora
import pyphen


class TestLedora:

    def test_analyse_words_1(self):

        words = ["atentamente", "acordaram", "olharam", "aproximaram"]

        positions_e = [1, 4, 6, 9], [1, 4, 6], [1, 4], [1, 4, 6, 8, 13]
        positions_c = Ledora.analyse_words(words=words, locale="pt_PT")

        for expected, calculated in zip(positions_e, positions_c):
            assert calculated == expected

    def test_analyse_words_2(self):

        words = ["outros", "bem-me-queremos-outros", "se", "se-se", "se-se-se", "sem-sem", "sem-sempre-sem", "disse-lhe", "bem-humorado"]

        positions_e = [2], [4, 7, 10, 12, 18], [], [3], [3, 6], [4], [4, 7, 11], [3, 6], [6, 8, 10]
        pp = pyphen.Pyphen(lang="pt_PT", left=1, right=1)

        for expected, word in zip(positions_e, words):
            calculated = Ledora.get_positions(word=word, pp=pp)
            assert calculated == expected
