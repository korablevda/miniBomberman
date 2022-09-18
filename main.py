import os
import pygame
import random
import sys

pygame.init()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        # image = pygame.image.load(fullname).convert()
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


FPS = 30
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
default_speed = 5
all_sprites = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
Background_group = pygame.sprite.Group()
Box_group = pygame.sprite.Group()
StoneBox_group = pygame.sprite.Group()
Bomb_group = pygame.sprite.Group()
Enemy_group = pygame.sprite.Group()
Exit_group = pygame.sprite.Group()
tile_width = tile_height = 50


class Game():
    # Класс самой игры: хранит параметры, загружает и запускает уровни
    levels = [file for file in os.listdir('data/levels') if file.endswith('.map')]

    def __init__(self, level=-1):
        self.level = level
        self.map = Game.levels[0]
        self.max_bomb = 2
        self.bomb = 0
        self.score = 0
        self.win = False
        self.lose = False
        self.enemy = 8
        self.box = 0
        self.exit = False
        self.IDDQD = False

    def run(self):
        # запускаем уровень, либо завершаем игру, если уровни закончились
        self.level += 1
        if self.level >= len(Game.levels):
            self.win = True
            return self.end_game()
        else:
            for sprite in all_sprites:
                sprite.kill()
            for sprite in Box_group:
                sprite.kill()
            for sprite in Background_group:
                sprite.kill()
            for sprite in StoneBox_group:
                sprite.kill()
            for sprite in Exit_group:
                sprite.kill()
            self.map = Game.levels[self.level]
            self.exit = False
            self.enemy = 8
            self.bomb = 0
            self.box = 0
            return self.play_level()

    def load_level(self, filename):
        # загрузка текствого файла для формирования уровня
        filename = "data/levels/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))

    def generate_level(self, level):
        # формирование уровня и создание персонажа
        hero, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    BGTile(Background_group, pos_x=x, pos_y=y)
                elif level[y][x] == '#':
                    BGTile(Background_group, pos_x=x, pos_y=y)
                    BoxTile(Box_group, pos_x=x, pos_y=y)
                    self.box += 1
                elif level[y][x] == '$':
                    BGTile(Background_group, pos_x=x, pos_y=y)
                    StoneTile(StoneBox_group, pos_x=x, pos_y=y)
                elif level[y][x] == '@':
                    BGTile(Background_group, pos_x=x, pos_y=y)
                    hero = AnimatedSprite(
                        pygame.transform.scale(load_image("hero2.png"), (tile_width * 3, tile_height * 4)),
                        3, 4, x * tile_width, y * tile_height, game=self)
                    level[y][x] = "."
        return hero, x, y

    def play_level(self):
        # запуск и отыгрыш уровня
        level_map = self.load_level(self.map)
        hero, max_x, max_y = self.generate_level(level_map)
        for _ in range(self.enemy):
            Enemy(Enemy_group, all_sprites, game=self)
        running = True
        while running:
            for event in pygame.event.get():
                hero.motion = False
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # бомбы ставим отдельно от движения для более плавной игры
                    if event.key == pygame.K_SPACE:
                        if self.bomb < self.max_bomb:
                            self.bomb += 1
                            x, y = hero.coords
                            Bomb(all_sprites, Bomb_group, x=x + tile_width // 4, y=y + tile_height // 4, game=self)
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP]:
                        hero.direction = 'N'
                        hero.motion = True
                    elif keys[pygame.K_DOWN]:
                        hero.direction = 'S'
                        hero.motion = True
                    elif keys[pygame.K_LEFT]:
                        hero.direction = 'W'
                        hero.motion = True
                    elif keys[pygame.K_RIGHT]:
                        hero.direction = 'E'
                        hero.motion = True
                    elif keys[pygame.K_w]:
                        self.win = True
                    elif keys[pygame.K_l]:
                        self.lose = True
                    elif keys[pygame.K_q]:
                        # режим бессмертия
                        self.IDDQD = True
            if self.win or self.lose:
                return self.end_game()
            else:
                screen.fill(pygame.Color("black"))
                font = pygame.font.Font('data/font/Cavorting.otf', tile_height)
                text = font.render("mini-BomberMan", True, (100, 255, 100))
                text_x = 10
                text_y = 5
                screen.blit(text, (text_x, text_y))
                text_score = font.render(f'score: {str(self.score)}', True, (100, 255, 100))
                text_score_x = WIDTH * 3 // 4
                text_score_y = 5
                screen.blit(text_score, (text_score_x, text_score_y))
                all_sprites.update()
                if not(self.win or self.lose):
                    Background_group.draw(screen)
                    StoneBox_group.draw(screen)
                    Bomb_group.draw(screen)
                    Box_group.draw(screen)
                    Exit_group.draw(screen)
                    all_sprites.draw(screen)
                    pygame.display.flip()
                    clock.tick(FPS)
        terminate()

    def start_game(self):
        # начальный экран
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    return self.run()
            if running:
                screen.fill(pygame.Color("black"))
                back = pygame.transform.scale(load_image('ogon.jpg'), (WIDTH, HEIGHT))
                screen.blit(back, (0, 0))
                font = pygame.font.Font('data/font/Cavorting.otf', WIDTH//6)
                text = font.render("mini-BomberMan", True, (255, 0, 0))
                text_x = WIDTH // 2 - text.get_width() // 2
                text_y = HEIGHT // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
                screen.blit(load_image('logo.png'), (WIDTH - 210, 0))
                keyboard = pygame.transform.scale(load_image('keyboard.png'),  (WIDTH//2, HEIGHT//4))
                screen.blit(keyboard, (WIDTH//2 - keyboard.get_width()//2, HEIGHT - keyboard.get_height()))
                bomber = pygame.transform.scale(load_image('bomber.jpg'), (WIDTH // 8, HEIGHT // 8))
                screen.blit(bomber, (5, 5))
                pygame.display.flip()
                clock.tick(FPS)
        terminate()

    def end_game(self):
        # окно финала игры
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = False
            if running:
                screen.fill(pygame.Color("black"))
                font = pygame.font.Font('data/font/Cavorting.otf', tile_height*2)
                if self.win:
                    text = font.render("You win!!!", True, (100, 255, 100))
                else:
                    text = font.render("You lose...", True, (100, 255, 100))
                text_x = WIDTH // 2 - text.get_width() // 2
                text_y = HEIGHT // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
                font_score = pygame.font.Font('data/font/Cavorting.otf', tile_height)
                text_score = font_score.render(f'Score: {self.score}', True, (100, 255, 100))
                text_score_x = WIDTH // 2 - text_score.get_width() // 2
                text_score_y = HEIGHT // 2 - text_score.get_height() // 2 + text.get_height() + 5
                screen.blit(text_score, (text_score_x, text_score_y))
                pygame.display.flip()
                clock.tick(FPS)
        terminate()


class ExitDoor(pygame.sprite.Sprite):
    # класс двери - перехода на следующий уровень
    image_o = pygame.transform.scale(load_image('exit_open.png'), (tile_width, tile_height))
    image_cl = pygame.transform.scale(load_image('exit_closed.png'), (tile_width, tile_height))

    def __init__(self, *group, pos_x, pos_y, game):
        super().__init__(*group)
        self.image = ExitDoor.image_cl
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.game = game
        self.open = False

    def update(self):
        # дверь открывается только тогда, когда все противники побеждены
        if self.game.enemy <= 0:
            self.open = True
            self.image = ExitDoor.image_o
            self.mask = pygame.mask.from_surface(self.image)
        # в открытом состоянии при касании игроком активируется переход на следуюший уровень
        if self.open:
            if pygame.sprite.spritecollideany(self, hero_group):
                self.rect = self.rect.move(WIDTH, HEIGHT)
                return self.game.run()


class Enemy(pygame.sprite.Sprite):
    # класс противников, внешний вид выбирается случайно при генерации
    image = {'enemy1': ['enemies/e_1_up.png', 'enemies/e_1_right.png', 'enemies/e_1_down.png', 'enemies/e_1_left.png'],
             'enemy2': ['enemies/e_2_up.png', 'enemies/e_2_right.png', 'enemies/e_2_down.png', 'enemies/e_2_left.png'],
             'enemy3': ['enemies/e_3_up.png', 'enemies/e_3_right.png', 'enemies/e_3_down.png', 'enemies/e_3_left.png'],
             'enemy4': ['enemies/e_4_up.png', 'enemies/e_4_right.png', 'enemies/e_4_down.png', 'enemies/e_4_left.png'],
             'enemy5': ['enemies/e_5_up.png', 'enemies/e_5_right.png', 'enemies/e_5_down.png', 'enemies/e_5_left.png'],
             'enemy6': ['enemies/e_6_up.png', 'enemies/e_6_right.png', 'enemies/e_6_down.png', 'enemies/e_6_left.png'],
             'enemy7': ['enemies/e_7_up.png', 'enemies/e_7_right.png', 'enemies/e_7_down.png', 'enemies/e_7_left.png'],
             'enemy8': ['enemies/e_8_up.png', 'enemies/e_8_right.png', 'enemies/e_8_down.png', 'enemies/e_8_left.png'],
             'enemy9': ['enemies/e_9_up.png', 'enemies/e_9_right.png', 'enemies/e_9_down.png', 'enemies/e_9_left.png']
             }

    def __init__(self, *group, x=WIDTH - tile_width * 2 + 5, y=HEIGHT - tile_height*2 + 5, game):
        super().__init__(*group)
        self.direction = random.randint(0, 3)
        self.im = random.choice(list(Enemy.image.keys()))
        self.image = pygame.transform.scale(load_image(Enemy.image[self.im][self.direction]),
                                            (int(tile_width*0.8), int(tile_height*0.8)))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(x, y)
        self.motion = random.randint(1*FPS, 5*FPS)
        self.coords = (x, y)
        self.speed = default_speed - 2
        self.game = game

    def update(self):
        # выбираем новое направление и длительноть перемещения, если предыдущее закончилось
        if self.motion <= 0:
            self.motion = random.randint(1 * FPS, 5 * FPS)
            self.direction = random.randint(0, 3)
        # делаем шаг и меняем картинку в зависимости от направления движения
        dx = dy = 0
        if self.direction == 0:
            dy -= self.speed
        elif self.direction == 1:
            dx += self.speed
        elif self.direction == 2:
            dy += self.speed
        else:
            dx -= self.speed
        self.image = pygame.transform.scale(load_image(Enemy.image[self.im][self.direction]),
                                            (int(tile_width*0.8), int(tile_height*0.8)))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.rect.move(dx, dy)
        self.motion -= 1
        # проверка корректности перемещения
        fl = False
        for box in Box_group:
            if pygame.sprite.collide_mask(self, box):
                fl = True
                break
        if not fl:
            for sbox in StoneBox_group:
                if pygame.sprite.collide_mask(self, sbox):
                    fl = True
                    break
        if not fl:
            for bomb in Bomb_group:
                if pygame.sprite.collide_mask(self, bomb) and not bomb.boom:
                    fl = True
                    break
        if fl:
            self.rect = self.rect.move(-dx*2, -dy*2)
            self.motion = random.randint(1 * FPS, 5 * FPS)
            self.direction = random.randint(0, 3)
            self.coords = (self.rect.x, self.rect.y)
        else:
            self.coords = (self.coords[0] + dx, self.coords[1] + dy)
        # из-за случайностей возврата из некорректного шага можем выйти за границы уровня,
        # в этом случае убиваем противника
        if not (tile_width//2 < self.coords[0] < WIDTH - tile_width//2):
            self.game.enemy -= 1
            self.kill()
        if not (tile_height * 1.5 < self.coords[1] < HEIGHT - tile_width//2):
            self.game.enemy -= 1
            self.kill()
        # проверка касания с игроком - в этом случае игра заканчивается
        for hero in hero_group:
            if pygame.sprite.collide_mask(self, hero) and not self.game.IDDQD:
                hero.kill()
                self.game.lose = True
                return self.game.run()


class Bomb(pygame.sprite.Sprite):
    # Класс бомбы, взрывается не сразу, поэтому нужно несколько картинок с разной длиной фитиля
    im_bomb3 = pygame.transform.scale(load_image('bomb3.png'), (tile_width//2, tile_height//2))
    im_bomb2 = pygame.transform.scale(load_image('bomb2.png'), (tile_width//2, tile_height//2))
    im_bomb1 = pygame.transform.scale(load_image('bomb1.png'), (tile_width//2, tile_height//2))
    im_boom = pygame.transform.scale(load_image('boom.png'), (int(tile_width*1.5), int(tile_height*1.5)))

    def __init__(self, *group, x, y, game):
        super().__init__(*group)
        self.image = Bomb.im_bomb3
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(x, y+tile_height)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.time = 4 * FPS
        self.game = game
        self.boom = False

    def update(self):
        # в зависимости от оставшегося времени существования меняем внешний вид бомбы
        self.time -= 1
        if self.time >= 3*FPS:
            self.image = Bomb.im_bomb3
            self.mask = pygame.mask.from_surface(self.image)
        elif self.time >= 2*FPS:
            self.image = Bomb.im_bomb2
            self.mask = pygame.mask.from_surface(self.image)
        elif self.time >= FPS:
            self.image = Bomb.im_bomb1
            self.mask = pygame.mask.from_surface(self.image)
        elif self.time >= 0:
            # взрываем бомбу
            self.boom = True
            self.image = Bomb.im_boom
            self.rect = self.image.get_rect().move(self.abs_pos[0] - int(tile_width * 0.5),
                                                   self.abs_pos[1] - int(tile_height * 0.5))
            self.mask = pygame.mask.from_surface(self.image)
            # убиваем попавших под взрыв противников
            for enemy in Enemy_group:
                if pygame.sprite.collide_mask(self, enemy):
                    self.game.score += 10
                    self.game.enemy -= 1
                    enemy.kill()
            # разрушаем ящики
            for box in Box_group:
                if pygame.sprite.collide_mask(self, box):
                    self.game.score += 1
                    self.game.box -= 1
                    if not self.game.exit and not(random.randint(0, self.game.box)):
                        self.game.exit = True
                        ExitDoor(Exit_group, all_sprites, pos_x=box.abs_pos[0], pos_y=box.abs_pos[1], game=self.game)
                    box.kill()
            # проверим, попал ли под взрыв игрок
            for hero in hero_group:
                if self.boom and pygame.sprite.collide_mask(self, hero):
                    if not self.game.IDDQD:
                        self.game.lose = True
                        return self.game.run()
        else:
            # убиваем саму бомбу
            self.game.bomb -= 1
            self.kill()


class BGTile(pygame.sprite.Sprite):
    # класс фоновой текстуры
    texture = ['ground.png', 'grass.png', 'ground.png', 'desert.png']
    image = pygame.transform.scale(load_image(random.choice(texture)), (tile_width, tile_height))

    def __init__(self, *group, pos_x, pos_y):
        super().__init__(*group)
        self.image = BGTile.image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y+tile_height)
        self.abs_pos = (self.rect.x, self.rect.y)


class BoxTile(pygame.sprite.Sprite):
    # класс разрушаемого ящика
    image = pygame.transform.scale(load_image('box.png'), (tile_width, tile_height))

    def __init__(self, *group, pos_x, pos_y):
        super().__init__(*group)
        self.image = BoxTile.image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y+tile_height)
        self.abs_pos = (self.rect.x, self.rect.y)


class StoneTile(pygame.sprite.Sprite):
    # класс неразрушаемого блока
    image = pygame.transform.scale(load_image('brick.png'), (tile_width, tile_height))

    def __init__(self, *group, pos_x, pos_y):
        super().__init__(*group)
        self.image = StoneTile.image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y+tile_height)
        self.abs_pos = (self.rect.x, self.rect.y)


class AnimatedSprite(pygame.sprite.Sprite):
    # класс игрока
    def __init__(self, sheet, columns, rows, x, y, game):
        super().__init__(all_sprites, hero_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.rect.move(x, y+tile_height)
        self.direction = 'S'
        self.motion = False
        self.coords = (x, y)
        self.speed = default_speed
        self.game = game

    def cut_sheet(self, sheet, columns, rows):
        # выбираем нужный фрагмент изображения для анимированного движения
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        # делаем шаг, меняя картинку
        if self.motion:
            new_x, new_y = self.coords
            if self.direction == 'N':
                if self.cur_frame in [9, 10, 11]:
                    self.cur_frame = (self.cur_frame + 1) % 3 + 9
                else:
                    self.cur_frame = 9
                new_y = max(0, new_y - self.speed)
            elif self.direction == 'S':
                if self.cur_frame in [0, 1, 2]:
                    self.cur_frame = (self.cur_frame + 1) % 3 + 0
                else:
                    self.cur_frame = 0
                new_y = min(HEIGHT - 30, new_y + self.speed)
            elif self.direction == 'W':
                if self.cur_frame in [3, 4, 5]:
                    self.cur_frame = (self.cur_frame + 1) % 3 + 3
                else:
                    self.cur_frame = 3
                new_x = max(0, new_x - self.speed)
            elif self.direction == 'E':
                if self.cur_frame in [6, 7, 8]:
                    self.cur_frame = (self.cur_frame + 1) % 3 + 6
                else:
                    self.cur_frame = 6
                new_x = min(WIDTH - 30, new_x + self.speed)
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
            dx = new_x - self.coords[0]
            dy = new_y - self.coords[1]
            self.rect = self.rect.move(dx, dy)
            # проверка корректности шага
            fl = False
            for box in Box_group:
                if pygame.sprite.collide_mask(self, box):
                    fl = True
                    break
            if not fl:
                for sbox in StoneBox_group:
                    if pygame.sprite.collide_mask(self, sbox):
                        fl = True
                        break
            if fl:
                self.rect = self.rect.move(-dx, -dy)
            else:
                self.coords = (new_x, new_y)


if __name__ == '__main__':
    Game().start_game()
    terminate()
