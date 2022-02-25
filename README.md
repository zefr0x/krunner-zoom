[![Get the runner from kde store](https://raw.githubusercontent.com/ZER0-X/badges/main/kde/store/get-the-app-runner.svg)](https://www.pling.com/p/1719808/)


A KRunner plugin to open zoom meetings from a saved list in an ini file or directly using the meeting id.

# Installation
## Dependencies
- Python3
- python-dbus
- Plasma5 desktop
- KRunner

🔴 You don't need to install any dependency, since most likely you will find all of them in any KDE Plasma5 desktop.
## Install from git source code
Go the the directory that you want to keep the code in.
```bash
$ git clone https://github.com/zer0-x/krunner-zoom.git
$ cd krunner-zoom
$ ./install.sh
```
🔴 Don't delete the source code after the installation.
### Uninstall
Go to the source code directory and run the uninstall script:
```bash
$ ./uninstall.sh
```
## Install from the kde store
1. Open system settings
2. Go to `search` > `KRunner`
3. Click on `Get New Plugins...`
4. Search for the Plugin
5. Click `Install`

### Uninstall
Please run the uninstall script manually, because the GUI will remove the script before running it.

# Usage & Configuration
## config file
1. Create a file in your home directory with the name: `.zoom_meetings_runner`
2. Open it with your text editor
3. Use the ini format to save your zoom meetings data, for example:
```ini
[meeting_1]
name=MATH-302 online class
id= 11111111111

[meeting_2]
name=Programming club weekly meeting
id= 123123123123
passcode=123

[meeting_3]
name=data since club meeting
id=45645646
passcode=somesecrettxt0123
```
## Join saved meetins
1. Type the keyword `zm` in KRunner.
2. type `<Space>` and search in your meeting list.
3. Click `<Enter>` the join the meeting.
4. Also you are able use the actions to copy the meeting id, passcode or uri.

## Join meeting directly with the id.
1. Type the keyword `zm` in KRunner.
2. type `<Space>` and then type the meeting id.
3. Click `<Enter>` to join the meeting.

## Load your config
If you edited your meetings list you are able to load the changes whitout restarting the plugin.
1. Type the keyword `zm` in KRunner.
2. type `<Space>` and then type `update`.
3. You should get a success message.
