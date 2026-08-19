# xmlquery 🔍
![CI](https://github.com/realMNohgee/xmlquery/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Query XML with XPath-like expressions, view tree structure, and validate syntax.** Zero dependencies, pure Python stdlib.

> Part of the **Trust & Reliability Layer for Agentic AI**

## Why it exists

XML powers configs (Maven, Android, SOAP), data interchange, and legacy APIs. But querying it shouldn't need heavy tooling. xmlquery gives you XPath-like find, tree visualization, and validation — all from a single lightweight CLI.

For agentic AI: extract structured data from XML responses, validate tool outputs, inspect config trees.

## One tool, many domains

| Domain | What xmlquery does |
|---|---|
| **DevOps** | Inspect Maven POMs, Android manifests, server configs |
| **Data Integration** | Extract fields from SOAP/XML API responses |
| **QA / Testing** | Validate XML fixtures, query test data |
| **Agentic AI** | Parse structured XML outputs, validate inter-agent messages |
| **Web Services** | Inspect WSDL, RSS/Atom feeds |

## Install

```bash
git clone git@github.com:realMNohgee/xmlquery.git
cd xmlquery
python3 xmlquery.py --help
```

## Quick start

```bash
# Validate XML
python3 xmlquery.py validate config.xml

# View tree structure
python3 xmlquery.py structure config.xml

# Find elements by tag
python3 xmlquery.py find config.xml "//dependency"

# Find with attribute filter
python3 xmlquery.py find config.xml "dependency[@groupId='com.example']"

# Navigate path
python3 xmlquery.py find config.xml "root/child/grandchild"

# Machine-readable output
python3 xmlquery.py find config.xml "//item" --format json
```

## License

MIT — see [LICENSE](LICENSE).

---
🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**
