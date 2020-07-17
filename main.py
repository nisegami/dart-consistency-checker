import time
import os, os.path
import multiprocessing

from plotly import graph_objects

from orcust import OrcustManager


def generate_sankey(filename, end_games):
    gs = [[0, 0, 0], [0, 0, 0]]
    combo = [[0, 0, 0], [0, 0, 0]]

    for game in end_games:
        if game.has_flag("going second card"):
            outer_index_gs = 0
        else:
            outer_index_gs = 1

        if game.has_flag("recycler"):
            inner_index_gs = 0
            outer_index_combo = 0
        elif game.has_flag("girsu"):
            inner_index_gs = 1
            outer_index_combo = 1
        else:
            inner_index_gs = 2
            gs[outer_index_gs][inner_index_gs] += 1
            continue

        if game.has_flag("full combo"):
            inner_index_combo = 0
        elif game.has_flag("basic combo"):
            inner_index_combo = 1
        else:
            inner_index_combo = 2

        gs[outer_index_gs][inner_index_gs] += 1
        combo[outer_index_combo][inner_index_combo] += 1

    fig = graph_objects.Figure(
        data=[
            graph_objects.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=[
                        "Going Second Card Drawn",  # 0
                        "No Going Second Card Drawn",  # 1
                        "Scrap Used",  # 2
                        "Girsu Used",  # 3
                        "Full Combo",  # 4
                        "Basic Combo",  # 5
                        "Brick",  # 6
                    ],
                    color=["green", "blue", "brown", "black", "green", "blue", "red"],
                ),
                link=dict(
                    source=[0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],
                    target=[2, 3, 6, 2, 3, 6, 4, 5, 6, 4, 5, 6],
                    value=gs[0] + gs[1] + combo[0] + combo[1],
                ),
            )
        ]
    )

    fig.write_html(os.path.join("output", f"{filename}.html"))


def run_one(manager):
    return manager.run()


def run_in_parallel(n):
    manager = OrcustManager()
    managers = [manager for _ in range(n)]
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        return pool.map(run_one, managers)


if __name__ == "__main__":
    start = time.time()
    end_games = run_in_parallel(5000)
    generate_sankey("orcust", end_games)
    duration = time.time() - start
    print(duration)
