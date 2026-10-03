"""One check for build.py's asset/locres surgery, on tiny fixtures (no game or tools needed): python test_build.py"""
from build import (add_import, add_row, add_weapon_entries, cdo, clone_package, read_locres, retarget_import,
                   source_hash, write_locres)

OLD, NEW = "/Game/Blueprints/Items/WeaponsRevised/Primary_X", "/Game/Mods/MoreRubberGuns/Weapons/RG_X"
bp = {
    "NameMap": [OLD, "Primary_X", "Primary_X_C", "Default__Primary_X_C", "X_Lookup"],
    "FolderName": OLD,
    "Imports": [{"ObjectName": "Primary_X", "ClassName": "Class", "OuterIndex": 0}],  # native parent, same name
    "Exports": [{"ObjectName": "Primary_X_C", "Data": []},
                {"ObjectName": "Default__Primary_X_C",
                 "Data": [{"Name": "LookupTableIdx", "Value": "X_Lookup"},
                          {"Name": "Soft", "Value": {"PackageName": OLD, "AssetName": "Primary_X_C"}},
                          {"Name": "Path", "Value": f"{OLD}.Primary_X_C"}]}],
}
c = clone_package(bp, OLD, NEW)
assert "Primary_X" not in str(c["Exports"]) + c["FolderName"], c  # no donor package/class/CDO name survives
assert c["Imports"][0]["ObjectName"] == "Primary_X"               # ...but a native class of that name does
assert {NEW, "RG_X_C", "Default__RG_X_C", "Primary_X"} <= set(c["NameMap"])
assert c["FolderName"] == NEW and cdo(c)["ObjectName"] == "Default__RG_X_C"
assert cdo(c)["Data"][2]["Value"] == f"{NEW}.RG_X_C"
assert cdo(c)["Data"][0]["Value"] == "X_Lookup"                    # unrelated names untouched
assert bp["FolderName"] == OLD                                     # donor dict not mutated

i = add_import(c, "/Game/Pkg/SK_Gun", "SK_Gun", "SkeletalMesh")
assert i == -3 and c["Imports"][2]["OuterIndex"] == -2 and c["Imports"][1]["ClassName"] == "Package"
assert add_import(c, "/Game/Pkg/SK_Gun", "SK_Gun", "SkeletalMesh") == i  # reused, not duplicated
retarget_import(c, i, "/Game/Mods/SK_Orange")
assert [im["ObjectName"] for im in c["Imports"][1:]] == ["/Game/Mods/SK_Orange", "SK_Orange"]

table = {"NameMap": ["Beanbag"], "Exports": [{"Table": {"Data": [
    {"Name": "Beanbag", "Value": [{"Name": "Damage", "Value": 5.0}, {"Name": "Icon", "Value": -1}]}]}}]}
add_row(table, "Beanbag", "RG_Rubber", [{"Name": "Damage", "Value": 3.0}])
add_row(table, "Beanbag", "RG_Rubber", [{"Name": "Damage", "Value": 2.0}])  # rebuilding replaces, never duplicates
rows = {r["Name"]: r["Value"] for r in table["Exports"][0]["Table"]["Data"]}
assert list(rows) == ["Beanbag", "RG_Rubber"] and "RG_Rubber" in table["NameMap"]
assert rows["RG_Rubber"] == [{"Name": "Damage", "Value": 2.0}, {"Name": "Icon", "Value": -1}]
assert rows["Beanbag"][0]["Value"] == 5.0

# scope offsets: donor entry duplicated for the clone, other weapons' entries left alone, names renumbered
mods = [{"Name": "0", "Value": {"PackageName": "/W/Other", "AssetName": "Other_C"}},
        {"Name": "1", "Value": {"PackageName": "/W/Donor", "AssetName": "Donor_C"}, "Offset": 3}]
assert add_weapon_entries(mods, lambda m: m["Value"], [("/W/Donor", "/Mod/RG_Y")], c) == 1
assert mods[2] == {"Name": "2", "Value": {"PackageName": "/Mod/RG_Y", "AssetName": "RG_Y_C"}, "Offset": 3}
assert mods[1]["Value"]["PackageName"] == "/W/Donor" and "RG_Y_C" in c["NameMap"]

# locres: legacy writer round-trips, Cyrillic included; hash is UE's StrCrc32 (verified on the game's en locres)
loc = {("MoreRubberGuns", "RG_X_Name"): (source_hash("MP5 LL Stinger"), "MP5 «Стингер» (резина)"),
       ("Game", "Ok"): (source_hash("OK"), "ОК")}
assert read_locres(write_locres(loc)) == loc
assert source_hash("Please Wait") == 0xC7A4BC45  # BuildPatchInstaller_GenericProgress in the game's en locres
print("ok")
