#!/bin/bash

for f in `find ./static/ -name "*.*"`
do
	name=`basename $f`
	count=`rgrep -l $name ./templates | wc -l`
	if [[ $count -eq 0 ]]
	then
		echo $f
	fi
done
