import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const rootDir = path.resolve();
const uiDir = path.join(rootDir, 'vertigo-ui');
const backendDir = path.join(rootDir, 'vertigo-backend');
const buildDir = path.resolve(rootDir, '../Build');

// Step 1: Read version
const pkg = JSON.parse(fs.readFileSync(path.join(uiDir, 'package.json'), 'utf8'));
const version = pkg.version;
const versionedBuildPath = path.join(buildDir, `vertigo_${version}`);

// Step 2: Build frontend
console.log('📦 Building frontend...');
execSync('npm run build', { cwd: "vertigo-backend/api/wwwroot", stdio: 'inherit' });

// Step 3: Prepare versioned folder
console.log(`📁 Creating versioned folder: ${versionedBuildPath}`);
if (!fs.existsSync(buildDir)) fs.mkdirSync(buildDir);
if (fs.existsSync(versionedBuildPath)) fs.rmSync(versionedBuildPath, { recursive: true });
fs.mkdirSync(versionedBuildPath);

// Step 4: Copy folders
console.log('📤 Copying backend and (optionally) frontend sources...');
execSync(`cp -r "${backendDir}" "${versionedBuildPath}/vertigo-backend"`);

// Step 5: Remove unwanted folders from backend copy
const backendCopyPath = path.join(versionedBuildPath, 'vertigo-backend');
const removeDirs = ['Config', 'env'];

removeDirs.forEach(dir => {
  const fullPath = path.join(backendCopyPath, dir);
  if (fs.existsSync(fullPath)) {
    fs.rmSync(fullPath, { recursive: true, force: true });
    console.log(`🧹 Removed ${dir} from backend copy.`);
  }
});

console.log('✅ Release completed successfully.');