# P7 Desktop Integration

P7-M6 adds package-owned desktop integration for the local Linux app.

## Desktop File

Source:

- `packaging/deb/alters-lab.desktop`

Package path:

- `/usr/share/applications/alters-lab.desktop`

Desktop entry summary:

- `Type=Application`
- `Name=Alters Lab`
- `Comment=Local personal calibration app`
- `Exec=alters-lab open`
- `Terminal=false`
- `Categories=Utility;X-Productivity;`
- `StartupNotify=true`
- `Icon=alters-lab`

The desktop file launches the existing package-owned CLI. It does not point at a repo checkout, does not start a separate frontend dev server, and does not own runtime state.

`X-Productivity` is used instead of bare `Productivity` because `desktop-file-validate` rejects unregistered non-`X-` category values.

## Icon

Source:

- `packaging/assets/alters-lab.svg`

Package path:

- `/usr/share/icons/hicolor/scalable/apps/alters-lab.svg`

The icon is a small project-owned SVG. It uses no external image assets.

## Package Staging

`tools/build_deb.py` stages the desktop file and icon during package build while preserving the P7-M5 exclusions for user config, secrets, logs, runtime records, `node_modules`, `.env`, and `.deb` artifacts.

## P6 Boundary

P7-M6 only adds desktop launch integration. It does not validate P6, seal P6, fabricate P6 records, call a live provider, or modify active YAML/rubric. P6 remains `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`.
