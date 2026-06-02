import pygame
import random
import math


class Vehicle:
    """Player's moon patrol vehicle"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 72
        self.height = 40
        self.vel_y = 0
        self.on_ground = True
        self.gravity = 0.8
        self.jump_power = -16
        self.ground_y = y
        self.alive = True
        self.wheel_angle = 0
        self.bullet_cooldown = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def shoot(self):
        if self.bullet_cooldown <= 0:
            self.bullet_cooldown = 12
            return Bullet(self.x + self.width, self.y + self.height // 2 - 4, direction=1)
        return None

    def update(self):
        if not self.on_ground:
            self.vel_y += self.gravity
            self.y += self.vel_y
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vel_y = 0
                self.on_ground = True

        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

        self.wheel_angle += 4

    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 8, self.width - 16, self.height - 8)

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y)

        # Body
        body_rect = pygame.Rect(cx + 6, cy + 6, self.width - 12, self.height - 16)
        pygame.draw.rect(surface, (40, 180, 90), body_rect, border_radius=6)
        pygame.draw.rect(surface, (60, 220, 110), body_rect, 2, border_radius=6)

        # Cockpit
        cockpit = pygame.Rect(cx + 18, cy, 28, 16)
        pygame.draw.rect(surface, (20, 100, 60), cockpit, border_radius=4)
        pygame.draw.rect(surface, (100, 255, 160), cockpit, 1, border_radius=4)

        # Cannon
        pygame.draw.rect(surface, (180, 180, 60), (cx + self.width - 18, cy + 14, 22, 7), border_radius=3)

        # Wheels
        for wx in [cx + 14, cx + self.width - 20]:
            wy = cy + self.height - 10
            pygame.draw.circle(surface, (50, 50, 50), (wx, wy), 10)
            pygame.draw.circle(surface, (100, 100, 100), (wx, wy), 10, 2)
            # Spokes
            for i in range(4):
                angle = math.radians(self.wheel_angle + i * 90)
                sx = wx + int(7 * math.cos(angle))
                sy = wy + int(7 * math.sin(angle))
                pygame.draw.line(surface, (160, 160, 160), (wx, wy), (sx, sy), 2)


class Bullet:
    """Projectile fired by the player"""

    def __init__(self, x, y, direction=1):
        self.x = float(x)
        self.y = float(y)
        self.speed = 14
        self.direction = direction
        self.active = True
        self.width = 14
        self.height = 5

    def update(self, scroll_speed):
        self.x += self.speed
        self.x -= scroll_speed  # bullets move with world scroll too

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y) - 2, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 80), (int(self.x), int(self.y) - 2, self.width, self.height), border_radius=2)
        pygame.draw.rect(surface, (255, 200, 0), (int(self.x), int(self.y) - 2, self.width, self.height), 1, border_radius=2)


class EnemyCar:
    """Enemy vehicle coming from the right"""

    def __init__(self, x, y, speed):
        self.x = float(x)
        self.y = float(y)
        self.width = 60
        self.height = 34
        self.speed = speed
        self.active = True
        self.wheel_angle = 0
        self.explosion_timer = 0
        self.exploding = False

    def update(self, scroll_speed):
        self.x -= self.speed + scroll_speed * 0.5
        self.wheel_angle += 5
        if self.exploding:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.active = False

    def explode(self):
        self.exploding = True
        self.explosion_timer = 25

    def get_rect(self):
        if self.exploding:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(int(self.x) + 6, int(self.y) + 6, self.width - 12, self.height - 8)

    def draw(self, surface):
        cx = int(self.x)
        cy = int(self.y)

        if self.exploding:
            # Explosion effect
            progress = 1 - (self.explosion_timer / 25)
            radius = int(30 * progress + 10)
            alpha = int(255 * (1 - progress))
            for i in range(8):
                angle = math.radians(i * 45 + self.explosion_timer * 15)
                dist = int(radius * 0.7)
                px = cx + self.width // 2 + int(dist * math.cos(angle))
                py = cy + self.height // 2 + int(dist * math.sin(angle))
                r = max(0, int(12 * (1 - progress)))
                if r > 0:
                    color_val = min(255, int(alpha))
                    pygame.draw.circle(surface, (color_val, color_val // 2, 0), (px, py), r)
            pygame.draw.circle(surface, (255, 200, 0), (cx + self.width // 2, cy + self.height // 2), max(1, radius // 2))
            return

        # Body
        body_rect = pygame.Rect(cx + 4, cy + 8, self.width - 8, self.height - 14)
        pygame.draw.rect(surface, (180, 40, 40), body_rect, border_radius=5)
        pygame.draw.rect(surface, (220, 80, 80), body_rect, 2, border_radius=5)

        # Cabin
        cabin = pygame.Rect(cx + 14, cy + 2, 22, 12)
        pygame.draw.rect(surface, (100, 20, 20), cabin, border_radius=3)

        # Wheels
        for wx in [cx + 12, cx + self.width - 16]:
            wy = cy + self.height - 8
            pygame.draw.circle(surface, (50, 50, 50), (wx, wy), 9)
            pygame.draw.circle(surface, (120, 40, 40), (wx, wy), 9, 2)
            for i in range(4):
                angle = math.radians(self.wheel_angle + i * 90)
                sx = wx + int(6 * math.cos(angle))
                sy = wy + int(6 * math.sin(angle))
                pygame.draw.line(surface, (160, 80, 80), (wx, wy), (sx, sy), 2)


class Obstacle:
    """Rock or crater on the ground"""

    def __init__(self, x, ground_y, kind="rock"):
        self.x = float(x)
        self.kind = kind
        self.active = True

        if kind == "rock":
            self.width = random.randint(22, 40)
            self.height = random.randint(20, 35)
            self.y = ground_y - self.height
            self.color = (140, 120, 100)
        else:  # hole/crater
            self.width = random.randint(40, 65)
            self.height = 18
            self.y = ground_y
            self.color = (20, 15, 10)

    def update(self, scroll_speed):
        self.x -= scroll_speed

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface, ground_y):
        cx = int(self.x)
        cy = int(self.y)

        if self.kind == "rock":
            points = [
                (cx + self.width // 2, cy),
                (cx + self.width, cy + self.height * 0.6),
                (cx + self.width * 0.85, cy + self.height),
                (cx + self.width * 0.15, cy + self.height),
                (cx, cy + self.height * 0.6),
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, (180, 160, 130), points, 2)
            # Highlight
            pygame.draw.line(surface, (200, 180, 150),
                             (cx + self.width // 3, cy + 4),
                             (cx + self.width * 2 // 3, cy + 4), 2)
        else:
            # Crater / hole
            pygame.draw.ellipse(surface, (15, 10, 5),
                                (cx, ground_y - 8, self.width, 20))
            pygame.draw.ellipse(surface, (40, 30, 20),
                                (cx, ground_y - 8, self.width, 20), 2)


class Star:
    """Background star"""

    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, int(screen_height * 0.65))
        self.size = random.choice([1, 1, 1, 2])
        self.speed = random.uniform(0.2, 0.8)
        self.brightness = random.randint(150, 255)

    def update(self, scroll_speed, screen_width):
        self.x -= self.speed * scroll_speed * 0.15
        if self.x < 0:
            self.x = screen_width
            self.y = random.randint(0, 200)

    def draw(self, surface):
        c = self.brightness
        pygame.draw.circle(surface, (c, c, c), (int(self.x), int(self.y)), self.size)


class ScoreTracker:
    """Tracks score and speed progression"""

    def __init__(self):
        self.score = 0
        self.kills = 0
        self.distance = 0
        self.base_speed = 4.0
        self.speed = self.base_speed
        self.high_score = 0

    def add_kill(self):
        self.kills += 1
        self.score += 100

    def add_distance(self, amount):
        self.distance += amount
        self.score += int(amount * 0.1)

    def update_speed(self):
        # Speed increases every 500 score points
        level = self.score // 500
        self.speed = self.base_speed + level * 0.4
        self.speed = min(self.speed, 12.0)

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
        return self.high_score

    def get_level(self):
        return self.score // 500 + 1