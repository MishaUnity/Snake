import pygame
import logging
import random
import time
import sys
import os

import targeting

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

pygame.init()

# Константы
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 10
FPS = 900

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

targeting.testWin = WIN

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Игровые переменные
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]

# Генерация фрукта в пикселях
def generate_fruit():
    return [
        random.randrange(1, WIDTH // CELL_SIZE) * CELL_SIZE,
        random.randrange(1, HEIGHT // CELL_SIZE) * CELL_SIZE
    ]

fruit_pos = generate_fruit()
fruit_spawn = True

direction = "RIGHT"
change_to = direction

start_time = time.time()
score = 0
max_score = 0

auto_mode = True

# Чтение рекорда
def read_max_score():
    try:
        with open("record.txt", "r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

max_score = read_max_score()

# Сохранение рекорда
def save_max_score(score_val):
    with open("record.txt", "w") as file:
        file.write(str(score_val))

# Функции отрисовки
def draw_snake(snake_body):
    for pos in snake_body:
        pygame.draw.rect(WIN, BLACK, pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE))

def draw_fruit(fruit_pos):
    pygame.draw.rect(WIN, RED, pygame.Rect(fruit_pos[0], fruit_pos[1], CELL_SIZE, CELL_SIZE))

def draw_timer(seconds):
    font = pygame.font.SysFont(None, 36)
    time_left = max(0, 15 - seconds)
    text = font.render(f'Time left: {time_left:.1f}', True, BLACK)
    WIN.blit(text, (10, 10))

def draw_score(score, max_score):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f'Score: {score} Max Score: {max_score}', True, BLACK)
    WIN.blit(text, (WIDTH - 350, 10))

def draw_pause():
    font = pygame.font.SysFont(None, 48)
    text = font.render("PAUSED", True, BLACK)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

def game_over():
    logging.info("Game is over")
    save_max_score(max_score)
    font = pygame.font.SysFont(None, 60)
    text = font.render("GAME OVER", True, RED)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))
    pygame.display.flip()
    time.sleep(2)  # Показать надпись 2 секунды
    pygame.quit()
    sys.exit()

# Проверка столкновений
def check_collisions(snake_pos, snake_body):
    # Стенки
    if snake_pos[0] < 0 or snake_pos[0] >= WIDTH or snake_pos[1] < 0 or snake_pos[1] >= HEIGHT:
        logging.info('Snake collided with the wall')
        return True
    # С собой
    if snake_pos in snake_body[1:]:
        logging.info("Snake collided with itself")
        return True
    return False

# Основной цикл
paused = False
paused_start_time = 0
clock = pygame.time.Clock()

targeting.start_search(snake_body, snake_pos, fruit_pos, CELL_SIZE, WIDTH, HEIGHT)

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_max_score(max_score)
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_max_score(max_score)
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    paused_start_time = time.time()
                    logging.info("Game paused")
                else:
                    pause_duration = time.time() - paused_start_time
                    start_time += pause_duration  # Сдвигаем start_time, чтобы компенсировать паузу
                    logging.info("Game resumed")

            if not paused:
                if event.key == pygame.K_LEFT:
                    change_to = "LEFT"
                    logging.info("Pressed LEFT")
                elif event.key == pygame.K_RIGHT:
                    change_to = "RIGHT"
                    logging.info("Pressed RIGHT")
                elif event.key == pygame.K_UP:
                    change_to = "UP"
                    logging.info("Pressed UP")
                elif event.key == pygame.K_DOWN:
                    change_to = "DOWN"
                    logging.info("Pressed DOWN")

    if not paused:
        if auto_mode == True:
            change_to = targeting.get_move_from_buffer()

        # Обновление направления (с защитой от разворота на 180°)
        if change_to == "LEFT" and direction != "RIGHT":
            direction = "LEFT"
        elif change_to == "RIGHT" and direction != "LEFT":
            direction = "RIGHT"
        elif change_to == "UP" and direction != "DOWN":
            direction = "UP"
        elif change_to == "DOWN" and direction != "UP":
            direction = "DOWN"

        # Движение змейки
        if direction == "LEFT":
            snake_pos[0] -= CELL_SIZE
        elif direction == "RIGHT":
            snake_pos[0] += CELL_SIZE
        elif direction == "UP":
            snake_pos[1] -= CELL_SIZE
        elif direction == "DOWN":
            snake_pos[1] += CELL_SIZE

        # Проверка столкновений
        if check_collisions(snake_pos, snake_body):
            game_over()

        # Обновление тела змейки
        snake_body.insert(0, list(snake_pos))

        # Проверка поедания фрукта
        if snake_pos[0] == fruit_pos[0] and snake_pos[1] == fruit_pos[1]:
            logging.info("Snake ate fruit")
            score += 1
            if score > max_score:
                max_score = score
            fruit_spawn = False
            start_time = time.time()  # Сброс таймера

            #targeting.start_search(snake_body, snake_pos, fruit_pos, CELL_SIZE, WIDTH, HEIGHT)
        else:
            snake_body.pop()

        # Генерация нового фрукта
        if not fruit_spawn:
            fruit_pos = generate_fruit()
            fruit_spawn = True

            targeting.start_search(snake_body.copy(), snake_pos, fruit_pos, CELL_SIZE, WIDTH, HEIGHT)

        # Проверка таймера
        if elapsed_time >= 150:
            logging.info("Time is over")
            game_over()

    # Отрисовка
    WIN.fill(WHITE)
    draw_snake(snake_body)
    for test in targeting.buffer:
        pygame.draw.rect(WIN, RED, pygame.Rect(test['pos'][0] * CELL_SIZE + CELL_SIZE / 4, test['pos'][1] * CELL_SIZE + CELL_SIZE / 4, CELL_SIZE / 2, CELL_SIZE / 2))
    for y in range(len(targeting.testBuffer)):
        x = targeting.testBuffer[y]
        pygame.draw.rect(WIN, (0, 255, max(min(255, (1 - y) * 255), 0)), pygame.Rect(x[0] * CELL_SIZE + CELL_SIZE / 4, x[1] * CELL_SIZE + CELL_SIZE / 4, CELL_SIZE / 3, CELL_SIZE / 3))
    draw_fruit(fruit_pos)
    draw_timer(elapsed_time if not paused else 0)
    draw_score(score, max_score)

    if paused:
        draw_pause()

    pygame.display.flip()
    clock.tick(FPS)