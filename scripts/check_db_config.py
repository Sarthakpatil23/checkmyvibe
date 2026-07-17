#!/usr/bin/env python3
import os
import sys
import re

SKIP_DIRS = {'node_modules', '.git', 'dist', 'build'}

# Permissive rules patterns for Firestore and Firebase Storage
FIREBASE_PERMISSIVE = re.compile(r'allow\s+[\w\s,]+:\s*if\s+true\s*;')

# Permissive Realtime Database rules
RTDB_PERMISSIVE = re.compile(r'"\.(read|write)"\s*:\s*"true"')

# Permissive policies in Supabase / SQL schema definition
SUPABASE_PERMISSIVE_POLICY = re.compile(r'(?i)create\s+policy\s+\w+\s+on\s+\w+\s+(?:for\s+\w+\s+)?to\s+(?:public|anon)\s+using\s*\(\s*true\s*\)')
SUPABASE_PERMISSIVE_POLICY_SIMPLE = re.compile(r'(?i)using\s*\(\s*true\s*\)|with\s+check\s*\(\s*true\s*\)')

def scan_firebase_rules(file_path):
    """Scan Firestore/Storage rules for allow-all statements."""
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if FIREBASE_PERMISSIVE.search(clean_line):
                    findings.append((line_num, f"Permissive allow-all rule found: `{clean_line}`"))
    except Exception:
        pass
    return findings

def scan_rtdb_rules(file_path):
    """Scan Firebase Realtime Database rules for true reads/writes."""
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if RTDB_PERMISSIVE.search(clean_line):
                    findings.append((line_num, f"Permissive RTDB allow-all rule found: `{clean_line}`"))
    except Exception:
        pass
    return findings

def scan_sql_rls(file_path):
    """Scan SQL files to check if RLS is enabled on all tables and check for permissive policies."""
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # 1. Strip comments to avoid false matches (e.g. commented-out commands or code annotations)
        # Strip single-line -- comments
        content_no_comments = re.sub(r'--.*$', '', content, flags=re.M)
        # Strip multiline /* */ comments
        content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.S)

        # 2. Find all CREATE TABLE statements (support schemas, quotes, etc.)
        created_tables = re.findall(r'(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?([\w\.]+)', content_no_comments)
        # Find all ENABLE ROW LEVEL SECURITY statements
        enabled_rls = re.findall(r'(?i)alter\s+table\s+(?:if\s+exists\s+)?([\w\.]+)\s+enable\s+row\s+level\s+security', content_no_comments)
        
        # Clean table names (strip quotes, normalize schemas)
        def clean_table_name(t):
            t = t.replace('"', '').replace("'", "")
            if '.' in t:
                t = t.split('.')[-1]
            return t.lower()
            
        created_clean = [clean_table_name(t) for t in created_tables]
        enabled_clean = [clean_table_name(t) for t in enabled_rls]
        
        for idx, table in enumerate(created_tables):
            clean_t = clean_table_name(table)
            if clean_t not in enabled_clean:
                # Find line number in original file
                escaped_t = re.escape(table)
                match = re.search(r'(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?' + escaped_t, content)
                line_num = content.count('\n', 0, match.start()) + 1 if match else 1
                findings.append((line_num, f"Table '{table}' is created but Row Level Security (RLS) is not enabled"))
                
        # 3. Find permissive policies:
        # Search for CREATE POLICY ... USING (true) or WITH CHECK (true)
        # Handles multiline policy definitions and quoted policy names
        policy_pattern = re.compile(
            r'(?i)create\s+policy\s+("[^"]+"|[a-zA-Z_]\w*)\s+on\s+([\w\.]+)\s+[^;]+?(?:using|with\s+check)\s*\(\s*true\s*\)',
            re.DOTALL
        )
        
        for match in policy_pattern.finditer(content_no_comments):
            policy_name = match.group(1)
            table_name = match.group(2)
            # Find the character position of this policy match in the original content
            orig_match = re.search(r'(?i)create\s+policy\s+' + re.escape(policy_name), content)
            line_num = content.count('\n', 0, orig_match.start()) + 1 if orig_match else 1
            findings.append((line_num, f"Permissive policy {policy_name} on table {table_name} allows public read/write via USING(true) / CHECK(true)"))
            
    except Exception:
        pass
    return findings

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    target_dir = os.path.abspath(target_dir)
    
    findings_by_file = {}
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, target_dir)
            
            # Check for Firebase Firestore/Storage rules
            if file in ['firestore.rules', 'storage.rules']:
                file_findings = scan_firebase_rules(file_path)
                if file_findings:
                    findings_by_file[rel_path] = file_findings
                    
            # Check for Firebase Realtime Database rules
            elif file == 'database.rules.json':
                file_findings = scan_rtdb_rules(file_path)
                if file_findings:
                    findings_by_file[rel_path] = file_findings
                    
            # Check for SQL migrations/schema files
            elif file.endswith('.sql'):
                file_findings = scan_sql_rls(file_path)
                if file_findings:
                    findings_by_file[rel_path] = file_findings
                    
    # Output findings
    if not findings_by_file:
        print("PASS: No database security misconfigurations detected in configuration files.")
        sys.exit(0)
        
    print("FAIL: The following database security issues were found:")
    for rel_path, file_findings in findings_by_file.items():
        for line_num, desc in file_findings:
            print(f"{rel_path}:{line_num}: {desc}")
    sys.exit(1)

if __name__ == '__main__':
    main()
