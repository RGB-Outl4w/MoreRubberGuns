"""More Rubber Guns: builds a Ready or Not less-lethal weapon pak straight from the game's own files.

    python build.py            -> build/pakchunk99-Mods_MoreRubberGuns_P.pak
    python build.py --install  -> ...and copy it into the game's Paks folder

Needs tools/repak.exe, tools/UAssetGUI.exe and tools/Mappings.usmap (see README).
Each new gun is a clone of a vanilla weapon blueprint (anims, attachment slots, stats) with a
recoloured clone of its mesh, firing a new rubber row in AmmoDataTable through a less-lethal
damage type. Vanilla scopes get sight offsets for the clones; texts get a Russian translation.
"""
import copy, json, os, re, shutil, struct, subprocess, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
OUT = ROOT / "build"
PAKS = None  # game Paks folder, set by main() via find_game()
PAK ="pakchunk99-Mods_MoreRubberGuns_P.pak"  # _P = patch pak; 99 loads after other mods' tables
MOD = "/Game/Mods/MoreRubberGuns"
ROOTS = {"/Game/": "ReadyOrNot/Content/",  # package path prefix -> path inside the game paks
         "/ReadyOrNotDLC4/": "ReadyOrNot/Plugins/GameFeatures/ReadyOrNotDLC4/Content/",
         "/Interchange/": "Engine/Plugins/Interchange/Runtime/Content/"}

WEAPON_DIR = "/Game/Blueprints/Items/WeaponsRevised"
AMMO_TABLE = "/Game/Blueprints/DataTables/AmmoDataTable"
BEANBAG_DT = "/Game/Blueprints/Logic/DamageTypes/BeanbagDamageType"  # vanilla: stun + health damage -> knocks down
STUN_DT = f"{MOD}/DamageTypes/RG_RubberStunDamage"
WHITE_TEX = "/Interchange/gltf/Textures/T_White_srgb"                 # 1x1 sRGB BGRA8 engine texture
TRAIL = "/Game/ReadyOrNot/VFX/VFXImpacts/P_BeanBag_ShootTrail"        # the beanbag's visible projectile trail
LTL_IMPACTS = "/Game/Blueprints/Logic/PepperballImpactEffects"        # beanbag's impacts: no bullet holes or blood
RU_LOCRES = "ReadyOrNot/Content/Localization/EngineOverrides/ru/EngineOverrides.locres"
COLOURS = {"Blue": (0x2F, 0x6F, 0xD6), "Orange": (0xFF, 0x6A, 0x13)}  # RGB

# ---- knobs: every text is (English, Russian) -----------------------------------------------------
# How the game stuns (Binaries/Win64/Difficulty.*, measured in playtests): a hit stuns once it deals
# StunHealth (100) "stun damage"; beanbag and rubberball stun types do 100/hit and stun for ~3 s, costing
# -0.2 / -0.1 morale per hit (suspects start at 0.65-0.9 and surrender when it runs low). The pepperball
# class needs 4 hits and stuns 8 s. Knockdown (incapacitation) happens at <= 50% health.
BATON_DT = f"{MOD}/DamageTypes/RG_BatonDamage"
DAMAGE_TYPES = {  # our package -> (vanilla source, property overrides)
    # light: beanbag stun reaction; health damage comes from the weapon's tiny Damage
    STUN_DT: (BEANBAG_DT, {"bCauseHealthDamage": False, "AdditionalUpcloseDamageIncrease": 0.0,
                           "AdditionalHeadDamageIncrease": 0.0}),
    # heavy AR: beanbag damage, but the rubberball stun type halves the morale hit so suspects stay hostile,
    # and they raise their weapon 0.5 s into the stun (beanbag: 4 s) at full speed
    BATON_DT: (BEANBAG_DT, {"StunType": "ST_Rubberball", "WeaponDownLengthOnStun": 0.5,
                            "MaxMovementSpeedWhenStunned": 1.0, "StunSpeedMultiplier": 1.0}),
}

