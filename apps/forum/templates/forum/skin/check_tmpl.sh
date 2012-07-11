#!/bin/bash

for file in  `find . -name "*.html"` 
do
	base=`basename $file`
	nb_occur=`rgrep -l $base * | wc -l`
	echo $file ':' $nb_occur
	echo '***************'
done
