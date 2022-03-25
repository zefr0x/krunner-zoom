#!/usr/bin/python3
"""A KRunner plugin to open zoom meetings from a saved list or directly using the meeting id."""

from pathlib import Path
from gettext import gettext, bindtextdomain, textdomain

# The next import are on-time imports in the middle of the file to save memory.
# from configparser import ConfigParser
# from subprocess import run as subprocess_run

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# Setup gettext for internationalization.
bindtextdomain("messages", "locales")
textdomain("messages")
_ = gettext


key_word = _("zm")
key_word_length = len(key_word) + 1
MAX_RESULTS = 13


icon_path = (
    str(Path.home()) + "/.local/share/pixmaps/com.github.zer0-x.krunner-zoom.png"
)

DBusGMainLoop(set_as_default=True)

OBJPATH = "/krunnerZoom"
IFACE = "org.kde.krunner1"
SERVICE = "com.github.zer0-x.krunner-zoom"


class Runner(dbus.service.Object):
    """Comunicate with KRunner, load the config file and metch the queries."""

    def __init__(self) -> None:
        """Get opener path and load meetings list."""
        dbus.service.Object.__init__(
            self,
            dbus.service.BusName(SERVICE, dbus.SessionBus()),
            OBJPATH,
        )
        return None

    def load_meetings(self) -> None:
        """Load meetings list if it was't loaded before in the match session."""
        if hasattr(self, "meetings"):
            return None

        self.meetings: list = []

        config = __import__("configparser").ConfigParser()
        config.read(Path.joinpath(Path.home(), ".zoom_meetings_runner"))

        for meeting in config.sections():
            if not meeting.startswith("meeting_"):
                continue

            try:
                meeting_id = config[meeting]["id"]
            except KeyError as e:
                print(e)
                continue
            try:
                meeting_name = config[meeting]["name"]
            except KeyError:
                meeting_name = meeting
            try:
                meeting_passcode = config[meeting]["passcode"]
            except KeyError:
                meeting_passcode = None

            self.meetings.append(
                {
                    "section": meeting,
                    "name": meeting_name,
                    "id": meeting_id,
                    "passcode": meeting_passcode,
                }
            )

        return None

    @dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
    def Match(self, query: str) -> list:
        """Get the matches and return a list of tupels."""
        returns: list = []

        if query.startswith(key_word + " ") or query == key_word:
            query = query[key_word_length:].strip()

            if query.isdecimal():
                self.temp_meeting = {
                    "section": "temp_meeting",
                    "name": query,
                    "id": str(int(query)),  # If non-ascii degits were used.
                    "passcode": None,
                }
                returns.append(
                    (
                        "temp_meeting",
                        _("Join meeting with id: %s") % query,
                        icon_path,
                        100,
                        1.0,
                        {"actions": ["copy_id", "copy_uri"]},
                    )
                )

            self.load_meetings()
            for meeting in self.meetings:
                if query in meeting["name"].lower():
                    if meeting["passcode"] is not None:
                        properties = {
                            "actions": ["copy_id", "copy_passcode", "copy_uri"]
                        }
                    else:
                        properties = {"actions": ["copy_id", "copy_uri"]}
                    # data, display text, icon, type (Plasma::QueryType), relevance (0-1),
                    # properties (subtext, category and urls ...)
                    returns.append(
                        (
                            meeting["section"],
                            meeting["name"],
                            icon_path,
                            100,
                            1.0,
                            properties,
                        )
                    )

            return returns[:MAX_RESULTS]
        return []

    @dbus.service.method(IFACE, out_signature="a(sss)")
    def Actions(self) -> list:
        """Return a list of actions."""
        return [
            # id, text, icon
            ("copy_id", _("Copy meeting id"), "edit-copy"),
            ("copy_passcode", _("Copy meeting passcode"), "password-copy"),
            ("copy_uri", _("Copy meeting uri"), "gnumeric-link-url"),
        ]

    @dbus.service.method(IFACE, in_signature="ss")
    def Run(self, data: str, action_id: str) -> None:
        """Handle actions calls."""
        if data == "":
            return None
        elif data == "temp_meeting":
            meeting_data = self.temp_meeting
        else:
            for meeting_data in self.meetings:
                if meeting_data["section"] == data:
                    break

        meeting_uri = (
            f"zoommtg://zoom.us/join?action=join&confno={meeting_data['id']}"
            + ("&pwd=" + meeting_data["passcode"] if meeting_data["passcode"] else "")
        )

        # Since the match session will be killed after we run an action,
        # no need to load thing in the object scope.

        if action_id == "":
            opener_path = None
            for opener in ["/usr/bin/xdg-open", "/usr/bin/open"]:
                if Path.exists(Path(opener)):
                    opener_path = opener
            if opener_path is None:
                raise FileNotFoundError(
                    "No open utility was found. Install `xdg-utils`."
                )
            else:
                __import__("subprocess").run([opener_path, meeting_uri])
            return None

        # Connect to a klipper Dbus interface if there was't one in the current match session.
        klipper_iface = dbus.Interface(
            dbus.SessionBus().get_object("org.kde.klipper", "/klipper"),
            "org.kde.klipper.klipper",
        )

        if action_id == "copy_id":
            klipper_iface.setClipboardContents(meeting_data["id"])
        elif action_id == "copy_passcode":
            klipper_iface.setClipboardContents(meeting_data["passcode"])
        elif action_id == "copy_uri":
            klipper_iface.setClipboardContents(meeting_uri)
        return None

    @dbus.service.method(IFACE)
    def Teardown(self) -> None:
        """Save memory by deleting the meetings list and klipper connetion from the memory."""
        del self.meetings
        del self.temp_meeting
        del self.klipper_iface
        return None


runner = Runner()
loop = GLib.MainLoop()
loop.run()
