import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";

export function setup() {
  const light = new THREE.DirectionalLight(0xffffff, 1);
  return { light, productionReady: false };
}
