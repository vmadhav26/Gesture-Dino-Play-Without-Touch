import cv2
import mediapipe as mp
import pygame
import random
import sys
import numpy as np

# -------------------- SETUP -----------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

pygame.init()
WIDTH, HEIGHT = 800, 400
WEBCAM_WIDTH = 320
win = pygame.display.set_mode((WIDTH + WEBCAM_WIDTH, HEIGHT))
pygame.display.set_caption("Gesture-Controlled Dino Game")
clock = pygame.time.Clock()

dino_img = pygame.image.load("C:/Users/Venumadhav Ananthula/OneDrive/Desktop/projects/dino_cv_game/assets/dino.png")
cactus_img = pygame.image.load("C:/Users/Venumadhav Ananthula/OneDrive/Desktop/projects/dino_cv_game/assets/cactus.png")
dino_img = pygame.transform.scale(dino_img, (60, 60))
cactus_img = pygame.transform.scale(cactus_img, (40, 60))

font = pygame.font.SysFont(None, 36)

# -------------------- FUNCTIONS -----------------------

def is_fist_closed(handLms):
    folded_fingers = 0
    finger_ids = [(8, 6), (12, 10), (16, 14), (20, 18)]
    for tip_id, mcp_id in finger_ids:
        if handLms.landmark[tip_id].y > handLms.landmark[mcp_id].y:
            folded_fingers += 1
    return folded_fingers >= 3

def draw_game(dino_y, cactus_x, cactus_y, score, webcam_surf, is_night):
    bg_color = (25, 25, 112) if is_night else (255, 255, 255)
    font_color = (255, 255, 255) if is_night else (0, 0, 0)

    win.fill(bg_color)
    win.blit(dino_img, (dino_x, dino_y))
    win.blit(cactus_img, (cactus_x, cactus_y))

    score_text = font.render(f"Score: {score}", True, font_color)
    win.blit(score_text, (10, 10))
    win.blit(webcam_surf, (WIDTH, 0))
    pygame.display.update()

def show_game_over_screen(final_score, is_night):
    bg_color = (25, 25, 112) if is_night else (0, 0, 0)
    font_color = (255, 255, 255)

    win.fill(bg_color)
    lines = [
        font.render("Game Over!", True, (255, 0, 0)),
        font.render(f"Your Score: {final_score}", True, font_color),
        font.render("Press R to Restart", True, font_color),
        font.render("Press ESC to Exit", True, font_color),
    ]
    for i, line in enumerate(lines):
        win.blit(line, (WIDTH // 2 - 120, HEIGHT // 2 - 60 + i * 40))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    return  # restart

def check_collision(dino_y, cactus_x, cactus_y):
    if cactus_x < dino_x + 60 and cactus_x + 40 > dino_x:
        if dino_y + 60 > cactus_y:
            return True
    return False

# -------------------- GAME LOOP FUNCTION -----------------------

def run_game():
    global dino_x  # needed for draw_game
    dino_x = 100
    dino_y = HEIGHT - 100
    jump = False
    jump_velocity = 15
    gravity = 1
    current_velocity = jump_velocity
    cactus_x = WIDTH
    cactus_y = HEIGHT - 100
    cactus_speed = 7
    score = 0
    is_night = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    is_night = not is_night

        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                if is_fist_closed(handLms) and not jump:
                    jump = True
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

        frame = cv2.resize(frame, (WEBCAM_WIDTH, HEIGHT))
        frame_surface = pygame.surfarray.make_surface(np.rot90(frame))

        # Dino Jump Logic
        if jump:
            dino_y -= current_velocity
            current_velocity -= gravity
            if current_velocity < -jump_velocity:
                jump = False
                current_velocity = jump_velocity
        else:
            dino_y = HEIGHT - 100

        # Cactus movement & score
        cactus_x -= cactus_speed
        if cactus_x < -40:
            cactus_x = WIDTH + random.randint(0, 200)
            score += 50

        score += 1

        if score % 200 == 0:
            cactus_speed += 0.5

        if check_collision(dino_y, cactus_x, cactus_y):
            show_game_over_screen(score, is_night)
            return  # restart loop

        draw_game(dino_y, cactus_x, cactus_y, score, frame_surface, is_night)
        clock.tick(30)

# -------------------- RUN GAME -----------------------
while True:
    run_game()
