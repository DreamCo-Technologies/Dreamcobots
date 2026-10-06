import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";

export function setup() {
  const mixer = new THREE.AnimationMixer(new THREE.Object3D());
  return { mixer, productionReady: false };
}
