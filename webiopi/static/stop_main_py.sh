#!/bin/sh

ps auxww | grep main.py | grep -v grep | awk '{ print "kill -9", $2}' | sh
