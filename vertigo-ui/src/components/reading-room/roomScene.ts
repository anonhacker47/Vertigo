/** The 3D shelf: a Three.js set seen head on. Nothing here depends on Vue; the view talks to it through the handle. */
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { RectAreaLightUniformsLib } from "three/examples/jsm/lights/RectAreaLightUniformsLib.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import smileyUrl from "@/assets/comedian-smiley.png";
import type { RoomCharacter, RoomIssue, RoomItem, RoomSeries, RoomSummary } from "./roomData";

/** A shelfie: a straight-on photo of the bookcase, kept as a print on the wall and as a JPEG. */
export interface RoomPhoto {
  id: number;
  taken: Date;
  url: string; // an object URL for the JPEG; the room revokes it when the print goes
}

export interface RoomOptions {
  onPhoto?: (photo: RoomPhoto | null) => void;
  onCharacter?: (character: RoomCharacter | null) => void;
  /** The shelf shows one page of the collection at a time; this reports which, and when it is mid-turn. */
  onPage?: (page: number, pages: number, busy: boolean) => void;
  /** Where the foot of the shelf sits on screen, as fractions of the stage, whenever that moves. */
  onLayout?: (shelfFoot: { x: number; y: number }) => void;
  /** Whether anything is in hand right now; the logo has no card, so onPick alone cannot say. */
  onHold?: (held: boolean) => void;
  /** The room has a secret; this says when it is showing. */
  onSecret?: (open: boolean) => void;
  onProgress?: (loaded: number, total: number) => void;
  onPick?: (item: RoomItem | null) => void;
  onHover?: (item: RoomItem | null) => void;
}

export interface RoomHandle {
  showPage(page: number): void;
  /** Takes a shelfie and pins it; null while the bookcase is away. */
  takeShelfie(): RoomPhoto | null;
  removePhoto(id: number): void;
  /** Stands pictures of these characters in the shelf's empty end slots. */
  setCharacters(list: RoomCharacter[]): void;
  /** What the plaque in the secret says; it can arrive after the room is up. */
  setSummary(summary: RoomSummary | null): void;
  putBack(): void;
  dispose(): void;
}

interface TimeOfDay {
  sky: [string, string, string];
  wall: number;
  windowColor: number;
  windowIntensity: number;
  hemiSky: number;
  hemiGround: number;
  hemi: number;
  lamp: number;
  key: number;
  exposure: number;
  env: number;
  stars: boolean;
}

/** The room is always late: a starry sky, warm lamps, and the window a cool fill. */
const NIGHT: TimeOfDay = { sky: ["#060a1f", "#0f1738", "#1f2a58"], wall: 0x37424f, windowColor: 0x6f84c4, windowIntensity: 2.6, hemiSky: 0x3a4664, hemiGround: 0x3a2a1f, hemi: 0.34, lamp: 1.1, key: 0.6, exposure: 0.94, env: 0.1, stars: true };

const FACE = { w: 0.62, h: 0.93, d: 0.09 };
const FACE_PER_SHELF = 7;
const SHELF_ROWS = 5;
/** How many series stand face out on the shelf at once. */
export const SHELF_SLOTS = FACE_PER_SHELF * SHELF_ROWS;
const FACE_STEP = 0.52;
const KEY_INTENSITY = 26;
const CAM = { x: 0.2, y: 2.25, z: 9.4, tx: 0.2, ty: 2.15, tz: -3 };
const BZ = -4; // the back wall
const H = 6.2; // the ceiling
/** A comic changing over to another item: it steps out, turns edge on, swaps, and turns back. */
interface Flip {
  start: number;
  dur: number;
  item: RoomItem | null;
  swapped: boolean;
}
/** Something you can pick up: where it lives, and how it sits in the hand. */
interface Pickable {
  item: RoomItem | null;
  home: THREE.Vector3;
  homeQ: THREE.Quaternion;
  parent: THREE.Object3D;
  lift: number;
  reach: number; // how far in front of the camera it floats
  offsetX: number;
  offsetY: number;
  tilt: number; // how much it tips with the pointer
  glow: number; // how much of the hand lights it wants: a cover needs reading, dark glass does not
  spin: number; // its turn about its own upright axis while it changes over
  pop: number; // how far it has stepped out of the shelf for that
  out: THREE.Vector3; // which way it lifts toward you on hover, in its parent's frame
  flip?: Flip;
}

