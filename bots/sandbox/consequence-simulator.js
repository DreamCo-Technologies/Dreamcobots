import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";

export function setup() {
  const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 10);
  return { camera, productionReady: false };
}
