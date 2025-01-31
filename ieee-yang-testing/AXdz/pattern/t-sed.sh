#!/bin/bash
input="t.err"
output="t.out"
sed 's/\(^libyang\[0\]: \)\(Unsatisfied.* to \)\(\".*patterns\[\)\(name=.*\)\(, line.*$\)/\2\4/' "$input" > "$output"
