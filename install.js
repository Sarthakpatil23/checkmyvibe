#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

// Source paths in the npm package
const srcSkill = path.join(__dirname, 'SKILL.md');
const srcScripts = path.join(__dirname, 'scripts');
const srcReferences = path.join(__dirname, 'references');

// Destination selection
const cwd = process.cwd();
const hasLocalClaude = fs.existsSync(path.join(cwd, '.claude'));

const localDest = path.join(cwd, '.claude', 'skills', 'checkmyvibe');
const globalDest = path.join(os.homedir(), '.claude', 'skills', 'checkmyvibe');

function copyRecursiveSync(src, dest) {
  if (fs.statSync(src).isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach((child) => {
      copyRecursiveSync(path.join(src, child), path.join(dest, child));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

function performInstall(destPath) {
  try {
    console.log(`\nInstalling checkmyvibe to: ${destPath}...`);
    
    // Clear destination if it already exists (overwrite mode)
    if (fs.existsSync(destPath)) {
      if (fs.rmSync) {
        fs.rmSync(destPath, { recursive: true, force: true });
      } else {
        fs.rmdirSync(destPath, { recursive: true });
      }
    }
    fs.mkdirSync(destPath, { recursive: true });

    // Copy SKILL.md
    fs.copyFileSync(srcSkill, path.join(destPath, 'SKILL.md'));
    
    // Copy folders
    copyRecursiveSync(srcScripts, path.join(destPath, 'scripts'));
    copyRecursiveSync(srcReferences, path.join(destPath, 'references'));

    console.log('\n=========================================');
    console.log('🎉 checkmyvibe Agent Skill installed!');
    console.log('=========================================');
    console.log('\nHow to run checkmyvibe:');
    console.log('1. Open your terminal in the target repository.');
    console.log('2. Ask your coding agent: "run checkmyvibe" or "perform a readiness check"');
    console.log('3. The agent will execute checkmyvibe\'s checks and output a prioritized report!');
    console.log('=========================================\n');
  } catch (err) {
    console.error('Error installing skill:', err.message);
    process.exit(1);
  }
}

if (hasLocalClaude) {
  // If .claude folder exists in the project root, install at project level directly
  performInstall(localDest);
} else {
  // Prompt user for local vs global/personal installation
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('No local .claude/ directory detected in the current working directory.');
  console.log(`1. Install locally to current directory: ${path.join('.claude', 'skills', 'checkmyvibe')}`);
  console.log(`2. Install globally/personally: ${globalDest.replace(os.homedir(), '~')}`);
  
  rl.question('\nSelect installation destination (1 or 2, default 2): ', (answer) => {
    rl.close();
    const selection = answer.trim();
    if (selection === '1') {
      performInstall(localDest);
    } else {
      performInstall(globalDest);
    }
  });
}
