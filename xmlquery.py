#!/usr/bin/env python3
"""xmlquery — Query, structure, and validate XML. Zero dependencies, pure Python stdlib."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET


def read_xml(file_arg: str) -> str:
    """Read XML text from a file or stdin."""
    if file_arg == "-":
        return sys.stdin.read()
    with open(file_arg, "r", encoding="utf-8") as f:
        return f.read()


def parse_xml(raw: str):
    """Parse XML and return root element."""
    return ET.fromstring(raw)


def xml_to_text(elem, indent=0):
    """Convert element to text representation."""
    text = elem.text.strip() if elem.text and elem.text.strip() else ""
    tail = elem.tail.strip() if elem.tail and elem.tail.strip() else ""
    result = ""
    if text:
        result += "  " * indent + f"{elem.tag}: {text}\n"
    else:
        result += "  " * indent + f"<{elem.tag}>\n"
    for child in elem:
        result += xml_to_text(child, indent + 1)
    if not text:
        result += "  " * indent + f"</{elem.tag}>\n"
    return result


def match_xpath(elem, xpath):
    """Basic XPath-like matching. Returns list of matching elements."""
    xpath = xpath.strip()

    # Handle //tag (anywhere in tree)
    if xpath.startswith("//"):
        tag = xpath[2:]
        # Check for [@attr='val'] predicate
        attr_name = None
        attr_val = None
        if "[@" in tag and "='" in tag:
            base_tag = tag[:tag.index("[@")]
            pred = tag[tag.index("[@")+2:].rstrip("]")
            if "='" in pred:
                attr_name, attr_val = pred.split("='", 1)
                attr_val = attr_val.rstrip("'")
            tag = base_tag
        results = []
        for el in elem.iter():
            if el.tag == tag:
                if attr_name is not None:
                    if el.get(attr_name) == attr_val:
                        results.append(el)
                else:
                    results.append(el)
        return results

    # Handle .//tag (descendants of current)
    if xpath.startswith(".//"):
        tag = xpath[3:]
        attr_name = None
        attr_val = None
        if "[@" in tag and "='" in tag:
            base_tag = tag[:tag.index("[@")]
            pred = tag[tag.index("[@")+2:].rstrip("]")
            if "='" in pred:
                attr_name, attr_val = pred.split("='", 1)
                attr_val = attr_val.rstrip("'")
            tag = base_tag
        results = []
        for el in elem.iter():
            if el.tag == tag:
                if attr_name is not None:
                    if el.get(attr_name) == attr_val:
                        results.append(el)
                else:
                    results.append(el)
        return results

    # Handle tag with predicate
    attr_name = None
    attr_val = None
    remaining = xpath
    if "[@" in xpath and "='" in xpath:
        idx_open = xpath.index("[@")
        idx_close = xpath.index("]", idx_open)
        pred = xpath[idx_open+2:idx_close]
        if "='" in pred:
            attr_name, attr_val = pred.split("='", 1)
            attr_val = attr_val.rstrip("'")
        remaining = xpath[:idx_open] + xpath[idx_close+1:]

    # Handle tag/child path
    if "/" in remaining:
        parts = remaining.split("/", 1)
        tag = parts[0]
        rest = parts[1]

        candidates = []
        if tag == "" or tag == ".":
            candidates = [elem]
        else:
            candidates = [c for c in elem if c.tag == tag]

        results = []
        for c in candidates:
            results.extend(match_xpath(c, rest))
        return results

    # Simple tag match
    if remaining == "." or remaining == "":
        return [elem]
    
    results = [c for c in elem if c.tag == remaining]
    return results


def cmd_find(args: argparse.Namespace) -> int:
    """Find elements matching an XPath-like expression."""
    try:
        raw = read_xml(args.file)
        root = parse_xml(raw)
    except ET.ParseError as e:
        print(f"✗ Invalid XML: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"✗ File not found: {args.file}", file=sys.stderr)
        return 1

    matches = match_xpath(root, args.xpath)

    if args.format == "json":
        output = []
        for m in matches:
            entry = {"tag": m.tag, "text": (m.text or "").strip(), "attrib": dict(m.attrib)}
            children = [c.tag for c in m]
            if children:
                entry["children"] = children
            output.append(entry)
        json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    else:
        if not matches:
            print("(no matches)")
        for m in matches:
            print(xml_to_text(m))

    return 0


def cmd_structure(args: argparse.Namespace) -> int:
    """Print XML tree structure (tag hierarchy)."""
    try:
        raw = read_xml(args.file)
        root = parse_xml(raw)
    except ET.ParseError as e:
        print(f"✗ Invalid XML: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"✗ File not found: {args.file}", file=sys.stderr)
        return 1

    def print_tree(elem, depth=0):
        indent = "  " * depth
        attr_str = ""
        if elem.attrib:
            attr_str = " " + " ".join(f'{k}="{v}"' for k, v in elem.attrib.items())
        print(f"{indent}{elem.tag}{attr_str}")
        for child in elem:
            print_tree(child, depth + 1)

    if args.format == "json":
        def tree_to_dict(elem):
            node = {"tag": elem.tag}
            if elem.attrib:
                node["attrib"] = dict(elem.attrib)
            children = [tree_to_dict(c) for c in elem]
            if children:
                node["children"] = children
            return node
        json.dump(tree_to_dict(root), sys.stdout, ensure_ascii=False, indent=2)
    else:
        print_tree(root)

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Check if valid XML."""
    try:
        raw = read_xml(args.file)
        ET.fromstring(raw)
    except ET.ParseError as e:
        if args.format == "json":
            json.dump({"valid": False, "error": str(e)}, sys.stdout)
        else:
            print(f"✗ Invalid XML: {e}")
        return 1
    except FileNotFoundError:
        if args.format == "json":
            json.dump({"valid": False, "error": f"File not found: {args.file}"}, sys.stdout)
        else:
            print(f"✗ File not found: {args.file}")
        return 1

    if args.format == "json":
        json.dump({"valid": True}, sys.stdout)
    else:
        print("✓ Valid XML")
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")

    p = argparse.ArgumentParser(description="xmlquery — Query, structure, and validate XML")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("find", parents=[common],
                        help="Find elements by XPath-like expression")
    sp.add_argument("file", help="XML file (- for stdin)")
    sp.add_argument("xpath", help="XPath-like expression (e.g., //tag, tag[@attr='val'], tag/child)")
    sp.set_defaults(func=cmd_find)

    sp = sub.add_parser("structure", parents=[common],
                        help="Print XML tree structure")
    sp.add_argument("file", help="XML file (- for stdin)")
    sp.set_defaults(func=cmd_structure)

    sp = sub.add_parser("validate", parents=[common],
                        help="Validate XML syntax")
    sp.add_argument("file", help="XML file (- for stdin)")
    sp.set_defaults(func=cmd_validate)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
