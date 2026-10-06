import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";

export function setup() {
  const listener = new THREE.AudioListener();
  return { listener, productionReady: false };
}
