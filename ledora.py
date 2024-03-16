import sys
from sys import exit
import os
from os import environ
import pygame as pg
import pyphen
from time import sleep
from datetime import datetime
from random import shuffle
import re
from external import pyperclip
import pygame.freetype


ASSETS_PATH = "assets"
WORD_DURATION = 0.5
WORD_DURATION_PER_CAR = 0.1
APP_NAME = "Ledora"
APP_VERSION = "1.0.2"
FONT_COLOR = (250, 240, 230)
FONT_COLOR_A = "steelblue3"
FONT_COLOR_B = "white"
LOGO_FILE = "logo_small.png"

environ['SDL_VIDEO_CENTERED'] = '1'

WORDS_MAPPING = {
    "pt": [
        {"text_input": "PT1", "kind": "frequent", "locale": "pt_PT", "language": "pt"},
        {"text_input": "PT2", "kind": "hard", "locale": "pt_PT", "language": "pt"},
    ],
    "es": [
        {"text_input": "ES1", "kind": "frequent", "locale": "es", "language": "es"},
        {"text_input": "ES2", "kind": "hard", "locale": "es", "language": "es"},
    ],
    "en": [
        {"text_input": "EN1", "kind": "frequent", "locale": "en", "language": "en"},
        {"text_input": "EN2", "kind": "hard", "locale": "en", "language": "en"},
    ],
    "fr": [
        {"text_input": "FR1", "kind": "frequent", "locale": "fr_FR", "language": "fr"},
        {"text_input": "FR2", "kind": "hard", "locale": "fr_FR", "language": "fr"},
    ],
}


def resource_path(*relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *relative_path)


def asset_item_path(file):
    return resource_path(ASSETS_PATH, file)


def get_font(size): # Returns Press-Start-2P in the desired size
    return pg.font.Font(asset_item_path("font.ttf"), size)


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


