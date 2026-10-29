# Issues found in smart_home.py

Name: Atharva Bidre
SRN: PES1UG24CS095

Line numbers refer to the original smart_home.py from the repo. Check them against your own before/after reports.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shared mutable default argument | Bug | `addDevice` (def line) | `settings={}` is created once, so every device without its own settings shares one dict. Setting the thermostat to 30 made "Light settings" print `{'temperature': 30}`. | Default to `None` and give each device its own copy with `dict(settings or {})`. |
| Hub binds to all interfaces | Security (Bandit B104, medium) | `HUB_HOST = "0.0.0.0"` | The hub listens on every network interface, so anyone on the network can reach it. | Default to `127.0.0.1` and read `HUB_HOST` from the environment if a different one is needed. |
| Hardcoded password | Security (Bandit B105, low) | `HUB_PASSWORD` | The password is written in the source code, so it ends up in git history. | Read it from the `HUB_PASSWORD` environment variable. |
| Shell command built from a string | Security (Bandit B602, high) | `runScene` | `shell=True` with a string joined from the caller's input allows command injection (and path tricks like `../`). | Call `subprocess.run(["bash", path], check=True)` without a shell, and only accept scene names that match `[\w.-]+\.sh`. |
| Bandit notes on `subprocess` (B404, B603, B607) | Security (low) | `import subprocess`, `runScene` | Bandit still flags the import and the call even after the fix. | Added `# nosec` comments with a reason, since the input is now validated. |
| Unknown device crashes the setter | Bug | `setTemperature` | `devices[deviceName]` raises `KeyError` for a device that does not exist, unlike `toggleDevice`, which prints a message. | Use `.get()` and print a message, returning `False`. |
| Inconsistent return | Quality (Pylint R1710) | `toggleDevice` | Returns the new state if the device exists, otherwise falls off the end with no return. | Check for the missing device first and `return None` explicitly. |
| Missing encoding on `open()` | Quality (Pylint W1514) | `saveState` | The file is opened without an encoding, so it depends on the machine. | Pass `encoding="utf-8"`. |
| Magic numbers | Quality | `setTemperature` | 16 and 30 are written inline. | Moved to `MIN_TEMP` and `MAX_TEMP`. |
| Names not in snake_case | Style (Pylint C0103) | all functions, `devices` | `addDevice`, `toggleDevice` etc. and the module-level `devices` do not follow PEP 8. | Renamed to `add_device`, `toggle_device`, ... and `DEVICES`. |
| No docstrings | Style (Pylint C0114, C0116) | module and every function | Nothing explains what the module or functions do. | Added a short docstring to each. |
| String concatenation | Style | `hubAddress` | `HUB_HOST + ":" + str(HUB_PORT)` is clumsy. | Use an f-string. |
| Formatting problems | Style (Flake8 E203, E261, E302, E305, E128) | `POWER_USAGE`, `print("Hub address"...)`, function gaps, `main()` | Space before `:`, one space before an inline comment, one blank line between functions, bad continuation indent. | Fixed spacing and used two blank lines between top-level blocks. |
| `main()` runs on import | Quality | last line | Importing the file would run the demo and write `home_state.json`. | Wrapped in `if __name__ == "__main__":`. |
