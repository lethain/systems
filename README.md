



## Installation

Currently, install via:

    git clone https://github.com/lethain/systems.git
    cd interactions
    python3 -m venv ./env
    source ./env/bin/activate
    pip install -r requirements.txt

I'll also put it up on PyPi at some point, but not quite yet.



## Using the command line tools

Generally, you should be able to accomplish

cat examples/hiring.txt | python viz.py | dot









##

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

Then you could run the simulation for 15 rounds:

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

## Links

If you want something a bit more sophisticated, you might also want to
include links between a flow and a stock, for example you might want
to model the number of recruiters and use that to influence the phone
screen rate instead of fixing it at a constant value.

## Error messages

The parser will do its best to give you a useful error message.
For example, if you're missing delimiters:

    cat examples/no_delim.txt | python parse.py
    line 1 is missing delimiter '>': "[a] < b @ 25"

At worst, it will give you the line number and line that is
creating an issue:

    cat examples/invalid_flow.txt | python parse.py
    line 1 could not be parsed: "a > b @ 0..2"
