# Atomic-Metric

Measure how atomic functions in a project are. The closest to common terminology
is: Atomic is the opposite of coupling. It encourages high variablity in
atomicity. Atomic functions can easly be unittested, read and understood.

It divides all the operations in a function into (from most to least atomic):
operator, builtin, standard_lib_function, library_function, unknown,
local_function, project_function. Note: Coupling is not exactly what atmomic-
metric measures.

The metric comes in two flavours:

- **standard**: It favours higher atomicity and higher variablity
- **variablity**: Only favours higher variablity

Standard will discourage code-reuse, I still recommend using stadnard, because
currently we overvalue code-reuse over testablity, readablity and intelligibly.

Variablity will only encourage seperation of atomic functions and integration
functions (highly coupled functions). Which is what test-driven development and
clean desgin usually encourage.

Unknown operations are those the static-anlysis library cannot understand, I
think a high penalty for such operations is good.
