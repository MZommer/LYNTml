import xml.etree.ElementTree as ET
from os import PathLike
from typing import get_args, get_origin

from .descriptors import (
    XMLAttribute,
    XMLElementCollection,
    XMLSiblingCollection,
    XMLSubElement,
)
from .elements import XMLElement
from .utils import from_str, type_arg
from .wrappers import Attribute, CollectionValue, SubElement


class XMLSerializer:
    """Stateless serializer for XMLElement trees.

    Usage:

        serializer = XMLSerializer()

        # write
        xml_str = serializer.to_string(my_element)
        serializer.to_file(my_element, "output.xml")

        # read
        el = serializer.from_string(general, xml_str)
        el = serializer.from_file(general, "input.xml")
    """

    DEFAULT_ENCODING = "utf-8"
    DEFAULT_INDENT = "    "

    def __init__(
        self,
        indent: str = DEFAULT_INDENT,
        encoding: str = DEFAULT_ENCODING,
        xml_declaration: bool = True,
    ) -> None:
        self.indent = indent
        self.encoding = encoding
        self.xml_declaration = xml_declaration

    def to_et(self, element: XMLElement) -> ET.Element:
        """Serialize an XMLElement to an ET.Element tree."""
        el = ET.Element(element.tag)
        hints = vars(type(element)).get("__annotations__", {})

        for field, ann in hints.items():
            origin = get_origin(ann)

            if origin is XMLSubElement:
                v: SubElement | None = element.__dict__.get(f"__sub_{field}")
                if v is not None:
                    ET.SubElement(el, field).text = v.text

            elif origin is XMLAttribute:
                v: Attribute | None = element.__dict__.get(f"__attr_{field}")
                if v is not None:
                    el.set(field, v.text)

            elif origin is XMLElementCollection or ann is XMLElementCollection:
                col: CollectionValue | None = element.__dict__.get(f"__col_{field}")
                if col and len(col):
                    container = ET.SubElement(el, field)
                    for item in col:
                        container.append(self.to_et(item))

            elif origin is XMLSiblingCollection or ann is XMLSiblingCollection:
                col: CollectionValue | None = element.__dict__.get(f"__sib_{field}")
                if col:
                    for item in col:
                        el.append(self.to_et(item))  # no wrapper — direct siblings

        return el

    def to_string(self, element: XMLElement) -> str:
        """Return a formatted XML string."""
        tree = self.to_et(element)
        ET.indent(tree, space=self.indent)
        return ET.tostring(
            tree, encoding=self.encoding, xml_declaration=self.xml_declaration
        )

    def to_file(self, element: XMLElement, path: str) -> None:
        """Write an element tree to a file."""
        el = self.to_et(element)
        ET.indent(el, space=self.indent)
        ET.ElementTree(el).write(
            path, encoding=self.encoding, xml_declaration=self.xml_declaration
        )

    def from_et(self, cls: type[XMLElement], el: ET.Element) -> XMLElement:
        """Deserialize an ET.Element into an instance of cls."""
        obj = cls.__new__(cls)
        hints = vars(cls).get("__annotations__", {})

        for field, ann in hints.items():
            origin = get_origin(ann)

            if origin is XMLSubElement:
                dtype = type_arg(ann)
                child = el.find(field)
                if child is not None and child.text is not None:
                    obj.__dict__[f"__sub_{field}"] = SubElement(
                        field, from_str(child.text.strip(), dtype), dtype
                    )

            elif origin is XMLAttribute:
                dtype = type_arg(ann)
                raw = el.get(field)
                if raw is not None:
                    obj.__dict__[f"__attr_{field}"] = Attribute(
                        field, from_str(raw, dtype), dtype
                    )

            elif origin is XMLElementCollection or ann is XMLElementCollection:
                item_type = type_arg(ann) if get_args(ann) else None
                col = CollectionValue(item_type=item_type)
                container_el = el.find(field)
                if container_el is not None and item_type is not None:
                    for child_el in container_el:
                        col.append(self.from_et(item_type, child_el))
                obj.__dict__[f"__col_{field}"] = col

            elif origin is XMLSiblingCollection or ann is XMLSiblingCollection:
                item_type = type_arg(ann) if get_args(ann) else None
                col = CollectionValue(item_type=item_type)
                if item_type is not None:
                    # Derive the XML tag from a throwaway instance's .tag property,
                    # which defaults to the class name — no instance data needed.
                    xml_tag = item_type.__name__
                    for child_el in el.findall(xml_tag):
                        col.append(self.from_et(item_type, child_el))
                obj.__dict__[f"__sib_{field}"] = col

        return obj

    def from_string(self, cls: type[XMLElement], xml_str: str) -> XMLElement:
        """Deserialize from a XML string."""
        return self.from_et(cls, ET.fromstring(xml_str))

    def from_file(self, cls: type[XMLElement], path: str | PathLike) -> XMLElement:
        """Deserialize from a file on disk."""
        return self.from_et(cls, ET.parse(path).getroot())
