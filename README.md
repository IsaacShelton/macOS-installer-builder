# macOS-installer-builder

Installer Builder for macOS.

Python re-write and re-structuring of `https://github.com/KosalaHerath/macos-installer-builder`, see NOTICE for details.

- `src/` The builder itself
- `stage/` The files used
    - `application/` Files for application
    - `installer/` Files for installer
- `build/` The build result

### Usage:
- Place application files in `stage/application`
- Modify files in `stage/installer/` to your liking
- Change `postinstall` script (comes with extra example instructions which you'll want to remove)
- Run `python3 src/build-installer.py AppName 1.0.0` with your app's name and version.
