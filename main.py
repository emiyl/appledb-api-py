import json
import jsonpickle
import time
from typing import Any
from pathlib import Path

class OsEntry:
    osStr: str = ""
    version: str = ""
    safariVersion: list[str] = []
    build: str = ""
    key: str = ""
    embeddedOSBuild: str = ""
    bridgeOSBuild: str = ""
    buildTrain: str = ""
    released: str = ""

    rc: bool = False
    beta: bool = False
    rsr: bool = False
    internal: bool = False
    sdk: bool = False

    class AppleDBInfo:
        class WebImage:
            id: str = ""
            align: str = "left"
        webImage: WebImage
        webUrl: str = ""
        apiUrl: str = ""
        hideFromLatestVersions: bool = False
    appledb: AppleDBInfo

    preinstalled: list[str] = []
    notes: str = ""
    releaseNotes: str = ""
    securityNotes: str = ""
    ipd: dict[str, str] = {}
    deviceMap: list[str] = []
    osMap: list[str] = []

    class Source:
        type: str
        prerequisiteBuild: list[str] = []
        deviceMap: list[str] = []
        osMap: list[str] = []
        
        class WindowsUpdateDetails:
            updateId: str = ""
            revisionId: str = ""
        windows_update_details: WindowsUpdateDetails

        class Link:
            url: str = ""
            active: bool = False
        links: list[Link]

        hashes: dict[str, str] = {}
        skipUpdateLinks: bool = False
        size: int = 0
    sources: list[Source]

def open_file_to_str(file_path: Path) -> str:
    with open(file_path, 'r') as file:
        data = file.read()
    return data

def open_json(file_path: Path) -> dict:
    json_str: str = open_file_to_str(file_path)
    return json.loads(json_str)

def write_str_to_file(file_path: Path, input_str: str) -> bool:
    with open(file_path, 'w') as file:
        file.write(input_str)
    return True

def write_to_json(file_path: Path, data: Any) -> bool:
    json_str = jsonpickle.encode(data, unpicklable=False)
    return write_str_to_file(file_path, json_str)

def get_val_from_dict(in_dict: dict, key: str) -> Any:
    keys: list = [*in_dict.keys()]
    if keys.__contains__(key): return in_dict[key]
    return None

def get_val_from_list(in_list: list, item: int) -> Any:
    length: int = in_list.__len__()
    if item < length: return in_list[item]
    return None

def get_val(a: Any, b: Any, expected_type: type) -> Any:
    if type(a) == dict and type(b) == str:
        ret = get_val_from_dict(a, b)
    if type(a) == list and type(b) == int:
        ret = get_val_from_list(a, b)
    if type(ret) == None or type(ret) != expected_type:
        #if type(ret) != expected_type: print("Expected type {}, got type {}".format(expected_type, type(ret)))
        if expected_type == str: return ""
        if expected_type == int: return 0
        if expected_type == bool: return False
        if expected_type == dict: return {}
        if expected_type == list: return []
        return None
    return ret

def get_type(a: Any, b:Any) -> type:
    if type(a) == dict and type(b) == str:
        return type(get_val_from_dict(a, b))
    if type(a) == list and type(b) == int:
        return type(get_val_from_list(a, b))
    return type(None)

