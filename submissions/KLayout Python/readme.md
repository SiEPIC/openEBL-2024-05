This folder must contain Python files which output GDS/OAS files in the parent folder. 

Limitations of the present GitHub Action scripts:
- The basename must be the same.
- Each .py file must generate one (exactly one) output file. One Python file cannot generate multiple outputs. Any helper Python files that don't generate the top cell must be placed elsewhere (e.g., subfolder)

