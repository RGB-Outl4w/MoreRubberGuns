<p align="center">
  <img src="docs/assets/banner.svg" alt="More Rubber Guns, a less-lethal weapon pack for Ready or Not" width="100%">
</p>

<p align="center">
  <b>English</b> · <a href="README-ru.md">Русский</a>
</p>

<p align="center">
  <a href="https://github.com/RGB-Outl4w/MoreRubberGuns/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/RGB-Outl4w/MoreRubberGuns?style=flat-square&color=FF6A13&label=release"></a>
  <img alt="Game" src="https://img.shields.io/badge/Ready%20or%20Not-build%2024942528-2F6FD6?style=flat-square">
  <img alt="Engine" src="https://img.shields.io/badge/Unreal%20Engine-5.3-555?style=flat-square">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-555?style=flat-square"></a>
  <a href="https://boosty.to/rgboutlaw"><img alt="Support on Boosty" src="https://img.shields.io/badge/support-Boosty-F15F2C?style=flat-square"></a>
</p>

**More Rubber Guns** adds five rubber-bullet weapons to Ready or Not: two assault rifles, two pistols and an SMG. The vanilla beanbag shotgun is no longer your only less-lethal long gun.

Every gun is a full-featured weapon built from the game's own assets: real models and animations, the complete attachment list, aligned scopes, and its own rubber cartridge and stats. Each one belongs to one of two classes:

- 🔵 **Light (Stinger)**: every hit stuns and pushes the target toward surrender, but never wounds.
- 🟠 **Heavy (Baton)**: hits hard enough to knock a suspect down, wounded but alive.

> [!NOTE]
> No UE4SS or other loaders are needed. It's a single `.pak` you drop into the game folder.

## Contents

