// Concept kinematics in illustrative scene units; not a hardware controller.
export function solveArmTarget(x, y, z, upper = 2, lower = 2, baseHeight = .65) {
  if (![x,y,z,upper,lower,baseHeight].every(Number.isFinite) || upper <= 0 || lower <= 0) return null;
  const r = Math.hypot(x,z), dy = y-baseHeight, d = Math.hypot(r,dy);
  if (d > upper+lower || d < Math.abs(upper-lower) || d < .001) return null;
  const elbow = Math.acos(Math.max(-1,Math.min(1,(d*d-upper*upper-lower*lower)/(2*upper*lower))));
  return { yaw:Math.atan2(-z,x), shoulder:Math.atan2(r,dy)-Math.atan2(lower*Math.sin(elbow),upper+lower*Math.cos(elbow)), elbow };
}
