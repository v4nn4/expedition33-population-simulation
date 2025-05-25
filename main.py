from pathlib import Path
import fire

from src.simulate import simulate_population
from src.plot import plot


class Paths:
    DATA = Path("data")
    GENERATED = DATA / Path("generated")


class Cli:
    def simulate(self):
        simulate_population(Paths.GENERATED)

    def plot(self):
        plot(Paths.GENERATED)


if __name__ == "__main__":
    fire.Fire(Cli)