def get_os_entry_from_dict(input_dict: dict) -> OsEntry:
    os_str = get_val(input_dict, "osStr", str)
    version = get_val(input_dict, "version", str)
    build = get_val(input_dict, "build", str)
    key = get_val(input_dict, "key", str)
    
    unique_build = get_val(input_dict, "uniqueBuild", str)
    key = "{};{}".format(os_str, key or unique_build or build or version)

    entry = OsEntry()
    
    attr_list: list = [*filter(lambda attr: not attr.startswith('__'), dir(OsEntry))]
    for attr in attr_list:
        match attr:
            case "key":
                entry.key = key

            case "osStr":
                entry.osStr = get_val(input_dict, attr, str)
            case "version":
                entry.version = get_val(input_dict, attr, str)
            case "safariVersion":
                entry.safariVersion = get_val(input_dict, attr, list)
            case "build":
                entry.build = get_val(input_dict, attr, str)
            case "embeddedOSBuild":
                entry.embeddedOSBuild = get_val(input_dict, attr, str)
            case "bridgeOSBuild":
                entry.bridgeOSBuild = get_val(input_dict, attr, str)
            case "buildTrain":
                entry.buildTrain = get_val(input_dict, attr, str)
            case "notes":
                entry.notes = get_val(input_dict, attr, str)
            case "securityNotes":
                entry.securityNotes = get_val(input_dict, attr, str)

            case "rc":
                entry.rc = get_val(input_dict, attr, bool)
            case "beta":
                entry.beta = get_val(input_dict, attr, bool)
            case "rsr":
                entry.rsr = get_val(input_dict, attr, bool)
            case "internal":
                entry.internal = get_val(input_dict, attr, bool)
            case "sdk":
                entry.sdk = get_val(input_dict, attr, bool)

            case "ipd":
                entry.ipd = get_val(input_dict, attr, dict)
            case "deviceMap":
                entry.deviceMap = get_val(input_dict, attr, list)
            case "osMap":
                entry.osMap = get_val(input_dict, attr, list)
                
            case "released":
                released = get_val(input_dict, attr, str)
                if released == "":
                    released = "1970-01-01"
                entry.released = released
            case "AppleDBInfo":
                appledb = OsEntry.AppleDBInfo()
                web_image = OsEntry.AppleDBInfo.WebImage()

                image_obj = get_val(input_dict, "appledbWebImage", dict)
                web_image.id = get_val(image_obj, "id", str)
                web_image_align = get_val(image_obj, "align", str)
                if not web_image_align: web_image_align = "left"

                appledb.webImage = image_obj
                appledb.webUrl = "https://appledb.dev/firmware/{}.html".format(key.replace(';','/'))
                appledb.apiUrl = "https://api.appledb.dev/firmware/{}.json".format(key.replace(';','/'))
                appledb.hideFromLatestVersions = get_val(input_dict, "hideFromLatestVersions", bool)
                
                entry.appledb = appledb
            case "preinstalled":
                preinstalled_type: type = get_type(input_dict, attr)
                if preinstalled_type == bool:
                    entry.preinstalled = get_val(input_dict, "deviceMap", list)
                    continue
                if preinstalled_type == list:
                    entry.preinstalled = get_val(input_dict, attr, list)
                    continue
                entry.preinstalled = []
            case "Source":
                input_source_list: list = get_val(input_dict, "sources", list)
                output_source_list = []
                source_attr_list: list = [*filter(lambda attr: not attr.startswith('__'), dir(OsEntry.Source))]
                for input_source in input_source_list:
                    output_source = OsEntry.Source()
                    for source_attr in source_attr_list:
                        match source_attr:
                            case "type":
                                output_source.type = get_val(input_source, source_attr, str)
                            case "prerequisiteBuild":
                                prerequisite_build_type = get_type(input_source, source_attr)
                                if prerequisite_build_type == list:
                                    output_source.prerequisiteBuild = get_val(input_source, source_attr, list)
                                    continue
                                if prerequisite_build_type == str:
                                    output_source.prerequisiteBuild = [get_val(input_source, source_attr, str)]
                                    continue
                                output_source.prerequisiteBuild = []
                            case "deviceMap":
                                output_source.deviceMap = get_val(input_source, source_attr, list)
                            case "osMap":
                                output_source.osMap = get_val(input_source, source_attr, list)
                            case "WindowsUpdateDetails":
                                output_wud = OsEntry.Source.WindowsUpdateDetails()
                                input_wud = get_val(input_source, "windowsUpdateDetails", dict)

                                output_wud.updateId = get_val(input_wud, "updateId", str)
                                output_wud.revisionId = get_val(input_wud, "revisionID", str)
                                output_source.windows_update_details = output_wud
                            case "Link":
                                output_link_list: list[OsEntry.Source.Link] = []
                                input_link_list = get_val(input_source, "links", list)
                                for input_link in input_link_list:
                                    output_link = OsEntry.Source.Link()
                                    output_link.url = get_val(input_link, "url", str)
                                    output_link.active = get_val(input_link, "Active", bool)
                                    output_link_list.append(output_link)
                                output_source.links = output_link_list
                            case "hashes":
                                output_source.hashes = get_val(input_source, source_attr, dict)
                            case "skipUpdateLinks":
                                output_source.skipUpdateLinks = get_val(input_source, source_attr, bool)
                            case "size":
                                output_source.size = get_val(input_source, source_attr, int)
                        
                    output_source_list.append(output_source)
                entry.sources = output_source_list


    return entry

def process_json_file_as_os_entry(file_path: Path):
    input_dict = open_json(file_path)
    entry = get_os_entry_from_dict(input_dict)

    output_file_path = Path("./out/firmware/{}.json".format(entry.key.replace(';','/')))
    output_dir_path = output_file_path.parent

    output_dir_path.mkdir(parents=True, exist_ok=True)
    write_to_json(output_file_path, entry)

start = time.time()
path_list = Path("./appledb/osFiles").rglob('*.json')
for path in path_list:
    process_json_file_as_os_entry(path)
end = time.time()
print(end - start)