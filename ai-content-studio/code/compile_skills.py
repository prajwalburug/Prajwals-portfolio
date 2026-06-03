#!/usr/bin/env python3
"""Compiles brand-kit.md + swipe-file/* into writing-skills.md for any AI to consume."""

import argparse
import os
import sys

VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_PATH", "./brands")

SWIPE_SECTIONS = [
    ("hooks.md", "Proven Hook Patterns"),
    ("frameworks.md", "Content Frameworks"),
    ("subject-lines.md", "Subject Line Library"),
    ("cta-library.md", "CTA Library"),
    ("channel-rules/linkedin.md", "LinkedIn Channel Rules"),
    ("channel-rules/email.md", "Email Channel Rules"),
    ("channel-rules/blog.md", "Blog Channel Rules"),
]


def load_file(path: str) -> str:
    if not os.path.exists(path):
        return f"<!-- {os.path.basename(path)} not found -->\n"
    with open(path, encoding="utf-8") as f:
        return f.read()


def compile_skills(brand: str, vault_root: str, swipe_dir: str) -> str:
    brand_path = os.path.join(vault_root, brand)
    lines = [f"# Writing Skills: {brand.replace('-', ' ').title()}", ""]
    kit = load_file(os.path.join(brand_path, "brand-kit.md"))
    lines.append(kit.strip())
    lines.append("")

    for filename, header in SWIPE_SECTIONS:
        lines.append(f"## {header}")
        lines.append("")
        content = load_file(os.path.join(swipe_dir, filename))
        lines.append(content.strip())
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compile brand kit + swipe file into writing-skills.md")
    parser.add_argument("--brand", required=True, help="Brand name (matches vault directory)")
    parser.add_argument("--output", help="Output path (default: brands/{name}/writing-skills.md)")
    parser.add_argument("--dry-run", action="store_true", help="Print compiled output without writing")
    args = parser.parse_args()

    vault_root = VAULT_ROOT
    brand_path = os.path.join(vault_root, args.brand)
    if not os.path.isdir(brand_path):
        print(f"Error: brand directory not found at {brand_path}", file=sys.stderr)
        available = [d for d in os.listdir(vault_root) if os.path.isdir(os.path.join(vault_root, d))]
        print(f"Available brands: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    swipe_dir = os.path.join(os.path.dirname(__file__), "..", "swipe-file")
    output = compile_skills(args.brand, vault_root, swipe_dir)

    if args.dry_run:
        sys.stdout.reconfigure(encoding="utf-8")
        print(output)
        print("\n[dry-run] No files written.", file=sys.stderr)
        return

    output_path = args.output or os.path.join(brand_path, "writing-skills.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
