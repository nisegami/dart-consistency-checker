import time
import os, os.path
import multiprocessing

from plotly import graph_objects

from orcust import OrcustManager
from invoked_dogma import InvokedDogmaManager


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


def run_one(manager):
    return manager.run()


def run_in_parallel(count, manager_class):
    manager = manager_class()
    managers = [manager for _ in range(count)]
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        return pool.map(run_one, managers)


if __name__ == "__main__":
    start = time.time()
    n = 20
    end_games = run_in_parallel(n, InvokedDogmaManager)
    # generate_sankey("pinpoint", *InvokedDogmaManager.generate_sankey_data(end_games))
    print(InvokedDogmaManager.generate_report(end_games))
    duration = time.time() - start
    print(duration)
