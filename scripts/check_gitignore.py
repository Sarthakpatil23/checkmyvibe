#!/usr/bin/env python3
import os
import sys
import fnmatch

# Potential local secret file patterns (glob format)
SECRET_PATTERNS = [
    '.env',
    '.env.*',
    '*service-account*.json',
    '*serviceAccount*.json',
    '*credentials*.json',
    '*.pem',
    '*.key',
    '*.p12',
    'secrets.json',
    'jwt_key*',
]

# Patterns that are allowed to be public (not secrets)
PUBLIC_EXCEPTIONS = [
    '*.example',
    '*.template',
    '*.sample',
    '*.dist',
    '*.config.json',
    'firebase.json',
]

def is_secret_file(filename):
    """Check if filename matches secret patterns and doesn't match public exceptions."""
    is_secret = False
    for pat in SECRET_PATTERNS:
        if fnmatch.fnmatch(filename, pat):
            is_secret = True
            break
            
    if not is_secret:
        return False
        
    for pat in PUBLIC_EXCEPTIONS:
        if fnmatch.fnmatch(filename, pat):
            return False
            
    return True

def parse_gitignore(gitignore_path):
    """Read and parse the .gitignore patterns, skipping comments and empty lines."""
    patterns = []
    if not os.path.exists(gitignore_path):
        return patterns
        
    with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Strip inline comments
            if ' #' in line:
                line = line.split(' #')[0].strip()
            patterns.append(line)
    return patterns

def is_ignored(file_rel_path, gitignore_patterns):
    """Verify if a relative file path matches any .gitignore pattern."""
    ignored = False
    parts = file_rel_path.split(os.sep)
    
    # Hardcoded check for system folders that are assumed ignored
    if 'node_modules' in parts or '.git' in parts or 'dist' in parts or 'build' in parts:
        return True

    for pattern in gitignore_patterns:
        negate = False
        if pattern.startswith('!'):
            negate = True
            pattern = pattern[1:]
            
        match = False
        if pattern.startswith('/'):
            clean_pattern = pattern[1:]
            match = fnmatch.fnmatch(file_rel_path, clean_pattern) or fnmatch.fnmatch(file_rel_path, clean_pattern + '/*')
        else:
            match = fnmatch.fnmatch(os.path.basename(file_rel_path), pattern) or \
                    fnmatch.fnmatch(file_rel_path, pattern) or \
                    fnmatch.fnmatch(file_rel_path, '*/' + pattern) or \
                    any(fnmatch.fnmatch(part, pattern) for part in parts)
                    
        if match:
            ignored = not negate
            
    return ignored

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    target_dir = os.path.abspath(target_dir)
    
    gitignore_path = os.path.join(target_dir, '.gitignore')
    has_gitignore = os.path.exists(gitignore_path)
    
    gitignore_patterns = parse_gitignore(gitignore_path) if has_gitignore else []
    
    secret_files_found = []
    unignored_secrets = []
    
    for root, dirs, files in os.walk(target_dir):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in {'node_modules', '.git', 'dist', 'build', '.next', '.svelte-kit'}]
        
        for file in files:
            if is_secret_file(file):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, target_dir)
                
                if is_ignored(rel_path, gitignore_patterns):
                    secret_files_found.append((rel_path, True))
                else:
                    secret_files_found.append((rel_path, False))
                    unignored_secrets.append(rel_path)
                    
    if not secret_files_found:
        print("PASS: No local secret files (like .env) were detected in the project.")
        sys.exit(0)
        
    if unignored_secrets:
        print("FAIL: The following local secret files are NOT excluded by .gitignore:")
        for sf in unignored_secrets:
            print(f"  - {sf}")
        if not has_gitignore:
            print("  (Note: No .gitignore file was found in the project root)")
        sys.exit(1)
    else:
        print("PASS: All detected local secret files are correctly listed in .gitignore:")
        for sf, ignored in secret_files_found:
            print(f"  - {sf} (ignored)")
        sys.exit(0)

if __name__ == '__main__':
    main()
