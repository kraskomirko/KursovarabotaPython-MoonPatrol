import pygame
import sys
import random
import math
from models import Vehicle, Bullet, EnemyCar, Obstacle, Star, ScoreTracker

# ── Constants ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 500
FPS = 60
GROUND_Y = 390          # top of ground surface
VEHICLE_START_X = 140
VEHICLE_START_Y = GROUND_Y - 46

# Colors
COL_SKY_TOP    = (5, 5, 25)
COL_SKY_BOT    = (15, 25, 60)
COL_GROUND     = (55, 45, 35)
COL_GROUND_TOP = (75, 65, 50)
COL_MOON       = (220, 215, 190)
COL_HUD_TEXT   = (180, 255, 160)
COL_WHITE      = (255, 255, 255)
COL_YELLOW     = (255, 220, 60)
COL_RED        = (255, 80, 80)
COL_GREEN      = (60, 220, 100)
COL_DARK       = (10, 10, 20)


# ── Helpers ───────────────────────────────────────────────────────────────────
def draw_gradient_rect(surface, top_color, bot_color, rect):
    for y in range(rect.height):
        t = y / rect.height
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b),
                         (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))


def draw_text_shadow(surface, font, text, x, y, color, shadow=(0, 0, 0), center=False):
    shadow_surf = font.render(text, True, shadow)
    text_surf   = font.render(text, True, color)
    if center:
        shadow_surf_r = shadow_surf.get_rect(center=(x + 2, y + 2))
        text_surf_r   = text_surf.get_rect(center=(x, y))
    else:
        shadow_surf_r = (x + 2, y + 2)
        text_surf_r   = (x, y)
    surface.blit(shadow_surf, shadow_surf_r)
    surface.blit(text_surf, text_surf_r)