class Ledora:


    def __init__(self):

        self.pg = pg
        self.pg.init()
        self.pg.display.set_icon(pg.image.load(asset_item_path(LOGO_FILE)))
        self.pg.display.set_caption(self.name)

        self.width, self.height = self.get_screen_size()
        self.height_usable = self.height - 100
        self.screen = self.get_screen()


        self.background = pg.transform.scale(self.pg.image.load(asset_item_path("Background.png")), (self.width, self.height))
        self.background_rect = self.background.get_rect(center=(self.width / 2, self.height / 2))

        self.set_states()
        self.initialize_words()

        # Instantiate mixer
        self.positive_sound = pygame.mixer.Sound(asset_item_path('positive_beeps-85504.mp3'))
        self.negative_sound = pygame.mixer.Sound(asset_item_path('negative_beeps-6008.mp3'))
        self.pause_sound = pygame.mixer.Sound(asset_item_path('pause-89443.mp3'))
        self.countdown_sound = pygame.mixer.Sound(asset_item_path('short-beep-countdown-81121.mp3'))
        self.results_sound = pygame.mixer.Sound(asset_item_path('crowd-cheer-ii-6263.mp3'))
        self.main_sound = pygame.mixer.Sound(asset_item_path('comic5-25269.mp3'))


    @property
    def name(self):
        """
        Returns the name of the application
        :return:
        """

        return f"{APP_NAME} v{APP_VERSION}"

    def get_screen_size(self):
        """
        Returns the screen size
        :return: tuple of width and height
        """
        info = self.pg.display.Info()
        return info.current_w, info.current_h

    def get_screen(self):
        """
        Returns the screen
        :return:
        """
        screen = self.pg.display.set_mode((self.width, self.height))
        self.pg.display.update()
        return screen

    def set_states(self):
        """
        Set the states of the application
        :return:
        """
        self.word_index = -1
        self.count_fails = 0
        self.start_time = None
        self.forward_datetime = datetime.now()
        self.duration = 0
        self.expected_duration = 0

    def initialize_words(self):
        """
        Initialize the words
        :return:
        """
        self.words = []
        self.positions = []
        self.n = 0

    @property
    def check_word_still_shown(self):
        """
        Check if the word is still shown
        :return:
        """

        return (datetime.now() - self.forward_datetime).total_seconds() < self.expected_duration

    def cls(self, gray=False):
        """
        Clear the screen
        :param gray:
        :return:
        """
        if gray:
            self.screen.blit( pg.transform.grayscale(self.background), self.background_rect)
        else:
            self.screen.blit(self.background, self.background_rect)
        self.display_flip()

    def hide_word(self):
        """
        Hide the word
        :return:
        """
        self.cls()
        self.wait = False
        self.duration = (datetime.now() - self.start_time).total_seconds()

    def next_word(self, play_sound =True):
        """
        Next word
        :return:
        """
        if play_sound:
            self.positive_sound.play()
        self.lock = True
        self.cls()
        self.word_index += 1
        text = self.words[self.word_index]
        position = self.positions[self.word_index]
        self.write_text_multicolor(text, position)
        self.forward_datetime = datetime.now()
        self.wait = True
        self.expected_duration = max(WORD_DURATION, len(text)*WORD_DURATION_PER_CAR)
        self.duration = (datetime.now() - self.start_time).total_seconds()
        self.draw_progress()
        self.display_flip()
        self.lock = False


    def pause_word(self):
        """
        Pause the word
        :return:
        """
        self.pause_sound.play()
        self.lock = True
        self.cls(gray=True)
        text = self.words[self.word_index]
        position = self.positions[self.word_index]
        self.write_text_multicolor(text, position)
        self.wait = False
        self.display_flip()
        self.lock = False

    def previous_word(self):
        """

        :return:
        """
        self.negative_sound.play()
        self.lock = True
        self.cls()
        self.draw_progress()
        if self.word_index and self.wait:
            self.word_index -= 1
        text = self.words[self.word_index]
        position = self.positions[self.word_index]
        self.write_text_multicolor(text, position)
        self.count_fails += 1
        self.forward_datetime = datetime.now()
        self.wait = True
        self.duration = (datetime.now() - self.start_time).total_seconds()
        self.display_flip()
        self.lock = False


    def display_flip(self):
        """
        Display flip
        :return:
        """
        self.pg.display.flip()

    def get_words(self, language="pt", kind="frequent", clipboard_=False):
        """
        Get words
        :param language:
        :param kind:
        :param clipboard_:
        :return:
        """

        text = None
        if clipboard_:
            try:
                text = pyperclip.paste()
            except:
                print("No clipboard")

        if kind and not text:
            file = f"{language}_{kind}.txt"
            with open(resource_path("txts", file), encoding='utf-8') as f:
                text = f.read()

        if not text:
            self.cls()
            self.write_title()
            self.write_message("Erro ao carregar palavras")
            self.display_flip()
            sleep(2)
            self.screen_initial()

        text = text.replace("\n", " ").replace(".", " ").replace(",", "")
        text = re.sub(' +', ' ', text)

        words = text.split(" ")
        if not clipboard_:
            shuffle(words)

        return words

    def get_position(self, words, locale="pt_PT"):
        """
        Get position
        :param words:
        :param locale:
        :return:
        """
        pp = pyphen.Pyphen(lang=locale)
        return [pp.positions(word) for word in words]


    def write_simple_text(self, text, font=None, dest=None):
        """
        Write simple text
        :param text:
        :param font:
        :param dest:
        :return:
        """
        if not font:
            font = pg.font.Font(None, 180)
        font_size = font.size(text)
        ren = font.render(text, 0, FONT_COLOR)
        if dest is not None:
            self.screen.blit(ren, dest)
        else:
            rect = ren.get_rect(center=(self.width / 2, self.height / 2))
            self.screen.blit(ren, rect)
        return font_size

    def write_text_multicolor(self, text, positions, font=None):
        """
        Write text with multiple colors according to the positions
        :param text:
        :param positions:
        :param font:
        :return:
        """
        if not font:
            font = pygame.freetype.Font(None, int(100*self.width/1920))
            font.origin = True

        text_surf_rect = font.get_rect(text)
        baseline = text_surf_rect.y
        text_surf = pg.Surface(text_surf_rect.size, pg.SRCALPHA)
        text_surf_rect.center = self.screen.get_rect().center
        metrics = font.get_metrics(text)

        start_index = 0
        possible_colors = ['lightgrey', 'steelblue3']
        colors = []
        for i, end_index in enumerate(positions + [len(text)]):
            for j in range(start_index, end_index):
                colors.append(possible_colors[i % 2])
                start_index += 1

        x = -2
        # render each letter of the current sentence one by one
        for color, letter, metric in zip(colors, text, metrics):
            font.render_to(text_surf, (x, baseline), letter, color)
            # and move the start position
            x += metric[4]

        self.screen.blit(text_surf, text_surf_rect)
        self.display_flip()

    def write_title(self):
        """
        Write the title
        :return:
        """
        options_text = get_font(100).render(APP_NAME, True, FONT_COLOR_A)
        rect = options_text.get_rect(center=(self.width / 2, 100))
        self.screen.blit(options_text, rect)

    def write_message(self, text):
        """
        Write a message
        :param text:
        :return:
        """
        options_text = get_font(50).render(text, True, FONT_COLOR_A)
        rect = options_text.get_rect(center=(self.width / 2, 400))
        self.screen.blit(options_text, rect)

    def write_text(self, text, x, y, font_size=45):
        """Draw text on the screen."""
        f = get_font(font_size)
        text_surface = f.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)


    def write_countdown(self, n=3):
        self.cls()
        self.countdown_sound.play()
        for i in range(n, 0, -1):
            self.cls()
            self.write_simple_text(str(i), font=get_font(200))
            self.display_flip()
            sleep(1)
        self.durations = 0
        self.cls()

    def draw_progress(self):
        """
        Draw the progress
        :return:
        """
        if self.n:
            rect = pg.Rect(0, self.height_usable-25, self.width*(self.word_index+1)/self.n, 20)
            self.pg.draw.rect(self.screen, FONT_COLOR_A, rect)

    def btn_menu(self, pos_x, pos_y, text, background_image = None):
        BUTTON_IMG = asset_item_path("Play Rect.png")
        if background_image:
            return Button(image=pg.image.load(BUTTON_IMG), pos=(pos_x, pos_y), text_input=text,
                         font=get_font(35), base_color=FONT_COLOR_A, hovering_color=FONT_COLOR_B)
        else:
            return Button(image=None, pos=(pos_x, pos_y), text_input=text,
                         font=get_font(35), base_color=FONT_COLOR_A, hovering_color=FONT_COLOR_B)

    def screen_initial(self):

        self.cls()
        self.write_title()

        btns = {}
        for i, (group, items) in enumerate(WORDS_MAPPING.items()):
            pos_y = 250 + i * 50
            nj = len(items)
            for j, item in enumerate(items):
                text = item["text_input"]
                pos_x = self.width/2 - 50 * nj + j * 150
                btn = self.btn_menu(pos_x, pos_y, text)
                btns[text] = btn

        clipboard_btn = self.btn_menu(self.width/2, self.height_usable - 180, "Ctrl+v")
        info_btn = self.btn_menu(self.width/2, self.height_usable - 120, "?")
        quit_btn = self.btn_menu(self.width/2, self.height_usable - 60, "Sair")

        self.main_sound.play(loops=True)

        while True:

            MENU_MOUSE_POS = pg.mouse.get_pos()

            for btn in btns.values():
                btn.changeColor(MENU_MOUSE_POS)
                btn.update(self.screen)
            clipboard_btn.changeColor(MENU_MOUSE_POS)
            clipboard_btn.update(self.screen)
            quit_btn.changeColor(MENU_MOUSE_POS)
            quit_btn.update(self.screen)
            info_btn.changeColor(MENU_MOUSE_POS)
            info_btn.update(self.screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:

                    for value in WORDS_MAPPING.values():
                        if quit_btn.checkForInput(MENU_MOUSE_POS):
                            pg.quit()
                            exit()
                        elif info_btn.checkForInput(MENU_MOUSE_POS):
                            self.main_sound.stop()
                            self.screen_intructions()
                        else:
                            for item in value:
                                btn = btns[item["text_input"]]
                                if btn.checkForInput(MENU_MOUSE_POS):
                                    self.main_sound.stop()
                                    self.screen_play(language=item["language"], locale=item["locale"], kind=item["kind"])
                            if clipboard_btn.checkForInput(MENU_MOUSE_POS):
                                self.main_sound.stop()
                                self.screen_play(language=None, locale="pt_PT", kind=None, clipboard_=True)

            pg.display.update()

    def screen_results(self):

        self.results_sound.play(loops=True)
        back_btn = self.btn_menu(self.width/2, self.height_usable - 120, "Voltar")

        kpi = 0
        for i in range(0, self.word_index+1):
            kpi += len(self.positions[i]) + 1

        pace = int(kpi / self.duration * 60)

        self.cls()
        self.write_title()
        self.draw_progress()
        options_text = get_font(32).render(f"{self.word_index} palavras", True, FONT_COLOR_B)
        rect = options_text.get_rect(center=(self.width / 2, 260))
        self.screen.blit(options_text, rect)
        options_text = get_font(32).render(f"{kpi} sílabas", True, FONT_COLOR_B)
        rect = options_text.get_rect(center=(self.width / 2, 310))
        self.screen.blit(options_text, rect)
        options_text = get_font(32).render(f"{pace} sílabas/minuto", True, FONT_COLOR_B)
        rect = options_text.get_rect(center=(self.width / 2, 360))
        self.screen.blit(options_text, rect)
        options_text = get_font(32).render(f"{self.count_fails} retornos", True, FONT_COLOR_B)
        rect = options_text.get_rect(center=(self.width / 2, 410))
        self.screen.blit(options_text, rect)

        s = 5
        if self.count_fails > 0:
            s -= 1

        if self.count_fails > self.n*0.3:
            s -= 1

        if self.duration > self.n*1:
            s -= 1

        if self.duration > self.n*2:
            s -= 1

        for i in range(5):
            star = pg.transform.scale(pg.image.load(resource_path("assets", "star.png")), (30, 30))
            if i + 1 > s:
                star = pg.transform.grayscale(star)
            self.screen.blit(star, ((i+1)*60+self.width/2 - 5*60/2, self.height_usable - 75))

        self.display_flip()

        while True:
            MENU_MOUSE_POS = pg.mouse.get_pos()
            back_btn.changeColor(MENU_MOUSE_POS)
            back_btn.update(self.screen)
            events = pg.event.get()
            for event in events:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.results_sound.stop()
                        self.screen_initial()
                elif event.type == pg.QUIT:
                    self.pg.quit()
                    exit()
                elif back_btn.checkForInput(MENU_MOUSE_POS):
                    self.results_sound.stop()
                    self.screen_initial()


    def screen_play(self, language, locale=None, kind=None, clipboard_=False):

        if not locale:
            locale = language
        self.lock = True
        self.words = self.get_words(language=language, kind=kind, clipboard_=clipboard_)
        self.positions = self.get_position(self.words, locale=locale)
        self.n = len(self.words)

        self.set_states()
        self.write_title()
        self.write_countdown()
        self.start_time = datetime.now()
        self.lock = False
        self.wait = True

        while True:
            events = pg.event.get()
            if self.lock:
                continue
            if self.wait and not self.check_word_still_shown:
                self.hide_word()
            for event in events:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.screen_initial()
                    elif self.word_index + 1 >= self.n or event.key in (pg.K_END,):
                        self.screen_results()
                    elif event.key in (pg.K_RIGHT,):
                        self.next_word()
                    elif event.key in (pg.K_LEFT,):
                        self.previous_word()
                    elif event.key in (pg.K_SPACE,):
                        self.pause_word()
                elif event.type == pg.QUIT:
                    self.pg.quit()
                    exit()


    def screen_intructions(self):
        """
        Screen instructions
        :return:
        """

        self.cls()
        self.write_title()
        self.write_text("Comandos", self.width // 2, 200, font_size=25)
        self.write_text("DIREITA para a próxima palavra", self.width // 2, 300, font_size=25)
        self.write_text("ESQUERDA para a palavra anterior", self.width // 2, 350, font_size=25)
        self.write_text("ESPAÇO para pausar", self.width // 2, 400, font_size=25)
        self.write_text("ESC para cancelar o jogo", self.width // 2, 450, font_size=25)
        self.write_text("END para finalizar o jogo", self.width // 2, 500, font_size=25)
        self.display_flip()

        waiting_for_key = True
        while waiting_for_key:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    self.screen_initial()
                    waiting_for_key = False
                    break


    def __del__(self):
        self.pg.quit()


def main():
    ldr = Ledora()
    ldr.screen_initial()


if __name__ == "__main__":
    main()