AMMO = {
    "RG_556_RB": dict(heavy=False, icon="556x45JHP",
                      caliber=("5.56x45mm RB", "5,56x45 мм RB"),
                      variety=("Rubber Stinger", "Резина, оглушающая"),
                      desc=("Low-velocity 5.56mm rubber-tipped round. Stuns on every hit, never wounds.",
                            "Резиновая пуля 5,56 мм пониженной скорости. Оглушает при каждом попадании и никогда не ранит.")),
    "RG_300_Baton": dict(heavy=True, icon="300AACJHP",
                         caliber=(".300 BLK Baton", ".300 BLK «Дубинка»"),
                         variety=("Rubber Baton", "Резина, сбивающая"),
                         desc=("Subsonic .300 Blackout case with a heavy rubber baton. Each hit briefly stuns; "
                               "sustained fire knocks suspects down.",
                               "Дозвуковой патрон .300 Blackout с тяжёлой резиновой пулей. Каждое попадание ненадолго "
                               "оглушает, плотный огонь сбивает с ног.")),
    "RG_9PA": dict(heavy=False, icon="9x19JHP",
                   caliber=("9mm P.A. Rubber", "9 мм Р.А."),
                   variety=("Rubber Stinger", "Резина, оглушающая"),
                   desc=("9mm P.A. (9x22) rubber ball round. Stuns on every hit, never wounds.",
                         "Травматический патрон 9 мм Р.А. (9x22) с резиновой пулей. Оглушает при каждом попадании и никогда не ранит.")),
    "RG_45_Rubber": dict(heavy=True, icon="45JHP",
                         caliber=(".45 Rubber", ".45 Rubber"),
                         variety=("Rubber Baton", "Резина, сбивающая"),
                         desc=(".45 Rubber (11.43x22) heavy rubber ball. Knocks suspects down in 2-3 hits.",
                               "Травматический патрон .45 Rubber (11,43x22) с тяжёлой резиновой пулей. Сбивает с ног за 2-3 попадания.")),
}

LIGHT = ("LIGHT less-lethal: every hit stuns, staggers and pressures the target toward compliance, "
         "but it never wounds or incapacitates, so a full magazine will not put anyone down.",
         "ЛЁГКОЕ нелетальное: каждое попадание оглушает, сбивает прицел и склоняет цель к сдаче, "
         "но никогда не ранит и не выводит из строя - даже полный магазин никого не уложит.")
HEAVY = ("HEAVY less-lethal: rubber baton rounds hit hard enough to knock suspects down and incapacitate them, "
         "wounded but alive. Like the beanbag, head shots and point-blank hits can still kill. Aim center-mass.",
         "ТЯЖЁЛОЕ нелетальное: резиновые пули бьют достаточно сильно, чтобы сбить подозреваемого с ног и вывести "
         "его из строя - раненым, но живым. Как и у травматического дробовика, выстрелы в голову и в упор "
         "могут убить. Цельтесь в корпус.")
HEAVY_AR = ("HEAVY less-lethal, sustained fire: each hit briefly stuns, but suspects recover fast and fight back. "
            "Keep firing to knock them down, wounded but alive. Head shots and point-blank hits can still kill.",
            "ТЯЖЁЛОЕ нелетальное, плотный огонь: каждое попадание ненадолго оглушает, но подозреваемый быстро "
            "приходит в себя и сопротивляется. Продолжайте стрелять, чтобы сбить его с ног - раненым, но живым. "
            "Выстрелы в голову и в упор могут убить.")

