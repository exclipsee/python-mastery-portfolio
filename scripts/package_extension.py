"""Package the dependency-free VS Code extension as an installable VSIX."""

import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
EXTENSION_DIR = ROOT / "extension"
OUTPUT = ROOT / "dist" / "lm-studio-chat.vsix"
VSIX_NAMESPACE = "http://schemas.microsoft.com/developer/vsx-schema/2011"
CONTENT_TYPES_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/content-types"


def build_manifest(package: dict[str, object]) -> bytes:
    engines = package.get("engines")
    if not isinstance(engines, dict) or not isinstance(engines.get("vscode"), str):
        raise ValueError("Extension package.json must declare a VS Code engine version.")

    manifest = ElementTree.Element(
        f"{{{VSIX_NAMESPACE}}}PackageManifest",
        {"Version": "2.0.0"},
    )
    metadata = ElementTree.SubElement(manifest, f"{{{VSIX_NAMESPACE}}}Metadata")
    ElementTree.SubElement(
        metadata,
        f"{{{VSIX_NAMESPACE}}}Identity",
        {
            "Language": "en-US",
            "Id": str(package["name"]),
            "Version": str(package["version"]),
            "Publisher": str(package["publisher"]),
        },
    )
    ElementTree.SubElement(metadata, f"{{{VSIX_NAMESPACE}}}DisplayName").text = str(
        package["displayName"]
    )
    ElementTree.SubElement(metadata, f"{{{VSIX_NAMESPACE}}}Description").text = str(
        package["description"]
    )
    properties = ElementTree.SubElement(metadata, f"{{{VSIX_NAMESPACE}}}Properties")
    ElementTree.SubElement(
        properties,
        f"{{{VSIX_NAMESPACE}}}Property",
        {
            "Id": "Microsoft.VisualStudio.Code.Engine",
            "Value": engines["vscode"],
        },
    )
    ElementTree.SubElement(
        properties,
        f"{{{VSIX_NAMESPACE}}}Property",
        {
            "Id": "Microsoft.VisualStudio.Code.Manifest",
            "Value": "extension/package.json",
        },
    )
    installation = ElementTree.SubElement(
        manifest, f"{{{VSIX_NAMESPACE}}}Installation"
    )
    ElementTree.SubElement(
        installation,
        f"{{{VSIX_NAMESPACE}}}InstallationTarget",
        {"Id": "Microsoft.VisualStudio.Code"},
    )
    ElementTree.SubElement(manifest, f"{{{VSIX_NAMESPACE}}}Dependencies")
    assets = ElementTree.SubElement(manifest, f"{{{VSIX_NAMESPACE}}}Assets")
    ElementTree.SubElement(
        assets,
        f"{{{VSIX_NAMESPACE}}}Asset",
        {
            "Type": "Microsoft.VisualStudio.Code.Manifest",
            "Path": "extension/package.json",
            "Addressable": "true",
        },
    )
    return ElementTree.tostring(manifest, encoding="utf-8", xml_declaration=True)


def build_content_types() -> bytes:
    content_types = ElementTree.Element(
        f"{{{CONTENT_TYPES_NAMESPACE}}}Types"
    )
    for extension, content_type in (
        ("json", "application/json"),
        ("js", "application/javascript"),
        ("xml", "text/xml"),
    ):
        ElementTree.SubElement(
            content_types,
            f"{{{CONTENT_TYPES_NAMESPACE}}}Default",
            {"Extension": extension, "ContentType": content_type},
        )
    ElementTree.SubElement(
        content_types,
        f"{{{CONTENT_TYPES_NAMESPACE}}}Override",
        {
            "PartName": "/extension.vsixmanifest",
            "ContentType": "text/xml",
        },
    )
    return ElementTree.tostring(
        content_types, encoding="utf-8", xml_declaration=True
    )


def main() -> None:
    package_path = EXTENSION_DIR / "package.json"
    extension_path = EXTENSION_DIR / "extension.js"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    if not extension_path.is_file():
        raise FileNotFoundError(f"Missing extension entry point: {extension_path}")
    required_fields = ("name", "publisher", "version", "displayName", "description")
    missing_fields = [field for field in required_fields if not package.get(field)]
    if missing_fields:
        raise ValueError(f"Extension package.json is missing: {', '.join(missing_fields)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": f"{package['publisher']}.{package['name']}",
        "publisherId": package["publisher"],
        "publisherDisplayName": package["publisher"],
        "targetPlatform": "universal",
    }
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", build_content_types())
        archive.writestr("extension.vsixmanifest", build_manifest(package))
        archive.writestr("manifest.json", json.dumps(metadata, indent=2))
        archive.write(package_path, "extension/package.json")
        archive.write(extension_path, "extension/extension.js")

    print(f"Created {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