/** A small deterministic generator, so the room looks the same every visit. */
function mulberry32(seed: number) {
  let a = seed | 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function createRoom(container: HTMLElement, series: RoomSeries[], issues: RoomIssue[], options: RoomOptions = {}): RoomHandle {
  const rng = mulberry32(21);
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio || 1));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.04;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.shadowMap.autoUpdate = false; // refreshed every other frame from the loop
  container.appendChild(renderer.domElement);
  RectAreaLightUniformsLib.init();

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0b10);
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 60);
  let disposed = false;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new RoomEnvironment();
  scene.environment = pmrem.fromScene(envScene, 0.04).texture;
  (envScene as THREE.Scene & { dispose?: () => void }).dispose?.();
  pmrem.dispose();
  scene.add(camera);
  const handLight = new THREE.PointLight(0xfff1dc, 0, 7, 2);
  handLight.position.set(1.0, 0.9, -0.8);
  camera.add(handLight);
  const handFill = new THREE.PointLight(0xffd9b8, 0, 6, 2);
  handFill.position.set(-1.1, -0.2, -0.6);
  camera.add(handFill);

  const pickables: THREE.Object3D[] = [];
  const states = new Map<THREE.Object3D, Pickable>();
  const coverMaterials = new Map<string, THREE.MeshPhysicalMaterial>();
  const disposables: { dispose(): void }[] = [];
  const mouse = new THREE.Vector2(-10, -10);
  const raycaster = new THREE.Raycaster();
  let hovered: THREE.Object3D | null = null;
  let focused: THREE.Object3D | null = null;
  let lastMove = 0;
  let frameNo = 0;
  let shadowFrames = 6; // shadow maps re-render only while something moves, plus a frame to settle
  let lean = 0;
  let camLean = 0;
  let loaded = 0;
  let total = 0;

  // ---- helpers ------------------------------------------------------------------------------
  const keep = <T extends { dispose(): void }>(g: T): T => { disposables.push(g); return g; };
  const std = (color: THREE.ColorRepresentation, roughness = 0.9, extra: THREE.MeshStandardMaterialParameters = {}) =>
    keep(new THREE.MeshStandardMaterial({ color, roughness, metalness: 0, ...extra }));
  const brassMat = keep(new THREE.MeshStandardMaterial({ color: 0xb08a3e, roughness: 0.32, metalness: 0.9 }));
  const box = (w: number, h: number, d: number, r = 0.02) => {
    const radius = Math.max(0.004, Math.min(r, w / 2, h / 2, d / 2));
    return keep(new RoundedBoxGeometry(w, h, d, radius <= 0.004 ? 1 : radius < 0.04 ? 2 : 3, radius)); // segments by how much rounding shows
  };
  const cyl = (rt: number, rb: number, h: number, seg = 32, open = false) => keep(new THREE.CylinderGeometry(rt, rb, h, seg, 1, open));
  const sphere = (r: number, w = 24, h = 18) => keep(new THREE.SphereGeometry(r, w, h));
  const capsule = (r: number, l: number, cs = 8, rs = 20) => keep(new THREE.CapsuleGeometry(r, l, cs, rs));
  interface Place { shadow?: boolean; parent?: THREE.Object3D; rot?: [number, number, number] }
  function put(geo: THREE.BufferGeometry, mat: THREE.Material | THREE.Material[], x: number, y: number, z: number, { shadow = true, parent = scene, rot }: Place = {}) {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    if (rot) m.rotation.set(rot[0], rot[1], rot[2]);
    m.castShadow = shadow;
    m.receiveShadow = true;
    parent.add(m);
    return m;
  }
  /** Static meshes under `root` that share a material become one mesh each; `skip` subtrees stay as they are. */
  function mergeStatic(root: THREE.Object3D, skip: THREE.Object3D[] = []) {
    const skipSet = new Set<THREE.Object3D>();
    for (const o of skip) o.traverse((c) => skipSet.add(c));
    scene.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert(), local = new THREE.Matrix4();
    // materials made alike are treated alike, so pieces built with their own copy of the same settings still merge
    const signature = (m: THREE.Mesh) => {
      const x = m.material as THREE.MeshPhysicalMaterial;
      return [x.type, x.color?.getHex(), x.roughness, x.metalness, x.map?.uuid, x.bumpMap?.uuid, x.bumpScale, x.normalMap?.uuid, x.emissive?.getHex(), x.emissiveIntensity, x.emissiveMap?.uuid, x.side, x.transparent, x.opacity, x.blending, x.depthWrite, x.clearcoat, x.envMap?.uuid, x.envMapIntensity, m.castShadow, m.receiveShadow, m.renderOrder].join("|");
    };
    const groups = new Map<string, { mat: THREE.Material; geos: THREE.BufferGeometry[]; meshes: THREE.Mesh[]; cast: boolean; receive: boolean; order: number }>();
    root.traverse((o) => {
      const m = o as THREE.Mesh;
      if (!m.isMesh || m === root || !m.visible || skipSet.has(m) || m.children.length || Array.isArray(m.material) || (m.material as THREE.Material).onBeforeCompile !== THREE.Material.prototype.onBeforeCompile) return;
      const geo = (m.geometry.index ? m.geometry.toNonIndexed() : m.geometry.clone()).applyMatrix4(local.multiplyMatrices(inv, m.matrixWorld));
      for (const name of Object.keys(geo.attributes)) if (name !== "position" && name !== "normal" && name !== "uv") geo.deleteAttribute(name);
      if (!geo.attributes.uv) geo.setAttribute("uv", new THREE.Float32BufferAttribute(new Float32Array(geo.attributes.position.count * 2), 2));
      const key = signature(m);
      const g = groups.get(key) ?? { mat: m.material as THREE.Material, geos: [], meshes: [], cast: false, receive: false, order: m.renderOrder };
      g.geos.push(geo); g.meshes.push(m); g.cast ||= m.castShadow; g.receive ||= m.receiveShadow;
      groups.set(key, g);
    });
    for (const g of groups.values()) {
      const merged = g.meshes.length > 1 ? mergeGeometries(g.geos, false) : null;
      g.geos.forEach((x) => x.dispose());
      if (!merged) continue;
      for (const m of g.meshes) m.parent?.remove(m);
      const mesh = new THREE.Mesh(keep(merged), g.mat);
      mesh.castShadow = g.cast; mesh.receiveShadow = g.receive; mesh.renderOrder = g.order;
      root.add(mesh);
    }
  }
  /** Many small static pieces of one material become one draw call. */
  interface Piece { geo: THREE.BufferGeometry; x: number; y: number; z: number; rot?: [number, number, number] }
  function merged(mat: THREE.Material, pieces: Piece[], shadow = false) {
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), one = new THREE.Vector3(1, 1, 1), p = new THREE.Vector3(), e = new THREE.Euler();
    const geos = pieces.map((piece) => {
      const g = piece.geo.clone();
      e.set(...(piece.rot ?? [0, 0, 0]));
      m4.compose(p.set(piece.x, piece.y, piece.z), q.setFromEuler(e), one);
      g.applyMatrix4(m4);
      return g;
    });
    const all = mergeGeometries(geos, false);
    geos.forEach((g) => g.dispose());
    if (!all) return null;
    keep(all);
    const mesh = new THREE.Mesh(all, mat);
    mesh.castShadow = shadow;
    mesh.receiveShadow = true;
    scene.add(mesh);
    return mesh;
  }
  function canvasTexture(draw: (g: CanvasRenderingContext2D, w: number, h: number) => void, w = 256, h = 256, srgb = true) {
    const c = document.createElement("canvas");
    c.width = w;
    c.height = h;
    draw(c.getContext("2d") as CanvasRenderingContext2D, w, h);
    const t = keep(new THREE.CanvasTexture(c));
    if (srgb) t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    return t;
  }
  function grainTexture(strength = 1, repeat = 4) {
    const t = canvasTexture((g, w, h) => {
      const img = g.createImageData(w, h);
      for (let i = 0; i < img.data.length; i += 4) { const v = 128 + (rng() - 0.5) * 70 * strength; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      g.putImageData(img, 0, 0);
    }, 256, 256, false);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(repeat, repeat);
    return t;
  }
  function radialSprite(color: string) {
    return canvasTexture((g) => {
      const gr = g.createRadialGradient(64, 64, 2, 64, 64, 64);
      gr.addColorStop(0, color);
      gr.addColorStop(0.35, color.replace(/[\d.]+\)$/, "0.35)"));
      gr.addColorStop(1, color.replace(/[\d.]+\)$/, "0)"));
      g.fillStyle = gr;
      g.fillRect(0, 0, 128, 128);
    }, 128, 128);
  }
  let blobTexture: THREE.Texture | null = null;
  function blob(x: number, z: number, w: number, d: number, opacity = 0.4) {
    if (!blobTexture) blobTexture = radialSprite("rgba(0,0,0,1)");
    const m = new THREE.Mesh(keep(new THREE.PlaneGeometry(w, d)), keep(new THREE.MeshBasicMaterial({ map: blobTexture, transparent: true, opacity, depthWrite: false })));
    m.rotation.x = -Math.PI / 2;
    m.position.set(x, 0.012, z);
    m.renderOrder = 1;
    scene.add(m);
  }
  const woodCanvas = (light: number) => (g: CanvasRenderingContext2D) => {
    for (let row = 0; row < 8; row++) {
      let x = -((row * 173) % 300);
      while (x < 512) {
        const len = 180 + ((row * 97 + x) % 200);
        g.fillStyle = `hsl(${24 + rng() * 6} ${30 + rng() * 10}% ${light + rng() * 6}%)`;
        g.fillRect(x, row * 64, len, 64);
        for (let k = 0; k < 10; k++) { g.fillStyle = `rgba(0,0,0,${0.04 + rng() * 0.07})`; g.fillRect(x + rng() * len, row * 64 + rng() * 62, 40 + rng() * len * 0.6, 1 + rng()); }
        if (rng() < 0.3) { g.fillStyle = "rgba(0,0,0,.25)"; g.beginPath(); g.ellipse(x + rng() * len, row * 64 + 20 + rng() * 24, 5, 3, rng(), 0, Math.PI * 2); g.fill(); }
        g.fillStyle = "rgba(0,0,0,.45)"; g.fillRect(x + len - 2, row * 64, 2, 64);
        x += len;
      }
      g.fillStyle = "rgba(0,0,0,.5)"; g.fillRect(0, row * 64 + 62, 512, 2);
    }
  };
  function woodTexture(light: number, along = true) {
    const t = canvasTexture(woodCanvas(light), 512, 512);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(2.2, 2.2);
    if (along) t.rotation = Math.PI / 2;
    return t;
  }
  const skyTexture = () => canvasTexture((g) => {
    const T = NIGHT;
    const gr = g.createLinearGradient(0, 0, 0, 256);
    gr.addColorStop(0, T.sky[0]); gr.addColorStop(0.62, T.sky[1]); gr.addColorStop(1, T.sky[2]);
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
    if (T.stars) {
      g.fillStyle = "#fff";
      for (let i = 0; i < 90; i++) { g.globalAlpha = 0.4 + rng() * 0.6; g.fillRect(rng() * 256, rng() * 150, 1.3, 1.3); }
      g.globalAlpha = 1;
      const m = g.createRadialGradient(196, 54, 2, 196, 54, 40); m.addColorStop(0, "rgba(255,246,216,1)"); m.addColorStop(0.35, "rgba(255,246,216,.9)"); m.addColorStop(0.4, "rgba(255,246,216,.15)"); m.addColorStop(1, "rgba(255,246,216,0)");
      g.fillStyle = m; g.fillRect(140, 0, 120, 120);
    }
    g.fillStyle = "rgba(8,10,22,.75)"; g.beginPath(); g.moveTo(0, 256);
    for (let x = 0; x <= 256; x += 6) g.lineTo(x, 206 + Math.sin(x / 23) * 9 + Math.sin(x / 7) * 3);
    g.lineTo(256, 256); g.closePath(); g.fill();
  });
  // the city outside: Gibbons-style window grids
  const townTexture = () => canvasTexture((g, w, h) => {
    g.clearRect(0, 0, w, h);
    const block = (x: number, top: number, bw: number, body: string, lights: string[], pitch: number, size: number, lit: number) => {
      g.fillStyle = body; g.fillRect(x, top, bw, h - top);
      for (let wy = top + pitch * 0.7; wy < h - size; wy += pitch) {
        for (let wx = x + pitch * 0.45; wx < x + bw - size; wx += pitch) {
          if (rng() < lit) { g.fillStyle = lights[Math.floor(rng() * lights.length)]; g.fillRect(wx, wy, size, size); }
        }
      }
    };
    for (let x = 0; x < w; ) { const bw = 30 + rng() * 60, top = 40 + rng() * 170; block(x, top, bw, "#0f1a30", ["rgba(140,180,255,.6)", "rgba(120,160,230,.4)", "rgba(190,210,255,.5)"], 7, 3, 0.55); x += bw + 2 + rng() * 8; }
    for (let x = -10; x < w; ) { const bw = 36 + rng() * 90, top = 120 + rng() * 250; block(x, top, bw, "#06070d", ["#f6c24a", "#f6c24a", "#f6c24a", "#f08a2a", "#ffe08a", "#d8321c", "#4fc46a"], 8, 4, 0.64); x += bw + 3 + rng() * 12; }
  }, 1024, 512);
  function coverPlaceholder(s: RoomItem) {
    return canvasTexture((g) => {
      const [r, gg, b] = s.rgb;
      const grad = g.createLinearGradient(0, 0, 200, 384);
      grad.addColorStop(0, `rgb(${r},${gg},${b})`);
      grad.addColorStop(1, `rgb(${Math.round(r * 0.45)},${Math.round(gg * 0.45)},${Math.round(b * 0.45)})`);
      g.fillStyle = grad; g.fillRect(0, 0, 256, 384);
      g.fillStyle = "rgba(255,255,255,.85)"; g.font = "900 26px Nunito, sans-serif"; g.textBaseline = "top";
      let line = "", y = 40;
      for (const w of s.title.split(" ")) {
        const t = line ? line + " " + w : w;
        if (g.measureText(t).width > 220) { g.fillText(line, 18, y); y += 30; line = w; } else line = t;
      }
      g.fillText(line, 18, y);
    }, 256, 384);
  }
  // the spine crease the app's cover tiles draw, baked into the colour; the normal map catches the lamps
  const spineShade = (shader: THREE.WebGLProgramParametersWithUniforms) => {
    shader.fragmentShader = shader.fragmentShader.replace(
      "#include <map_fragment>",
      `#include <map_fragment>
      #ifdef USE_MAP
      {
        float u = vMapUv.x;
        float s = u < 0.012 ? mix(0.7, 1.3, u / 0.012)
          : u < 0.06 ? mix(1.3, 1.0, (u - 0.012) / 0.048)
          : u < 0.08 ? mix(1.0, 0.8, (u - 0.06) / 0.02)
          : u < 0.092 ? mix(0.8, 1.2, (u - 0.08) / 0.012)
          : mix(1.2, 1.0, clamp((u - 0.092) / 0.11, 0.0, 1.0));
        diffuseColor.rgb *= s;
      }
      #endif`,
    );
  };
  const spineNormal = canvasTexture((g, w, h) => {
    const img = g.createImageData(w, h);
    const lift = (u: number) => (u < 0.012 ? u / 0.012 : u < 0.06 ? 1 : u < 0.08 ? 1 - (u - 0.06) / 0.02 : u < 0.092 ? (u - 0.08) / 0.012 : 1);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        const nx = -(lift((x + 1) / w) - lift((x - 1) / w)) * 1.4 + (rng() - 0.5) * 0.08;
        const ny = (rng() - 0.5) * 0.08;
        const len = Math.hypot(nx, ny, 1);
        img.data[i] = ((nx / len) * 0.5 + 0.5) * 255; img.data[i + 1] = ((ny / len) * 0.5 + 0.5) * 255; img.data[i + 2] = ((1 / len) * 0.5 + 0.5) * 255; img.data[i + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  }, 256, 256, false);
  /** The cover art as a glossy board with the spine crease, cached per series. */
  function coverMaterial(s: RoomItem, onDone: () => void) {
    const key = `${s.kind}:${s.id}`;
    const cached = coverMaterials.get(key);
    if (cached) { setTimeout(onDone, 0); return cached; }
    const mat = keep(new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.48, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.4, map: coverPlaceholder(s) }));
    mat.normalMap = spineNormal; mat.normalScale.set(0.6, 0.6); mat.onBeforeCompile = spineShade;
    coverMaterials.set(key, mat);
    const loader = new THREE.TextureLoader();
    loader.crossOrigin = "anonymous";
    loader.load(
      s.cover,
      (t) => { if (disposed) { t.dispose(); return; } t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; keep(t); mat.map?.dispose(); mat.map = t; mat.needsUpdate = true; onDone(); },
      undefined,
      () => onDone(),
    );
    return mat;
  }
  const pagesTexture = canvasTexture((g) => { g.fillStyle = "#e9e2d2"; g.fillRect(0, 0, 64, 64); for (let i = 0; i < 64; i += 2) { g.fillStyle = `rgba(0,0,0,${0.06 + rng() * 0.1})`; g.fillRect(0, i, 64, 1); } }, 64, 64);
  pagesTexture.wrapS = pagesTexture.wrapT = THREE.RepeatWrapping;
  pagesTexture.repeat.set(1, 6);
  const pages = std(0xffffff, 0.92, { map: pagesTexture });
  const plasterGrain = grainTexture(0.8, 3);
  const clothGrain = grainTexture(1.2, 6);

  function shelfUnit(width: number, height: number, depth: number, shelves: number, wood: THREE.Material, back: THREE.Material) {
    const g = new THREE.Group();
    const t = 0.07;
    put(box(t, height, depth, 0.01), wood, -width / 2 + t / 2, height / 2, 0, { parent: g });
    put(box(t, height, depth, 0.01), wood, width / 2 - t / 2, height / 2, 0, { parent: g });
    const backPanel = put(box(width, height, t, 0.005), back, 0, height / 2, -depth / 2 + t / 2, { parent: g });
    put(box(width + 0.14, t * 1.6, depth + 0.1, 0.015), wood, 0, height - t * 0.8, 0.03, { parent: g });
    put(box(width + 0.1, t * 1.2, depth + 0.06, 0.01), wood, 0, 0.02, 0.02, { parent: g });
    const ys: number[] = [];
    const lips: Piece[] = [];
    for (let k = 0; k < shelves; k++) {
      const y = 0.14 + k * ((height - 0.44) / shelves);
      put(box(width - 2 * t, t, depth - t, 0.008), wood, 0, y + t / 2, t / 2, { parent: g });
      lips.push({ geo: box(width - 2 * t, 0.012, 0.012, 0.004), x: 0, y: y + t + 0.006, z: depth / 2 - 0.01 });
      ys.push(y + t);
    }
    const lipMesh = merged(brassMat, lips);
    if (lipMesh) g.add(lipMesh);
    return { group: g, ys, inner: width - 2 * t - 0.12, backZ: -depth / 2 + t, back: backPanel };
  }
  /** A light you can switch: click any of its parts and its lights and glowing bits fade out, or back. */
  /** Halos and flames; the occlusion pass would draw these as solid squares, so it skips them. */
  const sprites: THREE.Sprite[] = [];
  interface Lamp { parts: THREE.Object3D[]; lights: { light: THREE.Light; max: number }[]; glows: { mat: THREE.MeshStandardMaterial; max: number }[]; on: boolean; level: number }
  const lamps: Lamp[] = [];
  const lampByMesh = new Map<THREE.Object3D, Lamp>();
  let lampHot: Lamp | null = null;
  const addLamp = (lamp: Lamp) => { lamps.push(lamp); for (const part of lamp.parts) lampByMesh.set(part, lamp); };
  function lamp(x: number, y: number, z: number, poleH: number, shadeR: number, power: number, drum = false, shadows = true) {
    const g = new THREE.Group();
    g.position.set(x, y, z);
    scene.add(g);
    put(keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.2, 0), new THREE.Vector2(0.2, 0.02), new THREE.Vector2(0.12, 0.05), new THREE.Vector2(0.05, 0.08), new THREE.Vector2(0.03, 0.1)], 32)), brassMat, 0, 0, 0, { parent: g });
    put(cyl(0.018, 0.018, poleH, 16), brassMat, 0, poleH / 2, 0, { parent: g });
    const bulbMat = std(0xfff3d6, 0.4, { emissive: 0xffd9a0, emissiveIntensity: 1.2 });
    put(sphere(0.06, 16, 12), bulbMat, 0, poleH + shadeR * 0.35, 0, { parent: g, shadow: false });
    const shadeMat = std(0xf3e5c9, 1, { side: THREE.DoubleSide, emissive: 0xffc48a, emissiveIntensity: 0.3, bumpMap: clothGrain, bumpScale: 0.004 });
    const shade = new THREE.Mesh(cyl(drum ? shadeR * 0.95 : shadeR * 0.66, shadeR, shadeR * (drum ? 0.9 : 1.15), 40, true), shadeMat);
    shade.position.set(0, poleH + shadeR * 0.4, 0);
    g.add(shade);
    put(keep(new THREE.TorusGeometry(drum ? shadeR * 0.95 : shadeR * 0.66, 0.006, 8, 40)), brassMat, 0, poleH + shadeR * 0.4 + (drum ? shadeR * 0.45 : shadeR * 0.575), 0, { parent: g, rot: [Math.PI / 2, 0, 0], shadow: false });
    const bulb = new THREE.SpotLight(0xffb36b, power * 2.2, 8, 1.0, 0.9, 1.3);
    bulb.position.set(0, poleH + shadeR * 0.15, 0);
    bulb.target.position.set(0, 0, 0);
    if (shadows) { bulb.castShadow = true; bulb.shadow.mapSize.set(512, 512); bulb.shadow.bias = -0.0006; bulb.shadow.radius = 4; }
    g.add(bulb, bulb.target);
    const parts: THREE.Object3D[] = [];
    g.traverse((o) => { if ((o as THREE.Mesh).isMesh) parts.push(o); });
    addLamp({ parts, lights: [{ light: bulb, max: power * 2.2 * NIGHT.lamp }], glows: [{ mat: shadeMat, max: 0.3 * NIGHT.lamp }, { mat: bulbMat, max: 1.2 }], on: true, level: 1 });
  }
  const leafShape = new THREE.Shape();
  leafShape.moveTo(0, 0);
  leafShape.bezierCurveTo(0.28, 0.12, 0.34, 0.55, 0, 0.9);
  leafShape.bezierCurveTo(-0.34, 0.55, -0.28, 0.12, 0, 0);
  const leafGeo = keep(new THREE.ExtrudeGeometry(leafShape, { depth: 0.008, bevelEnabled: false, curveSegments: 10 }));
  const UP = new THREE.Vector3(0, 1, 0);
  function plant(x: number, z: number, h: number, tall = false, parent: THREE.Object3D = scene) {
    const pot = std(0xb8705a, 0.75, { bumpMap: plasterGrain, bumpScale: 0.01 });
    put(keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.2, 0), new THREE.Vector2(0.26, 0.36), new THREE.Vector2(0.29, 0.38), new THREE.Vector2(0.29, 0.44), new THREE.Vector2(0.24, 0.44)], 32)), pot, x, 0, z, { parent });
    put(cyl(0.23, 0.23, 0.02, 24), std(0x2b2016, 1), x, 0.43, z, { parent, shadow: false });
    const leaves = tall ? 14 : 9;
    const stem = std(0x3f5c36, 0.9);
    for (let i = 0; i < leaves; i++) {
      const a = i * 2.39996 + rng() * 0.3;
      const size = (tall ? 0.6 : 0.42) * (0.75 + rng() * 0.5), rise = tall ? 0.6 + (i / leaves) * h * 1.3 : 0.4 + rng() * 0.25;
      const tilt = tall ? 0.55 + rng() * 0.5 : 0.9 + rng() * 0.5;
      const leaf = put(leafGeo, std(i % 3 ? 0x4f7f4b : 0x5d9256, 0.85), x + Math.cos(a) * 0.08, rise, z + Math.sin(a) * 0.08, { parent });
      leaf.rotation.set(-tilt, 0, 0);
      leaf.rotateOnWorldAxis(UP, -a + Math.PI / 2);
      leaf.scale.set(size, size, 1);
      if (tall) put(cyl(0.012, 0.016, rise - 0.4, 8), stem, x + Math.cos(a) * 0.03, 0.4 + (rise - 0.4) / 2, z + Math.sin(a) * 0.03, { parent, shadow: false });
    }
    if (parent === scene) blob(x, z, 1.1, 1.1, 0.35);
  }
  /** A comic as a slim hardcover: cover board and spine, then page block and back board. Groups: cover, pages. */
  function comicGeometry(w: number, h: number, d: number) {
    const board = 0.012, inset = 0.014;
    // the rounded boxes come non-indexed, so the plain ones must match before they can merge
    const plain = (geo: THREE.BufferGeometry) => { const n = geo.toNonIndexed(); geo.dispose(); return n; };
    const front = new RoundedBoxGeometry(w, h, board, 3, 0.006).translate(0, 0, d / 2 - board / 2);
    const block = plain(new THREE.BoxGeometry(w - inset, h - inset * 2, d - board * 2)).translate(inset / 2, 0, 0);
    const back = new RoundedBoxGeometry(w, h, board, 3, 0.006).translate(0, 0, -d / 2 + board / 2);
    const spine = plain(new THREE.BoxGeometry(0.02, h, d - board * 2)).translate(-w / 2 + 0.01, 0, 0);
    // the spine wears the cover's own left edge: every spine vertex samples a hair in from u = 0
    const uv = spine.attributes.uv as THREE.BufferAttribute, pos = spine.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, 0.004, (pos.getY(i) + h / 2) / h);
    const face = mergeGeometries([front, spine], false), body = mergeGeometries([block, back], false);
    if (!face || !body) throw new Error("comic geometry");
    const g = mergeGeometries([face, body], true);
    if (!g) throw new Error("comic geometry");
    for (const x of [front, block, back, spine, face, body]) x.dispose();
    return keep(g);
  }
  function addComic(s: RoomItem, geo: THREE.BufferGeometry, x: number, y: number, z: number, parent: THREE.Object3D, onDone: () => void) {
    const m = new THREE.Mesh(geo, [coverMaterial(s, onDone), pages]);
    m.position.set(x, y, z);
    m.rotation.x = -0.1;
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    pickables.push(m);
    states.set(m, { item: s, home: m.position.clone(), homeQ: m.quaternion.clone(), parent, lift: 0, reach: 2.2, offsetX: -0.3, offsetY: -0.05, tilt: 1, glow: 1, spin: 0, pop: 0, out: new THREE.Vector3(0, 0, 1) });
    return m;
  }
  /** The Vertigo mark as the solid its logo draws in isometric: two bars, two caps, a block where the sides meet. */
  function logoGeometry(height: number) {
    interface Face { pts: THREE.Vector3[]; lit: boolean }
    const V3 = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
    /** Faces of the box o + x·a + y·b + z·c, wound outward; `lit` lists the light faces, `skip` the ones another piece covers. */
    const boxFaces = (o: THREE.Vector3, a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3, lit: string[], skip: string[] = []): Face[] => {
      const flip = a.clone().cross(b).dot(c) < 0;
      const P = (x: number, y: number, z: number) => o.clone().addScaledVector(a, x).addScaledVector(b, y).addScaledVector(c, z);
      const face = (name: string, pts: THREE.Vector3[]): Face => ({ pts: flip ? pts.reverse() : pts, lit: lit.includes(name) });
      const all: [string, THREE.Vector3[]][] = [
        ["-a", [P(0, 0, 0), P(0, 0, 1), P(0, 1, 1), P(0, 1, 0)]],
        ["+a", [P(1, 0, 0), P(1, 1, 0), P(1, 1, 1), P(1, 0, 1)]],
        ["-b", [P(0, 0, 0), P(1, 0, 0), P(1, 0, 1), P(0, 0, 1)]],
        ["+b", [P(0, 1, 0), P(0, 1, 1), P(1, 1, 1), P(1, 1, 0)]],
        ["-c", [P(0, 0, 0), P(0, 1, 0), P(1, 1, 0), P(1, 0, 0)]],
        ["+c", [P(0, 0, 1), P(1, 0, 1), P(1, 1, 1), P(0, 1, 1)]],
      ];
      return all.filter(([name]) => !skip.includes(name)).map(([name, pts]) => face(name, pts));
    };
    /** Keeps the part of a convex solid on the n·p <= d side of a plane; `close` adds the new face on the cut. */
    const clip = (faces: Face[], n: THREE.Vector3, d: number, close = true): Face[] => {
      const out: Face[] = [], cut: THREE.Vector3[] = [];
      for (const f of faces) {
        const kept: THREE.Vector3[] = [];
        for (let i = 0; i < f.pts.length; i++) {
          const p = f.pts[i], q = f.pts[(i + 1) % f.pts.length];
          const sp = n.dot(p) - d, sq = n.dot(q) - d;
          if (sp <= 0) kept.push(p);
          if ((sp < 0 && sq > 0) || (sp > 0 && sq < 0)) { const x = p.clone().lerp(q, sp / (sp - sq)); kept.push(x); cut.push(x); }
        }
        if (kept.length >= 3) out.push({ pts: kept, lit: f.lit });
      }
      if (close && cut.length >= 3) {
        const centre = cut.reduce((sum, q) => sum.add(q), new THREE.Vector3()).multiplyScalar(1 / cut.length);
        const u = cut[0].clone().sub(centre).normalize(), v = n.clone().cross(u).normalize();
        const ring = cut
          .map((q) => ({ q, angle: Math.atan2(q.clone().sub(centre).dot(v), q.clone().sub(centre).dot(u)) }))
          .sort((x, y) => x.angle - y.angle)
          .map((x) => x.q)
          .filter((q, i, arr) => i === 0 || q.distanceTo(arr[i - 1]) > 1e-6);
        out.push({ pts: ring, lit: false });
      }
      return out;
    };
    // logo units: Z up, inner corner at X = Y = 0, cap tops at Z = 0; the right arm runs +X and down, the left mirrors it
    const W = 40, D = 67, T = 21, FLOOR = -169;
    const FRONT = 0.836 * 40 + 0.549 * T; // each bar's front face: 0.836·X + 0.549·Z = -FRONT (mirrored for the left arm)
    const right = V3(0.549, 0, -0.836).multiplyScalar(320), left = V3(0, 0.549, -0.836).multiplyScalar(320);
    const floor = (faces: Face[]) => clip(faces, V3(0, 0, -1), -FLOOR);
    const solid: Face[] = [
      ...boxFaces(V3(-107, 0, -T), V3(D, 0, 0), V3(0, W, 0), V3(0, 0, T), ["+a", "+c"], ["-c"]), // right cap: front and top light
      ...floor(clip(boxFaces(V3(-107, 0, -T), V3(D, 0, 0), V3(0, W, 0), right, ["+a"], ["-c"]), V3(1, -1, 0), 0, false)), // right bar
      ...boxFaces(V3(0, -107, -T), V3(W, 0, 0), V3(0, D, 0), V3(0, 0, T), ["+b", "+c"], ["-c"]), // left cap
      ...floor(clip(boxFaces(V3(0, -107, -T), V3(W, 0, 0), V3(0, D, 0), left, ["+b"], ["-c"]), V3(-1, 1, 0), 0, false)), // left bar
      ...clip(clip(boxFaces(V3(13.3, 13.3, FLOOR), V3(26.7, 0, 0), V3(0, 26.7, 0), V3(0, 0, -115 - FLOOR), ["+c"]), V3(-0.836, 0, -0.549), FRONT), V3(0, -0.836, -0.549), FRONT),
    ];
    const light: number[] = [], dark: number[] = [], lightUv: number[] = [], darkUv: number[] = [];
    const TILE = 260;
    for (const { pts, lit } of solid) {
      const out = lit ? light : dark, uvs = lit ? lightUv : darkUv;
      const u = pts[1].clone().sub(pts[0]).normalize();
      const n = u.clone().cross(pts[2].clone().sub(pts[0])).normalize();
      const v = n.cross(u);
      const ox = rng(), oy = rng();
      for (let i = 1; i + 1 < pts.length; i++) {
        for (const q of [pts[0], pts[i], pts[i + 1]]) {
          out.push(q.x, q.y, q.z);
          const d = q.clone().sub(pts[0]);
          uvs.push(ox + d.dot(u) / TILE, oy + d.dot(v) / TILE);
        }
      }
    }
    const iso = new THREE.Matrix4().makeBasis(V3(-0.7071, -0.4082, 0.5774), V3(0.7071, -0.4082, 0.5774), V3(0, 0.8165, 0.5774));
    const build = (arr: number[], uv: number[]) => {
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(arr, 3));
      g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
      g.applyMatrix4(iso);
      return g;
    };
    const parts = { light: build(light, lightUv), dark: build(dark, darkUv) };
    const box = new THREE.Box3();
    for (const g of Object.values(parts)) { g.computeBoundingBox(); box.union(g.boundingBox as THREE.Box3); }
    const k = height / (box.max.y - box.min.y);
    const fit = new THREE.Matrix4().makeScale(k, k, k).multiply(new THREE.Matrix4().makeTranslation(-(box.min.x + box.max.x) / 2, -box.min.y, -box.min.z));
    for (const g of Object.values(parts)) { g.applyMatrix4(fit); g.computeVertexNormals(); keep(g); }
    return parts;
  }
  /** Obsidian flow: a tiling height field of soft bumps as a normal map. */
  const obsidianFlow = (() => {
    const size = 256, h = new Float32Array(size * size);
    for (let i = 0; i < 44; i++) {
      const cx = rng() * size, cy = rng() * size, sigma = 18 + rng() * 54, amp = (rng() - 0.5) * 2;
      for (let y = 0; y < size; y++) {
        let dy = Math.abs(y - cy); dy = Math.min(dy, size - dy);
        for (let x = 0; x < size; x++) {
          let dx = Math.abs(x - cx); dx = Math.min(dx, size - dx);
          h[y * size + x] += amp * Math.exp(-(dx * dx + dy * dy) / (2 * sigma * sigma));
        }
      }
    }
    const t = canvasTexture((g) => {
      const img = g.createImageData(size, size);
      const at = (x: number, y: number) => h[((y + size) % size) * size + ((x + size) % size)];
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          const nx = -(at(x + 1, y) - at(x - 1, y)) * 0.9, ny = -(at(x, y + 1) - at(x, y - 1)) * 0.9, len = Math.hypot(nx, ny, 1);
          const i = (y * size + x) * 4;
          img.data[i] = ((nx / len) * 0.5 + 0.5) * 255; img.data[i + 1] = ((ny / len) * 0.5 + 0.5) * 255; img.data[i + 2] = ((1 / len) * 0.5 + 0.5) * 255; img.data[i + 3] = 255;
        }
      }
      g.putImageData(img, 0, 0);
    }, size, size, false);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  })();
  /** The mark, propped against the shelf back; it picks up like a comic. */
  function logo(x: number, y: number, z: number, height: number, parent: THREE.Object3D, turn = 0, lean = 0) {
    const g = new THREE.Group();
    g.position.set(x, y, z);
    g.rotation.order = "YXZ"; // lean back first, then turn
    g.rotation.set(-lean, turn, 0);
    parent.add(g);
    const { light, dark } = logoGeometry(height);
    // glass in the logo blues; it carries its own envMap because the scene's night setting mutes reflections
    const finish = (tone: number) => keep(new THREE.MeshPhysicalMaterial({ color: tone, emissive: tone, emissiveIntensity: 0.12, normalMap: obsidianFlow, normalScale: new THREE.Vector2(0.4, 0.4), roughness: 0.12, metalness: 0, ior: 1.5, clearcoat: 1, clearcoatRoughness: 0.05, envMap: scene.environment, envMapIntensity: 0.35 }));
    for (const [geo, c] of [[light, 0x127eff], [dark, 0x1159cc]] as const) {
      const m = new THREE.Mesh(geo, finish(c));
      m.castShadow = true;
      m.receiveShadow = true;
      g.add(m);
    }
    pickables.push(g);
    states.set(g, { item: null, home: g.position.clone(), homeQ: g.quaternion.clone(), parent, lift: 0, reach: 1.5, offsetX: 0, offsetY: -0.3, tilt: 1.7, glow: 0.3, spin: 0, pop: 0, out: new THREE.Vector3(0, 0, 1) });
  }
  /** A collector's figure: a bright little hero on a round base. */
  function figure(x: number, y: number, z: number, suit: number, cape: number | null, parent: THREE.Object3D, facing = 0) {
    const g = new THREE.Group();
    g.position.set(x, y, z);
    g.rotation.y = facing;
    parent.add(g);
    put(cyl(0.07, 0.075, 0.012, 24), std(0x202329, 0.5, { metalness: 0.3 }), 0, 0.006, 0, { parent: g, shadow: false });
    const suitMat = std(suit, 0.6), skin = std(0xe8c3a0, 0.7), dark = std(0x1a1c22, 0.6);
    put(capsule(0.022, 0.08, 4, 10), suitMat, -0.03, 0.07, 0, { parent: g });
    put(capsule(0.022, 0.08, 4, 10), suitMat, 0.03, 0.07, 0, { parent: g });
    put(capsule(0.05, 0.1, 6, 14), suitMat, 0, 0.19, 0, { parent: g });
    put(capsule(0.018, 0.09, 4, 10), suitMat, -0.07, 0.2, 0, { parent: g, rot: [0, 0, 0.35] });
    put(capsule(0.018, 0.09, 4, 10), suitMat, 0.07, 0.2, 0, { parent: g, rot: [0, 0, -0.35] });
    put(sphere(0.045, 16, 12), skin, 0, 0.31, 0, { parent: g });
    put(sphere(0.047, 16, 12), dark, 0, 0.32, -0.01, { parent: g, shadow: false }).scale.set(1, 0.7, 1);
    if (cape !== null) { const c = put(box(0.11, 0.2, 0.012, 0.004), std(cape, 0.8), 0, 0.17, -0.055, { parent: g }); c.rotation.x = 0.12; }
    mergeStatic(g);
  }

  // ---- the shell --------------------------------------------------------------------------
  const WT = 0.3;
  const paint = std(0x47546a, 0.96, { bumpMap: plasterGrain, bumpScale: 0.012 }), paintSide = std(0x3e4a5e, 0.96, { bumpMap: plasterGrain, bumpScale: 0.012 });
  const DOOR_X = -3.35, DOOR_W = 2.2, DOOR_H = 4.2;
  const floorTex = woodTexture(27);
  floorTex.repeat.multiplyScalar(1 / 14); // the floor shape below maps the texture by world units, not 0..1
  const SLOT = { x: -3.35, w: 4.8, z0: BZ - 0.005, z1: BZ + 0.905 };
  const floorShape = new THREE.Shape([new THREE.Vector2(-7, -7), new THREE.Vector2(7, -7), new THREE.Vector2(7, 10), new THREE.Vector2(-7, 10)]);
  // one hole for the slot and the passage: touching holes do not triangulate
  const at = (x: number, z: number) => new THREE.Vector2(x, 2 - z);
  floorShape.holes.push(new THREE.Path([
    at(SLOT.x - SLOT.w / 2, SLOT.z1), at(SLOT.x + SLOT.w / 2, SLOT.z1), at(SLOT.x + SLOT.w / 2, SLOT.z0),
    at(DOOR_X + DOOR_W / 2, SLOT.z0), at(DOOR_X + DOOR_W / 2, BZ - 3.7), at(DOOR_X - DOOR_W / 2, BZ - 3.7),
    at(DOOR_X - DOOR_W / 2, SLOT.z0), at(SLOT.x - SLOT.w / 2, SLOT.z0),
  ]));
  put(keep(new THREE.ShapeGeometry(floorShape)), std(0xffffff, 0.7, { map: floorTex, bumpMap: floorTex, bumpScale: 0.03 }), 0, 0, 2, { shadow: false, rot: [-Math.PI / 2, 0, 0] });
  const shaftMat = std(0x08090c, 1);
  const shaftZ = (SLOT.z0 + SLOT.z1) / 2, shaftD = SLOT.z1 - SLOT.z0;
  put(box(SLOT.w + 0.1, 5.8, 0.05, 0), shaftMat, SLOT.x, -2.9, SLOT.z1 + 0.025, { shadow: false });
  put(box(SLOT.w + 0.1, 5.8, 0.05, 0), shaftMat, SLOT.x, -2.9, SLOT.z0 - 0.025, { shadow: false });
  for (const x of [SLOT.x - SLOT.w / 2 - 0.025, SLOT.x + SLOT.w / 2 + 0.025]) put(box(0.05, 5.8, shaftD + 0.1, 0), shaftMat, x, -2.9, shaftZ, { shadow: false });
  put(box(SLOT.w + 0.1, 0.05, shaftD + 0.1, 0), shaftMat, SLOT.x, -5.8, shaftZ, { shadow: false });
  put(box(DOOR_X - DOOR_W / 2 + 6.2, H, WT, 0), paint, (-6.2 + DOOR_X - DOOR_W / 2) / 2, H / 2, BZ - WT / 2, { shadow: false });
  put(box(-(DOOR_X + DOOR_W / 2), H, WT, 0), paint, (DOOR_X + DOOR_W / 2) / 2, H / 2, BZ - WT / 2, { shadow: false });
  put(box(DOOR_W, H - DOOR_H, WT, 0), paint, DOOR_X, DOOR_H + (H - DOOR_H) / 2, BZ - WT / 2, { shadow: false });
  put(box(3.0, H, WT, 0), paint, 4.7, H / 2, BZ - WT / 2, { shadow: false });
  put(box(3.2, 2.3, WT, 0), paint, 1.6, 1.15, BZ - WT / 2, { shadow: false });
  put(box(3.2, H - 4.9, WT, 0), paint, 1.6, 4.9 + (H - 4.9) / 2, BZ - WT / 2, { shadow: false });
  put(box(WT, H, 12, 0), paintSide, -6 - WT / 2, H / 2, 2, { shadow: false });
  put(box(WT, H, 12, 0), paintSide, 6 + WT / 2, H / 2, 2, { shadow: false });
  const dark = std(0x2b1f17, 0.65), cream = std(0xd9cdb8, 0.8, { bumpMap: plasterGrain, bumpScale: 0.006 });
  const trim: Piece[] = [
    { geo: box(DOOR_X - DOOR_W / 2 + 6, 0.18, 0.06, 0.008), x: (-6 + DOOR_X - DOOR_W / 2) / 2, y: 0.09, z: BZ + 0.03 }, { geo: box(6 - DOOR_X - DOOR_W / 2, 0.18, 0.06, 0.008), x: (DOOR_X + DOOR_W / 2 + 6) / 2, y: 0.09, z: BZ + 0.03 },
    { geo: box(DOOR_X - DOOR_W / 2 + 6, 0.06, 0.05, 0.008), x: (-6 + DOOR_X - DOOR_W / 2) / 2, y: 2.05, z: BZ + 0.025 }, { geo: box(6 - DOOR_X - DOOR_W / 2, 0.06, 0.05, 0.008), x: (DOOR_X + DOOR_W / 2 + 6) / 2, y: 2.05, z: BZ + 0.025 },
    { geo: box(12, 0.14, 0.08, 0.01), x: 0, y: H - 0.07, z: BZ + 0.04 },
  ];
  for (const side of [-6, 6]) {
    const inward = side < 0 ? 1 : -1;
    trim.push({ geo: box(0.06, 0.18, 12, 0.008), x: side + inward * 0.03, y: 0.09, z: 2 }, { geo: box(0.05, 0.06, 12, 0.008), x: side + inward * 0.025, y: 2.05, z: 2 }, { geo: box(0.08, 0.14, 12, 0.01), x: side + inward * 0.04, y: H - 0.07, z: 2 });
    for (let z = -2.8; z < 7; z += 1.6) {
      const zx = side + inward * 0.02;
      trim.push({ geo: box(0.03, 0.04, 1.2, 0.006), x: zx, y: 1.75, z }, { geo: box(0.03, 0.04, 1.2, 0.006), x: zx, y: 0.4, z }, { geo: box(0.03, 1.39, 0.04, 0.006), x: zx, y: 1.075, z: z - 0.58 }, { geo: box(0.03, 1.39, 0.04, 0.006), x: zx, y: 1.075, z: z + 0.58 });
    }
  }
  for (const x of [3.95, 5.35]) trim.push({ geo: box(1.2, 0.04, 0.03, 0.006), x, y: 1.75, z: BZ + 0.015 }, { geo: box(1.2, 0.04, 0.03, 0.006), x, y: 0.4, z: BZ + 0.015 }, { geo: box(0.04, 1.39, 0.03, 0.006), x: x - 0.58, y: 1.075, z: BZ + 0.015 }, { geo: box(0.04, 1.39, 0.03, 0.006), x: x + 0.58, y: 1.075, z: BZ + 0.015 });
  merged(cream, trim);
  put(keep(new THREE.PlaneGeometry(14, 14)), std(0x2a3340, 1, { bumpMap: plasterGrain, bumpScale: 0.01 }), 0, H, 2, { shadow: false, rot: [Math.PI / 2, 0, 0] });

  const frame = std(0xd9d0be, 0.6, { bumpMap: plasterGrain, bumpScale: 0.004 });
  put(box(3.4, 0.1, WT + 0.06, 0.01), frame, 1.6, 2.3, BZ - WT / 2); put(box(3.4, 0.1, WT + 0.06, 0.01), frame, 1.6, 4.9, BZ - WT / 2);
  put(box(0.1, 2.7, WT + 0.06, 0.01), frame, 0.0, 3.6, BZ - WT / 2); put(box(0.1, 2.7, WT + 0.06, 0.01), frame, 3.2, 3.6, BZ - WT / 2);
  put(box(0.05, 0.25, 0.07, 0.01), frame, 1.6, 4.775, BZ - 0.08); put(box(0.05, 0.25, 0.07, 0.01), frame, 1.6, 2.425, BZ - 0.08);
  put(box(0.25, 0.05, 0.07, 0.01), frame, 0.125, 3.85, BZ - 0.08); put(box(0.25, 0.05, 0.07, 0.01), frame, 3.075, 3.85, BZ - 0.08);
  const bars = [
    put(box(0.05, 1.1, 0.07, 0.01), frame, 1.6, 3.1, BZ - 0.08), put(box(0.05, 1.1, 0.07, 0.01), frame, 1.6, 4.2, BZ - 0.08),
    put(box(1.35, 0.05, 0.07, 0.01), frame, 0.925, 3.85, BZ - 0.08), put(box(1.35, 0.05, 0.07, 0.01), frame, 2.275, 3.85, BZ - 0.08),
  ].map((mesh) => ({ mesh, home: mesh.position.clone(), flying: false, v: new THREE.Vector3(), spin: new THREE.Vector3() }));
  put(box(3.6, 0.1, 0.62, 0.02), frame, 1.6, 2.26, BZ + 0.16);
  // the pane is pre-cut into shards: at midnight frame-touching pieces stay as spikes, the rest burst out
  const PANE = { cx: 1.6, cy: 3.6, w: 3.2, h: 2.6, z: BZ - 0.1 };
  interface Shard { mesh: THREE.Mesh; edge: THREE.LineSegments; home: THREE.Vector3; remnant: boolean; flying: boolean; v: THREE.Vector3; spin: THREE.Vector3 }
  const shards: Shard[] = [];
  const shardMat = keep(new THREE.MeshPhysicalMaterial({ color: 0xdfeaff, transparent: true, opacity: 0.07, roughness: 0.05, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, side: THREE.DoubleSide, depthWrite: false }));
  const spikeMat = keep(new THREE.LineBasicMaterial({ color: 0xeef3ff, transparent: true, opacity: 0.95 }));
  for (const [x0, x1, y0, y1] of [[-1.6, -0.025, -1.3, 0.225], [0.025, 1.6, -1.3, 0.225], [-1.6, -0.025, 0.275, 1.3], [0.025, 1.6, 0.275, 1.3]]) {
    const nx = 4, ny = 3, cw = (x1 - x0) / nx, ch = (y1 - y0) / ny;
    const pts: THREE.Vector2[][] = [];
    for (let i = 0; i <= nx; i++) {
      pts.push([]);
      for (let j = 0; j <= ny; j++) {
        const onX = i === 0 || i === nx, onY = j === 0 || j === ny;
        pts[i].push(new THREE.Vector2(x0 + i * cw + (onX ? 0 : (rng() - 0.5) * cw * 0.7), y0 + j * ch + (onY ? 0 : (rng() - 0.5) * ch * 0.7)));
      }
    }
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const corners: [number, number][] = rng() < 0.5 ? [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]] : [[i + 1, j], [i + 1, j + 1], [i, j + 1], [i, j]];
      for (const tri of [[corners[0], corners[1], corners[2]], [corners[0], corners[2], corners[3]]]) {
        const v = tri.map(([a, b]) => pts[a][b]);
        // a spike is a piece with a whole edge on the outer frame; the mullions go, so nothing clings to them
        const onEdge = (k: number) => tri.filter(([a, b]) => (k === 0 ? a === 0 : k === 1 ? a === nx : k === 2 ? b === 0 : b === ny)).length >= 2;
        const touches = (x0 === -1.6 && onEdge(0)) || (x1 === 1.6 && onEdge(1)) || (y0 === -1.3 && onEdge(2)) || (y1 === 1.3 && onEdge(3));
        const c = new THREE.Vector2().add(v[0]).add(v[1]).add(v[2]).multiplyScalar(1 / 3);
        const geo = keep(new THREE.ShapeGeometry(new THREE.Shape(v.map((q) => q.clone().sub(c)))));
        const mesh = new THREE.Mesh(geo, shardMat);
        mesh.position.set(PANE.cx + c.x, PANE.cy + c.y, PANE.z);
        scene.add(mesh);
        const edge = new THREE.LineSegments(keep(new THREE.EdgesGeometry(geo)), spikeMat);
        edge.visible = false;
        mesh.add(edge);
        shards.push({ mesh, edge, home: mesh.position.clone(), remnant: touches && rng() < 0.72, flying: false, v: new THREE.Vector3(), spin: new THREE.Vector3() });
      }
    }
  }
  // until it breaks the pane is one merged mesh; the shards only draw once they are flying or spiking
  const paneGeo = mergeGeometries(shards.map((sh) => sh.mesh.geometry.clone().translate(sh.home.x, sh.home.y, sh.home.z)), false);
  if (!paneGeo) throw new Error("pane");
  const pane = new THREE.Mesh(keep(paneGeo), shardMat);
  scene.add(pane);
  for (const sh of shards) sh.mesh.visible = false;
  let shakeUntil = 0;
  const flash = put(keep(new THREE.PlaneGeometry(PANE.w, PANE.h)), keep(new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })), PANE.cx, PANE.cy, PANE.z + 0.01, { shadow: false });
  const flashMat = flash.material as THREE.MeshBasicMaterial;
  let glassBreakAt = 0, burstT = -1; // the burst keeps its own clock: it runs slow for its first half second
  function breakGlass() {
    burstT = 0;
    flashMat.opacity = 1;
    shakeUntil = performance.now() + 520;
    lightsOut();
    for (const b of bars) {
      b.flying = true;
      b.v.set((b.home.x - 1.7) * 0.8 + (rng() - 0.5) * 0.6, (b.home.y - 3.5) * 0.6 + 0.6 + rng() * 0.6, -(2.0 + rng() * 2.0));
      b.spin.set((rng() - 0.5) * 6, (rng() - 0.5) * 6, (rng() - 0.5) * 6);
    }
    pane.visible = false;
    for (const sh of shards) {
      sh.mesh.visible = true;
      sh.edge.visible = true; // broken glass is drawn in ink: the faint pane, white stroked edges
      if (sh.remnant) continue;
      sh.flying = true;
      const dx = sh.home.x - (PANE.cx + 0.2), dy = sh.home.y - (PANE.cy - 0.1), inward = rng() < 0.1;
      sh.v.set(dx * 1.5 + (rng() - 0.5) * 0.8, dy * 1.3 + 0.5 + rng() * 0.9, inward ? 1.0 + rng() * 1.4 : -(2.4 + rng() * 3.2));
      sh.spin.set((rng() - 0.5) * 12, (rng() - 0.5) * 12, (rng() - 0.5) * 12);
    }
  }
  function healGlass() {
    glassBreakAt = 0; burstT = -1; flashMat.opacity = 0;
    pane.visible = true;
    for (const sh of shards) { sh.mesh.position.copy(sh.home); sh.mesh.rotation.set(0, 0, 0); sh.mesh.visible = false; sh.edge.visible = false; sh.flying = false; }
    for (const b of bars) { b.mesh.position.copy(b.home); b.mesh.rotation.set(0, 0, 0); b.mesh.visible = true; b.flying = false; }
  }
  const skyMat = keep(new THREE.MeshBasicMaterial({ map: skyTexture() }));
  put(keep(new THREE.PlaneGeometry(10, 7)), skyMat, 1.6, 3.9, BZ - 4, { shadow: false });
  // the signal: a lit disc with the symbol from public/bat-signal.png if present, else the drawn one
  let batImage: HTMLImageElement | null = null;
  const drawSignal = (g: CanvasRenderingContext2D, w: number, h: number) => {
    const c = w / 2, R = w * 0.42;
    g.clearRect(0, 0, w, h);
    const halo = g.createRadialGradient(c, c, R * 0.2, c, c, R * 1.18);
    halo.addColorStop(0, "rgba(255,250,222,.98)"); halo.addColorStop(0.72, "rgba(255,244,205,.9)"); halo.addColorStop(0.86, "rgba(255,240,200,.35)"); halo.addColorStop(1, "rgba(255,240,200,0)");
    g.fillStyle = halo; g.beginPath(); g.arc(c, c, R * 1.18, 0, Math.PI * 2); g.fill();
    if (batImage) {
      // multiply, so a white background in the file does not show
      const bw = R * 1.5, bh = bw * (batImage.height / batImage.width);
      g.save(); g.globalCompositeOperation = "multiply"; g.drawImage(batImage, c - bw / 2, c - bh / 2, bw, bh); g.restore();
      return;
    }
    const P = (x: number, y: number): [number, number] => [c + x * R, c + y * R];
    g.fillStyle = "#0b0b12";
    g.beginPath();
    g.moveTo(...P(0, -0.3)); g.lineTo(...P(-0.07, -0.42)); g.lineTo(...P(-0.1, -0.26)); g.lineTo(...P(-0.16, -0.2)); g.lineTo(...P(-0.82, -0.34));
    g.quadraticCurveTo(...P(-0.72, -0.02), ...P(-0.58, 0.12)); g.quadraticCurveTo(...P(-0.46, 0), ...P(-0.34, 0.2)); g.quadraticCurveTo(...P(-0.22, 0.06), ...P(-0.1, 0.3));
    g.lineTo(...P(0, 0.42)); g.lineTo(...P(0.1, 0.3));
    g.quadraticCurveTo(...P(0.22, 0.06), ...P(0.34, 0.2)); g.quadraticCurveTo(...P(0.46, 0), ...P(0.58, 0.12)); g.quadraticCurveTo(...P(0.72, -0.02), ...P(0.82, -0.34));
    g.lineTo(...P(0.16, -0.2)); g.lineTo(...P(0.1, -0.26)); g.lineTo(...P(0.07, -0.42)); g.closePath(); g.fill();
  };
  const signalTex = canvasTexture(drawSignal, 512, 512);
  const signalMat = keep(new THREE.MeshBasicMaterial({ map: signalTex, transparent: true, opacity: 0, depthWrite: false }));
  const batFile = new Image();
  batFile.onload = () => { if (disposed) return; batImage = batFile; const c = signalTex.image as HTMLCanvasElement, g = c.getContext("2d"); if (g) { drawSignal(g, c.width, c.height); signalTex.needsUpdate = true; } };
  batFile.src = "/bat-signal.png";
  const SIGNAL = new THREE.Vector3(1.15, 5.05, BZ - 3.9), SIGNAL_FROM = new THREE.Vector3(3.0, 1.5, BZ - 3.95); // up in clear sky over the rooftops
  put(keep(new THREE.PlaneGeometry(1.05, 1.05)), signalMat, SIGNAL.x, SIGNAL.y, SIGNAL.z, { shadow: false });
  const beamTex = canvasTexture((g, w, h) => {
    g.clearRect(0, 0, w, h);
    const gr = g.createLinearGradient(0, h, 0, 0); gr.addColorStop(0, "rgba(255,240,200,.45)"); gr.addColorStop(1, "rgba(255,240,200,.03)");
    g.fillStyle = gr; g.beginPath(); g.moveTo(w / 2 - 3, h); g.lineTo(w / 2 + 3, h); g.lineTo(w, 0); g.lineTo(0, 0); g.closePath(); g.fill();
  }, 128, 512);
  const beamMat = keep(new THREE.MeshBasicMaterial({ map: beamTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  const beam = put(keep(new THREE.PlaneGeometry(0.95, SIGNAL.distanceTo(SIGNAL_FROM))), beamMat, (SIGNAL.x + SIGNAL_FROM.x) / 2, (SIGNAL.y + SIGNAL_FROM.y) / 2, SIGNAL_FROM.z, { shadow: false });
  beam.rotation.z = Math.atan2(SIGNAL.y - SIGNAL_FROM.y, SIGNAL.x - SIGNAL_FROM.x) - Math.PI / 2; // its wide end points at the signal
  let signalLevel = 0;
  // the city stops short of the passage behind the bookcase, so it cannot show through the corner there
  put(keep(new THREE.PlaneGeometry(6.4, 4.5)), keep(new THREE.MeshBasicMaterial({ map: townTexture(), transparent: true })), 2.0, 2.55, BZ - 2.4, { shadow: false });
  const drapeGeo = keep(new THREE.PlaneGeometry(0.46, 3.3, 24, 1));
  const dp = drapeGeo.attributes.position as THREE.BufferAttribute;
  for (let i = 0; i < dp.count; i++) dp.setZ(i, Math.sin(dp.getX(i) * 40) * 0.04);
  drapeGeo.computeVertexNormals();
  const drape = std(0x6b5670, 1, { side: THREE.DoubleSide, bumpMap: clothGrain, bumpScale: 0.01 });
  put(drapeGeo, drape, -0.27, 3.72, BZ + 0.3, { shadow: false }); put(drapeGeo, drape, 3.47, 3.72, BZ + 0.3, { shadow: false });
  put(cyl(0.02, 0.02, 4.6, 12), brassMat, 1.6, 5.42, BZ + 0.3, { rot: [0, 0, Math.PI / 2] });
  put(sphere(0.04, 12, 10), brassMat, -0.7, 5.42, BZ + 0.3); put(sphere(0.04, 12, 10), brassMat, 3.9, 5.42, BZ + 0.3);
  put(keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.08, 0), new THREE.Vector2(0.1, 0.12), new THREE.Vector2(0.11, 0.14), new THREE.Vector2(0.09, 0.14)], 24)), std(0xd6c9b4, 0.8), 2.6, 2.31, BZ + 0.2);
  for (let i = 0; i < 7; i++) { const a = i * 2.4; const l = put(leafGeo, std(0x7aa86f, 0.8), 2.6 + Math.cos(a) * 0.02, 2.44, BZ + 0.2 + Math.sin(a) * 0.02); l.rotation.set(-1.1, 0, 0); l.rotateOnWorldAxis(UP, -a + Math.PI / 2); l.scale.set(0.14, 0.14, 1); }

  // ---- the shelves and the comics -------------------------------------------------------------
  const shelfWood = woodTexture(22, false);
  shelfWood.repeat.set(1.2, 1.2);
  const walnut = std(0xffffff, 0.62, { map: shelfWood, bumpMap: shelfWood, bumpScale: 0.015 });
  const charcoal = std(0x1d1e23, 0.55, { metalness: 0.08, bumpMap: clothGrain, bumpScale: 0.005 }), charcoalBack = std(0x141519, 0.9, { bumpMap: plasterGrain, bumpScale: 0.01 });
  const unit = shelfUnit(4.7, 5.25, 0.85, SHELF_ROWS, charcoal, charcoalBack);
  // the bookcase rides a lift: when the secret opens it sinks through the slot in the floor, out of sight
  const lift = new THREE.Group();
  lift.position.set(DOOR_X, 0, BZ + 0.43);
  scene.add(lift);
  lift.add(unit.group);
  const LIFT_DROP = 5.5;

  // ---- the passage: lined a touch narrower than the cut so no plane is shared; landing, stairs, certificate ----
  const passage = new THREE.Group();
  passage.position.set(DOOR_X, 0, BZ);
  scene.add(passage);
  const PW = DOOR_W - 0.04;
  const graphite = std(0x15161b, 0.55, { metalness: 0.35, bumpMap: plasterGrain, bumpScale: 0.004 });
  const slate = std(0x1d1e24, 0.9, { bumpMap: plasterGrain, bumpScale: 0.01 });
  const seam = std(0x2f6fff, 0.4, { emissive: 0x4f8cff, emissiveIntensity: 1.8 });
  const PH = DOOR_H - 0.02; // the lining's ceiling sits just under the cut
  for (const sx of [-1, 1]) put(box(0.08, PH + 2.72, 3.52, 0.004), graphite, sx * (PW / 2 + 0.04), (PH - 2.72) / 2, -1.76, { parent: passage, shadow: false });
  put(box(PW + 0.16, 0.08, 3.52, 0.004), graphite, 0, PH + 0.04, -1.76, { parent: passage, shadow: false });
  put(box(PW + 0.16, PH + 2.8, 0.08, 0.004), slate, 0, (PH + 0.08 - 2.72) / 2, -3.57, { parent: passage, shadow: false });
  put(box(PW, 0.08, 1.2, 0.004), slate, 0, -0.04, -0.6, { parent: passage, shadow: false });
  put(box(PW, 0.08, 2.4, 0.004), slate, 0, -2.68, -2.4, { parent: passage, shadow: false });
  for (let i = 0; i < 8; i++) {
    const top = -0.26 * (i + 1), z = -1.2 - 0.275 * (i + 0.5);
    put(box(PW, top + 2.64, 0.275, 0.004), slate, 0, (top - 2.64) / 2, z, { parent: passage, shadow: false });
    put(box(PW - 0.08, 0.01, 0.016, 0.002), seam, 0, top + 0.005, z + 0.13, { parent: passage, shadow: false });
  }
  for (const sx of [-1, 1]) {
    put(box(0.012, 0.012, 3.3, 0.002), seam, sx * (PW / 2 - 0.004), 1.2, -1.75, { parent: passage, shadow: false });
    put(box(0.012, PH + 2.5, 0.012, 0.002), seam, sx * (PW / 2 - 0.02), (PH - 0.1 - 2.6) / 2, -3.5, { parent: passage, shadow: false });
  }
  const stairLight = new THREE.PointLight(0x3f7fff, 0, 7, 2);
  stairLight.position.set(0, -1.4, -2.9);
  passage.add(stairLight);
  const stone = std(0x17181d, 0.35, { metalness: 0.1, bumpMap: plasterGrain, bumpScale: 0.004 });
  const plaqueTex = canvasTexture((g, w, h) => { g.fillStyle = "#121318"; g.fillRect(0, 0, w, h); }, 1024, 680);
  let summary: RoomSummary | null = null;
  function drawPlaque(progress: number) {
    const c = plaqueTex.image as HTMLCanvasElement, g = c.getContext("2d");
    if (!g) return;
    const w = c.width, h = c.height, font = "system-ui, -apple-system, 'Segoe UI', sans-serif";
    const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, "#1a1b21"); bg.addColorStop(1, "#0e0f13");
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    const sheen = g.createRadialGradient(w / 2, h * 0.3, 20, w / 2, h * 0.3, w * 0.7); sheen.addColorStop(0, "rgba(255,255,255,.05)"); sheen.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = sheen; g.fillRect(0, 0, w, h);
    g.strokeStyle = "rgba(222,196,130,.85)"; g.lineWidth = 2.5; g.strokeRect(26, 26, w - 52, h - 52);
    g.strokeStyle = "rgba(222,196,130,.45)"; g.lineWidth = 1; g.strokeRect(42, 42, w - 84, h - 84);
    g.strokeStyle = "rgba(222,196,130,.85)"; g.lineWidth = 2;
    for (const [cx, cy, sx, sy] of [[42, 42, 1, 1], [w - 42, 42, -1, 1], [42, h - 42, 1, -1], [w - 42, h - 42, -1, -1]]) {
      g.beginPath(); g.moveTo(cx + sx * 34, cy); g.lineTo(cx, cy); g.lineTo(cx, cy + sy * 34); g.stroke();
    }
    g.fillStyle = "rgba(222,196,130,.9)"; g.strokeStyle = "rgba(222,196,130,.6)"; g.lineWidth = 1.5;
    g.beginPath(); g.moveTo(w / 2 - 150, 118); g.lineTo(w / 2 - 16, 118); g.moveTo(w / 2 + 16, 118); g.lineTo(w / 2 + 150, 118); g.stroke();
    g.beginPath(); g.moveTo(w / 2, 109); g.lineTo(w / 2 + 9, 118); g.lineTo(w / 2, 127); g.lineTo(w / 2 - 9, 118); g.closePath(); g.fill();
    g.textAlign = "center"; g.textBaseline = "middle";
    const amount = summary ? `${summary.symbol}${Math.round(summary.spent * progress).toLocaleString()}` : "— — —";
    g.font = `800 196px ${font}`;
    g.fillStyle = "rgba(0,0,0,.55)"; g.fillText(amount, w / 2 + 3, h * 0.42 + 4);
    g.fillStyle = "rgba(255,245,220,.18)"; g.fillText(amount, w / 2 - 1, h * 0.42 - 2);
    const gold = g.createLinearGradient(0, h * 0.26, 0, h * 0.58); gold.addColorStop(0, "#f6e9bf"); gold.addColorStop(0.55, "#d9b86a"); gold.addColorStop(1, "#b8923f");
    g.fillStyle = gold; g.fillText(amount, w / 2, h * 0.42);
    g.strokeStyle = "rgba(222,196,130,.5)"; g.lineWidth = 1;
    g.beginPath(); g.moveTo(w / 2 - 190, h * 0.66); g.lineTo(w / 2 + 190, h * 0.66); g.moveTo(w / 2, h * 0.72); g.lineTo(w / 2, h * 0.9); g.stroke();
    const figure = (x: number, value: string, label: string) => {
      g.fillStyle = "#e9d9ad"; g.font = `800 72px ${font}`; g.fillText(value, x, h * 0.78);
      g.fillStyle = "#9c8f6c"; g.font = `700 24px ${font}`;
      const spaced = label.split("").join(String.fromCharCode(8202)); // hair spaces: letterspacing without a browser flag
      g.fillText(spaced, x, h * 0.875);
    };
    if (summary) { figure(w / 2 - 120, summary.issues.toLocaleString(), "ISSUES"); figure(w / 2 + 120, summary.series.toLocaleString(), "SERIES"); }
    plaqueTex.needsUpdate = true;
  }
  drawPlaque(1);
  const PLAQUE = new THREE.Vector3(-PW / 2 + 0.03, 2.45, -1.0);
  put(box(0.78, 0.52, 0.016, 0.004), brassMat, PLAQUE.x - 0.015, PLAQUE.y, PLAQUE.z, { parent: passage, rot: [0, Math.PI / 2, 0], shadow: false });
  const plaque = new THREE.Mesh(box(0.72, 0.46, 0.03, 0.004), [stone, stone, stone, stone, keep(new THREE.MeshStandardMaterial({ map: plaqueTex, roughness: 0.4, metalness: 0.15 })), stone]);
  plaque.position.copy(PLAQUE);
  plaque.rotation.y = Math.PI / 2; // its face looks into the passage
  plaque.castShadow = true;
  passage.add(plaque);
  pickables.push(plaque);
  states.set(plaque, { item: null, home: plaque.position.clone(), homeQ: plaque.quaternion.clone(), parent: passage, lift: 0, reach: 1.1, offsetX: 0, offsetY: 0, tilt: 1.3, glow: 0.6, spin: 0, pop: 0, out: new THREE.Vector3(1, 0, 0) });
  const caseSpot = new THREE.SpotLight(0xd6e4ff, 0, 7, 0.5, 0.6, 1.2);
  caseSpot.position.set(0.2, PH - 0.1, -0.7);
  caseSpot.target.position.copy(PLAQUE);
  passage.add(caseSpot, caseSpot.target);
  blob(-3.35, BZ + 1.3, 5.2, 0.8, 0.5);
  const byLove = series.slice().sort((a, b) => b.rating * 12 + b.owned - (a.rating * 12 + a.owned));
  const shelves = unit.ys.slice().reverse();
  const onShelves = FACE_PER_SHELF * shelves.length;
  // the shelf holds the issues; the series stand elsewhere in the room as props
  const shelfItems: RoomItem[] = issues.length ? issues : byLove;
  const faceOut = shelfItems.slice(0, onShelves);
  total = faceOut.length + Math.min(3, byLove.length) + Math.min(4, byLove.length);
  const bump = () => { loaded++; options.onProgress?.(loaded, total); };
  const faceGeo = comicGeometry(FACE.w, FACE.h, FACE.d);
  const slots: { mesh: THREE.Mesh; row: number; col: number }[] = [];
  const standeeSlots: [number, number, number][] = [];
  shelves.forEach((y, si) => {
    const left = -unit.inner / 2;
    for (let i = 0; i < FACE_PER_SHELF; i++) {
      const s = faceOut[si * FACE_PER_SHELF + i];
      if (!s) break;
      slots.push({ mesh: addComic(s, faceGeo, left + FACE.w / 2 + i * FACE_STEP, y + FACE.h / 2 - 0.012, unit.backZ + 0.16 + i * 0.018, unit.group, bump), row: si, col: i });
    }
    const endX = unit.inner / 2 - 0.26, endZ = unit.backZ + 0.36;
    if (si === 1 || si === 2) standeeSlots.push([endX, y, endZ]);
    if (si === 3) logo(endX, y, unit.backZ + 0.2, 0.52, unit.group, 0.35, 0.22);
  });
  // turning the shelf over: each slot steps out, turns edge on, swaps its cover, turns back; staggered
  const pageCount = Math.max(1, Math.ceil(shelfItems.length / SHELF_SLOTS));
  const noop = () => {};
  let currentPage = 0, busyUntil = 0, pageBusy = false;
  function showPage(page: number) {
    const target = ((page % pageCount) + pageCount) % pageCount;
    const now = performance.now() / 1000;
    if (target === currentPage || now < busyUntil || secret !== "closed") return;
    if (focused && slots.some((slot) => slot.mesh === focused)) putBack();
    currentPage = target;
    for (const { mesh, row, col } of slots) {
      const s = shelfItems[target * SHELF_SLOTS + row * FACE_PER_SHELF + col] ?? null;
      if (s) coverMaterial(s, noop); // start the download now, ahead of the turn
      const start = now + row * 0.1 + col * 0.045;
      const st = states.get(mesh);
      if (st) st.flip = { start, dur: 0.75, item: s, swapped: false };
      busyUntil = Math.max(busyUntil, start + 0.75);
    }
    pageBusy = true;
    options.onPage?.(currentPage, pageCount, true);
  }
  options.onPage?.(0, pageCount, false);

  // ---- the desk under the window: a screen, keyboard, headphones, a stack of comics, the lamp ---------
  put(box(4.0, 0.1, 0.85, 0.03), walnut, 1.6, 1.0, BZ + 0.55);
  put(box(1.2, 0.72, 0.78, 0.02), walnut, 2.9, 0.59, BZ + 0.55);
  for (let k = 0; k < 2; k++) { put(box(1.08, 0.3, 0.03, 0.01), std(0x3a2a1c, 0.6, { map: shelfWood }), 2.9, 0.42 + k * 0.34, BZ + 0.96, { shadow: false }); put(sphere(0.025, 12, 10), brassMat, 2.9, 0.42 + k * 0.34, BZ + 0.99, { shadow: false }); }
  const leg = cyl(0.03, 0.04, 0.96, 14);
  for (const [dx, dz] of [[-1.9, -0.35], [-1.9, 0.35]]) put(leg, dark, 1.6 + dx, 0.48, BZ + 0.55 + dz);
  blob(1.6, BZ + 0.6, 4.4, 1.3, 0.4);
  // digital rain on an unlit canvas, stepped a few times a second
  const RAIN = { w: 640, h: 360, cell: 18, step: 20, glyphs: "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789VERTIGO" };
  const screenTex = canvasTexture((g, w, h) => { g.fillStyle = "#060914"; g.fillRect(0, 0, w, h); }, RAIN.w, RAIN.h);
  const rainCtx = (screenTex.image as HTMLCanvasElement).getContext("2d");
  const rainCols = Math.floor(RAIN.w / RAIN.cell);
  const rainDrops = Array.from({ length: rainCols }, () => Math.floor(rng() * (RAIN.h / RAIN.step)));
  const rainLast: string[] = Array.from({ length: rainCols }, () => "");
  let rainAt = 0;
  function rainStep() {
    const g = rainCtx;
    if (!g) return;
    g.fillStyle = "rgba(6,9,20,0.2)";
    g.fillRect(0, 0, RAIN.w, RAIN.h);
    g.font = "bold 18px ui-monospace, Menlo, monospace";
    g.textBaseline = "top";
    for (let i = 0; i < rainCols; i++) {
      const x = i * RAIN.cell, y = rainDrops[i] * RAIN.step;
      if (rainLast[i]) { g.fillStyle = "#127eff"; g.fillText(rainLast[i], x, y - RAIN.step); }
      const glyph = RAIN.glyphs[Math.floor(rng() * RAIN.glyphs.length)];
      g.fillStyle = "#cfe3ff";
      g.fillText(glyph, x, y);
      rainLast[i] = glyph;
      if (y > RAIN.h && rng() > 0.975) { rainDrops[i] = 0; rainLast[i] = ""; }
      rainDrops[i]++;
    }
    screenTex.needsUpdate = true;
  }
  let screenMode: "rain" | "comedian" = "rain", comedianAt = 0;
  const lobes = Array.from({ length: 8 }, (_, i) => ({ x: 0.06 + (i + rng() * 0.6) * (0.88 / 8), r: 0.035 + rng() * 0.06, len: 0.06 + rng() * 0.3, speed: 0.008 + rng() * 0.014 }));
  function comedianStep(now: number) {
    const g = rainCtx;
    if (!g) return;
    const w = RAIN.w, h = RAIN.h, t = Math.max(0, (now - comedianAt) / 1000);
    g.fillStyle = "#07070a"; g.fillRect(0, 0, w, h);
    const lines = ["Tonight, a comedian", "died in New York.", "Somebody knows why."];
    let left = Math.floor(t * 1000 / 55);
    g.font = "600 40px 'Courier New', ui-monospace, monospace"; g.fillStyle = "#e4dfd2"; g.textAlign = "center"; g.textBaseline = "middle";
    lines.forEach((text, i) => {
      const shown = text.slice(0, Math.max(0, left));
      const cursor = left >= 0 && left < text.length && Math.floor(now / 400) % 2 ? "_" : "";
      g.fillText(shown + cursor, w / 2, h * 0.5 + (i - 1) * 54);
      left -= text.length + 1 + (i === 1 ? 22 : 0); // a beat before the last line
    });
    const base = Math.min(0.58, 0.05 + t * 0.016) * h;
    const edge = (x: number) => { let y = base; for (const l of lobes) { const d = (x / w - l.x) / l.r; y += Math.min(l.len, t * l.speed) * h * Math.exp(-2 * d * d); } return y; };
    g.fillStyle = "#d8321c";
    g.beginPath(); g.moveTo(0, 0); g.lineTo(w, 0); g.lineTo(w, edge(w));
    for (let x = w; x >= 0; x -= 4) g.lineTo(x, edge(x));
    g.closePath(); g.fill();
    g.strokeStyle = "rgba(90,12,8,.55)"; g.lineWidth = 3; g.beginPath();
    for (let x = 0; x <= w; x += 4) { const y = edge(x); if (x === 0) g.moveTo(x, y); else g.lineTo(x, y); }
    g.stroke();
    screenTex.needsUpdate = true;
  }
  const screenMat = keep(new THREE.MeshBasicMaterial({ map: screenTex }));
  const monitor = new THREE.Group(); monitor.position.set(1.4, 1.05, BZ + 0.28); monitor.rotation.y = -0.06; scene.add(monitor);
  put(box(1.42, 0.84, 0.05, 0.015), std(0x15181f, 0.5, { metalness: 0.2 }), 0, 0.78, 0, { parent: monitor });
  put(keep(new THREE.PlaneGeometry(1.32, 0.74)), screenMat, 0, 0.78, 0.028, { parent: monitor, shadow: false });
  put(box(0.1, 0.4, 0.06, 0.01), std(0x15181f, 0.5, { metalness: 0.2 }), 0, 0.2, -0.02, { parent: monitor });
  put(box(0.5, 0.025, 0.26, 0.01), std(0x15181f, 0.5, { metalness: 0.2 }), 0, 0.012, 0.02, { parent: monitor });
  const screenLight = new THREE.PointLight(0x9fb8ff, 1.3, 2.6, 2); screenLight.position.set(1.4, 1.8, BZ + 0.8); scene.add(screenLight);
  const keysTex = canvasTexture((g) => { g.fillStyle = "#1c1f26"; g.fillRect(0, 0, 256, 96); for (let r = 0; r < 4; r++) for (let c = 0; c < 14; c++) { g.fillStyle = "#2b2f3a"; g.beginPath(); g.roundRect(6 + c * 17.6, 8 + r * 21, 14, 16, 3); g.fill(); } }, 256, 96);
  put(box(0.92, 0.035, 0.32, 0.01), std(0xffffff, 0.6, { map: keysTex }), 1.35, 1.07, BZ + 0.78);
  put(capsule(0.035, 0.05, 6, 14), std(0x23262e, 0.4, { metalness: 0.2 }), 2.0, 1.085, BZ + 0.8, { rot: [Math.PI / 2, 0, 0] });
  put(box(1.6, 0.012, 0.6, 0.006), std(0x1a1e27, 0.95, { bumpMap: clothGrain, bumpScale: 0.004 }), 1.55, 1.056, BZ + 0.7, { shadow: false });
  const hp = new THREE.Group(); hp.position.set(0.25, 1.05, BZ + 0.5); scene.add(hp);
  put(cyl(0.09, 0.1, 0.02, 24), std(0x23262e, 0.5, { metalness: 0.3 }), 0, 0.01, 0, { parent: hp });
  put(cyl(0.012, 0.012, 0.36, 10), std(0x23262e, 0.5, { metalness: 0.3 }), 0, 0.2, 0, { parent: hp });
  put(keep(new THREE.TorusGeometry(0.13, 0.016, 10, 28, Math.PI)), std(0x2d3039, 0.6), 0, 0.37, 0, { parent: hp, rot: [0, 0, 0] });
  put(cyl(0.07, 0.07, 0.05, 24), std(0x2d3039, 0.6), -0.13, 0.36, 0, { parent: hp, rot: [0, 0, Math.PI / 2] }); put(cyl(0.07, 0.07, 0.05, 24), std(0x2d3039, 0.6), 0.13, 0.36, 0, { parent: hp, rot: [0, 0, Math.PI / 2] });
  const flatGeo = comicGeometry(FACE.w, FACE.h, FACE.d * 0.7);
  byLove.slice(0, 4).forEach((s, i) => {
    const m = new THREE.Mesh(flatGeo, [coverMaterial(s, bump), pages]);
    m.position.set(-0.05 + (i % 2) * 0.03, 1.05 + 0.035 + i * 0.068, BZ + 0.75 + (i % 3) * 0.02);
    m.rotation.set(-Math.PI / 2, 0, 0.5 + (rng() - 0.5) * 0.2);
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
  });
  const mugMat = std(0xd9d2c3, 0.45, { bumpMap: plasterGrain, bumpScale: 0.003 });
  put(keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.09, 0), new THREE.Vector2(0.1, 0.03), new THREE.Vector2(0.105, 0.2), new THREE.Vector2(0.11, 0.22), new THREE.Vector2(0.095, 0.22), new THREE.Vector2(0.09, 0.03), new THREE.Vector2(0, 0.03)], 32)), mugMat, 2.45, 1.05, BZ + 0.8);
  put(keep(new THREE.TorusGeometry(0.055, 0.016, 10, 24, Math.PI)), mugMat, 2.56, 1.17, BZ + 0.8, { rot: [0, 0, -Math.PI / 2] });
  put(cyl(0.085, 0.085, 0.004, 24), std(0x3b2a1a, 0.5), 2.45, 1.25, BZ + 0.8, { shadow: false });
  lamp(3.3, 1.05, BZ + 0.7, 0.78, 0.27, 16, false, true);
  const overflow = Math.max(0, shelfItems.length - faceOut.length);
  if (overflow > 0) {
    const cardboard = std(0xe6dcc4, 0.9, { bumpMap: clothGrain, bumpScale: 0.004 });
    for (let i = 0; i < Math.min(2, Math.ceil(overflow / 100)); i++) { put(box(1.0, 0.42, 0.42, 0.02), cardboard, 0.9 + i * 0.03, 0.21 + i * 0.44, BZ + 0.52); put(box(0.98, 0.01, 0.4, 0.004), std(0xcfc3a8, 1), 0.9 + i * 0.03, 0.42 + i * 0.44, BZ + 0.52, { shadow: false }); }
  }

  // ---- the right side: cabinet with a console and figures, a wall of framed covers ---------
  put(box(2.3, 1.15, 0.6, 0.02), walnut, 4.6, 0.575, BZ + 0.35);
  put(box(2.36, 0.05, 0.66, 0.015), walnut, 4.6, 1.16, BZ + 0.35);
  for (const x of [4.05, 5.15]) { put(box(1.0, 0.8, 0.03, 0.008), std(0x3a2a1c, 0.6, { map: shelfWood }), x, 0.55, BZ + 0.66, { shadow: false }); put(box(0.05, 0.16, 0.02, 0.006), brassMat, x + (x < 4.6 ? 0.4 : -0.4), 0.55, BZ + 0.69, { shadow: false }); }
  blob(4.6, BZ + 0.5, 2.7, 1.1, 0.45);
  byLove.slice(7, 10).forEach((s, i) => addComic(s, faceGeo, 3.75 + i * 0.6, 1.185 + FACE.h / 2, BZ + 0.2 + i * 0.03, scene, bump));
  const consoleMat = std(0xd8d4c8, 0.55), consoleDark = std(0x2a2d35, 0.6);
  put(box(0.44, 0.09, 0.3, 0.015), consoleMat, 5.45, 1.23, BZ + 0.42);
  put(box(0.3, 0.012, 0.06, 0.004), consoleDark, 5.45, 1.28, BZ + 0.36, { shadow: false });
  put(sphere(0.012, 8, 6), std(0x3fff8a, 0.4, { emissive: 0x3fff8a, emissiveIntensity: 2 }), 5.62, 1.29, BZ + 0.52, { shadow: false });
  put(box(0.14, 0.08, 0.02, 0.006), std(0x8a8f99, 0.6), 5.45, 1.22, BZ + 0.59, { shadow: false });
  figure(5.0, 1.185, BZ + 0.5, 0xf2b632, 0xd23b3b, scene, 0.15);
  // ---- the dartboard and its darts ----------------------------------------------------------------
  const boardR = 0.55;
  const boardTex = canvasTexture((g, w, h) => {
    const cx = w / 2, cy = h / 2, R = w / 2 - 2;
    // sector i is centred i·18° clockwise from the top; a ring piece between two radii of it
    const piece = (r0: number, r1: number, i: number, colour: string) => {
      const a0 = -Math.PI / 2 + (i - 0.5) * (Math.PI / 10), a1 = a0 + Math.PI / 10;
      g.fillStyle = colour; g.beginPath(); g.arc(cx, cy, r1 * R, a0, a1); g.arc(cx, cy, r0 * R, a1, a0, true); g.closePath(); g.fill();
    };
    g.clearRect(0, 0, w, h);
    g.fillStyle = "#141414"; g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.fill();
    for (let i = 0; i < 20; i++) {
      const even = i % 2 === 0;
      piece(0.8, 0.86, i, even ? "#c0392b" : "#1e7a46");
      piece(0.53, 0.8, i, even ? "#1b1b1b" : "#e9dcbd");
      piece(0.47, 0.53, i, even ? "#c0392b" : "#1e7a46");
      piece(0.1, 0.47, i, even ? "#1b1b1b" : "#e9dcbd");
    }
    g.fillStyle = "#1e7a46"; g.beginPath(); g.arc(cx, cy, 0.1 * R, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#c0392b"; g.beginPath(); g.arc(cx, cy, 0.04 * R, 0, Math.PI * 2); g.fill();
    g.strokeStyle = "rgba(205,205,205,.6)"; g.lineWidth = 1.4;
    for (const r of [0.04, 0.1, 0.47, 0.53, 0.8, 0.86]) { g.beginPath(); g.arc(cx, cy, r * R, 0, Math.PI * 2); g.stroke(); }
    for (let i = 0; i < 20; i++) {
      const a = -Math.PI / 2 + (i - 0.5) * (Math.PI / 10);
      g.beginPath(); g.moveTo(cx + Math.cos(a) * 0.1 * R, cy + Math.sin(a) * 0.1 * R); g.lineTo(cx + Math.cos(a) * 0.86 * R, cy + Math.sin(a) * 0.86 * R); g.stroke();
    }
    const order = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5];
    g.fillStyle = "#f2efe8"; g.font = `bold ${Math.round(R * 0.085)}px system-ui, sans-serif`; g.textAlign = "center"; g.textBaseline = "middle";
    order.forEach((n, i) => { const a = -Math.PI / 2 + i * (Math.PI / 10); g.fillText(String(n), cx + Math.cos(a) * 0.93 * R, cy + Math.sin(a) * 0.93 * R); });
  }, 1024, 1024);
  const board = new THREE.Group();
  board.position.set(4.67, 3.95, BZ + 0.03);
  scene.add(board);
  put(cyl(boardR, boardR, 0.05, 72), std(0x1c1a17, 1), 0, 0, 0, { parent: board, rot: [Math.PI / 2, 0, 0] });
  put(keep(new THREE.TorusGeometry(boardR + 0.012, 0.024, 10, 72)), std(0x151515, 0.5, { metalness: 0.3 }), 0, 0, 0.012, { parent: board, shadow: false });
  put(keep(new THREE.PlaneGeometry(boardR * 2, boardR * 2)), std(0xffffff, 0.85, { map: boardTex, transparent: true, bumpMap: clothGrain, bumpScale: 0.004 }), 0, 0, 0.026, { parent: board, shadow: false });
  // a dart along +x, needle at the origin; on the board it points into the wall, tail up
  const steel = std(0xd8dde6, 0.25, { metalness: 0.95 }), tungsten = std(0x23262e, 0.4, { metalness: 0.85, bumpMap: clothGrain, bumpScale: 0.004 });
  const dartShaft = std(0x1159cc, 0.45, { metalness: 0.2 }), dartFlight = std(0x127eff, 0.55, { side: THREE.DoubleSide, emissive: 0x127eff, emissiveIntensity: 0.1 });
  const barrelGeo = keep(new THREE.LatheGeometry([[0, 0], [0.0055, 0], [0.0085, 0.012], [0.0095, 0.03], [0.0095, 0.05], [0.008, 0.068], [0.0065, 0.075], [0, 0.075]].map(([r, y]) => new THREE.Vector2(r, y)), 24));
  const finGeo = keep(new THREE.ShapeGeometry(new THREE.Shape([[0, 0.003], [0.004, 0.014], [0.03, 0.031], [0.056, 0.031], [0.056, -0.031], [0.03, -0.031], [0.004, -0.014], [0, -0.003]].map(([x, y]) => new THREE.Vector2(x, y)))));
  const grooveGeo = keep(new THREE.TorusGeometry(0.0096, 0.0011, 6, 24)), collarGeo = cyl(0.0045, 0.0062, 0.006, 16);
  function dart(x: number, y: number, tilt: number, skew: number) {
    const g = new THREE.Group();
    g.position.set(x, y, 0.026);
    board.add(g);
    put(cyl(0.0008, 0.0022, 0.06, 8), steel, -0.03, 0, 0, { parent: g, rot: [0, 0, Math.PI / 2], shadow: false });
    put(barrelGeo, tungsten, 0, 0, 0, { parent: g, rot: [0, 0, -Math.PI / 2] }); // the lathe runs +y; turned to run +x
    for (const gx of [0.028, 0.04, 0.052]) put(grooveGeo, steel, gx, 0, 0, { parent: g, rot: [0, Math.PI / 2, 0], shadow: false });
    put(collarGeo, steel, 0.078, 0, 0, { parent: g, rot: [0, 0, -Math.PI / 2], shadow: false });
    put(cyl(0.0028, 0.0034, 0.058, 12), dartShaft, 0.11, 0, 0, { parent: g, rot: [0, 0, Math.PI / 2] });
    put(finGeo, dartFlight, 0.136, 0, 0, { parent: g, shadow: false });
    put(finGeo, dartFlight, 0.136, 0, 0, { parent: g, rot: [Math.PI / 2, 0, 0], shadow: false });
    g.rotation.set(0, -Math.PI / 2, 0);
    g.rotateOnWorldAxis(new THREE.Vector3(1, 0, 0), tilt);
    g.rotateOnWorldAxis(new THREE.Vector3(0, 1, 0), skew);
    mergeStatic(g);
    pickables.push(g);
    states.set(g, { item: null, home: g.position.clone(), homeQ: g.quaternion.clone(), parent: board, lift: 0, reach: 0.65, offsetX: -0.07, offsetY: 0, tilt: 1.6, glow: 0.8, spin: 0, pop: 0, out: new THREE.Vector3(0, 0, 1) });
  }
  dart(0, 0.275, -0.32, 0.1); // treble twenty
  dart(-0.085, -0.26, -0.26, -0.14); // treble nineteen
  dart(0.012, -0.02, -0.36, 0.05); // the bull
  const clock = new THREE.Group();
  clock.position.set(-6 + 0.02, 3.9, -1.9);
  clock.rotation.y = Math.PI / 2; // its face looks into the room
  scene.add(clock);
  const clockR = 0.5;
  const clockFace = canvasTexture((g) => {
    g.fillStyle = "#f2efe8"; g.beginPath(); g.arc(128, 128, 128, 0, Math.PI * 2); g.fill();
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2, big = i % 3 === 0;
      g.fillStyle = big ? "#1a1c22" : "#b8b5ad"; g.beginPath(); g.arc(128 + Math.cos(a) * 108, 128 + Math.sin(a) * 108, big ? 4.5 : 3, 0, Math.PI * 2); g.fill();
    }
  }, 256, 256);
  const clockDark = std(0x15171c, 0.45, { metalness: 0.3 });
  put(cyl(clockR - 0.006, clockR - 0.006, 0.03, 64), std(0xffffff, 0.65, { map: clockFace }), 0, 0, 0.015, { parent: clock, rot: [Math.PI / 2, 0, 0], shadow: false });
  put(keep(new THREE.TorusGeometry(clockR, 0.014, 10, 96)), clockDark, 0, 0, 0.03, { parent: clock, shadow: false });
  const hand = (w: number, len: number, mat: THREE.Material, z: number, tail = 0.03) => {
    const geo = box(w, len + tail, 0.005, 0.002).translate(0, (len - tail) / 2, 0);
    return put(geo, mat, 0, 0, z, { parent: clock, shadow: false });
  };
  const clockHands = { hour: hand(0.036, 0.28, clockDark, 0.036, 0.04), minute: hand(0.026, 0.4, clockDark, 0.042, 0.04) };
  put(cyl(0.024, 0.024, 0.01, 24), clockDark, 0, 0, 0.05, { parent: clock, rot: [Math.PI / 2, 0, 0], shadow: false });
  const smileyMat = keep(new THREE.MeshPhysicalMaterial({ color: 0xf2c900, roughness: 0.42, metalness: 0, clearcoat: 0.7, clearcoatRoughness: 0.18, bumpMap: clothGrain, bumpScale: 0.0025 }));
  new THREE.TextureLoader().load(smileyUrl, (t) => { if (disposed) { t.dispose(); return; } t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; keep(t); smileyMat.map = t; smileyMat.color.setHex(0xffffff); smileyMat.needsUpdate = true; });
  put(keep(new THREE.CircleGeometry(clockR - 0.004, 64)), smileyMat, 0, 0, -0.002, { parent: clock, rot: [0, Math.PI, 0], shadow: false });
  put(keep(new THREE.TorusGeometry(clockR, 0.014, 10, 96)), clockDark, 0, 0, -0.008, { parent: clock, shadow: false });
  // take it down and a drag on the face winds the hands
  let clockMinutes = 10 * 60 + 10;
  const setClock = () => {
    clockHands.minute.rotation.z = (-(clockMinutes % 60) / 60) * Math.PI * 2;
    clockHands.hour.rotation.z = (-(clockMinutes % 720) / 720) * Math.PI * 2;
  };
  setClock();
  pickables.push(clock);
  states.set(clock, { item: null, home: clock.position.clone(), homeQ: clock.quaternion.clone(), parent: scene, lift: 0, reach: 2.7, offsetX: 0, offsetY: 0, tilt: 0.6, glow: 0.7, spin: 0, pop: 0, out: new THREE.Vector3(1, 0, 0) });
  // midnight turns the clock over; it turns back after a while or when the hands move
  let clockFlipped = false, midnightUntil = 0;
  const MIDNIGHT_LASTS = 30000;
  // at the hit every light goes bar the window and the screen
  let blackout = false, gloom = 0;
  const lampsBefore: boolean[] = [];
  function lightsOut() { blackout = true; lamps.forEach((l, i) => { lampsBefore[i] = l.on; l.on = false; }); }
  function lightsBack() { if (!blackout) return; blackout = false; lamps.forEach((l, i) => { l.on = lampsBefore[i] ?? true; }); }
  function setMidnight(on: boolean) {
    if (on) midnightUntil = performance.now() + MIDNIGHT_LASTS;
    if (on === clockFlipped) return;
    clockFlipped = on;
    const st = states.get(clock);
    if (st) st.homeQ.setFromEuler(new THREE.Euler(0, Math.PI / 2 + (on ? Math.PI : 0), 0));
    screenMode = on ? "comedian" : "rain";
    comedianAt = performance.now() + (on ? 2600 : 0); // the line starts once the glass has gone
    if (on) glassBreakAt = performance.now() + 900; else { healGlass(); lightsBack(); }
    screenLight.color.setHex(on ? 0xff5a5a : 0x9fb8ff);
  }
  plant(5.5, BZ + 1.2, 1.1, true);
  lamp(5.45, 0, 0.9, 3.3, 0.46, 13, true, false);

  // ---- the armchair, the side table, a gamepad, a plant -----------------------------------------------
  const fabric = std(0x2f5c63, 0.92, { bumpMap: clothGrain, bumpScale: 0.012 }), cushion = std(0xc49447, 0.92, { bumpMap: clothGrain, bumpScale: 0.012 });
  const chair = new THREE.Group();
  chair.position.set(3.9, 0, 0.9);
  chair.rotation.y = 0.5;
  scene.add(chair);
  put(box(1.5, 0.46, 1.4, 0.12), fabric, 0, 0.45, 0, { parent: chair });
  put(box(1.36, 0.2, 1.16, 0.09), cushion, 0, 0.78, 0.06, { parent: chair });
  const back = put(box(1.5, 1.3, 0.4, 0.16), fabric, 0, 1.08, -0.62, { parent: chair });
  back.rotation.x = -0.12;
  for (const [bx, by] of [[-0.35, 1.2], [0.35, 1.2], [0, 0.85]]) put(sphere(0.035, 10, 8), std(0x224247, 0.9), bx, by, -0.42, { parent: chair, shadow: false });
  const arm = capsule(0.17, 1.1, 8, 20);
  put(arm, fabric, -0.68, 0.78, 0.02, { parent: chair, rot: [Math.PI / 2, 0, 0] }); put(arm, fabric, 0.68, 0.78, 0.02, { parent: chair, rot: [Math.PI / 2, 0, 0] });
  const footGeo = cyl(0.03, 0.045, 0.26, 12);
  for (const [dx, dz] of [[-0.6, -0.55], [0.6, -0.55], [-0.6, 0.55], [0.6, 0.55]]) { const f = put(footGeo, dark, dx, 0.13, dz, { parent: chair }); f.rotation.set(dz * 0.12, 0, -dx * 0.12); }
  const throwMat = std(0xc4694a, 0.95, { bumpMap: clothGrain, bumpScale: 0.015 });
  put(box(0.5, 0.05, 0.9, 0.025), throwMat, -0.7, 0.98, 0.1, { parent: chair, rot: [0, 0, 0.08] });
  put(box(0.05, 0.6, 0.86, 0.025), throwMat, -0.92, 0.66, 0.1, { parent: chair });
  blob(3.9, 0.9, 2.8, 2.8, 0.5);
  put(box(2.6, 0.02, 2.4, 0.01), std(0x262a33, 0.98, { bumpMap: clothGrain, bumpScale: 0.01 }), 3.4, 0.01, 1.0, { shadow: false, rot: [0, 0.5, 0] });
  const tableTop = keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.36, 0), new THREE.Vector2(0.38, 0.03), new THREE.Vector2(0.36, 0.06), new THREE.Vector2(0, 0.06)], 40));
  put(tableTop, walnut, 2.2, 0.62, 1.7);
  put(cyl(0.03, 0.04, 0.6, 14), dark, 2.2, 0.31, 1.7);
  put(keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.24, 0), new THREE.Vector2(0.22, 0.03), new THREE.Vector2(0.06, 0.06), new THREE.Vector2(0.04, 0.1)], 32)), dark, 2.2, 0, 1.7);
  blob(2.2, 1.7, 1.0, 1.0, 0.4);
  const smallFlat = keep(new THREE.BoxGeometry(FACE.w * 0.9, FACE.d * 0.7, FACE.h * 0.9));
  byLove.slice(4, 7).forEach((s, i) => {
    const m = new THREE.Mesh(smallFlat, [pages, pages, coverMaterial(s, () => undefined), pages, pages, pages]);
    m.position.set(2.1 + (i % 2) * 0.02, 0.68 + i * 0.065, 1.78);
    m.rotation.y = 0.3 + (rng() - 0.5) * 0.3;
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
  });
  const pad = new THREE.Group(); pad.position.set(0.68, 0.96, 0.25); pad.rotation.y = -0.3; chair.add(pad);
  put(box(0.24, 0.04, 0.13, 0.015), std(0x23262e, 0.5), 0, 0, 0, { parent: pad });
  put(cyl(0.02, 0.02, 0.02, 12), std(0x3a3e48, 0.5), -0.05, 0.03, 0.01, { parent: pad, shadow: false }); put(cyl(0.02, 0.02, 0.02, 12), std(0x3a3e48, 0.5), 0.03, 0.03, 0.03, { parent: pad, shadow: false });
  [[0.07, -0.02, 0x3fd8c8], [0.09, 0.0, 0xd23b3b], [0.05, 0.0, 0xf2b632], [0.07, 0.02, 0x2d7fd6]].forEach(([x, z, c]) => put(sphere(0.008, 8, 6), std(c as number, 0.4, { emissive: c as number, emissiveIntensity: 0.3 }), x as number, 0.024, z as number, { parent: pad, shadow: false }));
  plant(-5.2, 1.4, 0.7);

  // ---- the secret: wind the clock to 10:47 and the bookcase sinks into the floor --------------------
  type SecretState = "closed" | "opening" | "open" | "closing";
  let secret: SecretState = "closed", secretAt = 0, ticks = 0;
  const smooth = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
  function openSecret() { secret = "opening"; secretAt = performance.now(); ticks = 0; options.onSecret?.(true); }
  function closeSecret() { if (secret !== "open") return; if (focused === plaque) putBack(); secret = "closing"; secretAt = performance.now(); }
  function setSummary(next: RoomSummary | null) { summary = next; drawPlaque(1); }

  // ---- light ------------------------------------------------------------------------------------
  const hemi = new THREE.HemisphereLight(0x5a6a90, 0x4a3a2c, 0.55);
  scene.add(hemi);
  scene.add(new THREE.AmbientLight(0xffe4c8, 0.12));
  const pendant = new THREE.Group(); pendant.position.set(-0.9, H, -1.0); scene.add(pendant);
  put(cyl(0.006, 0.006, 1.2, 8), dark, 0, -0.6, 0, { parent: pendant, shadow: false });
  put(cyl(0.05, 0.05, 0.03, 16), brassMat, 0, -0.015, 0, { parent: pendant, shadow: false });
  const dome = new THREE.Mesh(keep(new THREE.SphereGeometry(0.32, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)), std(0x3a2a1c, 0.5, { side: THREE.DoubleSide, metalness: 0.2 }));
  dome.position.set(0, -1.28, 0); pendant.add(dome); // the open half faces down, over the bulb
  const pendantBulbMat = std(0xfff3d6, 0.4, { emissive: 0xffd9a0, emissiveIntensity: 1.0 });
  const pendantBulb = put(sphere(0.05, 16, 12), pendantBulbMat, 0, -1.26, 0, { parent: pendant, shadow: false });
  const keyLight = new THREE.SpotLight(0xffd6b0, KEY_INTENSITY, 30, 0.95, 1, 1.3);
  keyLight.position.set(-0.5, 7.5, 5.5);
  keyLight.target.position.set(-1.0, 1.6, BZ);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(1536, 1536);
  keyLight.shadow.bias = -0.0004;
  keyLight.shadow.radius = 6;
  scene.add(keyLight, keyLight.target);
  const pendantLight = new THREE.PointLight(0xffd2a8, 7, 8, 2);
  // the pendant is the room's main light: switching it off takes the key light with it
  addLamp({ parts: [dome, pendantBulb], lights: [{ light: keyLight, max: KEY_INTENSITY * NIGHT.key }, { light: pendantLight, max: 7 * NIGHT.key }], glows: [{ mat: pendantBulbMat, max: 1.0 }], on: true, level: 1 });
  pendantLight.position.set(-0.9, H - 1.3, -1.0);
  scene.add(pendantLight);
  const windowLight = new THREE.RectAreaLight(0x9fb0e6, 4.5, 3.2, 2.6);
  windowLight.position.set(1.6, 3.6, BZ - 0.05);
  windowLight.lookAt(1.6, 1.2, 6);
  scene.add(windowLight);

  // ---- post: ambient occlusion seats everything on everything ----------------------------------------
  const composer = new EffectComposer(renderer);
  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);
  const gtao = new GTAOPass(scene, camera, container.clientWidth || 1, container.clientHeight || 1);
  gtao.output = GTAOPass.OUTPUT.Default;
  gtao.blendIntensity = 0.8;
  gtao.updateGtaoMaterial({ radius: 0.24, distanceExponent: 1, thickness: 1, scale: 1, samples: 10, distanceFallOff: 1, screenSpaceRadius: false });
  // GTAO draws sprites as solid squares; hide them for its normal pass
  const hidePointsAndLines = gtao.overrideVisibility.bind(gtao);
  gtao.overrideVisibility = () => { hidePointsAndLines(); for (const s of sprites) s.visible = false; };
  composer.addPass(gtao);
  composer.addPass(new OutputPass());

  function applyTime(T: TimeOfDay) {
    paint.color.setHex(T.wall);
    paintSide.color.setHex(T.wall).multiplyScalar(0.88);
    windowLight.color.setHex(T.windowColor);
    windowLight.intensity = T.windowIntensity;
    hemi.color.setHex(T.hemiSky);
    hemi.groundColor.setHex(T.hemiGround);
    hemi.intensity = T.hemi;
    keyLight.intensity = KEY_INTENSITY * T.key;
    pendantLight.intensity = 7 * T.key;
    renderer.toneMappingExposure = T.exposure;
    scene.environmentIntensity = T.env;
  }
  applyTime(NIGHT);

  // ---- character standees: a framed picture on a little base with a brass nameplate, in the shelf's empty
  // end slots; they come to hand like the comics --------------------------------------------------------
  const characterByMesh = new Map<THREE.Object3D, RoomCharacter>();
  const standees: THREE.Group[] = [];
  const standeeFrame = std(0x1a1b20, 0.5, { metalness: 0.2 }), standeePic = keep(new THREE.PlaneGeometry(0.33, 0.46)), standeePlate = keep(new THREE.PlaneGeometry(0.24, 0.022));
  function setCharacters(list: RoomCharacter[]) {
    for (const g of standees) {
      if (focused === g) putBack();
      pickables.splice(pickables.indexOf(g), 1);
      states.delete(g);
      characterByMesh.delete(g);
      unit.group.remove(g);
    }
    standees.length = 0;
    list.slice(0, standeeSlots.length).forEach((c, i) => {
      const [x, y, z] = standeeSlots[i];
      const g = new THREE.Group();
      g.position.set(x, y, z);
      g.rotation.x = -0.08;
      unit.group.add(g);
      put(box(0.3, 0.035, 0.14, 0.006), standeeFrame, 0, 0.017, 0, { parent: g });
      put(box(0.37, 0.5, 0.014, 0.004), standeeFrame, 0, 0.3, -0.02, { parent: g });
      const pic = std(0x2a2d35, 0.6);
      put(standeePic, pic, 0, 0.3, -0.012, { parent: g, shadow: false });
      const plate = canvasTexture((gc, w, h) => { gc.fillStyle = "#b08a3e"; gc.fillRect(0, 0, w, h); gc.fillStyle = "#2a1f0f"; gc.font = "bold 40px system-ui, sans-serif"; gc.textAlign = "center"; gc.textBaseline = "middle"; gc.fillText(c.title.toUpperCase(), w / 2, h / 2 + 2); }, 512, 64);
      put(standeePlate, std(0xffffff, 0.35, { map: plate, metalness: 0.5 }), 0, 0.018, 0.0705, { parent: g, shadow: false });
      const loader = new THREE.TextureLoader();
      loader.crossOrigin = "anonymous";
      loader.load(c.image, (tex) => {
        if (disposed) { tex.dispose(); return; }
        tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; keep(tex);
        const img = tex.image as { width: number; height: number }, want = 0.33 / 0.46, have = img.width / img.height;
        if (have > want) { tex.repeat.set(want / have, 1); tex.offset.set((1 - want / have) / 2, 0); } else { tex.repeat.set(1, have / want); tex.offset.set(0, (1 - have / want) / 2); }
        pic.map = tex; pic.color.setHex(0xffffff); pic.needsUpdate = true;
      });
      pickables.push(g);
      states.set(g, { item: null, home: g.position.clone(), homeQ: g.quaternion.clone(), parent: unit.group, lift: 0, reach: 1.15, offsetX: 0, offsetY: -0.27, tilt: 1.2, glow: 1, spin: 0, pop: 0, out: new THREE.Vector3(0, 0, 1) });
      characterByMesh.set(g, c);
      standees.push(g);
    });
    retarget();
  }

  // ---- shelfies: the bookcase shot straight on, then pinned to the wall by the window as a print --------
  interface Photo extends RoomPhoto { mesh: THREE.Mesh }
  const photos: Photo[] = [];
  const photoByMesh = new Map<THREE.Object3D, Photo>();
  let photoSeq = 0;
  const PINS = [[-0.72, 4.6], [-0.72, 3.86], [-0.72, 3.12]];
  const shelfCam = new THREE.PerspectiveCamera(44, 0.8, 0.1, 60);
  shelfCam.position.set(-3.35, 2.75, BZ + 0.86 + 8.6);
  shelfCam.lookAt(-3.35, 2.62, BZ);
  const paper = std(0xf4f0e8, 0.9), pinMat = std(0xc0392b, 0.4);
  const photoGeo = box(0.32, 0.5, 0.006, 0.002), pinGeo = sphere(0.012, 10, 8);
  function takeShelfie(): RoomPhoto | null {
    if (secret !== "closed") return null;
    const W = 1800, H = 2250;
    renderPass.camera = shelfCam; gtao.camera = shelfCam;
    renderer.setPixelRatio(1);
    renderer.setSize(W, H, false);
    composer.setSize(W, H);
    composer.render();
    // the canvas is read now and encoded off the main thread into a blob, so no multi-megabyte string is made
    const taken = new Date(), img = new Image();
    const photo: Photo = { id: ++photoSeq, taken, url: "", mesh: new THREE.Mesh() };
    renderer.domElement.toBlob((blob) => { if (!blob || disposed) return; photo.url = URL.createObjectURL(blob); img.src = photo.url; }, "image/jpeg", 0.92);
    renderPass.camera = camera; gtao.camera = camera;
    renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio || 1));
    resize();
    const tex = canvasTexture((g, w, h) => { g.fillStyle = "#f6f3ec"; g.fillRect(0, 0, w, h); g.fillStyle = "#1a1a1e"; g.fillRect(56, 56, w - 112, 1216); }, 1024, 1600);
    tex.anisotropy = 16;
    img.onload = () => {
      const c = tex.image as HTMLCanvasElement, g = c.getContext("2d");
      if (!g || disposed) return;
      g.drawImage(img, 56, 56, c.width - 112, 1216);
      g.fillStyle = "#2b2b33"; g.font = "64px 'Segoe Print', 'Bradley Hand', 'Comic Sans MS', cursive"; g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText(`3d shelf · ${taken.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })}`, c.width / 2, 1436);
      tex.needsUpdate = true;
    };
    const mesh = new THREE.Mesh(photoGeo, [paper, paper, paper, paper, keep(new THREE.MeshStandardMaterial({ map: tex, roughness: 0.7 })), paper]);
    put(pinGeo, pinMat, 0, 0.235, 0.008, { parent: mesh, shadow: false });
    mesh.castShadow = true;
    camera.getWorldDirection(mesh.position).multiplyScalar(2.2).add(camera.position); // it starts in front of you and flies to its pin
    scene.add(mesh);
    photo.mesh = mesh;
    photoByMesh.set(mesh, photo);
    pickables.push(mesh);
    states.set(mesh, { item: null, home: new THREE.Vector3(), homeQ: new THREE.Quaternion(), parent: scene, lift: 0, reach: 1.0, offsetX: 0, offsetY: 0, tilt: 1.2, glow: 1, spin: 0, pop: 0, out: new THREE.Vector3(0, 0, 1) });
    photos.unshift(photo);
    while (photos.length > PINS.length) dropPhoto(photos.pop() as Photo);
    pinPhotos();
    retarget();
    return { id: photo.id, taken, url: photo.url };
  }
  function pinPhotos() {
    photos.forEach((ph, i) => {
      const st = states.get(ph.mesh);
      if (!st) return;
      st.home.set(PINS[i][0], PINS[i][1], BZ + 0.02);
      st.homeQ.setFromEuler(new THREE.Euler(0, 0, (ph.id % 2 ? 1 : -1) * (0.03 + (ph.id % 3) * 0.015)));
    });
  }
  // a print that comes off the wall drops to the floor, lies there a moment, and fades away
  const falling: { mesh: THREE.Mesh; v: THREE.Vector3; spin: THREE.Vector3; landed: number; mats: THREE.Material[] }[] = [];
  function dropPhoto(ph: Photo) {
    if (focused === ph.mesh) putBack();
    setTimeout(() => URL.revokeObjectURL(ph.url), 2000);
    pickables.splice(pickables.indexOf(ph.mesh), 1);
    states.delete(ph.mesh);
    photoByMesh.delete(ph.mesh);
    const mats = (ph.mesh.material as THREE.Material[]).map((m) => { const c = m.clone(); c.transparent = true; return c; });
    ph.mesh.material = mats;
    falling.push({ mesh: ph.mesh, v: new THREE.Vector3((rng() - 0.5) * 0.4, 0.3, 0.5 + rng() * 0.5), spin: new THREE.Vector3((rng() - 0.5) * 4, (rng() - 0.5) * 3, (rng() - 0.5) * 5), landed: 0, mats });
  }
  function removePhoto(id: number) {
    const i = photos.findIndex((ph) => ph.id === id);
    if (i < 0) return;
    dropPhoto(photos[i]);
    photos.splice(i, 1);
    pinPhotos();
    retarget();
  }

  // When the machine cannot keep up, the costly half of the look goes quietly: occlusion first, then shadows.
  let detailLevel = 2;
  let slowFrames = 0;
  function degrade() {
    detailLevel--;
    if (detailLevel === 1) gtao.enabled = false;
    if (detailLevel === 0) {
      renderer.shadowMap.enabled = false;
      scene.traverse((o) => {
        const m = o as THREE.Mesh;
        if (!m.material) return;
        (Array.isArray(m.material) ? m.material : [m.material]).forEach((mat) => { mat.needsUpdate = true; });
      });
    }
  }

  // ---- pointing, picking, the loop -------------------------------------------------------------------
  mergeStatic(passage, [plaque]);
  mergeStatic(unit.group, pickables);
  mergeStatic(chair);
  mergeStatic(clock, [clockHands.hour, clockHands.minute]);
  const el = renderer.domElement;
  let press: { x: number; y: number } | null = null;
  const readMouse = (e: PointerEvent) => { const r = el.getBoundingClientRect(); mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); };
  let clockDrag: { angle: number } | null = null;
  const clockAngle = () => { clock.getWorldPosition(tmpV).project(camera); return Math.atan2(mouse.y - tmpV.y, (mouse.x - tmpV.x) * camera.aspect); };
  const onDown = (e: PointerEvent) => {
    if (e.button !== 0) return;
    press = { x: e.clientX, y: e.clientY };
    if (focused === clock && secret === "closed") {
      readMouse(e);
      raycaster.setFromCamera(mouse, camera);
      if (raycaster.intersectObjects(clock.children, true).length) { clockDrag = { angle: clockAngle() }; press = null; }
    }
  };
  const onMove = (e: PointerEvent) => {
    readMouse(e);
    lastMove = performance.now();
    if (clockDrag) {
      const a = clockAngle(), d = Math.atan2(Math.sin(a - clockDrag.angle), Math.cos(a - clockDrag.angle));
      clockMinutes -= (d / (Math.PI * 2)) * 60; // clockwise on the face winds forward
      clockDrag.angle = a;
      setClock();
      if (clockFlipped && Math.abs(d) > 0.01) setMidnight(false); // touching the hands ends midnight
    }
  };
  const onUp = (e: PointerEvent) => {
    if (clockDrag) {
      clockDrag = null;
      const m = ((clockMinutes % 720) + 720) % 720;
      if (Math.abs(m - 647) < 1.5) { clockMinutes = 647; setClock(); putBack(); openSecret(); } // 10:47, the Wayne Manor time
      else if (Math.min(m, 720 - m) < 1.5) { clockMinutes = 0; setClock(); putBack(); setMidnight(true); } // midnight
      press = null;
      return;
    }
    if (secret === "opening" || secret === "closing") { press = null; return; }
    if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) < 6) {
      if (focused) putBack();
      else if (lampHot) lampHot.on = !lampHot.on;
      else if (hovered) pickUp(hovered);
      else if (secret === "open") closeSecret();
    }
    press = null;
  };
  const onLeave = () => { mouse.set(-10, -10); el.style.cursor = ""; lampHot = null; };
  const lampParts = lamps.flatMap((l) => l.parts);
  // the walls and the bookcase's back panel count too, so nothing hidden behind them can be reached
  // everything static at scene level, last: the lift's subtree, lamps, the pane, the bars and the flash stay as they are
  mergeStatic(scene, [...pickables, ...lampParts, lift, pane, flash, ...bars.map((b) => b.mesh)]);
  const occluders: THREE.Object3D[] = [unit.back, ...scene.children.filter((o) => (o as THREE.Mesh).material === paint || (o as THREE.Mesh).material === paintSide)];
  let hitTargets = pickables.concat(lampParts, occluders);
  const retarget = () => { hitTargets = pickables.concat(lampParts, occluders); }; // when prints come and go
  // nothing smaller than a coin casts a shadow
  scene.traverse((o) => {
    const m = o as THREE.Mesh;
    if (!m.isMesh || !m.castShadow) return;
    m.geometry.computeBoundingSphere();
    if ((m.geometry.boundingSphere?.radius ?? 1) * Math.max(m.scale.x, m.scale.y, m.scale.z) < 0.06) m.castShadow = false;
  });
  const onWheel = (e: WheelEvent) => { e.preventDefault(); lean = Math.max(0, Math.min(1, lean + e.deltaY * -0.0012)); };
  el.addEventListener("pointerdown", onDown);
  el.addEventListener("pointermove", onMove);
  el.addEventListener("pointerup", onUp);
  el.addEventListener("pointercancel", onUp);
  el.addEventListener("pointerleave", onLeave);
  el.addEventListener("wheel", onWheel, { passive: false });

  function pickUp(m: THREE.Object3D) {
    focused = m;
    hovered = null;
    options.onHover?.(null);
    if (m.parent !== scene) scene.attach(m);
    options.onPick?.(states.get(m)?.item ?? null);
    const ph = photoByMesh.get(m);
    options.onPhoto?.(ph ? { id: ph.id, taken: ph.taken, url: ph.url } : null);
    options.onCharacter?.(characterByMesh.get(m) ?? null);
    options.onHold?.(true);
  }
  function putBack() {
    if (!focused) { closeSecret(); return; }
    const st = states.get(focused);
    if (st && st.parent !== scene) st.parent.attach(focused);
    focused = null;
    options.onPick?.(null);
    options.onPhoto?.(null);
    options.onCharacter?.(null);
    options.onHold?.(false);
  }

  const tmpV = new THREE.Vector3(), tmpQ = new THREE.Quaternion(), tmpE = new THREE.Euler(), tiltQ = new THREE.Quaternion();
  const footV = new THREE.Vector3(), lastFoot = { x: -1, y: -1 };
  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    if (!w || !h) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    composer.setSize(w, h);
  }
  const observer = new ResizeObserver(resize);
  observer.observe(container);
  resize();

  const started = performance.now();
  let last = started;
  function tick() {
    const now = performance.now();
    const dt = Math.min(0.05, (now - last) / 1000);
    const frameMs = now - last;
    last = now;
    const t = (now - started) / 1000;
    frameNo++;
    if (t > 2 && detailLevel > 0) { slowFrames = frameMs > 34 ? slowFrames + 1 : Math.max(0, slowFrames - 2); if (slowFrames > 90) { degrade(); slowFrames = 0; } }

    const px = mouse.x > -5 ? mouse.x : 0, py = mouse.y > -5 ? mouse.y : 0;
    camLean += (lean - camLean) * 0.06;
    camera.position.x += (CAM.x + px * 0.35 - camera.position.x) * 0.05;
    camera.position.y += (CAM.y + py * 0.18 - camera.position.y) * 0.05;
    camera.position.z += (CAM.z - camLean * 2.6 - camera.position.z) * 0.05;
    camera.lookAt(CAM.tx + px * 0.12, CAM.ty + py * 0.08, CAM.tz);
    if (now < shakeUntil) {
      const k = (shakeUntil - now) / 520;
      camera.position.x += (rng() - 0.5) * 0.45 * k; camera.position.y += (rng() - 0.5) * 0.32 * k;
      camera.rotation.z += (rng() - 0.5) * 0.06 * k;
    }
    const glow = focused ? states.get(focused)?.glow ?? 1 : 0;
    handLight.intensity += (11 * glow - handLight.intensity) * 0.1;
    handFill.intensity += (4 * glow - handFill.intensity) * 0.1;
    gloom += ((blackout ? 1 : 0) - gloom) * 0.12;
    const lit = 1 - gloom;

    if (!focused && now - lastMove < 120 && mouse.x > -5) {
      raycaster.setFromCamera(mouse, camera);
      const first = raycaster.intersectObjects(hitTargets, true).find((h) => h.object.visible);
      const hit = first && !occluders.includes(first.object) ? first : undefined;
      let next: THREE.Object3D | null = hit ? hit.object : null;
      lampHot = (hit && lampByMesh.get(hit.object)) ?? null;
      if (lampHot) next = null;
      while (next && !states.has(next)) next = next.parent;
      if (next && states.get(next)?.flip) next = null; // mid-turn, not for taking
      if (next !== hovered) {
        hovered = next;
        options.onHover?.(next ? states.get(next)?.item ?? null : null);
      }
      el.style.cursor = lampHot || (next && !states.get(next)?.item) ? "pointer" : "";
    }
    if (focused || secret === "opening" || secret === "closing" || burstT >= 0 || falling.length || clockDrag) shadowFrames = 2;
    for (const m of pickables) {
      const st = states.get(m);
      if (!st) continue;
      if (st.flip) shadowFrames = 2;
      if (st.flip) {
        const u = (now / 1000 - st.flip.start) / st.flip.dur;
        if (u >= 0) {
          const e = u >= 1 ? 1 : u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
          st.spin = (e < 0.5 ? e : 1 - e) * Math.PI;
          st.pop = Math.sin(e * Math.PI) * 0.55;
          if (!st.flip.swapped && e >= 0.5) {
            st.flip.swapped = true;
            const s = st.flip.item;
            st.item = s;
            m.visible = !!s;
            if (s) (m as THREE.Mesh).material = [coverMaterial(s, noop), pages];
          }
          if (u >= 1) { st.flip = undefined; st.spin = 0; st.pop = 0; }
        }
      }
      if (m === focused) {
        camera.getWorldDirection(tmpV);
        tmpV.multiplyScalar(st.reach).add(camera.position);
        tmpV.x += st.offsetX;
        tmpV.y += st.offsetY;
        m.position.lerp(tmpV, 0.1);
        tmpE.set(-(clockDrag ? 0 : py) * 0.28 * st.tilt, (clockDrag ? 0 : px) * 0.38 * st.tilt, 0); // winding the clock holds it still
        tiltQ.setFromEuler(tmpE);
        tmpQ.copy(camera.quaternion).multiply(tiltQ);
        m.quaternion.slerp(tmpQ, 0.1);
      } else if (m.parent === st.parent) {
        st.lift += ((m === hovered ? 1 : 0) - st.lift) * 0.15;
        tmpV.copy(st.home).addScaledVector(st.out, st.lift * 0.16 + st.pop);
        tmpV.y += st.lift * 0.03;
        tmpE.setFromQuaternion(st.homeQ);
        tmpE.x -= st.lift * 0.05;
        tmpE.y += st.spin;
        tmpQ.setFromEuler(tmpE);
        if (st.flip) { m.position.copy(tmpV); m.quaternion.copy(tmpQ); }
        else {
          if (m.position.distanceToSquared(tmpV) > 1e-8 || 1 - Math.abs(m.quaternion.dot(tmpQ)) > 1e-7) shadowFrames = 2;
          m.position.lerp(tmpV, 0.15); m.quaternion.slerp(tmpQ, 0.15);
        }
      }
    }
    if (pageBusy && now / 1000 >= busyUntil) { pageBusy = false; options.onPage?.(currentPage, pageCount, false); }
    if (now - rainAt > 150) { rainAt = now; if (screenMode === "rain") rainStep(); else comedianStep(now); }
    if (clockFlipped && now > midnightUntil) setMidnight(false);
    for (let i = falling.length - 1; i >= 0; i--) {
      const f = falling[i], m = f.mesh;
      if (!f.landed) {
        f.v.y -= 9 * dt;
        m.position.addScaledVector(f.v, dt);
        m.rotation.x += f.spin.x * dt; m.rotation.y += f.spin.y * dt; m.rotation.z += f.spin.z * dt;
        if (m.position.y <= 0.03) { m.position.y = 0.03; m.rotation.set(-Math.PI / 2, 0, m.rotation.z); f.landed = now; }
      } else if (now - f.landed > 900) {
        let gone = true;
        for (const mat of f.mats) { mat.opacity = Math.max(0, mat.opacity - dt * 1.4); if (mat.opacity > 0) gone = false; }
        if (gone) { scene.remove(m); f.mats.forEach((mat) => mat.dispose()); falling.splice(i, 1); }
      }
    }
    if (glassBreakAt && now >= glassBreakAt) { glassBreakAt = 0; breakGlass(); }
    if (burstT >= 0) {
      const step = dt * (burstT < 0.55 ? 0.18 : 1); // the slow beat, then real time
      burstT += step;
      flashMat.opacity = Math.max(0, flashMat.opacity - dt * 5);
      for (const sh of [...shards, ...bars]) {
        if (!sh.flying) continue;
        const m = sh.mesh;
        m.position.addScaledVector(sh.v, step);
        sh.v.y -= 7 * step;
        m.rotation.x += sh.spin.x * step; m.rotation.y += sh.spin.y * step; m.rotation.z += sh.spin.z * step;
        if (m.position.z < BZ - 0.15) { if (m.position.y < 1.9 || m.position.z < BZ - 2.3) { m.visible = false; sh.flying = false; } continue; }
        const ground = m.position.z > BZ + 0.5 ? 1.065 : 2.325;
        if (m.position.y <= ground) { m.position.y = ground; m.rotation.set(-Math.PI / 2, 0, m.rotation.z); sh.flying = false; }
      }
    }
    if (secret === "opening" || secret === "closing") {
      const sec = (now - secretAt) / 1000;
      if (secret === "opening") {
        // three ticks of the minute hand, the lamps go out one by one, then the bookcase goes down
        if (ticks < 3 && sec > 0.3 * (ticks + 1)) { ticks++; clockMinutes += 1; setClock(); }
        if (sec > 1.2) lamps[0].on = false;
        if (sec > 1.7) lamps[1].on = false;
        if (sec > 2.2) lamps[2].on = false;
        const u = smooth(Math.min(1, Math.max(0, (sec - 2.4) / 3.6)));
        lift.position.y = -u * LIFT_DROP;
        stairLight.intensity = u * 7;
        if (sec >= 6.0) secret = "open";
      } else {
        const u = 1 - smooth(Math.min(1, sec / 3.4));
        lift.position.y = -u * LIFT_DROP;
        stairLight.intensity = u * 7;
        if (sec > 3.6) lamps[2].on = true;
        if (sec > 4.0) lamps[1].on = true;
        if (sec > 4.4) lamps[0].on = true;
        if (sec >= 4.6) { secret = "closed"; options.onSecret?.(false); }
      }
    }
    const signalWant = secret === "open" || (secret === "opening" && now - secretAt > 2600) ? 1 : 0;
    signalLevel += (signalWant - signalLevel) * 0.03;
    signalMat.opacity = signalLevel * (0.93 + Math.sin(t * 2.6) * 0.07);
    beamMat.opacity = signalLevel * 0.55;
    const spotWant = secret === "open" || (secret === "opening" && now - secretAt > 5400) ? 20 : 0;
    const flicker = spotWant && now - secretAt < 6300 ? 0.7 + rng() * 0.3 : 1;
    caseSpot.intensity += (spotWant * flicker - caseSpot.intensity) * 0.3;

    for (const l of lamps) {
      l.level += ((l.on ? 1 : 0) - l.level) * 0.12;
      for (const { light, max } of l.lights) light.intensity = max * l.level;
      for (const { mat, max } of l.glows) mat.emissiveIntensity = max * l.level;
    }
    // the view pins the shelf switcher under the bookcase
    camera.updateMatrixWorld();
    unit.group.getWorldPosition(footV); footV.y = 0; footV.z += 0.55; footV.project(camera);
    const fx = (footV.x + 1) / 2, fy = (1 - footV.y) / 2;
    if (Math.abs(fx - lastFoot.x) > 0.002 || Math.abs(fy - lastFoot.y) > 0.002) { lastFoot.x = fx; lastFoot.y = fy; options.onLayout?.({ x: fx, y: fy }); }
    if (shadowFrames > 0) { renderer.shadowMap.needsUpdate = true; shadowFrames--; }
    composer.render();
  }
  renderer.setAnimationLoop(tick);

  return {
    showPage,
    takeShelfie,
    removePhoto,
    setCharacters,
    setSummary,
    putBack,
    dispose() {
      disposed = true;
      renderer.setAnimationLoop(null);
      observer.disconnect();
      el.removeEventListener("pointerdown", onDown);
      el.removeEventListener("pointermove", onMove);
      el.removeEventListener("pointerup", onUp);
      el.removeEventListener("pointercancel", onUp);
      el.removeEventListener("pointerleave", onLeave);
      el.removeEventListener("wheel", onWheel);
      for (const d of disposables) d.dispose();
      for (const f of falling) f.mats.forEach((m) => m.dispose());
      for (const ph of photos) if (ph.url) URL.revokeObjectURL(ph.url);
      gtao.dispose();
      composer.dispose();
      scene.environment?.dispose();
      renderer.dispose();
      el.remove();
    },
  };
}