# donor = vanilla blueprint in WeaponsRevised; velocity in m/s (also the projectile speed); dt = damage type;
# damage = health damage per hit (beanbag types add +25 up close, +50 and x2 to the head).
# Standard: suspects 360 health, civilians 200; both go down at <= 50%.
WEAPONS = [
    dict(donor="Primary_MK18", name="RG_MK18_Stinger", ammo="RG_556_RB", colour="Blue", velocity=180, barrel="262mm",
         dt=STUN_DT, damage=0.1, effect=LIGHT, title=("MK18 LL Stinger", "MK18 «Стингер» (резина)"),
         blurb=("A Simunition-blue MK18 rebuilt for low-velocity 5.56x45mm RB rubber-tipped rounds.",
                "MK18 в синем учебном исполнении, переделанный под резиновые патроны 5,56x45 мм RB пониженной скорости.")),
    dict(donor="Primary_LVAW", name="RG_LVAR_Baton", ammo="RG_300_Baton", colour="Orange", velocity=260, barrel="140mm",
         dt=BATON_DT, damage=40, effect=HEAVY_AR, title=("LVAR LL Baton", "LVAR «Дубинка» (резина)"),  # suspect: 5 hits
         blurb=("An integrally suppressed LVAR in less-lethal orange, firing subsonic .300 BLK rubber batons.",
                "LVAR с интегрированным глушителем в оранжевом нелетальном исполнении, стреляет дозвуковыми "
                "резиновыми пулями .300 BLK.")),
    dict(donor="Secondary_G19_V2", name="RG_G19_Stinger", ammo="RG_9PA", colour="Blue", velocity=330, barrel="102mm",
         dt=STUN_DT, damage=0.1, effect=LIGHT, title=("G19 LL Stinger", "G19 «Стингер» (резина)"),
         blurb=("A Simunition-blue G19 converted to 9mm P.A. rubber rounds.",
                "G19 в синем учебном исполнении, переделанный под травматический патрон 9 мм Р.А.")),
    dict(donor="Secondary_Kimber1911", name="RG_1911_Baton", ammo="RG_45_Rubber", colour="Orange", velocity=220,
         barrel="127mm", dt=BEANBAG_DT, damage=65, effect=HEAVY,  # suspect: 3 hits (2 up close); civilian: 2
         title=("1911 LL Baton", "1911 «Дубинка» (резина)"),
         blurb=("A TLE 1911 in less-lethal orange, chambered for heavy .45 Rubber rounds.",
                "TLE 1911 в оранжевом нелетальном исполнении под тяжёлый травматический патрон .45 Rubber.")),
    dict(donor="Primary_MP5A3", name="RG_MP5_Stinger", ammo="RG_9PA", colour="Blue", velocity=350, barrel="225mm",
         dt=STUN_DT, damage=0.1, effect=LIGHT, title=("MP5 LL Stinger", "MP5 «Стингер» (резина)"),
         blurb=("A Simunition-blue MP5A3 feeding 9mm P.A. rubber rounds.",
                "MP5A3 в синем учебном исполнении под травматический патрон 9 мм Р.А.")),
]

LOC = {}  # text key -> (English source, Russian)


# ---- pure JSON helpers (UAssetAPI JSON as written by `UAssetGUI tojson`) ----------------------------
def rename(o, mapping):
    """Rewrite every string equal to a mapping key, and every object path that starts with '<key>.'."""
    if isinstance(o, dict):
        return {k: rename(v, mapping) for k, v in o.items()}
    if isinstance(o, list):
        return [rename(v, mapping) for v in o]
    if isinstance(o, str):
        if o in mapping:
            return mapping[o]
        head, dot, tail = o.partition(".")
        if dot and head in mapping:
            return mapping[head] + "." + rename(tail, mapping)
    return o


def clone_package(asset, old_pkg, new_pkg):
    """Move an asset to new_pkg: package path, asset name, BP class and its CDO all follow.

    The bare asset name is only renamed on exports: it can also be a native parent class
    (BeanbagDamageType_C's parent is /Script/ReadyOrNot.BeanbagDamageType). Old names stay
    in the name map for the same reason; new ones are added.
    """
    old, new = old_pkg.rsplit("/", 1)[1], new_pkg.rsplit("/", 1)[1]
    mapping = {old_pkg: new_pkg, f"{old}_C": f"{new}_C", f"Default__{old}_C": f"Default__{new}_C"}
    names = asset["NameMap"]
    out = rename({k: v for k, v in asset.items() if k != "NameMap"}, mapping)
    for e in out["Exports"]:
        if e["ObjectName"] == old:
            e["ObjectName"] = new
    out["NameMap"] = list(names)
    for s in (*mapping.values(), new):
        add_name(out, s)
    return out


def add_name(asset, s):
    if s not in asset["NameMap"]:
        asset["NameMap"].append(s)
    return s


def add_import(asset, pkg, obj, cls, cls_pkg="/Script/Engine"):
    """Index (negative) of the import pkg.obj, created along with its package import if missing."""
    imps = asset["Imports"]

    def find_or_add(name, outer, class_name, class_pkg):
        for i, im in enumerate(imps, 1):
            if im["ObjectName"] == name and im["OuterIndex"] == outer and im["ClassName"] == class_name:
                return -i
        for s in (name, class_name, class_pkg):
            add_name(asset, s)
        imps.append({"$type": "UAssetAPI.Import, UAssetAPI", "ObjectName": name, "OuterIndex": outer,
                     "ClassPackage": class_pkg, "ClassName": class_name, "PackageName": None, "bImportOptional": False})
        return -len(imps)

    return find_or_add(obj, find_or_add(pkg, 0, "Package", "/Script/CoreUObject"), cls, cls_pkg)


