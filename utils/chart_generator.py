import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os


def generate_skill_chart(skills, filename):

    if not skills:
        return None

    chart_folder = os.path.join(
        "static",
        "charts"
    )

    os.makedirs(
        chart_folder,
        exist_ok=True
    )

    values = [1] * len(skills)

    plt.figure(figsize=(5, 5))

    plt.pie(
        values,
        labels=skills,
        autopct='%1.1f%%'
    )

    plt.title("Detected Skills")

    chart_path = os.path.join(
        chart_folder,
        f"{filename}.png"
    )

    plt.savefig(chart_path)

    plt.close()

    return f"charts/{filename}.png"