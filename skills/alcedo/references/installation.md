# Installation

`alcedo-cli` is a small program in the same folder as the Alcedo Studio program. It needs no
installation of its own, and the installers do not add it to `PATH`. Call it by its full path.

## Where the programs are

| Build | `alcedo-cli` | Alcedo Studio program (`alcedo_main`) |
| --- | --- | --- |
| Windows installer | `<install folder>\bin\alcedo-cli.exe` | `<install folder>\bin\alcedo_main.exe` |
| macOS disk image | `AlcedoStudio.app/Contents/MacOS/alcedo-cli` | `AlcedoStudio.app/Contents/MacOS/AlcedoStudio` |
| Windows build from source | `build/<preset>/alcedo_studio/src/alcedo-cli.exe` | `build/<preset>/alcedo_studio/src/alcedo_main.exe` |
| macOS build from source | `build/<preset>/alcedo_studio/src/alcedo-cli` | `build/<preset>/alcedo_studio/src/alcedo_main` |

- The default Windows install folder is `C:\Program Files\Alcedo Studio`, but the user can choose
  another folder in the installer. The usual macOS app is `/Applications/AlcedoStudio.app`.
- The packages of Alcedo Studio 0.3.3 and later contain `alcedo-cli`. The packages of 0.3.2 and
  earlier do not; with those versions, ask the user to update Alcedo Studio (the update check in
  Settings), or build `alcedo-cli` from source (target `alcedo-cli`).
- `<preset>` is the build folder of the CMake preset, for example `release` or `macos-debug`.
  See [Build from source](https://github.com/zidage/AlcedoStudio/blob/main/docs/build_from_source.md).

## Find alcedo-cli

Do these steps in order and stop at the first one that finds the program. Do not ask the user
before you tried all of them.

1. Try `alcedo-cli --version`. Some users put it on `PATH` themselves.
2. Windows: read the install folder that the installer registered. This finds a folder that the
   user chose in the installer:

   ```powershell
   $keys = 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Alcedo Studio',
           'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Alcedo Studio',
           'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Alcedo Studio'
   $entry = Get-ItemProperty $keys -ErrorAction SilentlyContinue | Select-Object -First 1
   Join-Path (Split-Path $entry.UninstallString.Trim('"')) 'bin\alcedo-cli.exe'
   ```

   `DisplayVersion` of the same entry is the installed version.
3. macOS: look in `/Applications/AlcedoStudio.app` and `~/Applications/AlcedoStudio.app`, then
   ask Spotlight for the app:

   ```bash
   mdfind "kMDItemCFBundleIdentifier == 'studio.alcedo.Studio'"
   ```

   `alcedo-cli` is `Contents/MacOS/alcedo-cli` in the app that it finds.
4. When Alcedo Studio is open, `alcedo-cli` is in the folder of the running program:

   ```powershell
   Split-Path (Get-Process alcedo_main).Path
   ```

   ```bash
   dirname "$(ps -o comm= -p "$(pgrep -x AlcedoStudio)")"
   ```

5. If you cannot find it, ask the user where Alcedo Studio is installed. If Alcedo Studio is not
   installed, tell the user to install Alcedo Studio 0.3.3 or later from
   https://github.com/zidage/AlcedoStudio/releases.

Then run `alcedo-cli --version`. It prints the Alcedo Studio version, for example `0.3.3`. A
program that answers `unknown command '--version'` is older than 0.3.3; parts of these pages do
not apply to it, so ask the user to update Alcedo Studio.

The examples in these pages call `alcedo-cli` by name. Use its full path in its place, for
example `"C:\Program Files\Alcedo Studio\bin\alcedo-cli.exe" session list` or
`/Applications/AlcedoStudio.app/Contents/MacOS/alcedo-cli session list`.

## How session start finds the program

`session start` uses `--host-binary <path>`. Without it, `session start` uses the Alcedo Studio
program in the folder of `alcedo-cli`: `alcedo_main.exe` on Windows, `AlcedoStudio` in the macOS
app, and `alcedo_main` in a macOS build from source.

Give `--host-binary` only when `alcedo-cli` and the program are in different folders.

A GUI session needs no `session start`: the Alcedo Studio window starts its own session.

## Open Alcedo Studio

When the user wants you to work in the Alcedo Studio window and `session list` shows no live
`gui` session, start the application yourself. It is the program beside `alcedo-cli`:

```powershell
Start-Process "<install folder>\bin\alcedo_main.exe"
```

```bash
open "/Applications/AlcedoStudio.app"
```

Then run `alcedo-cli session list` every 2 seconds, for at most 60 seconds, until the `gui`
session is `live`. The window can open on the welcome dialog with no project, or with the last
project loaded but not entered. In both cases `-32001` answers the first project or library
command: call `project.open` with the project path (`data.path` of the error names the loaded
project), or `project.create` (see [project](reference/project.md)). Ask the user which project
to use when the request does not name one.

For batch work without the window, do not open the application: start a headless session with
`session start --headless` (see [Concepts](concepts.md)).

## Check the setup

```bash
alcedo-cli --version
alcedo-cli help
alcedo-cli session list
```

`session list` prints `no session files in '<dir>'` when no session runs. When Alcedo Studio is
open, it prints the `gui` session:

```text
gui	live	gui	pid 36984	D:/Photos/trip.alcd
```

## The GUI session setting

The Alcedo Studio window starts the session `gui` when the setting `automation/serverEnabled` is
true. This is the default. The socket accepts connections only from the same OS user. To turn
the server off, set `automation/serverEnabled` to `false` in the Alcedo Studio settings and
restart the application. The settings page has no switch for it yet. The settings are in the
registry key `HKEY_CURRENT_USER\Software\Alcedo\Alcedo` on Windows and in
`~/Library/Preferences/app.alcedo.Alcedo.plist` on macOS.

```bash
reg add "HKCU\Software\Alcedo\Alcedo\automation" /v serverEnabled /t REG_SZ /d false /f
defaults write app.alcedo.Alcedo automation.serverEnabled -bool false
```

## Shell quoting

The parameters of `call` are one JSON object in one argument.

| Shell | Example |
| --- | --- |
| bash, zsh, Git Bash | `alcedo-cli call editor.get '{"fields":["exposure"]}'` |
| PowerShell 7.3 or later | `alcedo-cli call editor.get '{"fields":["exposure"]}'` |
| Windows PowerShell 5.1 | `alcedo-cli call editor.get '{\"fields\":[\"exposure\"]}'` |
| cmd.exe | `alcedo-cli call editor.get "{\"fields\":[\"exposure\"]}"` |