def retarget_import(asset, index, new_pkg):
    """Point import `index` (and its package import) at the same-named object in new_pkg."""
    im = asset["Imports"][-index - 1]
    asset["Imports"][-im["OuterIndex"] - 1]["ObjectName"] = add_name(asset, new_pkg)
    im["ObjectName"] = add_name(asset, new_pkg.rsplit("/", 1)[1])


def import_package(asset, index):
    return asset["Imports"][-asset["Imports"][-index - 1]["OuterIndex"] - 1]["ObjectName"]


def export(asset, name):
    return next(e for e in asset["Exports"] if e["ObjectName"] == name)


def cdo(asset):
    return next(e for e in asset["Exports"] if e["ObjectName"].startswith("Default__"))


def get(props, name):
    return next((p for p in props if p["Name"] == name), None)


def set_prop(props, p):
    """Replace the property with p's name, or append it (UAssetAPI orders unversioned props itself)."""
    for i, old in enumerate(props):
        if old["Name"] == p["Name"]:
            props[i] = p
            return
    props.append(p)


def _p(kind, name, value, **extra):
    return {"$type": f"UAssetAPI.PropertyTypes.Objects.{kind}PropertyData, UAssetAPI", **extra, "Name": name,
            "ArrayIndex": 0, "PropertyGuid": None, "IsZero": not value, "PropertyTagFlags": "None",
            "PropertyTypeName": None, "PropertyTagExtensions": "NoExtension", "Value": value}


def p_float(name, v): return _p("Float", name, float(v))
def p_bool(name, v): return _p("Bool", name, bool(v))
def p_str(name, v): return _p("Str", name, v)
def p_obj(name, index): return _p("Object", name, index)
def p_enum(name, enum, v): return _p("Enum", name, v, EnumType=enum, InnerType="ByteProperty")


def p_soft(asset, name, pkg, obj):
    return _p("SoftObject", name, {
        "$type": "UAssetAPI.PropertyTypes.Objects.FSoftObjectPath, UAssetAPI",
        "AssetPath": {"$type": "UAssetAPI.PropertyTypes.Objects.FTopLevelAssetPath, UAssetAPI",
                      "PackageName": add_name(asset, pkg), "AssetName": add_name(asset, obj)}, "SubPathString": None})


def p_text(asset, name, key, text):
    """Localizable text: English source string, Russian via our locres entry (LOC)."""
    LOC[key] = text
    for v in ("MoreRubberGuns", key):
        add_name(asset, v)
    return _p("Text", name, key, Flags=0, HistoryType="Base", Namespace="MoreRubberGuns",
              CultureInvariantString=text[0], SourceFmt=None, Arguments=None, ArgumentsData=None,
              TransformType="ToLower", SourceValue=None, FormatOptions=None, TargetCulture=None)


def p_array(name, inner, items):
    return _p("Array", name, [dict(it, Name=str(i)) for i, it in enumerate(items)], ArrayType=inner)


def add_row(table, template, new_name, props):
    """Copy DataTable row `template` as `new_name` with `props` (property dicts) replaced."""
    rows = table["Exports"][0]["Table"]["Data"]
    row = copy.deepcopy(next(r for r in rows if r["Name"] == template))
    row["Name"] = add_name(table, new_name)
    for p in props:
        set_prop(row["Value"], p)
    rows[:] = [r for r in rows if r["Name"] != new_name] + [row]
    return row


def add_weapon_entries(entries, key, pairs, asset):
    """For every entry whose soft weapon path (key(entry)) is a donor, append a copy for its clone."""
    added = []
    for donor_pkg, new_pkg in pairs:
        for e in [e for e in entries if key(e)["PackageName"] == donor_pkg]:
            n = copy.deepcopy(e)
            key(n)["PackageName"] = add_name(asset, new_pkg)
            key(n)["AssetName"] = add_name(asset, new_pkg.rsplit("/", 1)[1] + "_C")
            added.append(n)
    entries += added
    for i, e in enumerate(entries):
        e["Name"] = str(i)
    return len(added)


