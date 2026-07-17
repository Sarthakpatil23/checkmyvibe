#!/usr/bin/env python3
import os
import sys
import re
import math

# Directories to skip during scanning
SKIP_DIRS = {
    'node_modules', '.git', 'build', 'dist', '.next', '.svelte-kit', 
    '__pycache__', 'venv', '.venv', 'env', 'coverage', 'out', '.expo',
    '.output', '.nuxt'
}

# File extensions to skip (binary/media/lockfiles/assets)
SKIP_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', 
    '.gz', '.mp3', '.mp4', '.mov', '.db', '.sqlite', '.exe', '.dll',
    '.so', '.dylib', '.woff', '.woff2', '.ttf', '.eot', '.lock',
    '.package-lock.json', '.pnpm-lock.yaml', '.yarn.lock', '.map',
    '.svg', '.css', '.scss', '.less', '.html', '.xml'
}

# Regexes for known API key formats
API_KEY_PATTERNS = [
    (re.compile(r'AIza[0-9A-Za-z-_]{35}'), 'Google API Key'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS Access Key ID'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36,40}'), 'GitHub Personal Access Token'),
    (re.compile(r'sk_(live|test)_[0-9a-zA-Z]{24,96}'), 'Stripe Secret Key'),
    (re.compile(r'xox[bapr]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}'), 'Slack Token'),
]

# Regex for variable assignments with potential hardcoded secrets
# Matches: name = "string" or "name": "string", where name contains key, secret, token, password, credential, auth
ASSIGNMENT_PATTERN = re.compile(
    r'(?i)(?:[\'"`]?)\b(\w*(?:key|secret|token|password|credential|auth)\w*)\b(?:[\'"`]?)\s*(?:=|:)\s*([\'"`])([^\'"`\n\r]{8,256})\2'
)

# Regex for standalone high-entropy candidate words (length 32 to 128)
HIGH_ENTROPY_WORD_PATTERN = re.compile(r'\b([a-zA-Z0-9+/=_-]{32,128})\b')

def calculate_entropy(s):
    """Calculate the Shannon entropy of a string."""
    if not s:
        return 0
    entropy = 0
    for x in set(s):
        p_x = s.count(x) / len(s)
        entropy -= p_x * math.log2(p_x)
    return entropy

def is_binary(file_path):
    """Check if a file is binary by looking for null bytes."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk
    except Exception:
        return True

def scan_file(file_path):
    findings = []
    if is_binary(file_path):
        return findings

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # 1. Check known API key patterns
                for pattern, name in API_KEY_PATTERNS:
                    if pattern.search(line):
                        findings.append((line_num, f"Exposed {name}"))
                        
                # 2. Check variable assignments
                for match in ASSIGNMENT_PATTERN.finditer(line):
                    var_name, quote, val = match.groups()
                    
                    # Ignore environment variable references, string interpolation, or placeholders
                    if any(x in val for x in ['process.env', 'os.environ', 'os.getenv', 'ENV[', '${', '{{', '}}']):
                        continue
                    
                    # Ignore common placeholder value patterns
                    val_lower = val.lower()
                    placeholders = {
                        'true', 'false', 'null', 'undefined', 'placeholder', 'dummy', 
                        'your_key_here', 'your-key-here', 'your_secret_here', 'your-secret-here',
                        'test', 'mock', 'none', 'value', 'secret', 'password', 'key', 'token'
                    }
                    if val_lower in placeholders or all(c in '-_*' for c in val):
                        continue
                    
                    entropy = calculate_entropy(val)
                    if len(val) >= 12 and entropy > 3.0:
                        findings.append((line_num, f"Potential secret assigned to '{var_name}' (entropy: {entropy:.2f})"))
                    elif len(val) >= 16:
                        findings.append((line_num, f"Suspicious long literal assigned to '{var_name}'"))

                # 3. Check for standalone high-entropy words (only if not already matched above)
                # Keep threshold high to reduce noise from base64 assets/hashes
                for match in HIGH_ENTROPY_WORD_PATTERN.finditer(line):
                    word = match.group(1)
                    # Skip if it is part of a URL, or has common non-secret structures
                    if any(x in line for x in ['http://', 'https://', 'src=', 'href=', 'url(']):
                        continue
                    
                    # Skip common long words/hashes that are not secrets (e.g. standard CSS classes, hex colors)
                    if re.match(r'^[0-9a-fA-F]+$', word) and len(word) < 40:
                        # Small hex hashes are common (commit IDs, etc.) - require higher length or entropy
                        continue
                        
                    entropy = calculate_entropy(word)
                    # True high entropy strings (like keys) typically have entropy > 4.2 for 32+ char length
                    if len(word) >= 32 and entropy > 4.3:
                        # Make sure it's not already reported in assignments
                        if not any(word in f[1] for f in findings):
                            findings.append((line_num, f"Standalone high-entropy string found (entropy: {entropy:.2f})"))
                            
    except Exception:
        pass
        
    return findings

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    target_dir = os.path.abspath(target_dir)
    
    if not os.path.exists(target_dir):
        print(f"Error: Path '{target_dir}' does not exist.")
        sys.exit(1)
        
    for root, dirs, files in os.walk(target_dir):
        # Exclude directories in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            # Skip hidden files unless they are .env configuration files
            if ext in SKIP_EXTS or (file.startswith('.') and not file.startswith('.env')):
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, target_dir)
            
            findings = scan_file(file_path)
            for line_num, desc in findings:
                print(f"{rel_path}:{line_num}: {desc}")

if __name__ == '__main__':
    main()
