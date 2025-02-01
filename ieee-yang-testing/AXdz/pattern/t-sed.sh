#!/bin/bash
input="tep.err"
output="tep.out"
sed 's/\(^libyang\[0\]: \)\(Unsatisfied.* to \)\(\".*patterns\[\)\(name=.*\)\(, line.*$\)/\2\4/' "$input" > "$output"