# ---- locres (UE text localization) --------------------------------------------------------------
def source_hash(s):
    """FCrc::StrCrc32: CRC32 over the string as 4-byte chars."""
    return zlib.crc32(s.encode("utf-32-le"))


def _fstring(b, o):
    n, = struct.unpack_from("<i", b, o)
    if n < 0:
        return b[o + 4:o + 4 - 2 * n - 2].decode("utf-16-le"), o + 4 - 2 * n
    return b[o + 4:o + 3 + n].decode("latin-1") if n else "", o + 4 + n


def read_locres(b):
    """{(namespace, key): (source hash, translation)} from a .locres (legacy or v1-v3)."""
    ver, o = 0, 0
    if b[:16] == bytes.fromhex("0e147475674a03fc4a15909dc3377f1b"):  # LocResMagic; legacy files have none
        ver, o = b[16], 17
    strings = None
    if ver >= 1:
        at, = struct.unpack_from("<q", b, o)
        o += 8
        count, p = struct.unpack_from("<i", b, at)[0], at + 4
        strings = []
        for _ in range(count):
            s, p = _fstring(b, p)
            strings.append(s)
            p += 4 if ver >= 2 else 0  # ref count
        o += 4 if ver >= 2 else 0      # entries count
    out = {}
    namespaces, = struct.unpack_from("<i", b, o)
    o += 4
    for _ in range(namespaces):
        o += 4 if ver >= 2 else 0
        ns, o = _fstring(b, o)
        keys, = struct.unpack_from("<i", b, o)
        o += 4
        for _ in range(keys):
            o += 4 if ver >= 2 else 0
            key, o = _fstring(b, o)
            h, = struct.unpack_from("<I", b, o)
            o += 4
            if strings is None:
                s, o = _fstring(b, o)
            else:
                s, o = strings[struct.unpack_from("<i", b, o)[0]], o + 4
            out[(ns, key)] = (h, s)
    return out


def write_locres(entries):
    """Legacy .locres (no magic/hashes): still loaded by UE5 and needs no CityHash."""
    def fs(s):  # always UTF-16 (negative length); UE reads it for ASCII too
        u = s.encode("utf-16-le")
        return struct.pack("<i", -(len(u) // 2 + 1)) + u + b"\0\0"

    by_ns = {}
    for (ns, key), v in entries.items():
        by_ns.setdefault(ns, {})[key] = v
    out = [struct.pack("<i", len(by_ns))]
    for ns, keys in by_ns.items():
        out += [fs(ns), struct.pack("<i", len(keys))]
        for key, (h, s) in keys.items():
            out += [fs(key), struct.pack("<I", h), fs(s)]
    return b"".join(out)


# ---- tools ---------------------------------------------------------------------------------------
def run(*args, binary=False):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=not binary)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(map(str, args))}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def find_game():
    """RON_DIR if set, else the Steam library that actually holds the game's paks."""
    if os.environ.get("RON_DIR"):
        return Path(os.environ["RON_DIR"])
    steam = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam"
    vdf = steam / "steamapps/libraryfolders.vdf"
    paths = re.findall(r'"path"\s+"([^"]+)"', vdf.read_text()) if vdf.exists() else []
    for lib in [steam, *(Path(p.replace("\\\\", "\\")) for p in paths)]:
        game = lib / "steamapps/common/Ready Or Not"
        if (game / "ReadyOrNot/Content/Paks/pakchunk0-Windows.pak").exists():
            return game
    sys.exit("Ready or Not not found: set RON_DIR to the game folder (the one containing ReadyOrNot/)")


def disk_path(pkg):
    root = next(r for r in ROOTS if pkg.startswith(r))
    return ROOTS[root] + pkg[len(root):]


def pak_index():
    cache = OUT / "pak_index.json"
    if cache.exists():
        return json.loads(cache.read_text())
    index = {}
    for pak in sorted(PAKS.glob("pakchunk*-Windows.pak")):
        for line in run(TOOLS / "repak.exe", "list", pak).splitlines():
            index.setdefault(line.strip(), pak.name)
    OUT.mkdir(exist_ok=True)
    cache.write_text(json.dumps(index))
    return index


