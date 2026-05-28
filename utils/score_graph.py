import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os


def generate_score_graph(scores, user_id):

    if not scores:
        return None

    chart_folder = os.path.join(
        "static",
        "charts"
    )

    os.makedirs(
        chart_folder,
        exist_ok=True
    )

    chart_path = os.path.join(
        chart_folder,
        f"score_trend_{user_id}.png"
    )

    x_values = list(
        range(1, len(scores) + 1)
    )

    plt.figure(figsize=(6, 4))

    plt.plot(
        x_values,
        scores,
        marker='o'
    )

    plt.title("Resume Score Trend")

    plt.xlabel("Resume Number")

    plt.ylabel("Score")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    return f"charts/score_trend_{user_id}.png"