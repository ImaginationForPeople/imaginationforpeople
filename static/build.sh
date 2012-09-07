#!/bin/sh

WHERE=$( dirname $0 )
bundle exec compass compile $WHERE
