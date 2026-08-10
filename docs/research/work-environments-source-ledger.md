# Work Environments Feasibility Source Ledger

**Status:** Initial source ledger for a proposed design. It supports feasibility review only and does not freeze application or desktop interfaces.

## Sources

| Area | Upstream source | Design relevance |
|---|---|---|
| Krita resources and launch behavior | <https://docs.krita.org/en/reference_manual/linux_command_line.html> | Krita documents command-line file handling and named workspace selection, supporting a narrow adapter based on saved resources rather than internal-state scraping. |
| Krita sessions | <https://docs.krita.org/en/reference_manual/main_menu/file_menu.html> | Krita exposes a Sessions manager, supporting delegation of application-internal restoration to Krita itself. |
| VS Code files, folders, workspaces, and profiles | <https://code.visualstudio.com/docs/configure/command-line> | VS Code documents opening files, folders, workspaces, and named profiles, supporting one feasible code-editor reference integration. |
| VS Code profiles | <https://code.visualstudio.com/docs/configure/profiles> | Profiles are application-owned state; Felunyx can request a profile without owning VS Code's private session storage. |
| Portal architecture | <https://flatpak.github.io/xdg-desktop-portal/docs/> | Portals provide the standard integration path for sandboxed applications and desktop sessions. |
| Portal backend implementation | <https://flatpak.github.io/xdg-desktop-portal/docs/writing-a-new-backend.html> | A new desktop can compose or implement D-Bus-activated portal backends instead of inventing a separate sandbox integration system. |
| Portal backend selection | <https://flatpak.github.io/xdg-desktop-portal/docs/portals.conf.html> | Desktop and distribution configuration can choose portal backends per interface. |

## Conclusions supported

- Saved projects and files can provide useful restoration without generic process-memory capture.
- Application-native sessions should remain owned by applications.
- A code editor can expose a useful reference integration through documented launch interfaces.
- Portal compatibility is a required desktop integration surface, not optional visual polish.
- These sources do not prove window correlation, layout restoration, privacy detection, or cross-desktop parity; those remain implementation and runtime validation work.

## Refresh policy

Recheck exact options and contracts during the owning implementation phase. Record application and portal versions used by tests. Do not treat this ledger as a permanent compatibility guarantee.
