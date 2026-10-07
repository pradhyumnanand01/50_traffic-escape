import pygame
import random

LANE_W = 80

COLORS = [
    (220, 60, 60),
    (220, 140, 40),
    (140, 60, 180),
    (60, 180, 80),
    (180, 180, 40),
    (60, 80, 200)
]


class Car:

    def __init__(self, lane_x, y, direction, speed):

        self.rect = pygame.Rect(
            lane_x + 10,
            y,
            60,
            80
        )

        self.direction = direction
        self.speed = speed
        self.color = random.choice(COLORS)

    def update(self):

        self.rect.y += (
            self.direction * self.speed
        )

    def off_screen(self, height):

        return (
            self.rect.top > height + 100
            or self.rect.bottom < -100
        )

    def draw(self, screen, night=False):

        # ==========================================
        # CAR BODY
        # ==========================================

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=8
        )

        # ==========================================
        # WINDOWS
        # ==========================================

        pygame.draw.rect(
            screen,
            (180, 220, 240),
            pygame.Rect(
                self.rect.x + 8,
                self.rect.y + 10,
                44,
                22
            ),
            border_radius=4
        )

        # ==========================================
        # WHEELS
        # ==========================================

        for wx in [
            self.rect.x + 6,
            self.rect.right - 16
        ]:

            for wy in [
                self.rect.y + 4,
                self.rect.bottom - 16
            ]:

                pygame.draw.rect(
                    screen,
                    (30, 30, 30),
                    pygame.Rect(
                        wx,
                        wy,
                        10,
                        12
                    ),
                    border_radius=3
                )

        # ==========================================
        # TASK 4 — NIGHT HEADLIGHTS
        # ==========================================

        if night:

            # Transparent surface for the light beams
            light_surface = pygame.Surface(
                screen.get_size(),
                pygame.SRCALPHA
            )

            # --------------------------------------
            # CAR MOVING DOWN
            # --------------------------------------

            if self.direction == 1:

                headlights = [
                    (
                        self.rect.x + 18,
                        self.rect.bottom
                    ),
                    (
                        self.rect.x + 42,
                        self.rect.bottom
                    )
                ]

                for x, y in headlights:

                    # Large light beam
                    pygame.draw.polygon(
                        light_surface,
                        (255, 240, 150, 45),
                        [
                            (x - 10, y),
                            (x + 10, y),
                            (x + 45, y + 140),
                            (x - 45, y + 140)
                        ]
                    )

                    # Bright headlight
                    pygame.draw.circle(
                        light_surface,
                        (255, 255, 220, 230),
                        (x, y),
                        6
                    )

            # --------------------------------------
            # CAR MOVING UP
            # --------------------------------------

            else:

                headlights = [
                    (
                        self.rect.x + 18,
                        self.rect.top
                    ),
                    (
                        self.rect.x + 42,
                        self.rect.top
                    )
                ]

                for x, y in headlights:

                    # Large light beam
                    pygame.draw.polygon(
                        light_surface,
                        (255, 240, 150, 45),
                        [
                            (x - 10, y),
                            (x + 10, y),
                            (x + 45, y - 140),
                            (x - 45, y - 140)
                        ]
                    )

                    # Bright headlight
                    pygame.draw.circle(
                        light_surface,
                        (255, 255, 220, 230),
                        (x, y),
                        6
                    )

            # Put headlights onto the game screen
            screen.blit(
                light_surface,
                (0, 0)
            )


def make_car(lane_idx, height, speed):

    x = lane_idx * LANE_W

    direction = (
        1
        if lane_idx % 2 == 0
        else -1
    )

    y = (
        -90
        if direction == 1
        else height + 10
    )

    return Car(
        x,
        y,
        direction,
        speed
    )