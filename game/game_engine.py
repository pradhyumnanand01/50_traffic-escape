import pygame
import random
import json
import os

from game.player import Player, LANE_W
from game.traffic import make_car

LANES = 8
WIDTH = LANES * LANE_W
HEIGHT = 600
FPS = 60

SCORE_FILE = "highscores.json"

# Task 4: Day/Night cycle
DAY_NIGHT_TIME = 30_000  # 30 seconds

# Task 2: Water/log area
WATER_TOP = 270
WATER_BOTTOM = 350


class Log:
    def __init__(self, x, y, width, speed):
        self.rect = pygame.Rect(x, y, width, 35)
        self.speed = speed
        self.color = (130, 85, 40)

    def update(self):
        self.rect.x += self.speed

        # Wrap logs around the screen so they keep coming back
        if self.speed > 0 and self.rect.left > WIDTH:
            self.rect.right = -random.randint(20, 150)

        elif self.speed < 0 and self.rect.right < 0:
            self.rect.left = WIDTH + random.randint(20, 150)

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=8
        )

        # Log lines
        for x in range(self.rect.left + 10, self.rect.right, 20):
            pygame.draw.line(
                screen,
                (90, 55, 25),
                (x, self.rect.top + 5),
                (x, self.rect.bottom - 5),
                2
            )


