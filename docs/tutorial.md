
# Tutorial

Please follow the [installation instructions](../) before continuing with these steps.
Also see the [Jupyter notebook example](../notebooks/hiring.ipynb) for another example.

---

Let's say you wanted to describe your hiring funnel and retention
for a rapidly growing company, you could do so via:

     [PossibleRecruiters] > Recruiters(10, 15) @ 1
     [Candidates] > PhoneScreens @ Recruiters * 3
     PhoneScreens > Onsites      @ 0.5
     Onsites      > Offers       @ 0.5
     Offers       > Hires        @ 0.5
     Hires        > Employees    @ 1.0
     Employees    > Departures   @ Leak(0.1)
     Departures   > [Departed]   @ 1.0

Note that you're able to refer to the value of `Recruiters` when specifying
the size of the flow between `Candidates` and `PhoneScreens`. This allows you
to build feedback loops and such!

Then you could run the simulation for 10 rounds:

    cat examples/links.txt | systems-run -r10

            Recruiters      PhoneScreens    Onsites Offers  Hires   Employees       Departures
    0       10              0               0       0       0       0               0
    1       11              30              0       0       0       0               0
    2       12              33              15      0       0       0               0
    3       13              36              16      7       0       0               0
    4       14              39              18      8       3       0               0
    5       15              42              19      9       4       3               0
    6       15              45              21      9       4       7               0
    7       15              45              22      10      4       11              0
    8       15              45              22      11      5       14              1
    9       15              45              22      11      5       18              1
    10      15              45              22      11      5       22              1

You can also get the output as CSV:

    cat examples/links.txt | systems-run -r10 --csv

Which you could... load into a spreadsheet or something to graph!

