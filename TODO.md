
Some stuff to consider doing:

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