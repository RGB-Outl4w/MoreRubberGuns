# Changelog

## [1.0.0] - 2026-10-03

First release. Built against Ready or Not Steam build 24942528 (Unreal Engine 5.3).

### Added

- **5 rubber-bullet weapons** in the Less Lethal loadout tabs:

  | Weapon | Slot | Class | Cartridge |
  |---|---|---|---|
  | MK18 LL Stinger | Primary assault rifle | Light | 5.56x45mm RB |
  | MP5 LL Stinger | Primary SMG | Light | 9mm P.A. |
  | LVAR LL Baton | Primary assault rifle | Heavy | .300 BLK Baton |
  | G19 LL Stinger | Secondary pistol | Light | 9mm P.A. |
  | 1911 LL Baton | Secondary pistol | Heavy | .45 Rubber |

- **Light class:** each hit stuns like a beanbag and lowers morale, for 0.1 health damage.
- **Heavy pistol:** beanbag behaviour. Suspects go down after 3 body hits (2 up close).
- **Heavy rifle:** sustained fire. The stun is shaken off after 0.5 s and costs half the morale, and suspects go down after about 5 body hits.
- **4 rubber ammo types** in `AmmoDataTable`, with their own calibers, names and icons.
- **Finishes:** Simunition-blue for light guns, less-lethal orange for heavy ones, using recoloured mesh clones.
- **Projectiles** with visible trails, less-lethal impacts, and no blood or bullet holes.
- **Attachments and scopes:** full attachment lists from the original guns, minus suppressors, with scope alignment and magnifier animations for every optic.
- **Russian localization** for all names, descriptions and ammo texts.
- **`build.py`**, which rebuilds the whole pak from the installed game.
