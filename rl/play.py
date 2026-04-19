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
    from game.pygame_app import CELL_PX, FPS, HUD_PX, draw_state

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="ppo_pacman")
    parser.add_argument("--tick-ms", type=int, default=120)
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    model = PPO.load(args.model, device="cpu")

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

            hud = f"Score: {state['score']}  Return: {ep_reward:+.2f}  Status: {state['status']}  (R=reset, Esc=quit)"
            draw_state(
                screen,
                state,
                font=font,
                big_font=big_font,
                hud_text=hud,
                win_msg="AGENT WINS -- press R",
                lose_msg="AGENT LOST -- press R",
            )
            pygame.display.flip()
            dirty = False
            clock.tick(FPS)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
