#!/usr/bin/python3
"""A KRunner plugin to open zoom meetings from a saved list or directly using the meeting id."""

from pathlib import Path
from configparser import ConfigParser
from subprocess import run as subprocess_run

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

KEY_WORD = "zm"
MAX_RESULTS = 13


icon_path = (
    str(Path.home()) + "/.local/share/pixmaps/com.github.zer0-x.krunner-zoom.png"
)

DBusGMainLoop(set_as_default=True)

objpath = "/krunnerZoom"

iface = "org.kde.krunner1"


def get_opener_path() -> str:
    """Find the opening utility path."""
    openers_list = ["/usr/bin/xdg-open", "/usr/bin/open"]
    for opener in openers_list:
        if Path.exists(Path(opener)):
            return opener
    raise EnvironmentError("xdg-open utility was not found.")


def get_meetings_list() -> list:
    """Return a list of the saved meetings form an ini file."""
    meetings: list = []

    config = ConfigParser()
    config.read(Path.joinpath(Path.home(), ".zoom_meetings_runner"))

    for meeting in config.sections():
        if not meeting.startswith("meeting_"):
            continue

        try:
            meeting_name = config[meeting]["name"]
        except KeyError:
            meeting_name = "Unnamed meeting"
        try:
            meeting_id = config[meeting]["id"]
        except KeyError:
            continue
        try:
            meeting_passcode = config[meeting]["passcode"]
        except KeyError:
            meeting_passcode = None

        meetings.append(
            {
                "section": meeting,
                "name": meeting_name,
                "id": meeting_id,
                "passcode": meeting_passcode,
            }
        )

    return meetings


class Runner(dbus.service.Object):
    """Comunicate with KRunner, load the config file and metch the queries."""

    def __init__(self) -> None:
        """Get opener path and load meetings list."""
        dbus.service.Object.__init__(
            self,
            dbus.service.BusName("com.github.zer0-x.krunner-zoom", dbus.SessionBus()),
            objpath,
        )

        self.opener_path = get_opener_path()
        self.meetings = get_meetings_list()

        # Connect to klipper to use the clipboard.
        self.bus = dbus.SessionBus()
        self.klipper_iface = dbus.Interface(
            self.bus.get_object("org.kde.klipper", "/klipper"),
            "org.kde.klipper.klipper",
        )
        return None

    @dbus.service.method(iface, in_signature="s", out_signature="a(sssida{sv})")
    def Match(self, query: str) -> list:
        """Get the matches and return a list of tupels."""
        returns: list = []

        if query.startswith(KEY_WORD):
            query = query[3:].strip()

            if query == "update":
                self.meetings = get_meetings_list()
                return [
                    (
                        "",
                        "Config loaded successfully!",
                        icon_path,
                        100,
                        1.0,
                        {"actions": ""},  # TODO debug
                    )
                ]

            try:
                assert int(query)
            except Exception:
                pass
            else:
                self.temp_meeting = {
                    "section": "temp_meeting",
                    "name": query,
                    "id": query,
                    "passcode": None,
                }
                returns.append(
                    (
                        "temp_metting",
                        f"Join meeting with id: {query}",
                        icon_path,
                        100,
                        1.0,
                        {"actions": ["0", "2"]},
                    )
                )

            for meeting in self.meetings:
                if query in meeting["name"].lower():
                    # data, display text, icon, type (Plasma::QueryType), relevance (0-1),
                    # properties (subtext, category and urls)
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

    @dbus.service.method(iface, out_signature="a(sss)")
    def Actions(self) -> list:
        """Return a list of actions."""
        return [
            # id, text, icon
            ("0", "Copy meeting id", "edit-copy"),
            ("1", "Copy meeting passcode", "password-copy"),
            ("2", "Copy meeting uri", "gnumeric-link-url"),
        ]

    @dbus.service.method(iface, in_signature="ss")
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
            subprocess_run([self.opener_path, meeting_uri])
        elif action_id == "0":
            self.klipper_iface.setClipboardContents(meeting_data["id"])
        elif action_id == "1":
            try:
                self.klipper_iface.setClipboardContents(meeting_data["passcode"])
            except Exception:
                pass
        elif action_id == "2":
            self.klipper_iface.setClipboardContents(meeting_uri)
        return None


runner = Runner()
loop = GLib.MainLoop()
loop.run()
