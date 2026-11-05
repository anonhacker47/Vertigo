/**
 * The reading room: a small Three.js set seen head on. Shelves on the left hold the best-loved
 * series face out, the window sits over a desk with a screen, and the armchair waits in front.
 * It is always night: warm lamps, a cool window, and
 * screen-space ambient occlusion seats everything. Nothing here depends on Vue; the view owns the
 * DOM around it and talks to the scene through the handle this returns.
 */
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { RectAreaLightUniformsLib } from "three/examples/jsm/lights/RectAreaLightUniformsLib.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import type { RoomSeries } from "./roomData";

export interface RoomOptions {
  onProgress?: (loaded: number, total: number) => void;
  onPick?: (series: RoomSeries | null) => void;
  onHover?: (series: RoomSeries | null) => void;
}

export interface RoomHandle {
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
const FACE_STEP = 0.52;
const KEY_INTENSITY = 26;
const CAM = { x: 0.2, y: 2.25, z: 9.4, tx: 0.2, ty: 2.15, tz: -3 };
const BZ = -4; // the back wall
const H = 6.2; // the ceiling
/** Something you can pick up: where it lives, and how it sits in the hand. */
interface Pickable {
  series: RoomSeries | null;
  home: THREE.Vector3;
  homeQ: THREE.Quaternion;
  parent: THREE.Object3D;
  lift: number;
  reach: number; // how far in front of the camera it floats
  offsetX: number;
  offsetY: number;
  tilt: number; // how much it tips with the pointer
  glow: number; // how much of the hand lights it wants: a cover needs reading, dark glass does not
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

export function createRoom(container: HTMLElement, series: RoomSeries[], options: RoomOptions = {}): RoomHandle {
  const rng = mulberry32(21);
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio || 1));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.04;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);
  RectAreaLightUniformsLib.init();

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0b10);
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 60);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
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
  /** Whoever wants a cover's pixels once they arrive (the screen on the desk paints them). */
  const coverPainters = new Map<number, (img: HTMLImageElement) => void>();
  const disposables: { dispose(): void }[] = [];
  const mouse = new THREE.Vector2(-10, -10);
  const raycaster = new THREE.Raycaster();
  let hovered: THREE.Object3D | null = null;
  let focused: THREE.Object3D | null = null;
  let lastMove = 0;
  let lean = 0;
  let camLean = 0;
  let loaded = 0;
  let total = 0;

  // ---- helpers ------------------------------------------------------------------------------
  const keep = <T extends { dispose(): void }>(g: T): T => { disposables.push(g); return g; };
  const std = (color: THREE.ColorRepresentation, roughness = 0.9, extra: THREE.MeshStandardMaterialParameters = {}) =>
    keep(new THREE.MeshStandardMaterial({ color, roughness, metalness: 0, ...extra }));
  const brassMat = keep(new THREE.MeshStandardMaterial({ color: 0xb08a3e, roughness: 0.32, metalness: 0.9 }));
  const box = (w: number, h: number, d: number, r = 0.02) => keep(new RoundedBoxGeometry(w, h, d, 4, Math.max(0.004, Math.min(r, w / 2, h / 2, d / 2))));
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
  const townTexture = () => canvasTexture((g) => {
    g.clearRect(0, 0, 256, 256);
    let x = 0;
    while (x < 256) {
      const w = 18 + rng() * 30, h = 40 + rng() * 70;
      g.fillStyle = "#070a16"; g.fillRect(x, 256 - h, w, h);
      for (let wy = 256 - h + 8; wy < 248; wy += 12) for (let wx = x + 4; wx < x + w - 5; wx += 8) if (rng() < 0.45) { g.fillStyle = rng() < 0.7 ? "rgba(255,206,140,.9)" : "rgba(170,200,255,.8)"; g.fillRect(wx, wy, 3, 4); }
      x += w + 2 + rng() * 6;
    }
  });
  function coverPlaceholder(s: RoomSeries) {
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
  // The crease a hardcover has beside its spine, drawn the way the app's cover tiles draw it: a dark
  // edge, a lit bulge, the groove, a lit lip, fading out by a fifth of the width. The shade is baked
  // into the colour so it reads from across the room; the normal map lets the lamps catch it up close.
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
  /** The cover art as a glossy board. `print` leaves the spine crease off, for covers behind glass. */
  function coverMaterial(s: RoomSeries, onDone: () => void, print = false) {
    const key = `${s.id}:${print ? "print" : "board"}`;
    const cached = coverMaterials.get(key);
    if (cached) { setTimeout(onDone, 0); return cached; }
    const mat = keep(new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.48, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.4, map: coverPlaceholder(s) }));
    if (!print) { mat.normalMap = spineNormal; mat.normalScale.set(0.6, 0.6); mat.onBeforeCompile = spineShade; }
    coverMaterials.set(key, mat);
    const loader = new THREE.TextureLoader();
    loader.crossOrigin = "anonymous";
    loader.load(
      s.cover,
      (t) => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; keep(t); mat.map?.dispose(); mat.map = t; mat.needsUpdate = true; coverPainters.get(s.id)?.(t.image as HTMLImageElement); onDone(); },
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
  const glowTexture = radialSprite("rgba(255,205,140,1)");

  function shelfUnit(width: number, height: number, depth: number, shelves: number, wood: THREE.Material, back: THREE.Material) {
    const g = new THREE.Group();
    const t = 0.07;
    put(box(t, height, depth, 0.01), wood, -width / 2 + t / 2, height / 2, 0, { parent: g });
    put(box(t, height, depth, 0.01), wood, width / 2 - t / 2, height / 2, 0, { parent: g });
    put(box(width, height, t, 0.005), back, 0, height / 2, -depth / 2 + t / 2, { parent: g });
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
    return { group: g, ys, inner: width - 2 * t - 0.12, backZ: -depth / 2 + t };
  }
  const twinkles: THREE.MeshStandardMaterial[] = [];
  /** Halos and flames. The occlusion pass would draw these as solid squares, so it skips them. */
  const sprites: THREE.Sprite[] = [];
  function fairyLights(points: THREE.Vector3[]) {
    const curve = new THREE.CatmullRomCurve3(points);
    scene.add(new THREE.Mesh(keep(new THREE.TubeGeometry(curve, 48, 0.006, 5)), std(0x2a2520, 1)));
    const bulb = sphere(0.026, 10, 8);
    const n = Math.round(curve.getLength() / 0.28);
    for (let i = 1; i < n; i++) {
      const p = curve.getPointAt(i / n);
      const mat = std(0xffe2b0, 1, { emissive: 0xffc27a, emissiveIntensity: 1.1 });
      twinkles.push(mat);
      const b = new THREE.Mesh(bulb, mat);
      b.position.copy(p); b.position.y -= 0.035; scene.add(b);
      const halo = new THREE.Sprite(keep(new THREE.SpriteMaterial({ map: glowTexture, color: 0xffc98a, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false })));
      halo.position.copy(b.position); halo.scale.set(0.16, 0.16, 1); scene.add(halo); sprites.push(halo);
    }
  }
  interface Lamp { shade: THREE.MeshStandardMaterial; bulb: THREE.SpotLight; glow: THREE.PointLight; power: number }
  const lamps: Lamp[] = [];
  function lamp(x: number, y: number, z: number, poleH: number, shadeR: number, power: number, drum = false, shadows = true) {
    const g = new THREE.Group();
    g.position.set(x, y, z);
    scene.add(g);
    put(keep(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(0.2, 0), new THREE.Vector2(0.2, 0.02), new THREE.Vector2(0.12, 0.05), new THREE.Vector2(0.05, 0.08), new THREE.Vector2(0.03, 0.1)], 32)), brassMat, 0, 0, 0, { parent: g });
    put(cyl(0.018, 0.018, poleH, 16), brassMat, 0, poleH / 2, 0, { parent: g });
    put(sphere(0.06, 16, 12), std(0xfff3d6, 0.4, { emissive: 0xffd9a0, emissiveIntensity: 1.2 }), 0, poleH + shadeR * 0.35, 0, { parent: g, shadow: false });
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
    const glow = new THREE.PointLight(0xffb36b, power * 0.5, 6, 2);
    glow.position.set(0, poleH + shadeR * 0.6, 0);
    g.add(glow);
    lamps.push({ shade: shadeMat, bulb, glow, power });
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
  /**
   * A comic as a slim hardcover: a cover board with a soft fore edge, the page block set in behind it,
   * and a square spine wrapping round to the back board. Three material groups: cover, pages, spine.
   */
  function comicGeometry(w: number, h: number, d: number) {
    const board = 0.012, inset = 0.014;
    // the rounded boxes come non-indexed, so the plain ones must match before they can merge
    const plain = (geo: THREE.BufferGeometry) => { const n = geo.toNonIndexed(); geo.dispose(); return n; };
    const front = new RoundedBoxGeometry(w, h, board, 3, 0.006).translate(0, 0, d / 2 - board / 2);
    const block = plain(new THREE.BoxGeometry(w - inset, h - inset * 2, d - board * 2)).translate(inset / 2, 0, 0);
    const back = new RoundedBoxGeometry(w, h, board, 3, 0.006).translate(0, 0, -d / 2 + board / 2);
    const spine = plain(new THREE.BoxGeometry(0.02, h, d - board * 2)).translate(-w / 2 + 0.01, 0, 0);
    const shell = mergeGeometries([back, spine], false);
    if (!shell) throw new Error("comic shell");
    const g = mergeGeometries([front, block, shell], true);
    if (!g) throw new Error("comic geometry");
    for (const x of [front, block, back, spine, shell]) x.dispose();
    return keep(g);
  }
  const spineMaterial = (s: RoomSeries) => std(`rgb(${s.rgb.join(",")})`, 0.7);
  function addComic(s: RoomSeries, geo: THREE.BufferGeometry, x: number, y: number, z: number, parent: THREE.Object3D, onDone: () => void) {
    const m = new THREE.Mesh(geo, [coverMaterial(s, onDone), pages, spineMaterial(s)]);
    m.position.set(x, y, z);
    m.rotation.x = -0.1;
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    pickables.push(m);
    states.set(m, { series: s, home: m.position.clone(), homeQ: m.quaternion.clone(), parent, lift: 0, reach: 2.2, offsetX: -0.3, offsetY: -0.05, tilt: 1, glow: 1 });
  }
  /**
   * The Vertigo mark as the solid its logo draws. The logo is an isometric view of two square bars rising
   * from a shared corner, each capped by a cuboid, with a small square block where their two side faces
   * meet. Five boxes, flat-shaded, turned to that isometric view: looked at head on it reads as the mark,
   * in hand it is a crisp solid. Light faces are the ones the logo draws light (tops and fronts), dark
   * faces are the sides. Origin: the middle of the bottom back edge; the front faces +z.
   */
  function logoGeometry(height: number) {
    interface Face { pts: THREE.Vector3[]; lit: boolean }
    const V3 = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
    /**
     * The faces of the box o + x·a + y·b + z·c, wound outward; `lit` lists the light ones (+a -a +b -b +c -c)
     * and `skip` the ones left out because another piece covers them (a hidden face still bleeds through
     * along a shared edge, and lit sideways by the hand lights it shows as a bright seam).
     */
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
    // In the logo's units, Z up, the shared inner corner at X = Y = 0, the cap tops at Z = 0. The right arm
    // runs along +X and down, stops at the middle plane X = Y and at the floor; the left arm is its mirror.
    const W = 40, D = 67, T = 21, FLOOR = -169;
    const FRONT = 0.836 * 40 + 0.549 * T; // each bar's front face: 0.836·X + 0.549·Z = -FRONT (mirrored for the left arm)
    const right = V3(0.549, 0, -0.836).multiplyScalar(320), left = V3(0, 0.549, -0.836).multiplyScalar(320);
    const floor = (faces: Face[]) => clip(faces, V3(0, 0, -1), -FLOOR);
    const solid: Face[] = [
      // the caps sit on the bars, and the bars meet each other on the middle plane: none of those faces exist
      ...boxFaces(V3(-107, 0, -T), V3(D, 0, 0), V3(0, W, 0), V3(0, 0, T), ["+a", "+c"], ["-c"]), // right cap: front and top light
      ...floor(clip(boxFaces(V3(-107, 0, -T), V3(D, 0, 0), V3(0, W, 0), right, ["+a"], ["-c"]), V3(1, -1, 0), 0, false)), // right bar
      ...boxFaces(V3(0, -107, -T), V3(W, 0, 0), V3(0, D, 0), V3(0, 0, T), ["+b", "+c"], ["-c"]), // left cap
      ...floor(clip(boxFaces(V3(0, -107, -T), V3(W, 0, 0), V3(0, D, 0), left, ["+b"], ["-c"]), V3(-1, 1, 0), 0, false)), // left bar
      // the square block where the sides meet: flush with both sides, and only the part in front of the bars'
      // front faces, so it meets them edge to edge instead of overlapping them
      ...clip(clip(boxFaces(V3(13.3, 13.3, FLOOR), V3(26.7, 0, 0), V3(0, 26.7, 0), V3(0, 0, -115 - FLOOR), ["+c"]), V3(-0.836, 0, -0.549), FRONT), V3(0, -0.836, -0.549), FRONT),
    ];
    // every face is flat, so it gets texture coordinates by projecting onto its own plane, at one scale for
    // the whole solid and from a random corner of the tile so no two faces repeat each other
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
    // turn to the logo's isometric view: X left-down, Y right-down, Z up, the (1,1,1) diagonal toward the viewer
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
  /**
   * The surface of obsidian: no grain, just broad smooth undulations, like the flow lines in volcanic glass.
   * A height field of soft bumps, wrapped so it tiles, turned into a normal map.
   */
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
  /**
   * The Vertigo mark as a solid, semi-gloss plaque propped against the back of the shelf, turned a little
   * toward the room. Its origin is the middle of its bottom back edge. It picks up like a comic.
   */
  function logo(x: number, y: number, z: number, height: number, parent: THREE.Object3D, turn = 0, lean = 0) {
    const g = new THREE.Group();
    g.position.set(x, y, z);
    g.rotation.order = "YXZ"; // lean back first, then turn
    g.rotation.set(-lean, turn, 0);
    parent.add(g);
    const { light, dark } = logoGeometry(height);
    // glass in the logo's own two blues: polished smooth like obsidian, with sharp reflections and broad flow
    // lines in the surface, and a little self-colour so the sides never go grey in the dark. The material
    // carries the environment itself, since the scene's night setting would otherwise mute the reflections.
    const finish = (tone: number) => keep(new THREE.MeshPhysicalMaterial({ color: tone, emissive: tone, emissiveIntensity: 0.12, normalMap: obsidianFlow, normalScale: new THREE.Vector2(0.4, 0.4), roughness: 0.12, metalness: 0, ior: 1.5, clearcoat: 1, clearcoatRoughness: 0.05, envMap: scene.environment, envMapIntensity: 0.35 }));
    for (const [geo, c] of [[light, 0x127eff], [dark, 0x1159cc]] as const) {
      const m = new THREE.Mesh(geo, finish(c));
      m.castShadow = true;
      m.receiveShadow = true;
      g.add(m);
    }
    pickables.push(g);
    states.set(g, { series: null, home: g.position.clone(), homeQ: g.quaternion.clone(), parent, lift: 0, reach: 1.5, offsetX: 0, offsetY: -0.3, tilt: 1.7, glow: 0.3 });
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
  }

  // ---- the shell --------------------------------------------------------------------------
  const WT = 0.3;
  const floorTex = woodTexture(27);
  put(keep(new THREE.PlaneGeometry(14, 14)), std(0xffffff, 0.7, { map: floorTex, bumpMap: floorTex, bumpScale: 0.03 }), 0, 0, 2, { shadow: false, rot: [-Math.PI / 2, 0, 0] });
  const paint = std(0x47546a, 0.96, { bumpMap: plasterGrain, bumpScale: 0.012 }), paintSide = std(0x3e4a5e, 0.96, { bumpMap: plasterGrain, bumpScale: 0.012 });
  put(box(6.2, H, WT, 0), paint, -3.1, H / 2, BZ - WT / 2, { shadow: false });
  put(box(3.0, H, WT, 0), paint, 4.7, H / 2, BZ - WT / 2, { shadow: false });
  put(box(3.2, 2.3, WT, 0), paint, 1.6, 1.15, BZ - WT / 2, { shadow: false });
  put(box(3.2, H - 4.9, WT, 0), paint, 1.6, 4.9 + (H - 4.9) / 2, BZ - WT / 2, { shadow: false });
  put(box(WT, H, 12, 0), paintSide, -6 - WT / 2, H / 2, 2, { shadow: false });
  put(box(WT, H, 12, 0), paintSide, 6 + WT / 2, H / 2, 2, { shadow: false });
  const dark = std(0x2b1f17, 0.65), cream = std(0xd9cdb8, 0.8, { bumpMap: plasterGrain, bumpScale: 0.006 });
  // skirting, dado rail, cornice and wainscot panels, all one mesh
  const trim: Piece[] = [
    { geo: box(12, 0.18, 0.06, 0.008), x: 0, y: 0.09, z: BZ + 0.03 }, { geo: box(12, 0.06, 0.05, 0.008), x: 0, y: 2.05, z: BZ + 0.025 }, { geo: box(12, 0.14, 0.08, 0.01), x: 0, y: H - 0.07, z: BZ + 0.04 },
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

  // the window: a reveal through the wall, frame, mullions, glass, sill, the world outside, drapes beside it
  const frame = std(0xd9d0be, 0.6, { bumpMap: plasterGrain, bumpScale: 0.004 });
  put(box(3.4, 0.1, WT + 0.06, 0.01), frame, 1.6, 2.3, BZ - WT / 2); put(box(3.4, 0.1, WT + 0.06, 0.01), frame, 1.6, 4.9, BZ - WT / 2);
  put(box(0.1, 2.7, WT + 0.06, 0.01), frame, 0.0, 3.6, BZ - WT / 2); put(box(0.1, 2.7, WT + 0.06, 0.01), frame, 3.2, 3.6, BZ - WT / 2);
  put(box(0.05, 2.6, 0.07, 0.01), frame, 1.6, 3.6, BZ - 0.08); put(box(3.2, 0.05, 0.07, 0.01), frame, 1.6, 3.85, BZ - 0.08);
  put(box(3.6, 0.1, 0.62, 0.02), frame, 1.6, 2.26, BZ + 0.16);
  const glass = keep(new THREE.MeshPhysicalMaterial({ color: 0xcfe0ff, transparent: true, opacity: 0.06, roughness: 0.08, metalness: 0, clearcoat: 1 }));
  put(keep(new THREE.PlaneGeometry(3.2, 2.6)), glass, 1.6, 3.6, BZ - 0.1, { shadow: false });
  const skyMat = keep(new THREE.MeshBasicMaterial({ map: skyTexture() }));
  put(keep(new THREE.PlaneGeometry(10, 7)), skyMat, 1.6, 3.9, BZ - 4, { shadow: false });
  put(keep(new THREE.PlaneGeometry(7, 2.6)), keep(new THREE.MeshBasicMaterial({ map: townTexture(), transparent: true })), 1.6, 3.3, BZ - 2.4, { shadow: false });
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
  const walnut = std(0xffffff, 0.62, { map: shelfWood, bumpMap: shelfWood, bumpScale: 0.015 }), walnutBack = std(0x2c2016, 0.92, { bumpMap: plasterGrain, bumpScale: 0.01 });
  const unit = shelfUnit(4.7, 5.25, 0.85, 5, walnut, walnutBack);
  unit.group.position.set(-3.35, 0, BZ + 0.43);
  scene.add(unit.group);
  blob(-3.35, BZ + 0.85, 5.2, 1.3, 0.5);
  // a cool strip under the crown: the shelf is backlit, like a display case
  put(box(4.5, 0.012, 0.03, 0.004), std(0x000000, 1, { emissive: 0xaac8ff, emissiveIntensity: 1.4 }), -3.35, 5.1, BZ + 0.82, { shadow: false });
  const shelfGlow = new THREE.RectAreaLight(0xaac8ff, 1.4, 4.5, 0.08);
  shelfGlow.position.set(-3.35, 5.09, BZ + 0.8);
  shelfGlow.lookAt(-3.35, 0, BZ + 0.8);
  scene.add(shelfGlow);
  const byLove = series.slice().sort((a, b) => b.rating * 12 + b.owned - (a.rating * 12 + a.owned));
  const shelves = unit.ys.slice().reverse();
  const onShelves = FACE_PER_SHELF * shelves.length;
  const faceOut = byLove.slice(0, onShelves + 3);
  total = Math.min(series.length, onShelves + 3) + 4 + 4;
  const bump = () => { loaded++; options.onProgress?.(loaded, total); };
  const faceGeo = comicGeometry(FACE.w, FACE.h, FACE.d);
  shelves.forEach((y, si) => {
    const left = -unit.inner / 2;
    for (let i = 0; i < FACE_PER_SHELF; i++) {
      const s = faceOut[si * FACE_PER_SHELF + i];
      if (!s) break;
      addComic(s, faceGeo, left + FACE.w / 2 + i * FACE_STEP, y + FACE.h / 2 - 0.012, unit.backZ + 0.16 + i * 0.018, unit.group, bump);
    }
    const endX = unit.inner / 2 - 0.26, endZ = unit.backZ + 0.36;
    if (si === 1) { const g = new THREE.Group(); g.position.set(endX, y, endZ); g.scale.setScalar(0.45); unit.group.add(g); plant(0, 0, 0.6, false, g); }
    if (si === 3) logo(endX, y, unit.backZ + 0.2, 0.52, unit.group, 0.35, 0.22);
  });
  fairyLights([new THREE.Vector3(-5.8, 5.5, BZ + 0.9), new THREE.Vector3(-4.2, 5.22, BZ + 0.95), new THREE.Vector3(-2.5, 5.45, BZ + 0.92), new THREE.Vector3(-0.9, 5.18, BZ + 0.95)]);
  const twinkle = new THREE.PointLight(0xffc98a, 2.0, 4, 2);
  twinkle.position.set(-3.3, 5.1, BZ + 1.1);
  scene.add(twinkle);

  // ---- the desk under the window: a screen, keyboard, headphones, a stack of comics, the lamp ---------
  put(box(4.0, 0.1, 0.85, 0.03), walnut, 1.6, 1.0, BZ + 0.55);
  put(box(1.2, 0.72, 0.78, 0.02), walnut, 2.9, 0.59, BZ + 0.55);
  for (let k = 0; k < 2; k++) { put(box(1.08, 0.3, 0.03, 0.01), std(0x3a2a1c, 0.6, { map: shelfWood }), 2.9, 0.42 + k * 0.34, BZ + 0.96, { shadow: false }); put(sphere(0.025, 12, 10), brassMat, 2.9, 0.42 + k * 0.34, BZ + 0.99, { shadow: false }); }
  const leg = cyl(0.03, 0.04, 0.96, 14);
  for (const [dx, dz] of [[-1.9, -0.35], [-1.9, 0.35]]) put(leg, dark, 1.6 + dx, 0.48, BZ + 0.55 + dz);
  blob(1.6, BZ + 0.6, 4.4, 1.3, 0.4);
  // the screen shows the collection the way the app does, and the real covers drop in as they load;
  // it is unlit, so nothing in the room reflects off it
  const SCREEN = { cols: 6, x0: 56, y0: 86, cw: 120, ch: 180, gx: 152, gy: 224 };
  const screenSlot = (i: number): [number, number] => [SCREEN.x0 + (i % SCREEN.cols) * SCREEN.gx, SCREEN.y0 + Math.floor(i / SCREEN.cols) * SCREEN.gy];
  const onScreen = byLove.slice(0, 12);
  const screenTex = canvasTexture((g) => {
    g.fillStyle = "#0d1017"; g.fillRect(0, 0, 1024, 576);
    g.fillStyle = "#151a24"; g.fillRect(0, 0, 1024, 54);
    g.fillStyle = "rgba(255,255,255,.55)"; g.beginPath(); g.roundRect(28, 19, 96, 16, 8); g.fill();
    g.fillStyle = "rgba(255,255,255,.18)"; for (let i = 0; i < 4; i++) { g.beginPath(); g.roundRect(160 + i * 76, 21, 56, 12, 6); g.fill(); }
    g.fillStyle = "rgba(255,255,255,.35)"; g.beginPath(); g.arc(984, 27, 11, 0, Math.PI * 2); g.fill();
    onScreen.forEach((s, i) => {
      const [x, y] = screenSlot(i), [r, gg, b] = s.rgb;
      g.fillStyle = `rgb(${r},${gg},${b})`; g.fillRect(x, y, SCREEN.cw, SCREEN.ch);
      g.fillStyle = "rgba(255,255,255,.4)"; g.beginPath(); g.roundRect(x, y + SCREEN.ch + 12, 84, 8, 4); g.fill();
    });
  }, 1024, 576);
  const screenCanvas = screenTex.image as HTMLCanvasElement;
  onScreen.forEach((s, i) => coverPainters.set(s.id, (img) => {
    const g = screenCanvas.getContext("2d");
    if (!g) return;
    const [x, y] = screenSlot(i);
    try { g.drawImage(img, x, y, SCREEN.cw, SCREEN.ch); } catch { return; }
    const edge = g.createLinearGradient(x, 0, x + 22, 0); edge.addColorStop(0, "rgba(0,0,0,.4)"); edge.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = edge; g.fillRect(x, y, 22, SCREEN.ch);
    screenTex.needsUpdate = true;
  }));
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
  // headphones on a stand, left of the screen
  const hp = new THREE.Group(); hp.position.set(0.25, 1.05, BZ + 0.5); scene.add(hp);
  put(cyl(0.09, 0.1, 0.02, 24), std(0x23262e, 0.5, { metalness: 0.3 }), 0, 0.01, 0, { parent: hp });
  put(cyl(0.012, 0.012, 0.36, 10), std(0x23262e, 0.5, { metalness: 0.3 }), 0, 0.2, 0, { parent: hp });
  put(keep(new THREE.TorusGeometry(0.13, 0.016, 10, 28, Math.PI)), std(0x2d3039, 0.6), 0, 0.37, 0, { parent: hp, rot: [0, 0, 0] });
  put(cyl(0.07, 0.07, 0.05, 24), std(0x2d3039, 0.6), -0.13, 0.36, 0, { parent: hp, rot: [0, 0, Math.PI / 2] }); put(cyl(0.07, 0.07, 0.05, 24), std(0x2d3039, 0.6), 0.13, 0.36, 0, { parent: hp, rot: [0, 0, Math.PI / 2] });
  const flatGeo = comicGeometry(FACE.w, FACE.h, FACE.d * 0.7);
  byLove.slice(0, 4).forEach((s, i) => {
    const m = new THREE.Mesh(flatGeo, [coverMaterial(s, bump), pages, spineMaterial(s)]);
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
  // the desk lamp sits forward of the sill and the drape, and short enough that the shade clears the sill
  lamp(3.3, 1.05, BZ + 0.7, 0.78, 0.27, 16, false, true);
  // a cool strip under the desk edge, glowing onto the floor
  put(box(3.8, 0.012, 0.012, 0.004), std(0x000000, 1, { emissive: 0x3fd8c8, emissiveIntensity: 1.6 }), 1.6, 0.945, BZ + 0.97, { shadow: false });
  const underglow = new THREE.PointLight(0x3fd8c8, 1.4, 2.4, 2); underglow.position.set(1.6, 0.6, BZ + 1.1); scene.add(underglow);
  const overflow = series.length - faceOut.length;
  if (overflow > 0) {
    const cardboard = std(0xe6dcc4, 0.9, { bumpMap: clothGrain, bumpScale: 0.004 });
    for (let i = 0; i < Math.min(2, Math.ceil(overflow / 100)); i++) { put(box(1.0, 0.42, 0.42, 0.02), cardboard, 0.9 + i * 0.03, 0.21 + i * 0.44, BZ + 0.52); put(box(0.98, 0.01, 0.4, 0.004), std(0xcfc3a8, 1), 0.9 + i * 0.03, 0.42 + i * 0.44, BZ + 0.52, { shadow: false }); }
  }

  // ---- the right side: cabinet with a console and figures, a wall of framed covers ---------
  put(box(2.3, 1.15, 0.6, 0.02), walnut, 4.6, 0.575, BZ + 0.35);
  put(box(2.36, 0.05, 0.66, 0.015), walnut, 4.6, 1.16, BZ + 0.35);
  for (const x of [4.05, 5.15]) { put(box(1.0, 0.8, 0.03, 0.008), std(0x3a2a1c, 0.6, { map: shelfWood }), x, 0.55, BZ + 0.66, { shadow: false }); put(box(0.05, 0.16, 0.02, 0.006), brassMat, x + (x < 4.6 ? 0.4 : -0.4), 0.55, BZ + 0.69, { shadow: false }); }
  blob(4.6, BZ + 0.5, 2.7, 1.1, 0.45);
  byLove.slice(onShelves, onShelves + 3).forEach((s, i) => addComic(s, faceGeo, 3.75 + i * 0.6, 1.185 + FACE.h / 2, BZ + 0.2 + i * 0.03, scene, bump));
  const consoleMat = std(0xd8d4c8, 0.55), consoleDark = std(0x2a2d35, 0.6);
  put(box(0.44, 0.09, 0.3, 0.015), consoleMat, 5.45, 1.23, BZ + 0.42);
  put(box(0.3, 0.012, 0.06, 0.004), consoleDark, 5.45, 1.28, BZ + 0.36, { shadow: false });
  put(sphere(0.012, 8, 6), std(0x3fff8a, 0.4, { emissive: 0x3fff8a, emissiveIntensity: 2 }), 5.62, 1.29, BZ + 0.52, { shadow: false });
  put(box(0.14, 0.08, 0.02, 0.006), std(0x8a8f99, 0.6), 5.45, 1.22, BZ + 0.59, { shadow: false });
  figure(5.0, 1.185, BZ + 0.5, 0xf2b632, 0xd23b3b, scene, 0.15);
  const frameGeo = box(0.76, 1.08, 0.05, 0.012), matGeo = box(0.66, 0.98, 0.02, 0.004), printGeo = keep(new THREE.PlaneGeometry(0.5, 0.75));
  byLove.slice(0, 4).forEach((s, i) => {
    const x = 4.2 + (i % 2) * 0.95, y = 4.55 - Math.floor(i / 2) * 1.2;
    put(frameGeo, dark, x, y, BZ + 0.03, { shadow: false });
    put(matGeo, cream, x, y, BZ + 0.055, { shadow: false });
    const p = new THREE.Mesh(printGeo, coverMaterial(s, bump, true));
    p.position.set(x, y, BZ + 0.07);
    scene.add(p);
  });
  // the clock in the strip beside the window
  const clockFace = canvasTexture((g) => { g.fillStyle = "#e8dfcd"; g.beginPath(); g.arc(64, 64, 64, 0, Math.PI * 2); g.fill(); g.fillStyle = "#2a2520"; for (let i = 0; i < 12; i++) { const a = (i / 12) * Math.PI * 2; g.fillRect(64 + Math.cos(a) * 52 - 1.5, 64 + Math.sin(a) * 52 - 1.5, 3, 3); } }, 128, 128);
  put(cyl(0.24, 0.24, 0.05, 48), std(0xffffff, 0.6, { map: clockFace }), -0.72, 4.55, BZ + 0.04, { rot: [Math.PI / 2, 0, 0], shadow: false });
  put(keep(new THREE.TorusGeometry(0.24, 0.016, 12, 48)), brassMat, -0.72, 4.55, BZ + 0.07, { shadow: false });
  put(box(0.02, 0.16, 0.012, 0.004), dark, -0.72, 4.62, BZ + 0.08, { shadow: false }); put(box(0.13, 0.02, 0.012, 0.004), dark, -0.665, 4.55, BZ + 0.08, { shadow: false });
  plant(5.5, BZ + 1.2, 1.1, true);
  lamp(5.45, 0, 0.9, 3.3, 0.46, 13, true, false);

  // ---- the armchair, the side table, the candle, a gamepad, a plant ------------------------------------
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
  // a mat under the chair instead of a rug: dark, quiet
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
  put(cyl(0.045, 0.045, 0.16, 24), std(0xf1e6cf, 0.6), 2.46, 0.76, 1.52);
  put(cyl(0.05, 0.05, 0.01, 24), brassMat, 2.46, 0.685, 1.52, { shadow: false });
  const flameSprite = new THREE.Sprite(keep(new THREE.SpriteMaterial({ map: radialSprite("rgba(255,170,70,1)"), color: 0xffb050, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false })));
  flameSprite.position.set(2.46, 0.88, 1.52); flameSprite.scale.set(0.09, 0.14, 1); scene.add(flameSprite); sprites.push(flameSprite);
  const candleLight = new THREE.PointLight(0xffa050, 1.4, 2.6, 2);
  candleLight.position.set(2.46, 0.9, 1.52);
  scene.add(candleLight);
  // a gamepad on the chair's arm
  const pad = new THREE.Group(); pad.position.set(0.68, 0.96, 0.25); pad.rotation.y = -0.3; chair.add(pad);
  put(box(0.24, 0.04, 0.13, 0.015), std(0x23262e, 0.5), 0, 0, 0, { parent: pad });
  put(cyl(0.02, 0.02, 0.02, 12), std(0x3a3e48, 0.5), -0.05, 0.03, 0.01, { parent: pad, shadow: false }); put(cyl(0.02, 0.02, 0.02, 12), std(0x3a3e48, 0.5), 0.03, 0.03, 0.03, { parent: pad, shadow: false });
  [[0.07, -0.02, 0x3fd8c8], [0.09, 0.0, 0xd23b3b], [0.05, 0.0, 0xf2b632], [0.07, 0.02, 0x2d7fd6]].forEach(([x, z, c]) => put(sphere(0.008, 8, 6), std(c as number, 0.4, { emissive: c as number, emissiveIntensity: 0.3 }), x as number, 0.024, z as number, { parent: pad, shadow: false }));
  plant(-5.2, 1.4, 0.7);

  // ---- light ------------------------------------------------------------------------------------
  const hemi = new THREE.HemisphereLight(0x5a6a90, 0x4a3a2c, 0.55);
  scene.add(hemi);
  scene.add(new THREE.AmbientLight(0xffe4c8, 0.12));
  const pendant = new THREE.Group(); pendant.position.set(-0.9, H, -1.0); scene.add(pendant);
  put(cyl(0.006, 0.006, 1.2, 8), dark, 0, -0.6, 0, { parent: pendant, shadow: false });
  put(cyl(0.05, 0.05, 0.03, 16), brassMat, 0, -0.015, 0, { parent: pendant, shadow: false });
  const dome = new THREE.Mesh(keep(new THREE.SphereGeometry(0.32, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)), std(0x3a2a1c, 0.5, { side: THREE.DoubleSide, metalness: 0.2 }));
  dome.position.set(0, -1.2, 0); dome.rotation.x = Math.PI; pendant.add(dome);
  put(sphere(0.05, 16, 12), std(0xfff3d6, 0.4, { emissive: 0xffd9a0, emissiveIntensity: 1.0 }), 0, -1.26, 0, { parent: pendant, shadow: false });
  const keyLight = new THREE.SpotLight(0xffd6b0, KEY_INTENSITY, 30, 0.95, 1, 1.3);
  keyLight.position.set(-0.5, 7.5, 5.5);
  keyLight.target.position.set(-1.0, 1.6, BZ);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(1536, 1536);
  keyLight.shadow.bias = -0.0004;
  keyLight.shadow.radius = 6;
  scene.add(keyLight, keyLight.target);
  const pendantLight = new THREE.PointLight(0xffd2a8, 7, 8, 2);
  pendantLight.position.set(-0.9, H - 1.3, -1.0);
  scene.add(pendantLight);
  const windowLight = new THREE.RectAreaLight(0x9fb0e6, 4.5, 3.2, 2.6);
  windowLight.position.set(1.6, 3.6, BZ - 0.05);
  windowLight.lookAt(1.6, 1.2, 6);
  scene.add(windowLight);

  // ---- post: ambient occlusion seats everything on everything ----------------------------------------
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const gtao = new GTAOPass(scene, camera, container.clientWidth || 1, container.clientHeight || 1);
  gtao.output = GTAOPass.OUTPUT.Default;
  gtao.blendIntensity = 0.8;
  gtao.updateGtaoMaterial({ radius: 0.24, distanceExponent: 1, thickness: 1, scale: 1, samples: 10, distanceFallOff: 1, screenSpaceRadius: false });
  // the pass hides points and lines before its normal/depth render; hide the sprites too, or every halo
  // becomes a square occluder and draws a dark box around its bulb
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
    for (const l of lamps) {
      l.bulb.intensity = l.power * 2.2 * T.lamp;
      l.glow.intensity = l.power * 0.5 * T.lamp;
      l.shade.emissiveIntensity = 0.3 * T.lamp;
    }
    renderer.toneMappingExposure = T.exposure;
    scene.environmentIntensity = T.env;
  }
  applyTime(NIGHT);

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
  const el = renderer.domElement;
  let press: { x: number; y: number } | null = null;
  const onDown = (e: PointerEvent) => { if (e.button === 0) press = { x: e.clientX, y: e.clientY }; };
  const onMove = (e: PointerEvent) => {
    const r = el.getBoundingClientRect();
    mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    lastMove = performance.now();
  };
  const onUp = (e: PointerEvent) => {
    if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) < 6) {
      if (focused) putBack();
      else if (hovered) pickUp(hovered);
    }
    press = null;
  };
  const onLeave = () => { mouse.set(-10, -10); el.style.cursor = ""; };
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
    options.onPick?.(states.get(m)?.series ?? null);
  }
  function putBack() {
    if (!focused) return;
    const st = states.get(focused);
    if (st && st.parent !== scene) st.parent.attach(focused);
    focused = null;
    options.onPick?.(null);
  }

  const tmpV = new THREE.Vector3(), tmpQ = new THREE.Quaternion(), tmpE = new THREE.Euler(), tiltQ = new THREE.Quaternion();
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
    if (t > 2 && detailLevel > 0) { slowFrames = frameMs > 34 ? slowFrames + 1 : Math.max(0, slowFrames - 2); if (slowFrames > 90) { degrade(); slowFrames = 0; } }

    const px = mouse.x > -5 ? mouse.x : 0, py = mouse.y > -5 ? mouse.y : 0;
    camLean += (lean - camLean) * 0.06;
    camera.position.x += (CAM.x + px * 0.35 - camera.position.x) * 0.05;
    camera.position.y += (CAM.y + py * 0.18 - camera.position.y) * 0.05;
    camera.position.z += (CAM.z - camLean * 2.6 - camera.position.z) * 0.05;
    camera.lookAt(CAM.tx + px * 0.12, CAM.ty + py * 0.08, CAM.tz);
    const glow = focused ? states.get(focused)?.glow ?? 1 : 0;
    handLight.intensity += (11 * glow - handLight.intensity) * 0.1;
    handFill.intensity += (4 * glow - handFill.intensity) * 0.1;
    candleLight.intensity = 1.4 + Math.sin(t * 13.1) * 0.12 + Math.sin(t * 7.3) * 0.1;
    flameSprite.scale.set(0.09 + Math.sin(t * 11) * 0.008, 0.14 + Math.sin(t * 9) * 0.015, 1);
    for (let i = 0; i < twinkles.length; i++) twinkles[i].emissiveIntensity = 1.0 + Math.sin(t * 1.7 + i * 1.3) * 0.25;

    if (!focused && now - lastMove < 120 && mouse.x > -5) {
      raycaster.setFromCamera(mouse, camera);
      const hit = raycaster.intersectObjects(pickables, true)[0];
      let next: THREE.Object3D | null = hit ? hit.object : null;
      while (next && !states.has(next)) next = next.parent;
      if (next !== hovered) {
        hovered = next;
        options.onHover?.(next ? states.get(next)?.series ?? null : null);
      }
      // the view colours the cursor for comics; the logo has no card, so do it here
      el.style.cursor = next && !states.get(next)?.series ? "pointer" : "";
    }
    for (const m of pickables) {
      const st = states.get(m);
      if (!st) continue;
      if (m === focused) {
        camera.getWorldDirection(tmpV);
        tmpV.multiplyScalar(st.reach).add(camera.position);
        tmpV.x += st.offsetX;
        tmpV.y += st.offsetY;
        m.position.lerp(tmpV, 0.1);
        // in the hand it tips with the pointer, so the gloss and the thickness show
        tmpE.set(-py * 0.28 * st.tilt, px * 0.38 * st.tilt, 0);
        tiltQ.setFromEuler(tmpE);
        tmpQ.copy(camera.quaternion).multiply(tiltQ);
        m.quaternion.slerp(tmpQ, 0.1);
      } else if (m.parent === st.parent) {
        st.lift += ((m === hovered ? 1 : 0) - st.lift) * 0.15;
        tmpV.copy(st.home);
        tmpV.z += st.lift * 0.16;
        tmpV.y += st.lift * 0.03;
        m.position.lerp(tmpV, 0.15);
        tmpE.setFromQuaternion(st.homeQ);
        tmpE.x -= st.lift * 0.05;
        tmpQ.setFromEuler(tmpE);
        m.quaternion.slerp(tmpQ, 0.15);
      }
    }
    composer.render();
  }
  renderer.setAnimationLoop(tick);

  return {
    putBack,
    dispose() {
      renderer.setAnimationLoop(null);
      observer.disconnect();
      el.removeEventListener("pointerdown", onDown);
      el.removeEventListener("pointermove", onMove);
      el.removeEventListener("pointerup", onUp);
      el.removeEventListener("pointercancel", onUp);
      el.removeEventListener("pointerleave", onLeave);
      el.removeEventListener("wheel", onWheel);
      for (const d of disposables) d.dispose();
      gtao.dispose();
      composer.dispose();
      scene.environment?.dispose();
      pmrem.dispose();
      renderer.dispose();
      el.remove();
    },
  };
}
