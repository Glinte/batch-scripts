#!/usr/bin/env python3
"""Renames keys in the YAML front matter of a Markdown file.

If a directory is given, the script walks it (``glob('*.md')``) and processes every ``.md`` file it finds.

This version supports **shallow merging** when both the original key and the
new key already exist in the front‑matter:

* If *both* keys are present, their values are merged **shallowly**.
    * Dictionaries: one‑level ``dict`` merge (values from the *original* key take
        precedence). Any nested ``dict`` or ``list`` inside those dicts triggers an
        error.
    * Lists: concatenated while keeping order and de‑duplicating. A ``list`` that
        itself contains ``dict``/``list`` elements triggers an error.
    * Scalars: values from the *original* key overwrite the new key.
    * ``None`` can merge with anything and returns the non‑``None`` value.
* If the values of the two keys are of **different Python types** (except
    ``None``)
"""
# /// script
# dependencies = [
#   "pyyaml",
#   "typer",
# ]
# ///
import os
import sys
import argparse
import json
from pathlib import Path
from typing import Any

import yaml
import typer


app = typer.Typer()


# ───────────────────────────────────────────────────────────────────────────────
# Helper functions
# ───────────────────────────────────────────────────────────────────────────────

def _is_deep_structure(value: Any) -> bool:
    """Return ``True`` if *value* contains a nested ``dict`` or ``list``.

    Lists and dicts are considered *deep* when **any** of their direct children
    is itself a ``dict`` or ``list``.
    """
    if isinstance(value, dict):
        return any(isinstance(v, (dict, list)) for v in value.values())
    if isinstance(value, list):
        return any(isinstance(v, (dict, list)) for v in value)
    return False


def _merge_shallow(val_old: Any, val_new: Any) -> Any:
    """Merge *val_old* (from the original key) into *val_new* (target key).

    Rules:
    * ``None`` merges with anything → returns the non‑``None`` value.
    * Type mismatch → *ValueError*.
    * Dict → shallow ``dict`` merge, *val_old* wins on key collisions.
    * List → concatenation keeping order & removing duplicates; error if either
      list contains nested structures.
    * Scalar → *val_old* overwrites *val_new*.
    """
    if val_old is None:
        return val_new
    if val_new is None:
        return val_old

    if type(val_old) is not type(val_new):
        raise ValueError("type mismatch: cannot merge \n  "
                         f"old({type(val_old).__name__}) with "
                         f"new({type(val_new).__name__})")

    if isinstance(val_old, dict):
        if _is_deep_structure(val_old) or _is_deep_structure(val_new):
            raise ValueError("deep structures found in dict merge")
        merged: Dict[str, Any] = {**val_new, **val_old}  # old wins
        return merged

    if isinstance(val_old, list):
        if _is_deep_structure(val_old) or _is_deep_structure(val_new):
            raise ValueError("deep structures found in list merge")
        merged_list = val_new + [item for item in val_old if item not in val_new]
        return merged_list

    # Scalars (str, int, float, bool, etc.)
    return val_old  # original key overwrites


# ───────────────────────────────────────────────────────────────────────────────
# Core logic
# ───────────────────────────────────────────────────────────────────────────────
def rename_frontmatter_keys(file_path: str | Path, **key_mapping: str) -> bool:
    """
    Rename (and possibly merge) keys in the YAML front matter of a Markdown file.

    Args:
        file_path: Path to the Markdown file
        key_mapping: A mapping of original keys to their new names as keyword arguments

    Returns:
        bool: True if file was successfully modified, False otherwise
    """
    if not key_mapping:
        raise ValueError("Error: No key mappings provided.")

    if not os.path.exists(file_path):
        raise ValueError(f"File {file_path} does not exist.")

    with open(file_path, 'r', encoding='utf-8') as file:  # Error reading file will be caught by the caller
        content = file.read()

    if not content.startswith('---'):
        print(f"No front matter found in the file {file_path}.")
        return False

    # Split on the first two occurrences of '---' (Should be start & end of front‑matter)
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"No front matter found in the file {file_path}.")
        return False

    try:
        front_matter: dict[str, Any] = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parsing YAML front matter in {file_path}") from exc

    for old_key, new_key in key_mapping.items():
        if old_key not in front_matter:
            continue  # Nothing to rename

        old_val = front_matter.pop(old_key)
        if new_key in front_matter:
            try:
                front_matter[new_key] = _merge_shallow(old_val, front_matter[new_key])
            except ValueError as exc:
                raise ValueError(f"Error merging '{old_key}' into '{new_key}' in {file_path}") from exc
        else:
            front_matter[new_key] = old_val

    # Re‑assemble the document
    # default_flow_style=False ensures that lists and dicts are not dumped in a single line
    # Mostly important for the top-level tag mapping, we need to avoid pyyaml dumping it as a single line like
    #   {Aliases: [], Date Created: 'Friday, May 2nd 2025, 11:16:47 am'}
    new_front_yaml = yaml.safe_dump(front_matter, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{new_front_yaml}---{parts[2]}"

    try:
        file_path.write_text(new_content, encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Error writing file") from exc

    print(f"Successfully processed {file_path}")
    return True


@app.command()
def main(
    path: Path = typer.Argument(..., help="Path to a Markdown file or a directory containing Markdown files"),
    initial_keys: list[str] = typer.Option(..., "--initial_keys", "-i", help="List of original keys to be renamed"),
    target_keys: list[str] = typer.Option(..., "--target_keys", "-o", help="List of new keys to replace original keys"),
) -> bool:
    """Renames keys in the YAML front matter of a Markdown file.

    If a directory is given, the script walks it (``glob('*.md')``) and processes every ``.md`` file it finds.

    This version supports **shallow merging** when both the original key and the
    new key already exist in the front‑matter:

    * If *both* keys are present, their values are merged **shallowly**.
        * Dictionaries: one‑level ``dict`` merge (values from the *original* key take
            precedence). Any nested ``dict`` or ``list`` inside those dicts triggers an
            error.
        * Lists: concatenated while keeping order and de‑duplicating. A ``list`` that
            itself contains ``dict``/``list`` elements triggers an error.
        * Scalars: values from the *original* key overwrite the new key.
        * ``None`` can merge with anything and returns the non‑``None`` value.
    * If the values of the two keys are of **different Python types** (except
        ``None``), the script aborts with an error message.
    """
    if len(initial_keys) != len(target_keys):
        print(f"Error: The number of initial keys and target keys must be the same, but got {len(initial_keys)} and {len(target_keys)} respectively.")
        return False

    key_mapping = dict(zip(initial_keys, target_keys))

    if path.is_file():
        success = rename_frontmatter_keys(path, **key_mapping)
        raise typer.Exit(code=0 if success else 1)

    if path.is_dir():
        md_files = list(path.glob("*.md"))
        if not md_files:
            typer.echo("No Markdown files found in the directory.", err=True)
            raise typer.Exit(code=1)

        success_count = 0
        for md in md_files:
            success_count += rename_frontmatter_keys(md, **key_mapping)  # Let errors propagate

        print(f"Processed {success_count} out of {len(md_files)} Markdown files.")
        raise typer.Exit(code=0)

    typer.echo("Provided path is neither a file nor a directory.", err=True)
    raise typer.Exit(code=1)


if __name__ == '__main__':
    app()
