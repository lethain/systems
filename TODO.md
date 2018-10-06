
Some stuff to consider doing:

* move systems.lexer.readable into systems.formatter and add a script
    for formatting system definitions properly (along lines of pep8
    or gofmt). Also add some basic tests for that functionality.
* make systems.simple which provides similar interface to systems.model
    but lets you pass in floats, ints or strings instead of Formula,
    and then make sure system.model only supports formulas
* add more tests to support more sophisticated formula, right now
    formula validation is based on a single, very basic test,
    particularly should lock down behavior around division
* need to build a dependency graph across variables, to figure out
    whether a given system is deterministic and reject if it isn't.
    the current handling of complex initial values is quite jank,
    maybe jank enough that we should explicitly reject them until
    this work is done
* formulas should support parentheses and do proper operation sequencing
* support a whitelist of functions being called in formulas, e.g. max, min, etc
* support for fair-weighting of flows if there are more consumers of a flow
    than there is capacity in the flow to support (e.g. round robin capacity
    across the outflows until capacity is consumed)
    (there are probably a bunch of illegal flow combinations that this
    should identify and reject)
* Formulas should be presented in Graphviz exports
    (I looked into this, and wow, it's kind of annoying. It's going to require
    making invisible nodes and setting `rank: same` to a bunch of things to
    somehow many this actually work.)
* exporting a model to Excel formula