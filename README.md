# Drop After Round Three (DART) Consistency Checker
---

## Justification

Programmatically checking the consistency of decklists has been around for a bit. However, after being used to craft the winning Dragon Link FTK list at LCS 4, much more people have become aware of this technique. Due to this popularity, I have decided to revive a dormant project I started and then immediately dropped a few months ago. The goal of the project is to provide a generic framework for performing consistency checking on decklists. Instead of coding each deck individually, decklists and combos are described in YAML. I chose YAML over XML or JSON because I believe it to be the most human-readable of these formats. If successful, this project will open up this technique to those without a background in coding. 

However, that doesn't mean you can simply export a DuelingNetwork deck list into this program. The input file must follow a specific format and be free of errors. Also, note that the creator of this file must be very well-acquainted with their deck in order to describe the chain of plays that comprise the deck's combo(s). Complex decks with many lines of play will likely never be easily modelled with this system. The decks best suited to this system are those with 1-card or 2-card combos where the starting hand can be described as "this card and any of these cards OR any of these cards and any of those cards, but only if you don't draw this card". The Dragon Link FTK was an ideal deck for this technique because it required only two dragons to start the combo.

## Sample Output

Using the provided `machina_nekroz.yml`, the following output can be obtained:
```
None 18.673
unicore-fallback 44.962
coltwing-combo 35.941
get-to-halq 0.424
```

Improving the user experience will come with time.

## Installing and Running

Soon?