def extract(pkgs):
    """Unpack the packages' .uasset/.uexp/.ubulk from the game paks into build/raw."""
    index, by_pak = pak_index(), {}
    for pkg in pkgs:
        base = disk_path(pkg)
        if base + ".uasset" not in index:
            sys.exit(f"not in game paks: {pkg}")
        for ext in (".uasset", ".uexp", ".ubulk"):
            if base + ext in index:
                by_pak.setdefault(index[base + ext], []).append(base + ext)
    for pak, files in by_pak.items():
        run(TOOLS / "repak.exe", "unpack", "-q", "-f", "-o", OUT / "raw",
            *[a for f in files for a in ("-i", f)], PAKS / pak)


def load(pkg):
    src, dst = OUT / "raw" / (disk_path(pkg) + ".uasset"), OUT / "json" / (pkg.rsplit("/", 1)[1] + ".json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(TOOLS / "UAssetGUI.exe", "tojson", src, dst, "VER_UE5_3", "RoN")
    return json.loads(dst.read_text(encoding="utf-8"))


def save(asset, pkg):
    """Write asset into the pak staging tree and prove it reads back (UAssetGUI fails silently)."""
    dst = OUT / "stage" / (disk_path(pkg) + ".uasset")
    dst.parent.mkdir(parents=True, exist_ok=True)
    js = OUT / "json" / (pkg.rsplit("/", 1)[1] + ".out.json")
    check = js.with_suffix(".check.json")
    check.unlink(missing_ok=True)
    js.write_text(json.dumps(asset), encoding="utf-8")
    run(TOOLS / "UAssetGUI.exe", "fromjson", js, dst, "RoN")
    run(TOOLS / "UAssetGUI.exe", "tojson", dst, check, "VER_UE5_3", "RoN")
    if not check.exists() or json.loads(check.read_text(encoding="utf-8"))["FolderName"] != pkg:
        sys.exit(f"UAssetGUI could not write {pkg} (see {js})")
    return dst


def install_mappings():
    dst = Path(os.environ["LOCALAPPDATA"]) / "UAssetGUI/Mappings/RoN.usmap"
    if not (TOOLS / "Mappings.usmap").exists():
        sys.exit("tools/Mappings.usmap missing: dump it with UE4SS (README, step 1)")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TOOLS / "Mappings.usmap", dst)


# ---- build steps ---------------------------------------------------------------------------------
def build_textures():
    tex = {}
    for colour, (r, g, b) in COLOURS.items():
        pkg = f"{MOD}/Textures/T_RG_{colour}"
        uexp = save(clone_package(load(WHITE_TEX), WHITE_TEX, pkg), pkg).with_suffix(".uexp")
        data = uexp.read_bytes()
        assert data.count(b"\xff\xff\xff\xff") == 1, "white pixel not found exactly once"
        uexp.write_bytes(data.replace(b"\xff\xff\xff\xff", bytes((b, g, r, 0xFF))))  # BGRA
        tex[colour] = pkg
    return tex


def build_damage_types():
    for pkg, (src, overrides) in DAMAGE_TYPES.items():
        dt = clone_package(load(src), src, pkg)
        for name, v in overrides.items():
            p = (p_bool(name, v) if isinstance(v, bool) else p_float(name, v) if isinstance(v, float)
                 else p_enum(name, "EStunType", v))
            set_prop(cdo(dt)["Data"], p)
        save(dt, pkg)


def build_ammo_table():
    table = load(AMMO_TABLE)
    rows = {r["Name"]: r for r in table["Exports"][0]["Table"]["Data"]}
    for name, a in AMMO.items():
        add_row(table, "12gaBeanbag", name, [
            p_text(table, "AmmoVariety", f"{name}_Variety", a["variety"]),
            p_text(table, "AmmoCaliber", f"{name}_Caliber", a["caliber"]),
            p_text(table, "AmmoDescription", f"{name}_Desc", a["desc"]),
            copy.deepcopy(get(rows[a["icon"]]["Value"], "LoadoutIcon")),
        ])
    save(table, AMMO_TABLE)


