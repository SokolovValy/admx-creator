from lxml import etree

def generate_admx(config: dict, output_path: str):
    root = etree.Element("policyDefinitions", 
        xmlns="http://schemas.microsoft.com/GroupPolicy/2006/07/PolicyDefinitions",
        revision="1.0"
    )

    # Namespaces
    namespaces = etree.SubElement(root, "policyNamespaces")
    etree.SubElement(namespaces, "target", prefix="system", namespace="BaseALT.Policies.System")

    # Categories
    categories = etree.SubElement(root, "categories")
    for cat in ["System", "Security", "Services", "SSHD", "Systemd", "Network", "Hardware", "Virtualization"]:
        etree.SubElement(categories, "category", 
            name=f"ALT_{cat}",
            displayName=f"$(string.ALT_{cat})"
        )

    # SupportedOn
    resources = etree.SubElement(root, "resources")
    etree.SubElement(resources, "stringTable")

    supported_on = etree.SubElement(root, "supportedOn")
    for ver in ["P10", "P11"]:
        etree.SubElement(supported_on, "definition",
            name=f"SUPPORTED_Alt{ver}",
            displayName=f"$(string.SUPPORTED_Alt{ver})"
        )

    # Policies
    policies = etree.SubElement(root, "policies")

    for policy in config["policies"]:
        if policy["type"] == "simple":
            policy_elem = etree.SubElement(policies, "policy",
                name=policy["name"],
                **{"class": policy["class"]},
                displayName=f"$(string.{policy['name']})",
                explainText=f"$(string.{policy['name']}_help)",
                key=policy["key"],
                valueName=policy["valueName"]
            )

            # Parent Category
            etree.SubElement(policy_elem, "parentCategory",
                ref=f"system:ALT_{policy['category']}"
            )

            # SupportedOn
            etree.SubElement(policy_elem, "supportedOn",
                ref=f"system:SUPPORTED_Alt{policy['altVersion']}"
            )

            # Values
            if policy["valueType"] == "string":
                enabled_value = etree.SubElement(policy_elem, "enabledValue")
                etree.SubElement(enabled_value, "string").text = "enabled"
                
                disabled_value = etree.SubElement(policy_elem, "disabledValue")
                etree.SubElement(disabled_value, "string").text = "disabled"
            else:
                enabled_value = etree.SubElement(policy_elem, "enabledValue")
                etree.SubElement(enabled_value, "decimal", value="1")
                
                disabled_value = etree.SubElement(policy_elem, "disabledValue")
                etree.SubElement(disabled_value, "decimal", value="0")


    # Внутри функции generate_admx, в разделе обработки политик:
    for policy in config["policies"]:
        if policy["type"] == "dropdown":
            policy_elem = etree.SubElement(policies, "policy",
                name=policy["name"],
                **{"class": policy["class"]},
                displayName=f"$(string.{policy['name']})",
                explainText=f"$(string.{policy['name']}_help)",
                key=policy["key"],
                valueName=policy["valueName"],
                presentation=policy["presentation"]
            )

            # Parent Category
            etree.SubElement(policy_elem, "parentCategory",
                ref=f"system:ALT_{policy['category']}"
            )

            # SupportedOn
            etree.SubElement(policy_elem, "supportedOn",
                ref=f"system:SUPPORTED_Alt{policy['altVersion']}"
            )

            # Elements
            elements = etree.SubElement(policy_elem, "elements")
            enum = etree.SubElement(elements, "enum",
                id=policy["enumId"],
                required="true",
                valueName=policy["valueName"]
            )

            for item in policy["items"]:
                item_elem = etree.SubElement(enum, "item",
                    displayName=f"$(string.{policy['enumId']}-{item['name']})"
                )
                value_elem = etree.SubElement(item_elem, "value")
                value_elem.text = str(item["value"])

    etree.ElementTree(root).write(output_path, encoding="utf-8", pretty_print=True)