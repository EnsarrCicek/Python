import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame

try:
    import imageio.v2 as imageio
except Exception:
    imageio = None


WIDTH, HEIGHT = 900, 700
FPS = 60
BG = (8, 7, 18)
PINK = (255, 95, 162)
SOFT_PINK = (255, 182, 212)
WHITE = (250, 245, 255)
GLOW = (255, 120, 190)

NAME = "Sevgilim"
SUBTITLE = "İyi ki varsın ❤️"
EXPORT_GIF = False          # True yaparsan GIF üretir
GIF_SECONDS = 5
GIF_FPS = 24
OUTPUT_GIF = "heart_gift.gif"


@dataclass
class Particle:
    x: float
    y: float
    target_x: float
    target_y: float
    size: int
    speed: float
    phase: float

    def update(self, t: float) -> None:
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Hafif nefes alma / titreşim efekti
        self.x += math.sin(t * 2.3 + self.phase) * 0.25
        self.y += math.cos(t * 2.1 + self.phase) * 0.25

    def draw(self, surface: pygame.Surface, t: float) -> None:
        pulse = 0.85 + 0.25 * math.sin(t * 3.0 + self.phase)
        r = max(1, int(self.size * pulse))
        pygame.draw.circle(surface, PINK, (int(self.x), int(self.y)), r)


class HeartField:
    def __init__(self, center_x: int, center_y: int, scale: float = 15.0, count: int = 380):
        self.center_x = center_x
        self.center_y = center_y
        self.scale = scale
        self.count = count
        self.particles = self._create_particles()

    def heart_point(self, t: float) -> tuple[float, float]:
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        return x, y

    def _create_particles(self) -> list[Particle]:
        particles = []
        for _ in range(self.count):
            a = random.uniform(0, 2 * math.pi)
            hx, hy = self.heart_point(a)
            spread = random.uniform(0.82, 1.08)
            tx = self.center_x + hx * self.scale * spread
            ty = self.center_y - hy * self.scale * spread
            particles.append(
                Particle(
                    x=random.uniform(0, WIDTH),
                    y=random.uniform(0, HEIGHT),
                    target_x=tx,
                    target_y=ty,
                    size=random.randint(2, 4),
                    speed=random.uniform(0.035, 0.07),
                    phase=random.uniform(0, math.pi * 2),
                )
            )
        return particles

    def update(self, t: float) -> None:
        breath = 1.0 + 0.03 * math.sin(t * 2.0)
        for i, p in enumerate(self.particles):
            a = (i / self.count) * 2 * math.pi
            hx, hy = self.heart_point(a)
            p.target_x = self.center_x + hx * self.scale * breath
            p.target_y = self.center_y - hy * self.scale * breath
            p.update(t)

    def draw(self, surface: pygame.Surface, t: float) -> None:
        for p in self.particles:
            p.draw(surface, t)


class FloatingSpark:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.speed = random.uniform(0.2, 0.8)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(50, 140)

    def update(self) -> None:
        self.y -= self.speed
        if self.y < -10:
            self.x = random.uniform(0, WIDTH)
            self.y = HEIGHT + 10

    def draw(self, surface: pygame.Surface) -> None:
        sparkle = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(sparkle, (255, 255, 255, self.alpha), (5, 5), self.size)
        surface.blit(sparkle, (self.x, self.y))


class RomanticGiftApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Kalp Animasyonu")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arial", 54, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 28)
        self.hint_font = pygame.font.SysFont("arial", 20)
        self.heart = HeartField(WIDTH // 2, HEIGHT // 2 + 20)
        self.sparks = [FloatingSpark() for _ in range(90)]
        self.running = True

    def draw_background(self) -> None:
        self.screen.fill(BG)
        for s in self.sparks:
            s.draw(self.screen)

    def draw_text(self, t: float) -> None:
        # Glow yazı
        glow_scale = 1.0 + 0.02 * math.sin(t * 2.0)
        title = self.title_font.render(NAME, True, WHITE)
        subtitle = self.subtitle_font.render(SUBTITLE, True, SOFT_PINK)
        hint = self.hint_font.render("ESC ile çık | G ile ekran görüntüsü al", True, (200, 190, 220))

        glow = pygame.transform.smoothscale(
            title,
            (int(title.get_width() * glow_scale), int(title.get_height() * glow_scale)),
        )
        glow_surface = pygame.Surface((glow.get_width() + 30, glow.get_height() + 30), pygame.SRCALPHA)
        glow_rect = glow.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
        glow_surface.blit(glow, glow_rect)
        tint = pygame.Surface(glow_surface.get_size(), pygame.SRCALPHA)
        tint.fill((*GLOW, 70))
        glow_surface.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        title_rect = title.get_rect(center=(WIDTH // 2, 120))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT - 90))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        glow_pos = glow_surface.get_rect(center=title_rect.center)

        self.screen.blit(glow_surface, glow_pos)
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(hint, hint_rect)

    def update(self, t: float) -> None:
        self.heart.update(t)
        for s in self.sparks:
            s.update()

    def draw(self, t: float) -> None:
        self.draw_background()
        self.heart.draw(self.screen, t)
        self.draw_text(t)
        pygame.display.flip()

    def save_screenshot(self) -> None:
        out = Path("heart_screenshot.png")
        pygame.image.save(self.screen, str(out))
        print(f"Ekran görüntüsü kaydedildi: {out.resolve()}")

    def export_gif(self) -> None:
        if imageio is None:
            print("GIF için imageio kur: pip install imageio")
            return

        frames = []
        total_frames = GIF_SECONDS * GIF_FPS
        print("GIF oluşturuluyor...")
        for i in range(total_frames):
            t = i / GIF_FPS
            self.update(t)
            self.draw_background()
            self.heart.draw(self.screen, t)
            self.draw_text(t)

            rgb_array = pygame.surfarray.array3d(self.screen)
            frame = rgb_array.swapaxes(0, 1)
            frames.append(frame)

        imageio.mimsave(OUTPUT_GIF, frames, fps=GIF_FPS)
        print(f"GIF kaydedildi: {Path(OUTPUT_GIF).resolve()}")

    def run(self) -> None:
        if EXPORT_GIF:
            self.export_gif()
            pygame.quit()
            return

        while self.running:
            t = pygame.time.get_ticks() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_g:
                        self.save_screenshot()

            self.update(t)
            self.draw(t)
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    RomanticGiftApp().run()
