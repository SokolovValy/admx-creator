from lxml import etree

def generate_adml(config: dict, lang: str, output_path: str):
    root = etree.Element("policyDefinitionResources",
        xmlns="http://schemas.microsoft.com/GroupPolicy/2006/07/PolicyDefinitions"
    )

    resources = etree.SubElement(root, "resources")
    string_table = etree.SubElement(resources, "stringTable")

    # Категории
    for cat in ["System", "Security", "Services", "SSHD", "Systemd", "Network", "Hardware", "Virtualization"]:
        etree.SubElement(string_table, "string", id=f"ALT_{cat}").text = f"ALT {cat}"

    # Версии
    for ver in ["P10", "P11"]:
        etree.SubElement(string_table, "string", id=f"SUPPORTED_Alt{ver}").text = f"ALT Linux {ver}"

    # Политики
    for policy in config["policies"]:
        # Общие строки для всех политик
        etree.SubElement(string_table, "string", id=policy["name"]).text = policy["displayName"]
        etree.SubElement(string_table, "string", id=f"{policy['name']}_help").text = policy["description"]

        if policy["type"] == "dropdown":
            # Строки для элементов dropdown
            for item in policy["items"]:
                etree.SubElement(string_table, "string",
                    id=f"{policy['enumId']}-{item['name']}"
                ).text = item["name"]

            # Presentation
            presentation = etree.SubElement(root, "presentation",
                id=policy["presentation"]
            )
            etree.SubElement(presentation, "dropdownList",
                noSort="true",
                defaultItem="0",
                refId=policy["enumId"]
            ).text = policy["listName"]

    etree.ElementTree(root).write(output_path, encoding="utf-8", pretty_print=True)