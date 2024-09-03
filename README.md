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

## Repository Status: Sharing / Inactive

This repository hosts code that I’ve chosen to share publicly for educational,
demonstration, or archival purposes. Please note the following:

- **No Active Maintenance**: This project is not actively maintained or updated.
  It serves primarily as a snapshot of a certain stage of development for those
  who might find parts of the code useful or interesting. I try to accept pull-
  request, but do not expect anything. If interest in the project increases, I
  might change the repository status.
- **No Support Provided**: As this is an inactive project, I’m unable to provide
  support, answer issues, or accommodate pull requests.
- **Use at Your Own Risk**: While you’re welcome to explore, fork, or use the
  code in your own projects, please do so with the understanding that this
  repository is provided as-is, without any guarantees on its functionality or
  security.

Feel free to explore the code and utilize it under the terms of the license
attached to this repository!
