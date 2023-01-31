#!/bin/sh

cd $1 && ffmpeg -framerate 30 -i $2 -c copy $3