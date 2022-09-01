import os

for module in os.listdir(os.path.dirname(__file__)):
    if (
        module == "__init__.py"
        or module[-3:] != ".py"
        or module == "particle_generator_base.py"
    ):
        continue
    __import__(module[:-3], locals(), globals())
del module
