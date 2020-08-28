from typing import Dict, List, Optional, Type
import time
import os, os.path
import multiprocessing
from functools import wraps
from time import time

from plotly import graph_objects
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style

from framework import DeckList, Game, Manager
from orcust import OrcustManager
from invoked_dogma import InvokedDogmaManager
from synchro_dogma import SynchroDogmaManager


def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            print(f"Total execution time: {end_ if end_ > 0 else 0} ms")

    return _time_it


def generate_sankey(
    filename: str,
    label: List[str],
    color: List[str],
    source: List[int],
    target: List[int],
    value: List[int],
):
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


def generate_table(name: str, data: List[List[str]]) -> str:
    writer = MarkdownTableWriter(
        table_name=name,
        headers=["Label", "Frequency"],
        column_styles=[Style(align="center"), Style(align="right")],
        value_matrix=data,
        margin=1,
    )
    return writer.dumps()


def generate_overall_table(name: str, headers: List[str], data: List[List[str]]) -> str:
    writer = MarkdownTableWriter()
    writer.table_name = name
    writer.headers = headers
    writer.column_styles = [Style(align="center")] + [
        Style(align="right") for _ in headers[1:]
    ]
    writer.value_matrix = data
    writer.margin = 1
    return writer.dumps()


def run_one(manager: Manager) -> Game:
    return manager.run()


def run_in_parallel(
    count: int, manager_class: Type[Manager], decklist: Optional[DeckList] = None
) -> List[Game]:
    manager = manager_class(decklist)
    managers = [manager for _ in range(count)]
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        return pool.map(run_one, managers)


def run_many(
    n: int, manager_class: Type[Manager], decklist: Optional[DeckList] = None
) -> Dict[str, float]:
    return run_in_parallel(n, manager_class, decklist)


def compare_decklists(
    filename: str,
    title: str,
    manager_class: Type[Manager],
    decklists: Dict[str, DeckList],
    n=5000,
) -> None:
    overall_data = []
    headers = []
    with open(os.path.join("output", f"{filename}.md"), "w") as outfile:
        for (decklist_title, decklist) in decklists.items():
            end_games = run_many(n, manager_class, decklist)
            decklist_data = manager_class.generate_stats(end_games)
            overall_data.append(
                [decklist_title] + [datapoint[1] for datapoint in decklist_data]
            )
            headers = ["Decklist"] + [datapoint[0] for datapoint in decklist_data]
        if not overall_data:
            return
        table = generate_overall_table(title, headers, overall_data)
        print(table, file=outfile)


def test_synchro_dogma():
    decklists = {}
    decklists["2 Desires, 1 O-Lion, 1 Upstart, 3 Tuning"] = (
        (SynchroDogmaManager.tuning, 3),
        (SynchroDogmaManager.jet, 3),
        (SynchroDogmaManager.o_lion, 1),
        (SynchroDogmaManager.deskbot, 1),
        (SynchroDogmaManager.righty, 3),
        (SynchroDogmaManager.lefty, 1),
        (SynchroDogmaManager.ecclesia, 3),
        (SynchroDogmaManager.maximus, 2),
        (SynchroDogmaManager.fleur, 2),
        (SynchroDogmaManager.punishment, 1),
        (SynchroDogmaManager.servant, 3),
        (SynchroDogmaManager.schism, 1),
        (SynchroDogmaManager.desires, 2),
        (SynchroDogmaManager.upstart, 1),
        (SynchroDogmaManager.imperm, 3),
        (SynchroDogmaManager.ash, 3),
        (SynchroDogmaManager.called, 3),
        (SynchroDogmaManager.droplet, 1),
        (SynchroDogmaManager.ogre, 3),
    )
    decklists["2 Desires, 2 O-Lion, 0 Upstart, 3 Tuning"] = (
        (SynchroDogmaManager.tuning, 3),
        (SynchroDogmaManager.jet, 3),
        (SynchroDogmaManager.o_lion, 2),
        (SynchroDogmaManager.deskbot, 1),
        (SynchroDogmaManager.righty, 3),
        (SynchroDogmaManager.lefty, 1),
        (SynchroDogmaManager.ecclesia, 3),
        (SynchroDogmaManager.maximus, 2),
        (SynchroDogmaManager.fleur, 2),
        (SynchroDogmaManager.punishment, 1),
        (SynchroDogmaManager.servant, 3),
        (SynchroDogmaManager.schism, 1),
        (SynchroDogmaManager.desires, 2),
        (SynchroDogmaManager.imperm, 3),
        (SynchroDogmaManager.ash, 3),
        (SynchroDogmaManager.called, 3),
        (SynchroDogmaManager.droplet, 1),
        (SynchroDogmaManager.ogre, 3),
    )
    decklists["3 Desires, 1 O-Lion, 0 Upstart, 3 Tuning"] = (
        (SynchroDogmaManager.tuning, 3),
        (SynchroDogmaManager.jet, 3),
        (SynchroDogmaManager.o_lion, 1),
        (SynchroDogmaManager.deskbot, 1),
        (SynchroDogmaManager.righty, 3),
        (SynchroDogmaManager.lefty, 1),
        (SynchroDogmaManager.ecclesia, 3),
        (SynchroDogmaManager.maximus, 2),
        (SynchroDogmaManager.fleur, 2),
        (SynchroDogmaManager.punishment, 1),
        (SynchroDogmaManager.servant, 3),
        (SynchroDogmaManager.schism, 1),
        (SynchroDogmaManager.desires, 3),
        (SynchroDogmaManager.imperm, 3),
        (SynchroDogmaManager.ash, 3),
        (SynchroDogmaManager.called, 3),
        (SynchroDogmaManager.droplet, 1),
        (SynchroDogmaManager.ogre, 3),
    )
    decklists["3 Desires, 2 O-Lion, 0 Upstart, 2 Tuning"] = (
        (SynchroDogmaManager.tuning, 2),
        (SynchroDogmaManager.jet, 3),
        (SynchroDogmaManager.o_lion, 2),
        (SynchroDogmaManager.deskbot, 1),
        (SynchroDogmaManager.righty, 3),
        (SynchroDogmaManager.lefty, 1),
        (SynchroDogmaManager.ecclesia, 3),
        (SynchroDogmaManager.maximus, 2),
        (SynchroDogmaManager.fleur, 2),
        (SynchroDogmaManager.punishment, 1),
        (SynchroDogmaManager.servant, 3),
        (SynchroDogmaManager.schism, 1),
        (SynchroDogmaManager.desires, 3),
        (SynchroDogmaManager.imperm, 3),
        (SynchroDogmaManager.ash, 3),
        (SynchroDogmaManager.called, 3),
        (SynchroDogmaManager.droplet, 1),
        (SynchroDogmaManager.ogre, 3),
    )
    compare_decklists("synchro_dogma", "Synchro Dogma", SynchroDogmaManager, decklists, 5000)


@measure
def main():
    test_synchro_dogma()


if __name__ == "__main__":
    main()