def build_mesh(w, mesh_pkg, tex_pkg):
    """Clone the donor mesh with each material swapped for a recoloured clone (base texture -> flat colour).

    Done on the mesh asset, not as component OverrideMaterials: the game rebuilds weapon
    materials from the mesh and drops component overrides.
    """
    extract([mesh_pkg])
    new_pkg = f"{MOD}/Meshes/SK_{w['name']}"
    mesh = clone_package(load(mesh_pkg), mesh_pkg, new_pkg)
    mats = [i for i, im in enumerate(mesh["Imports"], 1) if im["ClassName"] == "MaterialInstanceConstant"]
    for letter, i in zip("ABCDEFGH", mats):  # letters: names ending in _<digits> become FName numbers
        src = import_package(mesh, -i)
        dst = f"{MOD}/Materials/MI_{w['name']}_{letter}"
        extract([src])
        mi = clone_package(load(src), src, dst)
        params = get(export(mi, dst.rsplit("/", 1)[1])["Data"], "TextureParameterValues")["Value"]
        base = next(p for p in params if get(p["Value"], "ParameterInfo")["Value"][0]["Value"] == "B")
        get(base["Value"], "ParameterValue")["Value"] = add_import(mi, tex_pkg, tex_pkg.rsplit("/", 1)[1], "Texture2D")
        save(mi, dst)
        retarget_import(mesh, -i, dst)
    save(mesh, new_pkg)
    return new_pkg


def build_weapon(w, tex):
    a = AMMO[w["ammo"]]
    donor_pkg, pkg = f"{WEAPON_DIR}/{w['donor']}", f"{MOD}/Weapons/{w['name']}"
    bp = clone_package(load(donor_pkg), donor_pkg, pkg)
    props = cdo(bp)["Data"]
    secondary = get(props, "Subclass")["Value"] == "WS_Pistol"
    dt_idx = add_import(bp, w["dt"], w["dt"].rsplit("/", 1)[1] + "_C", "BlueprintGeneratedClass")
    capacity = int(get(props, "AmmoMax")["Value"])
    auto = len(get(props, "AvailableFireModes")["Value"]) > 1
    effect = w["effect"]
    desc = (f"{w['blurb'][0]}\r\n\r\n{effect[0]}\r\n\r\nCaliber: {a['caliber'][0]} | {capacity} rds | "
            f"{'Semi/Auto' if auto else 'Semi'} | ~{w['velocity']} m/s",
            f"{w['blurb'][1]}\r\n\r\n{effect[1]}\r\n\r\nКалибр: {a['caliber'][1]} | {capacity} патр. | "
            f"{'одиночный/автомат' if auto else 'одиночный'} | ~{w['velocity']} м/с")

    for p in (
        p_text(bp, "ItemName", f"{w['name']}_Name", w["title"]),
        p_text(bp, "ItemDescription", f"{w['name']}_Desc", desc),
        p_text(bp, "RoundSize", f"{w['ammo']}_Caliber", a["caliber"]),
        _p("Name", "LookupTableIdx", add_name(bp, w["name"])),
        p_bool("bShowInLoadout", True),
        # less-lethal tabs + flags, as on the vanilla beanbag (primary) and taser (secondary)
        p_enum("Subclass", "EWeaponSubclass", "WS_LessLethal_Secondary" if secondary else "WS_LessLethal"),
        p_array("AmmunitionTypes", "NameProperty", [_p("Name", "0", add_name(bp, w["ammo"]))]),
        p_obj("DefaultDamageType", dt_idx),
        p_obj("ArmorPiercingDamageType", dt_idx),
        p_float("Damage", w["damage"]),
        p_bool("bDrawBlood", False),
        p_bool("bADSCountsAsAbuse", False),
        # slow projectile with the beanbag's trail instead of hitscan: you can see where you shot
        p_bool("bHitScan", False),
        p_bool("bNoSpawnTracerForFiringPlayer", False),
        p_float("ProjectileMovementSpeed", w["velocity"] * 100),
        p_obj("ProjectileAttachedParticle", add_import(bp, TRAIL, TRAIL.rsplit("/", 1)[1], "ParticleSystem")),
        p_soft(bp, "ImpactEffects", LTL_IMPACTS, LTL_IMPACTS.rsplit("/", 1)[1] + "_C"),
        p_str("CartridgeText", a["caliber"][0]),
        p_str("CapacityText", f"{capacity} rounds"),
        p_str("BarrelLengthText", w["barrel"]),
        p_str("MuzzleVelocityText", f"~{w['velocity']} m/s"),
    ):
        set_prop(props, p)
    if not secondary:
        set_prop(props, p_enum("WeaponType", "EWeaponType", "WT_PrimaryNonLethal"))

    attachments = {}
    for p in props:  # rubber rounds + suppressor makes no sense; drop them, keep everything else
        if p["Name"].startswith("Available") and p["Name"].endswith("Attachments"):
            p["Value"] = [v for v in p["Value"] if "Suppress" not in v["Value"]["AssetPath"]["AssetName"]]
            for i, v in enumerate(p["Value"]):
                v["Name"] = str(i)
            attachments[p["Name"][9:-11]] = [v["Value"]["AssetPath"]["PackageName"] for v in p["Value"]
                                             if not v["Value"]["AssetPath"]["AssetName"].startswith(("Null_", "No"))]

    mesh_idx = get(export(bp, "ItemMesh")["Data"], "SkeletalMesh")["Value"]
    retarget_import(bp, mesh_idx, build_mesh(w, import_package(bp, mesh_idx), tex[w["colour"]]))
    save(bp, pkg)
    return donor_pkg, pkg, attachments


