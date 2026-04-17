"""Watch a trained PPO agent play Pacman in the pygame window.

Usage:
    python -m rl.play --model ppo_pacman [--tick-ms 120] [--deterministic] [--seed 0]

Press R to reset with a new map, Esc to quit.
"""
import argparse


def main():
    import pygame
    from stable_baselines3 import PPO

    from game.core import PacmanGame
    from game.types import Action
    from game.pygame_app import (
        BG, WALL, DOT, PLAYER, GHOST, WIN_TEXT, LOSE_TEXT,
        CELL_PX, FPS, HUD_PX,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="ppo_pacman")
    parser.add_argument("--tick-ms", type=int, default=120)
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    model = PPO.load(args.model)

    pygame.init()
    try:
        game = PacmanGame(seed=args.seed)
        state = game.get_state()
        width, height = state["width"], state["height"]
        window_w = width * CELL_PX
        window_h = height * CELL_PX + HUD_PX
        screen = pygame.display.set_mode((window_w, window_h))
        pygame.display.set_caption(f"Pacman — {args.model}")

        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 24)
        big_font = pygame.font.SysFont(None, 48)
        last_tick = pygame.time.get_ticks()
        ep_reward = 0.0
        dirty = True

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        game.reset()
                        state = game.get_state()
                        ep_reward = 0.0
                        last_tick = pygame.time.get_ticks()
                        dirty = True

            if not running:
                break

            now = pygame.time.get_ticks()
            if state["status"] == "playing" and now - last_tick >= args.tick_ms:
                obs = game.to_tensor()
                action_idx, _ = model.predict(obs, deterministic=args.deterministic)
                _, reward, _ = game.step(Action(int(action_idx)))
                ep_reward += reward
                state = game.get_state()
                last_tick = now
                dirty = True

            if not dirty:
                clock.tick(FPS)
                continue

            screen.fill(BG)
            for (wx, wy) in state["walls"]:
                pygame.draw.rect(screen, WALL, pygame.Rect(wx * CELL_PX, wy * CELL_PX, CELL_PX, CELL_PX))
            for (dx, dy) in state["dots"]:
                pygame.draw.circle(screen, DOT, (dx * CELL_PX + CELL_PX // 2, dy * CELL_PX + CELL_PX // 2), 3)
            px, py = state["player"]
            pygame.draw.circle(screen, PLAYER, (px * CELL_PX + CELL_PX // 2, py * CELL_PX + CELL_PX // 2), CELL_PX // 2 - 2)
            for (gx, gy) in state["ghosts"]:
                pygame.draw.circle(screen, GHOST, (gx * CELL_PX + CELL_PX // 2, gy * CELL_PX + CELL_PX // 2), CELL_PX // 2 - 3)

            hud_y = height * CELL_PX
            pygame.draw.rect(screen, BG, pygame.Rect(0, hud_y, window_w, HUD_PX))
            hud = f"Score: {state['score']}  Return: {ep_reward:+.2f}  Status: {state['status']}  (R=reset, Esc=quit)"
            surf = font.render(hud, True, (0, 0, 0))
            screen.blit(surf, (8, hud_y + (HUD_PX - surf.get_height()) // 2))

            if state["status"] in ("won", "lost"):
                overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))
                msg = "AGENT WINS -- press R" if state["status"] == "won" else "AGENT LOST -- press R"
                color = WIN_TEXT if state["status"] == "won" else LOSE_TEXT
                text = big_font.render(msg, True, color)
                screen.blit(text, text.get_rect(center=(window_w // 2, window_h // 2)))

            pygame.display.flip()
            dirty = False
            clock.tick(FPS)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
