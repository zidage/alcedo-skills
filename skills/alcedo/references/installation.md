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

- The default Windows install folder is `C:\Program Files\Alcedo Studio`. The usual macOS app
  is `/Applications/AlcedoStudio.app`.
- The packages of Alcedo Studio 0.3.2 and earlier do not contain `alcedo-cli`. With those
  versions, build it from source (target `alcedo-cli`).
- `<preset>` is the build folder of the CMake preset, for example `release` or `macos-debug`.
  See [Build from source](https://github.com/zidage/AlcedoStudio/blob/main/docs/build_from_source.md).

## Find alcedo-cli

1. Try `alcedo-cli help`. Some users put it on `PATH` themselves.
2. Look in the default location of the table above.
3. When Alcedo Studio is open, `alcedo-cli` is in the folder of the running program:

   ```powershell
   Split-Path (Get-Process alcedo_main).Path
   ```

   ```bash
   dirname "$(ps -o comm= -p "$(pgrep -x AlcedoStudio)")"
   ```

4. If you cannot find it, ask the user where Alcedo Studio is installed.

The examples in these pages call `alcedo-cli` by name. Use its full path in its place, for
example `"C:\Program Files\Alcedo Studio\bin\alcedo-cli.exe" session list` or
`/Applications/AlcedoStudio.app/Contents/MacOS/alcedo-cli session list`.

## How session start finds the program

`session start` uses `--host-binary <path>`. Without it, `session start` uses the Alcedo Studio
program in the folder of `alcedo-cli`: `alcedo_main.exe` on Windows, `AlcedoStudio` in the macOS
app, and `alcedo_main` in a macOS build from source.

Give `--host-binary` only when `alcedo-cli` and the program are in different folders.

A GUI session needs no `session start`: the Alcedo Studio window starts its own session.

## Check the setup

```bash
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
