#!/bin/bash
s="1"
for ((i=3; i<=4095; i+=2))
do
  s="$s,$i"
done

echo $s
