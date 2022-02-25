#!/bin/bash

# Exit if something fails
set -e

mkdir -p ~/.local/share/kservices5/
mkdir -p ~/.local/share/dbus-1/services/
mkdir -p ~/.local/share/pixmaps

cp assets/com.github.zer0-x.krunner-zoom.png ~/.local/share/pixmaps/

sed "s|%{ICON}|${HOME}/.local/share/pixmaps/com.github.zer0-x.krunner-zoom.png|" "plasma-runner-zoom.desktop" > ~/.local/share/kservices5/plasma-runner-zoom.desktop
sed "s|%{PROJECTDIR}/%{APPNAMELC}.py|${PWD}/main.py|" "com.github.zer0-x.krunner-zoom.service" > ~/.local/share/dbus-1/services/com.github.zer0-x.krunner-zoom.service

kquitapp5 krunner