- [Features](#features)
- [The arsenal](#the-arsenal)
- [How it plays](#how-it-plays)
- [Installation](#installation)
- [Compatibility](#compatibility)
- [Building from source](#building-from-source)
- [How it works](#how-it-works)
- [Support the project](#support-the-project)
- [License and credits](#license-and-credits)

## Features

- **5 new weapons** in the **Less Lethal** loadout tabs: 2 assault rifles and 1 SMG as primaries, 2 pistols as secondaries.
- **Two damage classes** with different behaviour:
  - Light guns stun.
  - The heavy pistol knocks suspects down.
  - The heavy rifle needs sustained fire, because suspects shake off its stun and fight back.
- **Real rubber cartridges** with their own ammo entries: 5.56x45 RB, .300 BLK Baton, 9mm P.A. and .45 Rubber.
- **Colour-coded finishes:** Simunition blue for light guns, less-lethal orange for heavy ones.
- **Every attachment slot** from the original gun, with all scopes properly aligned. Suppressors are removed.
- **Visible projectile trails**, so you can see where your rounds land. No blood and no bullet holes.
- **Counts as less-lethal force** for the rules of engagement, like the beanbag and the taser.
- **English and Russian.** Texts switch to Russian when the game is set to Russian, and fall back to English for every other language.

## The arsenal

| | MK18 LL Stinger | MP5 LL Stinger | LVAR LL Baton | G19 LL Stinger | 1911 LL Baton |
|---|:---:|:---:|:---:|:---:|:---:|
| **Slot** | Primary · AR | Primary · SMG | Primary · AR | Secondary | Secondary |
| **Class** | 🔵 Light | 🔵 Light | 🟠 Heavy | 🔵 Light | 🟠 Heavy |
| **Cartridge** | 5.56x45mm RB | 9mm P.A. (9x22) | .300 BLK Baton | 9mm P.A. (9x22) | .45 Rubber (11.43x22) |
| **Magazine** | 30 | 30 | 30 | 15 | 7 |
| **Fire modes** | Semi / Auto | Semi / Auto | Semi / Auto | Semi | Semi |
| **Rate of fire** | 700 rpm | 800 rpm | 750 rpm | n/a | n/a |
| **Muzzle velocity** | ~180 m/s | ~350 m/s | ~260 m/s, subsonic | ~330 m/s | ~220 m/s |
| **Barrel** | 262 mm | 225 mm | 140 mm, integral suppressor | 102 mm | 127 mm |
| **Health damage per hit** | 0.1 | 0.1 | 40 | 0.1 | 65 |
| **Body hits to down a suspect** | never | never | ~5 | never | 3 (2 up close) |
| **Body hits to down a civilian** | never | never | 3 | never | 2 |

<details>
<summary><b>Attachments per weapon</b></summary>

Each gun gets the full list from its original weapon, minus suppressors.

- **MK18 LL Stinger**
  - Optics: carry-handle irons, SRS, Micro T-2 (raised), M5B, HS510C, EXPS3, BOSS Xe, SDR, MRO HD 3x
  - Muzzle: ASR compensator, SFMB brake, 14" barrel
  - Underbarrel: VFG, AFG, combat grip, RK-1, CQR
  - Overbarrel: laser, PEQ, MAWL
  - Light: M600V
  - Magazine: PMAG
- **MP5 LL Stinger**
  - Optics: RMR (mounted), SRO, Micro T-2, Aimpro, HS510C, EXPS3, BOSS Xe
  - Underbarrel: VFG, AFG, combat grip, RK-1
  - Overbarrel: laser, PEQ
  - Light: Inforce WML
- **LVAR LL Baton**
  - Optics: SRS, Micro T-2 (raised), M5B, HS510C, EXPS3, BOSS Xe, SDR, ATACR, MRO HD 3x
  - Canted irons
  - Underbarrel: AFG, combat grip, VFG, RK-1
  - Overbarrel: MAWL, laser, PEQ
  - Lights: M600V, Inforce WML
- **G19 LL Stinger**
  - Optics: SRO, RMR
  - Muzzle: compensator
  - Underbarrel: laser, light, IR laser, Steiner PL
- **1911 LL Baton**
  - Optics: SRO, RMR
  - Muzzle: double-port compensator
  - Underbarrel: light, laser

</details>

## How it plays

**🔵 Light guns: MK18, MP5, G19.** Every hit stuns the target like a beanbag and drains their will to fight, so a couple of hits usually end with a suspect on their knees. The damage is a token 0.1 per hit, so even a full magazine won't put anyone down.

**🟠 1911 LL Baton.** It works like the vanilla beanbag, with more punch. Each hit stuns hard and costs a lot of morale. If a suspect still won't comply, 3 body hits put them down (2 up close).

**🟠 LVAR LL Baton.** This one is built for sustained fire. Each hit stuns, but the suspect raises their weapon again within half a second and loses only a little morale. They stay hostile, and you won't close a 10–20 m gap before they recover. Keep firing: about 5 body hits put a suspect down.

> [!WARNING]
> As with the vanilla beanbag, **head shots and point-blank hits** from the heavy guns can still kill. Aim center-mass.

<details>
<summary><b>Numbers under the hood</b></summary>

These were measured on Standard difficulty.

| | |
|---|---|
| Suspect health | 360 |
| Civilian health | 200 |
| Knocked down (incapacitated) at | 50% health or below |
| Stun per rubber hit | ~3 s |
| Morale lost per hit, light guns and 1911 | ~0.2–0.25 |
| Morale lost per hit, LVAR | ~0.1–0.14 |
| Suspect starting morale | 0.65–0.9 |
| LVAR: weapon raised again after | 0.5 s (beanbag: 4 s) |
| Heavy close-range bonus | +25 damage |
| Heavy head-shot damage | ×2, then +50 |

</details>

## Installation

1. Download `pakchunk99-Mods_MoreRubberGuns_P.pak` from the [latest release](https://github.com/RGB-Outl4w/MoreRubberGuns/releases/latest).
2. Copy it to `…\steamapps\common\Ready Or Not\ReadyOrNot\Content\Paks\`.
3. Start the game. Open **Loadout**, then go to **Primary → Less Lethal** or **Secondary → Less Lethal**.

To uninstall, delete the `.pak` file.

> [!IMPORTANT]
> **Multiplayer:** every player in the lobby needs the mod.

## Compatibility

- Built against Ready or Not Steam build **24942528** (September 2026, Unreal Engine 5.3).
- A big game update can break the mod. If it does, rebuild it ([below](#building-from-source)) or wait for an updated release.
- The mod adds new content and also extends a few vanilla files. **Other mods that replace these files will conflict** with it, and whichever loads last wins:

  | File | What this mod adds |
  |---|---|
  | `Blueprints/DataTables/AmmoDataTable` | 4 rubber ammo types |
  | 17 scope blueprints, plus the DLC4 carry-handle sight | Sight alignment for the new guns |
  | 5 DLC4 `*_AttachmentData` assets | Magnifier toggle animations |
  | `Localization/EngineOverrides/ru/EngineOverrides.locres` | Russian texts |

## Building from source

The release `.pak` is generated by `build.py` straight from your installed game. Nothing VOID-owned is stored in this repo. After a game patch you can rebuild against the new files:

```bash
python build.py --install
```

<details>
<summary><b>One-time setup</b></summary>

1. **Requirements:** Windows, [Python 3.10+](https://www.python.org/), and the [.NET 8 Desktop Runtime](https://dotnet.microsoft.com/download/dotnet/8.0).
2. **Tools**, placed in `tools/`:
   - [`repak.exe`](https://github.com/trumank/repak/releases)
   - [`UAssetGUI.exe`](https://github.com/atenfyr/UAssetGUI/releases)
3. **Type mappings:**
   1. Install [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) and start the game.
   2. Press **Ctrl+Numpad6**, which runs UE4SS's `DumpUSMAP`.
   3. Copy the `.usmap` file it writes in `Binaries\Win64\ue4ss\` to `tools\Mappings.usmap`.
   4. Repeat this after major game updates.
4. **Game folder:** found automatically through your Steam libraries. If that fails, set `RON_DIR` to the folder that contains `ReadyOrNot\`.

`python build.py` writes `build/pakchunk99-Mods_MoreRubberGuns_P.pak`, and `--install` also copies it into the game. `python test_build.py` checks the asset-editing logic without needing the game.

</details>

All balance values and texts (English and Russian) live in the `DAMAGE_TYPES`, `AMMO` and `WEAPONS` tables at the top of [`build.py`](build.py):
- `damage`: health damage per hit
- `dt`: stun behaviour
- `velocity`: muzzle velocity, which also sets the projectile speed
- colours, names and descriptions

## How it works

<details>
<summary><b>Technical overview</b></summary>

The build works on cooked game assets directly: no Unreal Editor, no SDK.

1. **Extract:** `repak` unpacks the vanilla weapon blueprints, meshes, materials, damage types and data tables from the game paks. `UAssetGUI` converts them to JSON using the dumped type mappings.
2. **Clone the weapons.** Each gun is a renamed copy of a vanilla blueprint (MK18, MP5A3, LVAR, G19, TLE 1911), so it keeps the original's animations, sockets, sounds and attachment slots. The loadout lists any `BaseItem` blueprint under `/Game`, so the copies show up automatically.
3. **Make them rubber:**
   - New `AmmoDataTable` rows provide the rubber cartridges.
   - The guns fire beanbag-style projectiles instead of hitscan.
   - Damage goes through a less-lethal damage type:
     - **light:** a beanbag clone with no health damage
     - **heavy pistol:** the vanilla beanbag
     - **heavy rifle:** a beanbag clone using the game's *rubberball* stun type, which costs half the morale, and a 0.5 s weapon-down time
4. **Recolour.** The skeletal mesh is cloned with each material swapped for a copy whose base-colour texture is a generated 1×1 blue or orange texture. Normal and roughness maps are kept, which gives a painted Simunition or less-lethal finish.
5. **Align the scopes.** Vanilla scopes store sight offsets per exact weapon class, so each clone gets the offsets of the gun it was cloned from.
6. **Localize.** The Russian strings are merged into the game's own `ru` engine-override locres, written in the legacy format that UE 5.3 still loads.
7. **Pack.** Everything is written back to `.uasset`, re-read to verify it, and packed with `repak` into a `_P` patch pak.

</details>

## Support the project

If you enjoy the mod, you can support its development on **[Boosty](https://boosty.to/rgboutlaw)** ❤️

[![Support on Boosty](https://img.shields.io/badge/Boosty-support%20the%20dev-F15F2C?style=for-the-badge)](https://boosty.to/rgboutlaw)

Bug reports and ideas are welcome in [Issues](https://github.com/RGB-Outl4w/MoreRubberGuns/issues).

## License and credits

- **Code, docs and website:** [MIT](LICENSE) © OutlawRGB.
- **Game content:** *Ready or Not* and all of its assets belong to **VOID Interactive**. The released `.pak` contains modified game data. It is a free, non-commercial fan mod that requires a legitimate copy of the game, and it is not affiliated with or endorsed by VOID Interactive.
- **Built with:**
  - [repak](https://github.com/trumank/repak)
  - [UAssetGUI / UAssetAPI](https://github.com/atenfyr/UAssetGUI)
  - [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)
  - the [Unofficial Ready or Not Modding Guide](https://unofficial-modding-guide.com/)
