import pygame
from math import cos
from pygame.math import Vector2
import random

pygame.init()
screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)
clock = pygame.time.Clock()

land = pygame.sprite.Sprite()
land.image = pygame.surface.Surface((500, 200))
land.image.fill((200, 200, 200))
land.rect = land.image.get_rect(midtop=(500, 300))


class ParticleManager:
    def __init__(self, screen):
        self.screen: pygame.surface.Surface = screen
        self.generators = []
        self.count = 0

    def update(self):
        for g in self.generators:
            g.update()

    def draw(self):
        for g in self.generators:
            g.draw()


class continuous:
    def __init__(self, manager, source, radius, max=100):
        self.source = source
        self.radius = radius
        self.count = 0
        self.cache = {}
        self.manager: ParticleManager = manager
        self.manager.generators.append(self)
        self.particles = []
        self.max = max
        self.disabled = False
        self.lifetime = 100
        self.size = 5
        self.halo = pygame.surface.Surface(
            (self.size * 4, self.size * 4), pygame.SRCALPHA
        )
        pygame.draw.circle(
            self.halo, (50, 50, 50), self.halo.get_rect().center, self.size * 2
        )
        # self.emit(self.max)

    # override
    def init_particle(self):
        return [
            Vector2(
                self.source.x + random.randint(-self.radius, self.radius),
                self.source.y + random.randint(-self.radius, self.radius),
            ),
            Vector2(random.uniform(-20, 20), random.uniform(-4, 4)),
            self.lifetime,
        ]

    def go_to(self, source):
        self.source.update(source)

    def emit(self, n=1):
        if n > 1:
            self.emit(n - 1)
        if self.count > self.max:
            self.particles.pop(0)
            self.count -= 1
        self.count += 1
        particle = self.init_particle()
        self.particles.append(particle)

    def start(self):
        self.disabled = False

    def stop(self):
        self.disabled = True

    # override
    def update(self):
        # print(self.count)
        for i, particle in enumerate(self.particles):

            particle[0].x += particle[1].x
            if land.rect.collidepoint(particle[0]):
                if particle[1].x > 0:
                    particle[0].x = land.rect.left
                elif particle[1].x < 0:
                    particle[0].x = land.rect.right
                particle[1].x *= -1

            particle[0].y += particle[1].y
            if land.rect.collidepoint(particle[0]):
                if particle[1].y > 0:
                    particle[0].y = land.rect.top
                elif particle[1].y < 0:
                    particle[0].y = land.rect.bottom
                particle[1].y *= -1

            particle[2] -= 1
            if particle[2] == 0:
                self.particles.pop(i)
                self.count -= 1
            particle[1].x *= 0.95
            particle[1].y *= 0.95
        if not self.disabled:
            # if  not self.disabled:

            self.emit()

    # override
    def draw(self):
        for particle in self.particles:
            if self.manager.screen.get_rect().collidepoint(particle[0]):
                width = int(self.size * (particle[2] / self.lifetime))
                pygame.draw.circle(
                    self.manager.screen,
                    (200, 200, 100),
                    particle[0],
                    width,
                )
                # self.halo.set_alpha(10)
                self.manager.screen.blit(
                    self.halo,
                    (particle[0].x - self.size * 2, particle[0].y - self.size * 2),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )


pm = ParticleManager(screen)
gen = continuous(pm, Vector2(500, 200), 200, 200)
loop = True
while loop:
    screen.fill((20, 7, 15))
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            loop = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                print(clock.get_fps())
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                # print("Here")
                gen.disabled = not gen.disabled
            if event.button == 1:
                gen.go_to(pygame.mouse.get_pos())

    screen.blit(land.image, land.rect)
    pm.update()
    pm.draw()
    clock.tick(60)
    #
    # print(pm.count)
    pygame.display.flip()

pygame.quit()
