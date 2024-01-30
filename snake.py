import os
import sys
import configparser
import random
import pygame

#  цвета
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive"
    except NameError:
        application_path = os.getcwd()
        running_mode = 'Interactive'

w = 800
h = 600

dis = pygame.display.set_mode((w, h), pygame.RESIZABLE)
current_size = dis.get_size()

virtual_surface = pygame.Surface((w, h))
clock = pygame.time.Clock()

pygame.font.init()
font_gi = pygame.font.Font(f'{application_path}/data/fonts/gi.ttf', 30)


class Menu:
    def __init__(self):
        self.option_surfaces = []
        self._callbacks = []
        self._current_option_index = 0
        self.option_padding = 20

    def append_options(self, option, callback):
        self.option_surfaces.append(font_gi.render(option, True, white))
        self._callbacks.append(callback)

    def switch(self, direction):
        self._current_option_index = (self._current_option_index + direction) % len(self.option_surfaces)

    def select(self):
        self._callbacks[self._current_option_index]()

    def draw(self, surf, x, y):
        option_height = max(option.get_height() for option in self.option_surfaces)
        total_height = len(self.option_surfaces) * (option_height + self.option_padding)
        start_y = y - total_height // 2

        for i, option in enumerate(self.option_surfaces):
            option_rect = option.get_rect()
            option_rect.midtop = (x, start_y + i * (option_height + self.option_padding))

            if i == self._current_option_index:
                pygame.draw.rect(surf, (0, 100, 0), option_rect.inflate(10, 5))
            else:
                pygame.draw.rect(surf, (0, 0, 0), option_rect.inflate(10, 5), 2)

            surf.blit(option, option_rect)


def menu():
    def choose_difficulty():
        i = int(snake_game.difficult_int)
        snake_game.set_difficulty((i + 1) % 5)
        snake_game.difficult_int = f'{(i + 1) % 5}'
        menu.option_surfaces[1] = font_gi.render(f'Difficulty: {snake_game.level_difficult}', True, white)

    def start():
        snake_game.load_configuration()
        snake_game.set_difficulty(int(snake_game.difficult_int))
        snake_game.game_loop()

    global current_size
    pygame.mixer.music.load(f'{application_path}/data/sounds/mainmenutheme.mp3')
    pygame.mixer.music.play(-1, 0.0)
    pygame.mouse.set_visible(1)
    menu = Menu()
    menu.append_options('Start Game', start)
    menu.append_options(f'Difficulty: {snake_game.level_difficult}', choose_difficulty)
    menu.append_options('Quit', sys.exit)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.VIDEORESIZE:
                current_size = e.size
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w or e.key == pygame.K_UP:
                    menu.switch(-1)
                    s = pygame.mixer.Sound(f'{application_path}/data/sounds/chose.ogg')
                    s.set_volume(snake_game.volume)
                    s.play()
                elif e.key == pygame.K_s or e.key == pygame.K_DOWN:
                    menu.switch(1)
                    s = pygame.mixer.Sound(f'{application_path}/data/sounds/chose.ogg')
                    s.set_volume(snake_game.volume)
                    s.play()
                elif e.key == pygame.K_RETURN:
                    s = pygame.mixer.Sound(f'{application_path}/data/sounds/ichosed.ogg')
                    s.set_volume(snake_game.volume)
                    s.play()
                    menu.select()
                elif e.key == pygame.K_ESCAPE:
                    sys.exit()

        virtual_surface.fill((0, 0, 100))
        name = font_gi.render('Snake Game', True, (255, 255, 255))
        virtual_surface.blit(name, (300, 20))
        menu.draw(virtual_surface, 399, 300)
        scaled_surface = pygame.transform.scale(virtual_surface, current_size)
        dis.blit(scaled_surface, (0, 0))
        clock.tick(10)
        pygame.display.flip()