def patch_scopes(built):
    """Vanilla scopes keep sight offsets per exact weapon class: give each clone its donor's offsets."""
    by_scope = {}
    for donor, new, att in built:
        for scope in att.get("Scope", []):
            by_scope.setdefault(scope, []).append((donor, new))
    extract(by_scope)
    for scope, pairs in by_scope.items():
        asset = load(scope)
        mods = get(cdo(asset)["Data"], "ScopeMods")
        if mods and add_weapon_entries(mods["Value"], lambda m: get(m["Value"], "WeaponClass")["Value"]["AssetPath"],
                                       pairs, asset):
            save(asset, scope)


def patch_attachment_anims(built):
    """Magnifier/flip-up toggle animations list their weapons too (WeaponAttachmentAnimData.ParentWeapons)."""
    pairs = [(donor, new) for donor, new, _ in built]
    pkgs = [r + d[len(ROOTS[r]):-len(".uasset")] for d in pak_index() if d.endswith("AttachmentData.uasset")
            for r in ROOTS if d.startswith(ROOTS[r])]
    extract(pkgs)
    for pkg in pkgs:
        asset = load(pkg)
        parents = get(export(asset, pkg.rsplit("/", 1)[1])["Data"], "ParentWeapons")
        if parents and add_weapon_entries(parents["Value"], lambda e: e["Value"]["AssetPath"], pairs, asset):
            save(asset, pkg)


def build_locres():
    """Russian: the game's own ru EngineOverrides entries plus ours (UE loads one locres per target)."""
    game = read_locres(run(TOOLS / "repak.exe", "get", PAKS / pak_index()[RU_LOCRES], RU_LOCRES, binary=True))
    ours = {("MoreRubberGuns", k): (source_hash(en), ru) for k, (en, ru) in LOC.items()}
    dst = OUT / "stage" / RU_LOCRES
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(write_locres({**game, **ours}))
    assert read_locres(dst.read_bytes()) == {**game, **ours}


def main():
    global PAKS
    PAKS = find_game() / "ReadyOrNot/Content/Paks"
    install_mappings()
    shutil.rmtree(OUT / "stage", ignore_errors=True)
    extract([WHITE_TEX, AMMO_TABLE, *{src for src, _ in DAMAGE_TYPES.values()},
             *{f"{WEAPON_DIR}/{w['donor']}" for w in WEAPONS}])
    tex = build_textures()
    build_damage_types()
    build_ammo_table()
    built = []
    for w in WEAPONS:
        built.append(build_weapon(w, tex))
        print(f"{w['title'][0]:16} {AMMO[w['ammo']]['caliber'][0]:16} " +
              "; ".join(f"{k}: {', '.join(p.rsplit('/', 1)[1] for p in v)}" for k, v in built[-1][2].items() if v))
    patch_scopes(built)
    patch_attachment_anims(built)
    build_locres()
    pak = OUT / PAK
    pak.unlink(missing_ok=True)
    run(TOOLS / "repak.exe", "pack", "--version", "V11", OUT / "stage", pak)
    print(f"built {pak} ({pak.stat().st_size // 1024} KB)")
    if "--install" in sys.argv:
        shutil.copyfile(pak, PAKS / PAK)
        print(f"installed -> {PAKS / PAK}")


if __name__ == "__main__":
    main()