class GameEngine:

    def __init__(self, screen):
        self.screen = screen

        pygame.font.init()

        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 52)
        self.small_font = pygame.font.SysFont(None, 24)

        self.reset()

    # ---------------------------------------------------------
    # RESET GAME
    # ---------------------------------------------------------

    def reset(self):

        self.player = Player(
            WIDTH // 2,
            HEIGHT - 70
        )

        # -------------------------
        # Traffic
        # -------------------------

        self.cars = []

        self.timer = 0
        self.spawn_interval = 45

        self.speed = 3

        # -------------------------
        # Score
        # -------------------------

        self.score = 0

        # -------------------------
        # Task 1: Lives
        # -------------------------

        self.lives = 3
        self.game_over = False
        self.won = False

        self.last_hit_time = 0

        # -------------------------
        # Task 2: Moving logs
        # -------------------------

        self.logs = [
            Log(20, 285, 150, 2),
            Log(280, 285, 180, 2),
            Log(600, 285, 140, 2),

            Log(100, 325, 180, -2),
            Log(420, 325, 150, -2),
            Log(650, 325, 120, -2),
        ]

        # -------------------------
        # Task 4: Day/Night
        # -------------------------

        self.start_time = pygame.time.get_ticks()

        self.night = False

        # -------------------------
        # High scores
        # -------------------------

        self.high_scores = self.load_high_scores()

    # ---------------------------------------------------------
    # HIGH SCORE SYSTEM
    # ---------------------------------------------------------

    def load_high_scores(self):

        if not os.path.exists(SCORE_FILE):
            return []

        try:
            with open(SCORE_FILE, "r") as f:
                scores = json.load(f)

            if isinstance(scores, list):
                return sorted(scores, reverse=True)[:5]

        except Exception:
            pass

        return []

    def save_high_score(self):

        scores = self.load_high_scores()

        scores.append(self.score)

        scores = sorted(scores, reverse=True)[:5]

        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(scores, f, indent=4)
        except Exception:
            pass

        self.high_scores = scores

    # ---------------------------------------------------------
    # LOSE LIFE
    # ---------------------------------------------------------

    def lose_life(self):

        current_time = pygame.time.get_ticks()

        # Prevent multiple life losses from one collision
        if current_time - self.last_hit_time < 1000:
            return

        self.last_hit_time = current_time

        self.lives -= 1

        self.player.reset_position()

        # Game over when lives reach zero
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True
            self.save_high_score()

    # ---------------------------------------------------------
    # CHECK PLAYER ON LOG
    # ---------------------------------------------------------

    def player_on_log(self):

        # If player isn't inside the water area,
        # they are automatically safe.
        if (
            self.player.rect.bottom < WATER_TOP
            or self.player.rect.top > WATER_BOTTOM
        ):
            return True

        # Check whether player is standing on a log
        for log in self.logs:

            if self.player.rect.colliderect(log.rect):

                return True

        return False

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self, keys):

        if self.game_over or self.won:
            return

        # =====================================================
        # TASK 4: DAY / NIGHT CYCLE
        # =====================================================

        elapsed = pygame.time.get_ticks() - self.start_time

        cycle = elapsed // DAY_NIGHT_TIME

        self.night = (cycle % 2 == 1)

        # =====================================================
        # PLAYER MOVEMENT
        # =====================================================

        self.player.move(
            keys,
            0,
            WIDTH
        )

        # =====================================================
        # TRAFFIC
        # =====================================================

        self.timer += 1

        if self.timer >= self.spawn_interval:

            self.timer = 0

            lane = random.randint(
                0,
                LANES - 1
            )

            direction = random.choice(
                [-1, 1]
            )

            car = make_car(
                lane,
                direction,
                self.speed
            )

            self.cars.append(car)

        # Update cars
        for car in self.cars:

            car.update()

        # Remove cars outside screen
        self.cars = [
            car
            for car in self.cars
            if not car.off_screen(HEIGHT)
        ]

        # =====================================================
        # TASK 2: MOVING LOGS
        # =====================================================

        for log in self.logs:
            log.update()

        # =====================================================
        # COLLISION WITH CARS
        # =====================================================

        for car in self.cars:

            if car.rect.colliderect(
                self.player.rect
            ):

                self.lose_life()

                break

        # =====================================================
        # WATER CHECK
        # =====================================================

        in_water = (
            self.player.rect.centery >= WATER_TOP
            and self.player.rect.centery <= WATER_BOTTOM
        )

        if in_water:

            if not self.player_on_log():

                self.lose_life()

        # =====================================================
        # SCORE
        # =====================================================

        if not self.game_over:

            self.score += 1

        # =====================================================
        # WIN CONDITION
        # =====================================================

        if self.player.rect.top <= 0:

            self.won = True

            self.save_high_score()

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------

    def draw(self):

        # =====================================================
        # TASK 4: DAY / NIGHT BACKGROUND
        # =====================================================

        if self.night:

            self.screen.fill(
                (15, 20, 40)
            )

        else:

            self.screen.fill(
                (60, 60, 60)
            )

        # =====================================================
        # ROAD
        # =====================================================

        pygame.draw.rect(
            self.screen,
            (65, 65, 65),
            pygame.Rect(
                0,
                0,
                WIDTH,
                HEIGHT
            )
        )

        # =====================================================
        # WATER
        # =====================================================

        pygame.draw.rect(
            self.screen,
            (30, 100, 170),
            pygame.Rect(
                0,
                WATER_TOP,
                WIDTH,
                WATER_BOTTOM - WATER_TOP
            )
        )

        # Water lines
        for y in range(
            WATER_TOP + 10,
            WATER_BOTTOM,
            15
        ):

            pygame.draw.line(
                self.screen,
                (80, 160, 210),
                (0, y),
                (WIDTH, y),
                2
            )

        # =====================================================
        # SIDEWALKS
        # =====================================================

        pygame.draw.rect(
            self.screen,
            (110, 110, 110),
            pygame.Rect(
                0,
                WATER_TOP - 20,
                WIDTH,
                20
            )
        )

        pygame.draw.rect(
            self.screen,
            (110, 110, 110),
            pygame.Rect(
                0,
                WATER_BOTTOM,
                WIDTH,
                20
            )
        )

        # =====================================================
        # LOGS
        # =====================================================

        for log in self.logs:

            log.draw(
                self.screen
            )

        # =====================================================
        # CARS
        # =====================================================

        for car in self.cars:

            # Task 4:
            # Tell the car whether it is night.
            car.draw(
                self.screen,
                self.night
            )

        # =====================================================
        # PLAYER
        # =====================================================

        self.player.draw(
            self.screen
        )

        # =====================================================
        # HUD
        # =====================================================

        score_surface = self.font.render(
            f"Score: {self.score}",
            True,
            (255, 255, 255)
        )

        lives_surface = self.font.render(
            f"Lives: {self.lives}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            score_surface,
            (10, 7)
        )

        self.screen.blit(
            lives_surface,
            (120, 7)
        )

        # =====================================================
        # DAY / NIGHT INDICATOR
        # =====================================================

        mode = "NIGHT" if self.night else "DAY"

        mode_color = (
            (255, 230, 120)
            if self.night
            else (255, 255, 255)
        )

        mode_surface = self.font.render(
            mode,
            True,
            mode_color
        )

        self.screen.blit(
            mode_surface,
            (270, 7)
        )

        # =====================================================
        # GAME OVER
        # =====================================================

        if self.game_over:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 150)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            game_over_surface = self.big_font.render(
                "GAME OVER",
                True,
                (255, 80, 80)
            )

            self.screen.blit(
                game_over_surface,
                (
                    WIDTH // 2 -
                    game_over_surface.get_width() // 2,
                    190
                )
            )

            # High score heading
            title_surface = self.font.render(
                "TOP 5 HIGH SCORES",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                title_surface,
                (
                    WIDTH // 2 -
                    title_surface.get_width() // 2,
                    270
                )
            )

            # High score list
            for i, score in enumerate(
                self.high_scores[:5]
            ):

                score_text = self.font.render(
                    f"{i + 1}. {score}",
                    True,
                    (255, 255, 255)
                )

                self.screen.blit(
                    score_text,
                    (
                        WIDTH // 2 -
                        score_text.get_width() // 2,
                        305 + i * 30
                    )
                )

        # =====================================================
        # WIN SCREEN
        # =====================================================

        if self.won:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 140)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            win_surface = self.big_font.render(
                "YOU WIN!",
                True,
                (100, 255, 120)
            )

            self.screen.blit(
                win_surface,
                (
                    WIDTH // 2 -
                    win_surface.get_width() // 2,
                    220
                )
            )

            score_surface = self.font.render(
                f"Score: {self.score}",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                score_surface,
                (
                    WIDTH // 2 -
                    score_surface.get_width() // 2,
                    285
                )
            )