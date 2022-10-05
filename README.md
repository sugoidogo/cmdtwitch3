# CMDTwitch
OBS Script for launching commands on your pc for twitch redeems
## Install
### Windows
Before OBS can use python scripts, it needs to know where to find a compatible python interpreter. You can either:
- Use my [OBS Python Installer](https://github.com/sugoidogo/obs-python-installer) to detect or install a compatible python interpreter and update your obs settings automatically
- Locate your existing python install via `Tools > Scripts > Python Settings`
### All Platforms
Download and extract the [latest release](https://github.com/sugoidogo/obs-startup-apps/releases/latest) into any directory, and then add the script to OBS via `Tools > Scripts > +` (bottom-left of the scripts window). From there you can add or remove any startup apps.
## Usage
0. You should automatically be prompted to give "CommandRunner" access to your twitch channel redeems. If not, try reloading or resetting the script.
1. Add the program or script you want to run via redeems
    - For simplicity, pick a file here. OBS will let you pick a file, directory, or input whatever you want via the url/path option, but whatever string you put in goes straight into [Popen](https://docs.python.org/3/library/subprocess.html#popen-constructor) with no other args.
2. The twitch redeems manager UI should pop up at this point, and you should have a new redeem with the name of the file you added. Customise to your liking and enable when you're ready to use it.
3. ...
4. Profit?
## Support
- Get support via [Discord](https://discord.gg/PbGT9tVWTC)
- Give support via [PayPal](https://paypal.me/SugoiDogo)
