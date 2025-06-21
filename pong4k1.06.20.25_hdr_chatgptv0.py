# simple_pong.py  —  zero‑shot Pygame implementation
import pygame, sys, random

# ---------- config ----------
WIDTH, HEIGHT      = 800, 450          # window size (16:9)
BG_COLOR           = (30, 30, 30)
WHITE              = (240, 240, 240)
PADDLE_W, PADDLE_H = 12, 90
BALL_SIZE          = 14
BALL_SPEED_X       = 5
BALL_SPEED_Y       = 4
AI_MAX_SPEED       = 4                 # pixels per frame
WIN_SCORE          = 5
FONT_SIZE          = 48

pygame.init()
screen   = pygame.display.set_mode((WIDTH, HEIGHT))
clock    = pygame.time.Clock()
font_big = pygame.font.SysFont(None, FONT_SIZE)

# ---------- game objects ----------
ball     = pygame.Rect(WIDTH//2 - BALL_SIZE//2,
                       HEIGHT//2 - BALL_SIZE//2,
                       BALL_SIZE, BALL_SIZE)
p_left   = pygame.Rect(40,  HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
p_right  = pygame.Rect(WIDTH-40-PADDLE_W, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
ball_vel = pygame.Vector2(random.choice((-BALL_SPEED_X, BALL_SPEED_X)),
                          random.choice((-BALL_SPEED_Y, BALL_SPEED_Y)))

score_l = score_r = 0
game_over = False
winner = None  # "PLAYER" or "CPU"

# ---------- helpers ----------
def reset_ball():
    global ball_vel
    ball.center = (WIDTH//2, HEIGHT//2)
    ball_vel = pygame.Vector2(random.choice((-BALL_SPEED_X, BALL_SPEED_X)),
                              random.choice((-BALL_SPEED_Y, BALL_SPEED_Y)))

def restart_game():
    global score_l, score_r, game_over, winner
    score_l = score_r = 0
    game_over = False
    winner = None
    reset_ball()

# ---------- main loop ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                restart_game()
            elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

    # --------------- update ---------------
    if not game_over:
        # left paddle follows mouse (clamp to screen)
        mouse_y = pygame.mouse.get_pos()[1]
        p_left.centery = max(PADDLE_H//2, min(HEIGHT - PADDLE_H//2, mouse_y))

        # simple AI: move toward ball with capped speed
        if ball.centery < p_right.centery - 5:
            p_right.centery -= AI_MAX_SPEED
        elif ball.centery > p_right.centery + 5:
            p_right.centery += AI_MAX_SPEED
        p_right.centery = max(PADDLE_H//2, min(HEIGHT - PADDLE_H//2, p_right.centery))

        # move ball
        ball.x += int(ball_vel.x)
        ball.y += int(ball_vel.y)

        # top/bottom collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel.y *= -1

        # paddle collisions
        if ball.colliderect(p_left) and ball_vel.x < 0:
            ball.left = p_left.right
            ball_vel.x *= -1
        if ball.colliderect(p_right) and ball_vel.x > 0:
            ball.right = p_right.left
            ball_vel.x *= -1

        # scoring
        if ball.left <= 0:
            score_r += 1
            reset_ball()
        if ball.right >= WIDTH:
            score_l += 1
            reset_ball()

        # check win
        if score_l == WIN_SCORE or score_r == WIN_SCORE:
            game_over = True
            winner = "PLAYER" if score_l > score_r else "CPU"

    # --------------- draw ---------------
    screen.fill(BG_COLOR)

    # center dividing line
    pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

    # paddles & ball
    pygame.draw.rect(screen, WHITE, p_left)
    pygame.draw.rect(screen, WHITE, p_right)
    pygame.draw.ellipse(screen, WHITE, ball)

    # scores
    score_txt = font_big.render(f"{score_l}   {score_r}", True, WHITE)
    screen.blit(score_txt, score_txt.get_rect(center=(WIDTH//2, 40)))

    # game‑over overlay
    if game_over:
        over_txt = font_big.render(f"{winner} WINS!", True, WHITE)
        prompt   = font_big.render("Play again?  Y / N", True, WHITE)
        screen.blit(over_txt, over_txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

    pygame.display.flip()
    clock.tick(60)
