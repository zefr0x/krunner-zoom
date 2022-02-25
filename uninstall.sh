#!/bin/bash

# Exit if something fails
set -e

rm ~/.local/share/kservices5/plasma-runner-zoom.desktop
rm ~/.local/share/dbus-1/services/com.github.zer0-x.krunner-zoom.service
rm ~/.local/share/pixmaps/com.github.zer0-x.krunner-zoom.png
kquitapp5 krunner