class SnakeGame:
    def __init__(self):
        self.application_path = ''
        self.config = None
        self.nickname = ''
        self.difficult_int = 0
        self.screen_mode = 0
        self.volume = 0.0

        # Инициализация pygame
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.display.set_caption('Snake Game')

        #  Размер пикселя змейки
        self.snake_block = w // 40

        #  Начальная настройка
        self.level_difficult = 'Easy'
        self.color = ''

        #  Скорость змейки
        self.snake_speed = 30
        self.length_of_snake = 1

        #  Иконка
        pygame_icon = pygame.image.load(f'{application_path}/data/icons/icon512.png')
        pygame_icon = pygame.transform.scale(pygame_icon, (64, 64))
        pygame.display.set_icon(pygame_icon)

        #  Background
        self.bg1 = pygame.image.load(f"{application_path}/data/background/bg1.png")
        self.bg1 = pygame.transform.scale(self.bg1, (w, h))

        self.bg2 = pygame.image.load(f"{application_path}/data/background/bg2.png")
        self.bg2 = pygame.transform.scale(self.bg2, (w, h))
        # просто переменные
        self.bestscore = 0
        self.fake_chance = 0
        self.failscore = 0

    def load_configuration(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.application_path, 'data', 'config.ini'))
        self.difficult_int = self.config['DEFAULT']['int-diff']
        self.volume = float(self.config['DEFAULT']['volume'])

        pygame.mixer.music.set_volume(self.volume)

    def set_volume(self, value):
        self.volume = value / 100
        pygame.mixer.music.set_volume(self.volume)
        self.config['DEFAULT']['volume'] = str(self.volume)
        with open(os.path.join(self.application_path, 'data', 'config.ini'), 'w') as configfile:
            self.config.write(configfile)

    def set_difficulty(self, difficulty):
        difficulty_levels = {
            0: ('Easy', 10, 5),
            1: ('Normal', 15, 20),
            2: ('Hard', 25, 40),
            3: ('Lunatic', 30, 65),
            4: ('PB', 40, 97)
        }
        self.level_difficult, self.snake_speed, self.fake_chance = difficulty_levels[difficulty]
        self.config['DEFAULT']['int-diff'] = str(difficulty)
        with open(f'{application_path}/data/config.ini', 'w') as configfile:
            self.config.write(configfile)

    def nick_name(self, name):
        self.config['DEFAULT']['nickname'] = name
        with open(f'{application_path}/data/config.ini', 'w') as configfile:
            self.config.write(configfile)

    def start_the_game(self):
        pygame.mixer.music.stop()

    def apple(self):
        pass

    def play_music(self):
        music_dict = {
            'Easy': 'desiredrive.mp3',
            'Normal': 'sp6.ogg',
            'Hard': 'Dreams.mp3',
            'Lunatic': 'un.mp3',
            'PB': 'zunnofn.mp3'
        }
        pygame.mixer.music.load(f'{application_path}/data/sounds/{music_dict[self.level_difficult]}')
        pygame.mixer.music.play(-1, 0.0)

    def render_score(self, score_type, best_score=0, score=None, level=None):
        color_dict = {
            'Easy': white,
            'Normal': yellow,
            'Hard': red,
            'Lunatic': black,
            'PB': black
        }
        if score_type == 'your_score':
            value = font_gi.render("Score: " + str(score), True, yellow)
            virtual_surface.blit(value, [w * 0.025, 10])
        elif score_type == 'fail_score':
            value = font_gi.render("FS: " + str(score), True, yellow)
            virtual_surface.blit(value, [w * 0.37, 10])
        elif score_type == 'best_score':
            value = font_gi.render("BS: " + str(best_score), True, yellow)
            virtual_surface.blit(value, [w * 0.225, 10])
        elif score_type == 'level':
            value = font_gi.render(f"Difficult: {self.level_difficult}",
                                   True, color_dict[self.level_difficult])
            virtual_surface.blit(value, [w / 2 * 1.15, 10])
        else:
            return 'Инвалид type скор'

    def your_score(self, score):
        return self.render_score('your_score', score=score)

    def fail_score(self, score):
        return self.render_score('fail_score', score=score)

    def best_score(self, score):
        return self.render_score('best_score', score)

    def level(self, level):
        return self.render_score('level', level=level)

    def our_snake(self, snake_list):
        for x in snake_list:
            pygame.draw.rect(virtual_surface, black, [x[0], x[1], self.snake_block, self.snake_block])

    def game_loop(self):
        global current_size
        pygame.mouse.set_visible(False)
        game_over = False
        game_close = False

        self.play_music()

        x1 = w / 2
        y1 = h / 2

        x1_change = 0
        y1_change = 0

        snake_list = []
        self.length_of_snake = 1
        self.failscore = 0

        foodx = round(random.randint(20, w - 20 - self.snake_block) / self.snake_block, 0) * self.snake_block
        foody = round(random.randint(60, h - 20 - self.snake_block) / self.snake_block, 0) * self.snake_block
        flap = True
        while not game_over:
            flag = True
            if flap:
                flap = False
            while game_close:
                if flag:
                    pygame.mixer.music.load(f'{application_path}/data/sounds/Whyifail.mp3')
                    pygame.mixer.music.play(-1, 0)
                virtual_surface.blit(self.bg1, (0, 0))
                virtual_surface.blit(self.bg2, (0, 0))
                self.your_score(self.length_of_snake - 1)
                self.fail_score(self.failscore)
                self.best_score(self.bestscore)
                self.level(self.level_difficult)
                pygame.draw.aaline(virtual_surface, black,
                                   [0, h // 10],
                                   [w, h // 10], 5)
                pygame.draw.aaline(virtual_surface, black,
                                   [w // 2, 0],
                                   [w // 2, h // 10], 5)
                pygame.draw.aaline(virtual_surface, black,
                                   [19, 60],
                                   [19, h - 20], 5)
                pygame.draw.aaline(virtual_surface, black,
                                   [w - 20, 60],
                                   [w - 20, h - 20], 5)
                pygame.draw.aaline(virtual_surface, black,
                                   [19, h - 20],
                                   [w - 20, h - 20], 5)
                ifall = pygame.image.load(f'{application_path}/data/images/Whyifail.png')
                imagerect = ifall.get_rect()
                imagerect.x, imagerect.y = 21, 280
                virtual_surface.blit(ifall, imagerect)
                scaled_surface = pygame.transform.scale(virtual_surface, current_size)
                dis.blit(scaled_surface, (0, 0))
                clock.tick(10)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.VIDEORESIZE:
                        current_size = event.size
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.bestscore = 0
                            menu()
                        if event.key == pygame.K_c:
                            snake_game.game_loop()
                        elif event.key == pygame.K_F1:
                            self.volume = self.volume + 0.1
                            pygame.mixer.music.set_volume(self.volume)
                        elif event.key == pygame.K_F2:
                            self.volume = self.volume - 0.1
                            pygame.mixer.music.set_volume(self.volume)
                    if event.type == pygame.QUIT:
                        exit()
                flag = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.VIDEORESIZE:
                    current_size = event.size
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if (x1_change != -self.snake_block and x1_change != self.snake_block
                                or self.length_of_snake <= 2):
                            x1_change = -self.snake_block
                            y1_change = 0
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if (x1_change != -self.snake_block and x1_change != self.snake_block
                                or self.length_of_snake <= 2):
                            x1_change = self.snake_block
                            y1_change = 0
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if (y1_change != -self.snake_block and y1_change != self.snake_block
                                or self.length_of_snake <= 2):
                            y1_change = -self.snake_block
                            x1_change = 0
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if (y1_change != -self.snake_block and y1_change != self.snake_block
                                or self.length_of_snake <= 2):
                            y1_change = self.snake_block
                            x1_change = 0
                    elif event.key == pygame.K_F1:
                        self.volume = self.volume + 0.1
                        pygame.mixer.music.set_volume(self.volume)
                    elif event.key == pygame.K_F2:
                        self.volume = self.volume - 0.1
                        pygame.mixer.music.set_volume(self.volume)
                    elif event.key == pygame.K_m:
                        pass
                    elif event.key == pygame.K_ESCAPE:
                        self.bestscore = 0
                        menu()
            x1 += x1_change
            y1 += y1_change
            if (x1 in range(w - w // 40, w) or x1 in range(0, w // 40)
                    or y1 in range(h - h // 20, h) or y1 in range(0, h // 10)):
                flap = True
                flag = True
                game_close = True
                if x1 >= w - self.snake_block or x1 < self.snake_block:
                    x1_change = -x1_change
                if y1 >= h - self.snake_block or y1 < h // 10 + self.snake_block:
                    y1_change = -y1_change
            if [foodx, foody] in snake_list:
                foodx = round(random.randint(w // 40, w - w // 40 - self.snake_block)
                              / self.snake_block, 0) * self.snake_block
                foody = round(random.randint(h // 10, h - h // 10 - self.snake_block)
                              / self.snake_block, 0) * self.snake_block
            virtual_surface.blit(self.bg2, (0, 0))
            pygame.draw.ellipse(virtual_surface, red, (foodx, foody, self.snake_block, self.snake_block))
            snake_head = list()
            snake_head.append(x1)
            snake_head.append(y1)
            snake_list.append(snake_head)
            if len(snake_list) > self.length_of_snake:
                del snake_list[0]
            for x in snake_list[:-1]:
                if x == snake_head:
                    game_close = True
            self.our_snake(snake_list)
            virtual_surface.blit(self.bg1, (0, 0))
            self.your_score(self.length_of_snake - 1)
            self.fail_score(self.failscore)
            self.best_score(self.bestscore)
            self.level(self.level_difficult)
            pygame.draw.aaline(virtual_surface, black,
                               [0, h // 10],
                               [w, h // 10], 5)
            pygame.draw.aaline(virtual_surface, black,
                               [w // 2, 0],
                               [w // 2, h // 10], 5)
            pygame.draw.aaline(virtual_surface, black,
                               [19, 60],
                               [19, h - 20], 5)
            pygame.draw.aaline(virtual_surface, black,
                               [w - 20, 60],
                               [w - 20, h - 20], 5)
            pygame.draw.aaline(virtual_surface, black,
                               [19, h - 20],
                               [w - 20, h - 20], 5)
            a = random.randint(0, 100)
            if x1 == foodx and y1 == foody and a >= self.fake_chance:
                foodx = (round(random.randint(w // 40, w - 20 - self.snake_block) / self.snake_block, 0)
                         * self.snake_block)
                foody = round(random.randint(h // 10, h - 20 - self.snake_block) / self.snake_block,
                              0) * self.snake_block
                self.length_of_snake += 1
                if self.length_of_snake - 1 > self.bestscore:
                    self.bestscore = self.length_of_snake - 1
                s = pygame.mixer.Sound(f'{application_path}/data/sounds/effect_done.wav')
                s.set_volume(self.volume)
                s.play()
            elif x1 == foodx and y1 == foody and a <= self.fake_chance:
                foodx = (round(random.randint(w // 40, w - 20 - self.snake_block) / self.snake_block, 0)
                         * self.snake_block)
                foody = round(random.randint(h // 10, h - 20 - self.snake_block) / self.snake_block,
                              0) * self.snake_block
                s = pygame.mixer.Sound(f'{application_path}/data/sounds/fuc.wav')
                self.failscore += 1
                s.set_volume(self.volume)
                s.play()
            scaled_surface = pygame.transform.scale(virtual_surface, current_size)
            dis.blit(scaled_surface, (0, 0))
            pygame.display.update()
            clock.tick(self.snake_speed)
        exit()


if __name__ == "__main__":
    snake_game = SnakeGame()
    snake_game.load_configuration()
    snake_game.set_difficulty(int(snake_game.difficult_int))
    menu()
    sys.exit()
