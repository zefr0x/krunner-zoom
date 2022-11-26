> **Warning** : This repository/project is no longer maintained. I'm no longer using zoom, and I don't use KDE any more. If you are interested in the plugin, it's free software under the GPL-3.0 license, so you can create a fork and do any thing you want with it.

[![Get the runner from kde store](https://raw.githubusercontent.com/ZER0-X/badges/main/kde/store/get-the-app-runner.svg)](https://www.pling.com/p/1719808/)


A KRunner plugin to open zoom meetings from a saved list in an ini file or directly using the meeting id.

# Installation
## Dependencies
- python3
- xdg-utils
- python-dbus
- klipper

🔴 Most likely you will find all of them in any KDE Plasma5 desktop.
## Install from git source code
Go to the directory that you want to keep the code in.
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
id=11111111111

[meeting_2]
name=Programming club weekly meeting
id=123123123123
passcode=123

[meeting_3]
name=data science club meeting
id=45645646
passcode=SoMEseCrEtTExT489
```
## Join saved meetins
> The key words are different depending on the language so check the list bellow.
1. Type the keyword `zm` in KRunner.
2. type `<Space>` and search in your meeting list.
3. Click `<Enter>` the join the meeting.
4. Also you are able use the actions to copy the meeting id, passcode or uri.

## Join meeting directly with the id.
> The key words are different depending on the language so check the list bellow.
1. Type the keyword `zm` in KRunner.
2. type `<Space>` and then type the meeting id.
3. Click `<Enter>` to join the meeting.

# Key words list
The key words are different form laguage to another so check the list bellow to find the appropriate key words for you.
- Arabic
    - `زم`
- English
    - `zm`
- Dutch
    - `zm`
- ...
    - `zm`
