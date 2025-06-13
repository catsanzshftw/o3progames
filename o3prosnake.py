#!/usr/bin/env python3
"""
snake_nokia3310_atari.py — zero‑asset Snake in Atari style for 84×48 Nokia LCD
───────────────────────────────────────────────────────────────────
Transforms the Nokia Snake into a classic Atari‑style Snake:
• 🚫 No wrap‑around: running into a wall ends the game.
• ⚡ Dynamic speed: each time you eat, the game speeds up (down to a cap).
• 🎶 Retains simple beeps for eat and death, 60 fps display.

Run with Python ≥ 3.8 and pygame ≥ 2.1.0.
"""

import sys
import random
from pathlib import Path  # noqa: F401 (unused import kept for symmetry)

import numpy as np
import pygame

# ─── CONFIG ────────────────────────────────────────────────────────────────────
LOGICAL_W, LOGICAL_H = 84, 48          # Nokia 3310 LCD resolution (pixels)
SCALE               = 8                # visibility scale
CELL                = 4                # 84/4=21 cols, 48/4=12 rows
GRID_W, GRID_H      = LOGICAL_W // CELL, LOGICAL_H // CELL
WINDOW_SIZE         = (LOGICAL_W * SCALE, LOGICAL_H * SCALE)
INITIAL_MOVE_MS     = 100              # starting move interval (10 Hz)
MIN_MOVE_MS         = 40               # fastest move interval (25 Hz)
SPEED_STEP_MS       = 5                # decrease interval by 5 ms per food
FPS_TARGET          = 60               # screen refresh
COL_FG, COL_BG      = (150, 255, 150), (20, 20, 20)
TONE_EAT_HZ         = 880
TONE_DEAD_HZ        = 110
# ────────────────────────────────────────────────────────────────────────────────

pygame.init()
pygame.mixer.init(frequency=22_050, size=-16, channels=1)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Snake — Atari Mode")
clock = pygame.time.Clock()

# ─── AUDIO HELPERS ─────────────────────────────────────────────────────────────

def synth_tone(freq_hz: int, dur_sec: float = 0.12) -> pygame.mixer.Sound:
    freq, _size, channels = pygame.mixer.get_init()
    length = int(freq * dur_sec)
    t = np.arange(length)
    mono = (np.sign(np.sin(2 * np.pi * freq_hz * t / freq)) * 32767).astype(np.int16)
    wave = mono if channels == 1 else np.repeat(mono[:, None], channels, axis=1)
    return pygame.sndarray.make_sound(wave)

SND_EAT  = synth_tone(TONE_EAT_HZ, 0.08)
SND_DEAD = synth_tone(TONE_DEAD_HZ, 0.20)

# ─── GAME CONSTANTS ────────────────────────────────────────────────────────────
DIRS = {"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
KEY_TO_DIR = {pygame.K_w:"UP", pygame.K_s:"DOWN", pygame.K_a:"LEFT", pygame.K_d:"RIGHT"}

# ─── HELPERS ────────────────────────────────────────────────────────────────────
def new_food(snake):
    choices = [(x, y) for x in range(GRID_W) for y in range(GRID_H) if (x,y) not in snake]
    return random.choice(choices) if choices else None

def render_rect(col, pos):
    x,y = pos
    pygame.draw.rect(screen, col, (x*CELL*SCALE, y*CELL*SCALE, CELL*SCALE, CELL*SCALE))

# ─── MAIN LOOP ─────────────────────────────────────────────────────────────────
def game_loop():
    snake = [(GRID_W//2, GRID_H//2)]
    direction = "RIGHT"
    food = new_food(snake)
    move_ms = INITIAL_MOVE_MS
    last_step = pygame.time.get_ticks()
    alive = True

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in KEY_TO_DIR:
                    nd = KEY_TO_DIR[ev.key]
                    if len(snake)==1 or (DIRS[nd][0]!=-DIRS[direction][0] and DIRS[nd][1]!=-DIRS[direction][1]):
                        direction = nd
                if not alive and ev.key==pygame.K_SPACE:
                    return

        now = pygame.time.get_ticks()
        if alive and now - last_step >= move_ms:
            last_step = now
            dx, dy = DIRS[direction]
            head = (snake[0][0]+dx, snake[0][1]+dy)
            # Atari-style: no wrap → hitting wall kills
            if head[0]<0 or head[0]>=GRID_W or head[1]<0 or head[1]>=GRID_H or head in snake:
                alive = False; SND_DEAD.play()
            else:
                snake.insert(0, head)
                if head==food:
                    food=new_food(snake); SND_EAT.play()
                    move_ms = max(MIN_MOVE_MS, move_ms - SPEED_STEP_MS)
                else:
                    snake.pop()

        # Render
        screen.fill(COL_BG)
        for seg in snake: render_rect(COL_FG, seg)
        if food: render_rect(COL_FG, food)
        if not alive and (now//300)%2:
            pygame.draw.rect(screen, COL_BG, (0,0,*WINDOW_SIZE))
        pygame.display.flip()
        clock.tick(FPS_TARGET)

# ─── ENTRYPOINT ────────────────────────────────────────────────────────────────
if __name__=="__main__":
    while True: game_loop()
