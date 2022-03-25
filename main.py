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


def get_opener_path() -> str:
    """Find the opening utility path."""
    openers_list = ["/usr/bin/xdg-open", "/usr/bin/open"]
    for opener in openers_list:
        if Path.exists(Path(opener)):
            return opener
    raise EnvironmentError("xdg-open utility was not found.")


class Runner(dbus.service.Object):
    """Comunicate with KRunner, load the config file and metch the queries."""

    def __init__(self) -> None:
        """Get opener path and load meetings list."""
        dbus.service.Object.__init__(
            self,
            dbus.service.BusName(SERVICE, dbus.SessionBus()),
            OBJPATH,
        )

        self.opener_path = get_opener_path()

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

    def load_klipper_interface(self) -> None:
        """Connect to a klipper Dbus interface if there was't one in the current match session."""
        self.klipper_iface = dbus.Interface(
            dbus.SessionBus().get_object("org.kde.klipper", "/klipper"),
            "org.kde.klipper.klipper",
        )
        return None

    @dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
    def Match(self, query: str) -> list:
        """Get the matches and return a list of tupels."""
        returns: list = []

        if query.startswith(key_word):
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
                        "temp_metting",
                        _("Join meeting with id: %s") % query,
                        icon_path,
                        100,
                        1.0,
                        {"actions": ["0", "2"]},
                    )
                )

            self.load_meetings()
            for meeting in self.meetings:
                if query in meeting["name"].lower():
                    # data, display text, icon, type (Plasma::QueryType), relevance (0-1),
                    # properties (subtext, category and urls ...)
                    returns.append(
                        (
                            meeting["section"],
                            meeting["name"],
                            icon_path,
                            100,
                            1.0,
                            {},
                        )
                    )

            return returns[:MAX_RESULTS]
        return []

    @dbus.service.method(IFACE, out_signature="a(sss)")
    def Actions(self) -> list:
        """Return a list of actions."""
        return [
            # id, text, icon
            ("0", _("Copy meeting id"), "edit-copy"),
            ("1", _("Copy meeting passcode"), "password-copy"),
            ("2", _("Copy meeting uri"), "gnumeric-link-url"),
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

        if action_id == "":
            __import__("subprocess").run([self.opener_path, meeting_uri])
            return None

        self.load_klipper_interface()
        if action_id == "0":
            self.klipper_iface.setClipboardContents(meeting_data["id"])
        elif action_id == "1":
            try:
                self.klipper_iface.setClipboardContents(meeting_data["passcode"])
            except Exception:
                pass
        elif action_id == "2":
            self.klipper_iface.setClipboardContents(meeting_uri)
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
