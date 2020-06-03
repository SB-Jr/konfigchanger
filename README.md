# KonfChanger
This project is a simple command line utility that can be used to backup and restore a set of configuration file and folders.

## Use Cases
- Toggle light/dark theme
- Backup configs to replicate the same settings in another system
- Replicate and automate basic system configs post installation of a new distro
- Backup existing configs to restore in case of session/distro break
- and many more....

## TODO
 - [x] Backup current set of configurations
 - [x] Restore a named config pack
   - [ ] Restore a named config pack with backing up current set of configurations
 - [ ] Schedule applying of config packs
 - [ ] Schedule backing-up of set of configs
 - [ ] Add back/restore options for Applications
   - [ ] Atom
   - [ ] Chrome
   - [ ] Latte Dock
   - [ ] Vim
   - [ ] Konsole
- [ ] Provide configuration file to give options on source for backup and restore
- [x] Provide options to add folder/files to add for back/restore thus entending to uncovered applications and settings
- [ ] Provide option to listen to events and change configurations based on the change
