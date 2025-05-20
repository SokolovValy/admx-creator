from lxml import etree

def validate_xml(xml_path: str) -> bool:
    """Проверяет валидность XML"""
    try:
        etree.parse(xml_path)
        return True
    except etree.XMLSyntaxError as e:
        print(f"XML Error: {e}")
        return False