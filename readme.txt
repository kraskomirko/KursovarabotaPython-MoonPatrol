═══════════════════════════════════════════════════════
           MOON PATROL — Python Pygame Edition
═══════════════════════════════════════════════════════

DESCRIPTION
-----------
A Python recreation of the classic Moon Patrol arcade game.
You pilot a lunar vehicle that moves automatically to the right.
Survive as long as possible by shooting enemies and dodging obstacles.

PROJECT STRUCTURE
-----------------
  main.py          — Game loop, menu, rendering, input handling
  models.py        — Game entity classes (Vehicle, Bullet, EnemyCar,
                     Obstacle, Star, ScoreTracker)
  requirements.txt — Python library dependencies
  readme.txt       — This file

LIBRARIES USED
--------------
  pygame >= 2.1.0
    • Game window, rendering, input, timing
    • Install with: pip install pygame

INSTALLATION
------------
  1. Make sure Python 3.8+ is installed.
  2. Install dependencies:
       pip install -r requirements.txt
  3. Run the game:
       python main.py

HOW TO PLAY
-----------
  • Your vehicle moves forward automatically — you cannot control speed direction.
  • SPACE          : Jump (clear rocks and craters)
  • LEFT CLICK     : Fire your cannon to destroy enemy vehicles
  • ESC            : Return to menu

  ► Avoid ROCKS  — jump over them with SPACE
  ► Avoid HOLES  — jump over them with SPACE (being airborne is safe)
  ► Shoot ENEMY CARS with left click before they reach you
  ► Every kill = +100 points
  ► Distance travelled adds to your score automatically

SCORING & SPEED
---------------
  • Score increases continuously as you travel.
  • +100 points per enemy car destroyed.
  • Every 500 points, your speed increases by one level (up to max).
  • High score is saved per session.

CLASSES IN models.py
--------------------
  Vehicle       — Player rover with jump, shoot, physics, and wheel animation
  Bullet        — Projectile with scroll-aware movement
  EnemyCar      — Enemy rover with explosion animation
  Obstacle      — Rock or crater with polygon/ellipse drawing
  Star          — Parallax background star
  ScoreTracker  — Score, kills, distance, speed progression logic

NOTES
-----
  • No external assets (images/sounds) required — fully drawn with pygame primitives.
  • The game window is 900×500 pixels.
  • Randomised obstacle and enemy spawning scales with score.

═══════════════════════════════════════════════════════