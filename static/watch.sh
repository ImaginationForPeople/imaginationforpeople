#!/bin/sh

WHERE=$( dirname $0 )
# NOTE: compass sometimes crashes in the 'watch' action.
while true; do bundle exec compass watch $WHERE ; done
