class ParticleGeneratorBase:
    def __init__(self, particle_manager):
        self.particle_manager = particle_manager
        self.counter = 0
        self.max = 100
        self.particle_list = []

    def go_to(self):
        pass

    def remove_particle(self):
        pass

    def add_particle(self):
        pass

    def draw(self):
        pass

    def update(self, dt):
        pass
