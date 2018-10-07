
Some stuff to consider doing:

* exporting a model to Excel formula
* formulas should support parentheses and do proper operation sequencing
* spend some more time working on the error messages after the move to
    tokenizer/lexer approach for parsing definition files
* support a whitelist of functions being called in formulas, e.g. max, min, etc
* support for fair-weighting of flows if there are more consumers of a flow
    than there is capacity in the flow to support (e.g. round robin capacity
    across the outflows until capacity is consumed)
    (there are probably a bunch of illegal flow combinations that this
    should identify and reject)
* add more tests to support more sophisticated formula, right now
    formula validation is based on a single, very basic test,
    particularly should lock down behavior around division
* Formulas should be presented in Graphviz exports
    (I looked into this, and wow, it's kind of annoying. It's going to require
    making invisible nodes and setting `rank: same` to a bunch of things to
    somehow many this actually work.)

Stuff I've considered but then decided agaisnt doing:

* make systems.simple which provides similar interface to systems.model
    but lets you pass in floats, ints or strings instead of Formula,
    and then make sure system.model only supports formulas