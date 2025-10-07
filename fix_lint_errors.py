#!/usr/bin/env python3
"""Fix Ruff linting errors in backend code."""

import re
from pathlib import Path

def fix_exception_handling(file_path: Path) -> None:
    """Add 'from e' to exception handling in a file."""
    content = file_path.read_text()

    # Pattern: raise HTTPException(...) without 'from e/err/etc'
    # Match raise HTTPException that's NOT already followed by 'from'
    pattern = r'(except \w+ as (\w+):.*?)(raise HTTPException\([^)]*\))\s*$'

    def replacer(match):
        full_except = match.group(1)
        exception_var = match.group(2)
        raise_stmt = match.group(3)
        if 'from' not in match.group(0):
            return f"{full_except}{raise_stmt} from {exception_var}"
        return match.group(0)

    # Simpler approach: find all 'raise HTTPException' not followed by 'from'
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if this is a raise HTTPException line
        if 'raise HTTPException' in line and 'from' not in line:
            # Look backwards for the exception variable
            for j in range(i-1, max(0, i-10), -1):
                prev_line = lines[j]
                match = re.search(r'except \w+ as (\w+):', prev_line)
                if match:
                    exception_var = match.group(1)
                    # Add 'from exception_var' to the current line
                    if line.rstrip().endswith(')'):
                        line = line.rstrip() + f' from {exception_var}'
                    break
        new_lines.append(line)
        i += 1

    new_content = '\n'.join(new_lines)
    if new_content != content:
        file_path.write_text(new_content)
        print(f"Fixed: {file_path}")

def remove_unused_variable(file_path: Path) -> None:
    """Remove unused options variable from auth.py."""
    content = file_path.read_text()

    # Remove the options dict that's not used
    pattern = r'        # Initialize with proper options structure\n        # The headers attribute is needed by the Supabase client\n        options = \{[^}]+\}\n\n'
    replacement = '        # Create the client - options like auto_refresh_token, persist_session,\n        # and custom headers would be configured here if needed\n'

    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if new_content != content:
        file_path.write_text(new_content)
        print(f"Fixed: {file_path}")

def main():
    backend_dir = Path(__file__).parent / 'backend' / 'app'

    # Fix exception handling in all endpoint files
    for file_path in backend_dir.rglob('*.py'):
        if 'endpoints' in str(file_path):
            fix_exception_handling(file_path)

    # Fix unused variable in auth service
    auth_file = backend_dir / 'services' / 'supabase' / 'auth.py'
    if auth_file.exists():
        remove_unused_variable(auth_file)

    print("Done!")

if __name__ == '__main__':
    main()
