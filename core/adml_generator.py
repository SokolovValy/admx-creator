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
        if policy["type"] == "simple":
            etree.SubElement(string_table, "string", id=policy["name"]).text = policy["displayName"]
            etree.SubElement(string_table, "string", id=f"{policy['name']}_help").text = policy["description"]
    
    etree.ElementTree(root).write(output_path, encoding="utf-8", pretty_print=True)