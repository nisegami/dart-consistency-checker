# Drop After Round Three (DART) Consistency Checker
---

## Justification

Programmatically checking the consistency of decklists has been around for a bit. However, after being used to craft the winning Dragon Link FTK list at LCS 4, much more people have become aware of this technique. Due to this popularity, I have decided to revive a dormant project I started and then immediately dropped a few months ago. The goal of the project is to provide a generic framework for performing consistency checking on decklists. Originally, the goal was to use a markup language such as YAML to describe combos, but YuGiOh proved to be too complex, so I settled for coding each deck individually. Although this limits the accessibility of the project, DART sitll provides a useful framework for modelling and working with YuGiOh gamestates and provides many useful abstractions. 

## Sample Output

```
end_games = [SynchroDogmaManager().run() for _ in range(10000)]
print(SynchroDogmaManager.generate_report(end_games))
```
produces
```
% of games with Winda: 74.72
% of games with Herald: 72.91
% of games with Savage: 61.98
% of games with >=3 disruptions: 91.24
% of games with >=3 disruptions and Winda: 70.46
% of bricks (<3 disruptions and no Winda): 4.48
```

## Installing and Running

Probably not soon.