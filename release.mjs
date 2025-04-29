import { fileURLToPath } from 'url';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Actual project paths
const rootDir = path.resolve(__dirname);
const uiDir = path.join(rootDir, 'vertigo-ui');
const backendDir = path.join(rootDir, 'vertigo-backend');
const buildDir = path.resolve(rootDir, '../Build');

// Step 1: Read version
const pkg = JSON.parse(fs.readFileSync(path.join(uiDir, 'package.json'), 'utf8'));
const version = pkg.version;
const versionedBuildPath = path.join(buildDir, `vertigo_${version}`);

// Step 2: Build frontend
console.log('📦 Building frontend...');
try {
  // Changed to use absolute path and proper Windows commands
  const buildCommand = process.platform === 'win32' ? 'npm.cmd run build' : 'npm run build';
  execSync(buildCommand, { 
    cwd: uiDir,  // Fixed path
    stdio: 'inherit',
    shell: true,
    env: process.env  // Explicitly pass environment
  });
} catch (error) {
  console.error('🚨 Frontend build failed!');
  process.exit(1);
}

// Step 3: Prepare versioned folder
console.log(`📁 Creating versioned folder: ${versionedBuildPath}`);
if (!fs.existsSync(buildDir)) fs.mkdirSync(buildDir, { recursive: true });
if (fs.existsSync(versionedBuildPath)) fs.rmSync(versionedBuildPath, { recursive: true });
fs.mkdirSync(versionedBuildPath);

// Step 4: Copy folders
console.log('📤 Copying backend and (optionally) frontend sources...');
try {
  // Windows-safe copy command
  const copyCommand = process.platform === 'win32' 
    ? `xcopy /E /I "${backendDir}" "${versionedBuildPath}"`
    : `cp -r "${backendDir}" "${versionedBuildPath}/vertigo-backend"`;
  
  execSync(copyCommand, { stdio: 'inherit', shell: true });
} catch (error) {
  console.error('🚨 Copy operation failed!');
  process.exit(1);
}

// Step 5: Remove unwanted folders from backend copy
const backendCopyPath = path.join(versionedBuildPath);
const removeDirs = ['Config', 'env'];

removeDirs.forEach(dir => {
  const fullPath = path.join(backendCopyPath, dir);
  if (fs.existsSync(fullPath)) {
    fs.rmSync(fullPath, { recursive: true, force: true });
    console.log(`🧹 Removed ${dir} from backend copy.`);
  }
});

console.log('✅ Release completed successfully.');
