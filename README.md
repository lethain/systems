This is a quick experiment in describing systems in a text format
and then evaluating the defined systems.


Let's say you wanted to describe your hiring funnel and retention
for a rapidly growing company, you could do so via:

     # wrap with [] to indicate an infinite stock that
     # isn't included in each table
     # integers are implicitly steady rates
     [Candidates] > PhoneScreens @ 25

     # floats are implicitly conversions that convert the
     # source stock into the destination stock at a discount
     # e.g. a source at 10 with a 0.5 conversion would empty
     # itself and add 5 units to the destination
     PhoneScreens > Onsites      @ 0.5
     Onsites      > Offers       @ 0.5
     Offers       > Hires        @ 0.5
     Hires        > Employees    @ 1.0

     # specify leak to avoid a destructive conversion
     Employees    > Departures   @ 0.1, leak
     Departures   > [Departed]   @ 1.0

Then you could run the simulation for 3 rounds:

    > cat hiring.txt | python3 parse.py -r15
            PhoneScreens    Onsites Offers  Hires   Employees       Departures
    0       0               0       0       0       0               0
    1       25              0       0       0       0               0
    2       25              12      0       0       0               0
    3       25              12      6       0       0               0
    4       25              12      6       3       0               0
    5       25              12      6       3       3               0
    6       25              12      6       3       6               0
    7       25              12      6       3       9               0
    8       25              12      6       3       12              0
    9       25              12      6       3       14              1
    10      25              12      6       3       16              1
    11      25              12      6       3       18              1
    12      25              12      6       3       20              1
    13      25              12      6       3       21              2
    14      25              12      6       3       22              2
    15      25              12      6       3       23              2


You can also get the output as CSV:

    cat hiring.txt | python3 parse.py -r2 --csv
    ,PhoneScreens,Onsites,Offers,Hires,Employees,Departures
    0,0,0,0,0,0,0
    1,25,0,0,0,0,0
    2,25,12,0,0,0,0

Which you could... load into a spreadsheet or something to graph!