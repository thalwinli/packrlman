"""Pygame presentation shell for the Pacman game.

This is the ONLY module permitted to import pygame. Pygame imports
happen lazily inside `run()` so that importing this module
(e.g. via `main.py`) does not require pygame to be installed until
the game is actually launched.
"""

# Rendering / timing constants
CELL_PX = 28
TICK_MS = 150
FPS = 60
HUD_PX = 32

# Color constants (RGB)
BG = (0, 0, 0)
WALL = (30, 30, 200)
DOT = (255, 255, 255)
PLAYER = (255, 230, 0)
GHOST = (220, 50, 50)
WIN_TEXT = (50, 220, 50)
LOSE_TEXT = (220, 50, 50)


def run() -> None:
    """Launch the pygame-driven Pacman application.

    Pygame is imported lazily so that `import game.pygame_app` does
    not require pygame to be installed.
    """
    import pygame

    from game.core import PacmanGame
    from game.types import Action

    pygame.init()
    try:
        game = PacmanGame()
        state = game.get_state()
        width = state["width"]
        height = state["height"]

        window_w = width * CELL_PX
        window_h = height * CELL_PX + HUD_PX
        screen = pygame.display.set_mode((window_w, window_h))
        pygame.display.set_caption("Pacman")

        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 24)
        big_font = pygame.font.SysFont(None, 48)

        pending_action = None
        last_tick = pygame.time.get_ticks()

        key_to_action = {
            pygame.K_UP: Action.UP,
            pygame.K_DOWN: Action.DOWN,
            pygame.K_LEFT: Action.LEFT,
            pygame.K_RIGHT: Action.RIGHT,
        }

        running = True
        while running:
            # --- Event polling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in key_to_action:
                        pending_action = key_to_action[event.key]
                    elif event.key == pygame.K_r:
                        if state["status"] != "playing":
                            game.reset()
                            state = game.get_state()
                            pending_action = None
                            last_tick = pygame.time.get_ticks()

            if not running:
                break

            # --- Tick timer ---
            now = pygame.time.get_ticks()
            if state["status"] == "playing" and now - last_tick >= TICK_MS:
                action = pending_action if pending_action is not None else Action.NOOP
                game.step(action)
                state = game.get_state()
                pending_action = None
                last_tick = now

            # --- Render ---
            screen.fill(BG)

            # Walls
            for (wx, wy) in state["walls"]:
                pygame.draw.rect(
                    screen,
                    WALL,
                    pygame.Rect(wx * CELL_PX, wy * CELL_PX, CELL_PX, CELL_PX),
                )

            # Dots
            for (dx, dy) in state["dots"]:
                cx = dx * CELL_PX + CELL_PX // 2
                cy = dy * CELL_PX + CELL_PX // 2
                pygame.draw.circle(screen, DOT, (cx, cy), 3)

            # Player
            px, py = state["player"]
            pcx = px * CELL_PX + CELL_PX // 2
            pcy = py * CELL_PX + CELL_PX // 2
            pygame.draw.circle(screen, PLAYER, (pcx, pcy), CELL_PX // 2 - 2)

            # Ghosts
            for (gx, gy) in state["ghosts"]:
                gcx = gx * CELL_PX + CELL_PX // 2
                gcy = gy * CELL_PX + CELL_PX // 2
                pygame.draw.circle(screen, GHOST, (gcx, gcy), CELL_PX // 2 - 3)

            # HUD bar
            hud_y = height * CELL_PX
            pygame.draw.rect(
                screen, BG, pygame.Rect(0, hud_y, window_w, HUD_PX)
            )
            hud_text = f"Score: {state['score']}   Status: {state['status']}"
            hud_surface = font.render(hud_text, True, (255, 255, 255))
            screen.blit(hud_surface, (8, hud_y + (HUD_PX - hud_surface.get_height()) // 2))

            # --- Overlays ---
            if state["status"] in ("won", "lost"):
                overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))

                if state["status"] == "won":
                    msg = "YOU WIN -- press R"
                    color = WIN_TEXT
                else:
                    msg = "GAME OVER -- press R"
                    color = LOSE_TEXT
                text_surface = big_font.render(msg, True, color)
                rect = text_surface.get_rect(
                    center=(window_w // 2, window_h // 2)
                )
                screen.blit(text_surface, rect)

            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
