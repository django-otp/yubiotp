#!/bin/sh

{ watchmedo-2.7 shell-command \
    -p '*.rst;*.py' \
    -R \
    -c echo \
    source ..
} | while read line; do make html; done