# ── Game class ────────────────────────────────────────────────────────────────
class MoonPatrol:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("MOON PATROL")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_big   = pygame.font.SysFont("Courier New", 52, bold=True)
        self.font_med   = pygame.font.SysFont("Courier New", 28, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 18)
        self.font_hud   = pygame.font.SysFont("Courier New", 22, bold=True)

        self.state = "menu"   # menu | playing | gameover
        self.high_score = 0

        self._init_stars()
        self._reset_game()

    # ── Initialisation ────────────────────────────────────────────────────────
    def _init_stars(self):
        self.stars = [Star(WIDTH, HEIGHT) for _ in range(120)]

    def _reset_game(self):
        self.vehicle   = Vehicle(VEHICLE_START_X, VEHICLE_START_Y)
        self.bullets   = []
        self.enemies   = []
        self.obstacles = []
        self.score_tracker = ScoreTracker()
        self.score_tracker.high_score = self.high_score
        self.spawn_timer   = 0
        self.enemy_timer   = 0
        self.scroll_offset = 0
        self.particles     = []

    # ── Spawning ──────────────────────────────────────────────────────────────
    def _try_spawn(self):
        speed = self.score_tracker.speed

        self.spawn_timer += 1
        interval = max(40, 90 - int(self.score_tracker.score / 300))
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            kind = random.choices(["rock", "hole"], weights=[55, 45])[0]
            # Don't stack obstacles too close to each other
            if not self.obstacles or self.obstacles[-1].x < WIDTH - 180:
                self.obstacles.append(Obstacle(WIDTH + 40, GROUND_Y, kind))

        self.enemy_timer += 1
        enemy_interval = max(80, 180 - int(self.score_tracker.score / 200))
        if self.enemy_timer >= enemy_interval:
            self.enemy_timer = 0
            enemy_speed = 2.5 + random.uniform(0, 1.5) + self.score_tracker.score / 2000
            self.enemies.append(EnemyCar(WIDTH + 60, VEHICLE_START_Y + 6, enemy_speed))

    # ── Collision ─────────────────────────────────────────────────────────────
    def _check_collisions(self):
        v_rect = self.vehicle.get_rect()

        # Bullet vs enemy
        for bullet in self.bullets:
            if not bullet.active:
                continue
            b_rect = bullet.get_rect()
            for enemy in self.enemies:
                if enemy.active and not enemy.exploding and b_rect.colliderect(enemy.get_rect()):
                    bullet.active = False
                    enemy.explode()
                    self.score_tracker.add_kill()
                    self._spawn_particles(int(enemy.x + enemy.width // 2),
                                          int(enemy.y + enemy.height // 2), COL_YELLOW)

        # Vehicle vs obstacle / enemy
        for obs in self.obstacles:
            if not obs.active:
                continue
            o_rect = obs.get_rect()
            if v_rect.colliderect(o_rect):
                if obs.kind == "hole" and not self.vehicle.on_ground:
                    continue   # jumping over hole → safe
                self.vehicle.alive = False

        for enemy in self.enemies:
            if enemy.active and not enemy.exploding:
                if v_rect.colliderect(enemy.get_rect()):
                    self.vehicle.alive = False

    # ── Particles ─────────────────────────────────────────────────────────────
    def _spawn_particles(self, x, y, color, count=18):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(2, 7)
            self.particles.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(18, 35),
                "color": color,
            })

    def _update_particles(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.3
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]

    def _draw_particles(self):
        for p in self.particles:
            alpha = min(255, p["life"] * 7)
            r, g, b = p["color"]
            color = (min(255, r), min(255, g), min(255, b))
            pygame.draw.circle(self.screen, color, (int(p["x"]), int(p["y"])), 3)

    # ── Background ────────────────────────────────────────────────────────────
    def _draw_background(self):
        draw_gradient_rect(self.screen, COL_SKY_TOP, COL_SKY_BOT,
                           pygame.Rect(0, 0, WIDTH, HEIGHT))

        # Moon
        moon_x = int(WIDTH * 0.82 - (self.scroll_offset * 0.01) % WIDTH)
        pygame.draw.circle(self.screen, COL_MOON, (moon_x, 80), 52)
        pygame.draw.circle(self.screen, (200, 195, 170), (moon_x, 80), 52, 2)
        # Craters on moon
        for cx, cy, r in [(moon_x - 18, 68, 9), (moon_x + 20, 90, 6), (moon_x + 5, 58, 5)]:
            pygame.draw.circle(self.screen, (200, 196, 172), (cx, cy), r)
            pygame.draw.circle(self.screen, (185, 180, 155), (cx, cy), r, 1)

        # Stars
        for star in self.stars:
            star.draw(self.screen)

        # Distant mountains
        mountain_offset = int(self.scroll_offset * 0.08) % WIDTH
        pts = []
        step = 60
        for i in range(-1, WIDTH // step + 2):
            bx = i * step - mountain_offset
            by = random.seed(i * 7 + 42) or 0
            by = 180 + int(math.sin(i * 1.3 + 1) * 45 + math.cos(i * 0.7) * 30)
            pts.extend([(bx, by), (bx + step // 2, by - random.randint(10, 40))])

        mtn_pts = [(0, GROUND_Y)]
        for i in range(WIDTH // 30 + 2):
            sx = i * 30 - (int(self.scroll_offset * 0.12) % (30))
            sy = 230 + int(math.sin(i * 1.1 + self.scroll_offset * 0.001) * 40)
            mtn_pts.append((sx, sy))
        mtn_pts.append((WIDTH, GROUND_Y))
        if len(mtn_pts) >= 3:
            pygame.draw.polygon(self.screen, (25, 20, 40), mtn_pts)
            pygame.draw.lines(self.screen, (45, 40, 60), False, mtn_pts[1:-1], 1)

    def _draw_ground(self):
        # Ground fill
        pygame.draw.rect(self.screen, COL_GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, COL_GROUND_TOP, (0, GROUND_Y, WIDTH, 5))

        # Scrolling ground texture lines
        line_gap = 40
        offset = int(self.scroll_offset) % line_gap
        for x in range(-line_gap + offset, WIDTH + line_gap, line_gap):
            pygame.draw.line(self.screen, (65, 55, 42), (x, GROUND_Y + 10), (x + 20, HEIGHT), 1)

        # Small rocks texture
        for i in range(20):
            rx = (i * 53 + int(self.scroll_offset * 0.7)) % WIDTH
            ry = GROUND_Y + 8 + (i * 17) % 30
            pygame.draw.circle(self.screen, (70, 60, 48), (rx, ry), 2)

    # ── HUD ───────────────────────────────────────────────────────────────────
    def _draw_hud(self):
        st = self.score_tracker
        # Score
        draw_text_shadow(self.screen, self.font_hud, f"SCORE: {st.score:06d}",
                         18, 14, COL_HUD_TEXT)
        # High score
        draw_text_shadow(self.screen, self.font_hud,
                         f"BEST:  {st.high_score:06d}", 18, 40, (140, 220, 255))
        # Kills
        draw_text_shadow(self.screen, self.font_hud,
                         f"KILLS: {st.kills:03d}", 18, 66, COL_YELLOW)
        # Level / Speed
        level = st.get_level()
        draw_text_shadow(self.screen, self.font_hud,
                         f"SPEED LV {level}", WIDTH - 170, 14, COL_RED)
        # Speed bar
        bar_w = int(120 * min(1.0, (st.speed - st.base_speed) / (12 - st.base_speed)))
        pygame.draw.rect(self.screen, (40, 40, 40), (WIDTH - 170, 42, 120, 12), border_radius=4)
        pygame.draw.rect(self.screen, COL_RED, (WIDTH - 170, 42, bar_w, 12), border_radius=4)
        pygame.draw.rect(self.screen, (200, 80, 80), (WIDTH - 170, 42, 120, 12), 1, border_radius=4)

        # Controls reminder (small)
        draw_text_shadow(self.screen, self.font_small,
                         "SPACE=Jump  LMB=Shoot", WIDTH // 2, HEIGHT - 22,
                         (100, 140, 100), center=True)

    # ── Menu ──────────────────────────────────────────────────────────────────
    def _draw_menu(self, tick):
        self._draw_background()
        self._draw_ground()

        # Animated vehicle on menu
        vx = 80 + int(math.sin(tick * 0.03) * 20)
        vy = VEHICLE_START_Y
        temp_v = Vehicle(vx, vy)
        temp_v.wheel_angle = tick * 4
        temp_v.draw(self.screen)

        # Title panel
        panel = pygame.Rect(WIDTH // 2 - 260, 90, 520, 220)
        panel_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        panel_surf.fill((5, 10, 30, 190))
        self.screen.blit(panel_surf, panel.topleft)
        pygame.draw.rect(self.screen, (60, 220, 110), panel, 2, border_radius=8)

        # Title
        draw_text_shadow(self.screen, self.font_big, "MOON PATROL",
                         WIDTH // 2, 130, COL_GREEN, shadow=(0, 60, 20), center=True)
        draw_text_shadow(self.screen, self.font_small, "── LUNAR ASSAULT DIVISION ──",
                         WIDTH // 2, 178, (80, 180, 100), center=True)

        # High score
        if self.high_score > 0:
            draw_text_shadow(self.screen, self.font_med,
                             f"HIGH SCORE: {self.high_score:06d}",
                             WIDTH // 2, 210, COL_YELLOW, center=True)

        # Blinking play button
        if (tick // 25) % 2 == 0:
            btn = pygame.Rect(WIDTH // 2 - 130, 248, 260, 46)
            pygame.draw.rect(self.screen, (20, 120, 55), btn, border_radius=8)
            pygame.draw.rect(self.screen, COL_GREEN, btn, 2, border_radius=8)
            draw_text_shadow(self.screen, self.font_med, "▶  PLAY",
                             WIDTH // 2, 271, COL_WHITE, center=True)

        # Controls
        controls = [
            ("SPACE", "Jump over rocks & holes"),
            ("LEFT CLICK", "Shoot enemy vehicles"),
            ("AUTO", "Vehicle moves forward automatically"),
        ]
        y0 = 355
        for key, desc in controls:
            draw_text_shadow(self.screen, self.font_small,
                             f"{key:<12} {desc}", WIDTH // 2, y0,
                             (140, 200, 140), center=True)
            y0 += 24

        pygame.display.flip()

    # ── Game Over ─────────────────────────────────────────────────────────────
    def _draw_gameover(self, tick):
        self._draw_background()
        self._draw_ground()

        panel = pygame.Rect(WIDTH // 2 - 240, 110, 480, 240)
        panel_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        panel_surf.fill((30, 5, 5, 210))
        self.screen.blit(panel_surf, panel.topleft)
        pygame.draw.rect(self.screen, COL_RED, panel, 2, border_radius=8)

        draw_text_shadow(self.screen, self.font_big, "GAME OVER",
                         WIDTH // 2, 148, COL_RED, center=True)

        st = self.score_tracker
        draw_text_shadow(self.screen, self.font_med,
                         f"SCORE:  {st.score:06d}", WIDTH // 2, 210, COL_WHITE, center=True)
        draw_text_shadow(self.screen, self.font_med,
                         f"KILLS:  {st.kills:03d}", WIDTH // 2, 242, COL_YELLOW, center=True)
        if st.score >= self.high_score:
            draw_text_shadow(self.screen, self.font_med,
                             "★  NEW HIGH SCORE!  ★", WIDTH // 2, 274, COL_YELLOW, center=True)

        if (tick // 22) % 2 == 0:
            btn = pygame.Rect(WIDTH // 2 - 150, 305, 300, 40)
            pygame.draw.rect(self.screen, (100, 20, 20), btn, border_radius=7)
            pygame.draw.rect(self.screen, COL_RED, btn, 2, border_radius=7)
            draw_text_shadow(self.screen, self.font_med,
                             "PRESS SPACE TO RETRY", WIDTH // 2, 325, COL_WHITE, center=True)

        pygame.display.flip()

    # ── Main game update / draw ───────────────────────────────────────────────
    def _update_game(self):
        st = self.score_tracker
        speed = st.speed

        # Scroll
        self.scroll_offset += speed
        st.add_distance(speed)
        st.update_speed()
        self.high_score = st.update_high_score()

        # Stars parallax
        for star in self.stars:
            star.update(speed, WIDTH)

        self.vehicle.update()
        self._try_spawn()

        for b in self.bullets:
            b.update(speed)
        self.bullets = [b for b in self.bullets if b.active and b.x < WIDTH + 50]

        for e in self.enemies:
            e.update(speed)
        self.enemies = [e for e in self.enemies if e.active and e.x > -120]

        for o in self.obstacles:
            o.update(speed)
        self.obstacles = [o for o in self.obstacles if o.active and o.x > -120]

        self._check_collisions()
        self._update_particles()

        if not self.vehicle.alive:
            self.state = "gameover"

    def _draw_game(self):
        self._draw_background()
        self._draw_ground()

        for obs in self.obstacles:
            obs.draw(self.screen, GROUND_Y)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.vehicle.draw(self.screen)

        for b in self.bullets:
            b.draw(self.screen)

        self._draw_particles()
        self._draw_hud()
        pygame.display.flip()

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        tick = 0
        while True:
            tick += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "menu":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self._reset_game()
                        self.state = "playing"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._reset_game()
                        self.state = "playing"

                elif self.state == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.vehicle.jump()
                        if event.key == pygame.K_ESCAPE:
                            self.state = "menu"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        bullet = self.vehicle.shoot()
                        if bullet:
                            self.bullets.append(bullet)

                elif self.state == "gameover":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self._reset_game()
                        self.state = "playing"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._reset_game()
                        self.state = "playing"

            if self.state == "menu":
                self._draw_menu(tick)

            elif self.state == "playing":
                self._update_game()
                self._draw_game()

            elif self.state == "gameover":
                self._draw_gameover(tick)

            self.clock.tick(FPS)


if __name__ == "__main__":
    game = MoonPatrol()
    game.run()