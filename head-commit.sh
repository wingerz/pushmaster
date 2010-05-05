#!/bin/bash
git log -1 --pretty=oneline | awk '{ print $1 }'
