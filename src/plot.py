from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from PIL import Image
import numpy as np


def plot(output_path: Path):
    plt.rcParams["font.family"] = "DejaVu Sans"

    # Load data
    df = pd.read_csv(output_path / "population.csv").set_index("year")
    x_start, x_end = df.index.min(), df.index.max()

    # Color palette
    palette = [
        "#817",
        "#a35",
        "#c66",
        "#e94",
        "#ed0",
        "#9d5",
        "#4d8",
        "#2cb",
        "#0bc",
        "#09c",
        "#36b",
        "#639",
    ]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 9))

    # Plot stacked area chart
    ax.stackplot(
        df.index,
        df.T,
        labels=df.columns[::-1],
        colors=palette[: len(df.columns)][::-1],
        zorder=1,
    )

    # Determine plot limits
    ymax = ax.get_ylim()[1]
    ax.set_xlim(x_start, x_end)
    ax.set_ylim(0, ymax)

    # Overlay grayscale background image
    img = Image.open("assets/lumiere.png").convert("L")
    gray_img = np.array(img)
    ax.imshow(
        gray_img,
        cmap="gray",
        extent=[x_start, x_end, 0, ymax],
        aspect="auto",
        alpha=0.25,
        zorder=0,
    )

    # Axis labels and title
    ax.set_title(
        "What if the Fracture Happened in 1900?\nParis Population Simulation (1900–1967)",
        fontsize=20,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Year", fontsize=18)
    ax.set_ylabel("Population (millions)", fontsize=18)
    ax.tick_params(axis="both", labelsize=16)
    ax.set_xticks([*df.index[::10], x_end])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x / 1e6:.1f}M"))

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels[::-1],
        title="Age Group",
        loc="upper right",
        fontsize=16,
        title_fontsize=18,
    )

    # Save and show
    fig.savefig(output_path / "plot.png", dpi=100, bbox_inches="tight")
    plt.show()
