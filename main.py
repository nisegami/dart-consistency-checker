from typing import List
from framework import Game
import time
import os, os.path
import multiprocessing

from plotly import graph_objects

from orcust import OrcustManager
from invoked_dogma import InvokedDogmaManager
from synchro_dogma import SynchroDogmaManager


def generate_sankey(filename, label, color, source, target, value):
    fig = graph_objects.Figure(
        data=[
            graph_objects.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=label,
                    color=color,
                ),
                link=dict(source=source, target=target, value=value,),
            )
        ]
    )

    fig.write_html(os.path.join("output", f"{filename}.html"))


def run_one(manager) -> Game:
    return manager.run()


def run_in_parallel(count, manager_class) -> List[Game]:
    manager = manager_class()
    managers = [manager for _ in range(count)]
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        return pool.map(run_one, managers)


if __name__ == "__main__":
    start = time.time()
    n = 10000
    end_games = run_in_parallel(n, SynchroDogmaManager)
    print(SynchroDogmaManager.generate_report(end_games))
    # for game in end_games:
    #     print(game.disruption_report())
    duration = time.time() - start
    print(duration)
