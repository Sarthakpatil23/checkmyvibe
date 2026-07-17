#!/usr/bin/env python3
import os
import sys
import re

SKIP_DIRS = {
    'node_modules', '.git', 'build', 'dist', '.next', '.svelte-kit', 
    '__pycache__', 'venv', '.venv', 'env', 'coverage', 'out'
}

SKIP_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', 
    '.gz', '.mp3', '.mp4', '.mov', '.db', '.sqlite', '.exe', '.dll',
    '.so', '.dylib', '.woff', '.woff2', '.ttf', '.eot', '.lock',
    '.package-lock.json', '.pnpm-lock.yaml', '.yarn.lock', '.map',
    '.svg', '.css', '.scss', '.less', '.html', '.xml'
}

# 1. Naming patterns for fake/mock/bypass authentication
AUTH_KEYWORDS = [
    r'mockAuth', r'fakeLogin', r'tempAuth', r'bypassAuth', 
    r'mockLogin', r'fakeAuth', r'bypassLogin', r'dummyAuth',
    r'bypassUser', r'mockUser', r'fakeUser'
]
KEYWORD_REGEX = re.compile(r'(?i)\b(' + '|'.join(AUTH_KEYWORDS) + r')\b')

# 2. Stubbed functions or parameters returning true (always passing)
STUB_PATTERNS = [
    # JS arrow function returning true: e.g. checkAuth = () => true
    (re.compile(r'(?i)\b\w*(?:auth|login|signin|signup|admin|role|permission|credential)\w*\b\s*=\s*(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>\s*true\b(?!\s*==)'), 
     "Arrow function returning true directly"),
    
    # JS standard function returning true: function checkAuth(...) { return true; }
    (re.compile(r'(?i)\bfunction\s+\w*(?:auth|login|signin|signup|admin|role|permission|credential)\w*\b\s*\([^)]*\)\s*\{\s*return\s+true;?\s*\}'),
     "Function returning true directly"),
     
    # Python function returning True: def is_auth(...): return True
    (re.compile(r'(?i)\bdef\s+\w*(?:auth|login|signin|signup|admin|role|permission|credential)\w*\b\s*\([^)]*\)\s*:\s*return\s+True\b'),
     "Python function returning True directly"),
     
    # Generic bypass function or property: e.g. "authBypass: true", "skipAuth: true"
    (re.compile(r'(?i)\b(?:authBypass|skipAuth|disableAuth|bypassAuthentication|devAuth)\b\s*:\s*true\b'),
     "Authentication bypass flag set to true")
]

def is_binary(file_path):
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
            content = f.read()
            
        lines = content.splitlines()
        
        # 1. Search for keyword matches line by line
        for line_num, line in enumerate(lines, 1):
            match = KEYWORD_REGEX.search(line)
            if match:
                findings.append((line_num, f"Mock/Bypass auth keyword '{match.group(1)}' found", line.strip()))
                
        # 2. Search for stub patterns in the file content
        for pattern, desc in STUB_PATTERNS:
            for match in pattern.finditer(content):
                start_pos = match.start()
                # Find line number of this match
                line_num = content.count('\n', 0, start_pos) + 1
                matched_text = match.group(0).replace('\n', ' ').strip()
                # Avoid adding multiple duplicate findings for the same line
                if not any(f[0] == line_num for f in findings):
                    findings.append((line_num, f"Stubbed Auth: {desc}", matched_text))
                    
    except Exception:
        pass
        
    findings.sort(key=lambda x: x[0])
    return findings

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    target_dir = os.path.abspath(target_dir)
    
    if not os.path.exists(target_dir):
        print(f"Error: Path '{target_dir}' does not exist.")
        sys.exit(1)
        
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SKIP_EXTS or file.startswith('.'):
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, target_dir)
            
            findings = scan_file(file_path)
            for line_num, desc, context in findings:
                print(f"{rel_path}:{line_num}: {desc} -> `{context}`")

if __name__ == '__main__':
    main()
