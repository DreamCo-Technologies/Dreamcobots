// Authored visual detailing in arbitrary scene units. No fabrication dimensions.
import * as T from './vendor/three/three.module.js';
export function detailInvention(parts,model){
 const metal=new T.MeshStandardMaterial({color:0x718997,metalness:.8,roughness:.29}),ceramic=new T.MeshStandardMaterial({color:0xd3ddd9,metalness:.28,roughness:.48}),dark=new T.MeshStandardMaterial({color:0x172431,metalness:.6,roughness:.4}),copper=new T.MeshStandardMaterial({color:0xbc8553,metalness:.75,roughness:.3}),light=new T.MeshStandardMaterial({color:0x8cffe1,emissive:0x36caa8,emissiveIntensity:1.1}),amber=new T.MeshStandardMaterial({color:0xffc571,emissive:0xdb8229,emissiveIntensity:.45});
 const add=(g,geo,mat,pos,rot=[0,0,0])=>{const m=new T.Mesh(geo,mat.clone());m.position.set(...pos);m.rotation.set(...rot);m.castShadow=true;m.receiveShadow=true;g.add(m);return m};
 const box=(g,s,p,m=metal)=>add(g,new T.BoxGeometry(...s),m,p);
 const ring=(g,r,t,p,m=metal,rot=[0,0,0])=>add(g,new T.TorusGeometry(r,t,8,40),m,p,rot);
 const tube=(g,points,r=.025,m=copper)=>add(g,new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),24,r,6,false),m,[0,0,0]);
 const bolt=(g,p,rot=[0,0,0])=>add(g,new T.CylinderGeometry(.04,.04,.035,6),metal,p,rot);
 const label=(g,text,pos,width=.65,rot=[0,0,0])=>{const c=document.createElement('canvas');c.width=256;c.height=64;const x=c.getContext('2d');x.fillStyle='#132535';x.fillRect(0,0,256,64);x.fillStyle='#b8e3db';x.font='bold 27px monospace';x.fillText(text,12,42);const map=new T.CanvasTexture(c);map.colorSpace=T.SRGBColorSpace;const m=new T.MeshBasicMaterial({map,side:T.DoubleSide});add(g,new T.PlaneGeometry(width,width/4),m,pos,rot);m.dispose()};
 const get=id=>parts.find(p=>p.id===id)?.group;
 if(model==='spacecraft'){
  const shell=get('upper-shell');for(let z=-1.3;z<2.5;z+=.62)for(const side of [-1,1]){box(shell,[.57,.045,.47],[side*.43,1.42,z],ceramic);for(const dx of [-.22,.22])bolt(shell,[side*.43+dx,1.46,z+.15]);box(shell,[.32,.024,.04],[side*.43,1.46,z-.13],dark)}
  for(const side of [-1,1]){const engine=get(side<0?'engine-port':'engine-starboard'),x=side*1.4;for(let i=0;i<3;i++)ring(engine,.28-i*.07,.028,[x,0,3.51+i*.018],i===1?light:copper);for(let a=0;a<8;a++){const theta=a*Math.PI/4,dx=Math.cos(theta)*.45,dy=Math.sin(theta)*.45;tube(engine,[[x+dx,dy,1.1],[x+dx*1.16,dy*1.16,1.4],[x+dx*1.16,dy*1.16,2.5],[x+dx,dy,2.95]],.018,a%2?copper:metal)}for(let i=0;i<9;i++)box(engine,[.17,.08,.045],[x,.49,1.25+i*.18],dark);
   const wing=get(side<0?'port-wing':'starboard-wing');for(let i=0;i<5;i++){box(wing,[.75,.035,.08],[side*(1.25+i*.33),.16,1.1+i*.29],dark);box(wing,[.28,.05,.055],[side*(1.5+i*.32),.17,1.3+i*.27],copper)}label(wing,side<0?'ASTER / 01':'DREAMCO',[side*2.25,.2,2.2],.85,[-Math.PI/2,0,0]);
  }
  const cabin=get('cabin');for(const x of [-.69,.69]){tube(cabin,[[x,.3,-1.65],[x,.65,-1.3],[x,.65,1.7],[x,.3,2.1]],.028);for(let z=-.8;z<2;z+=.75){box(cabin,[.1,.025,.45],[x,.74,z],light);for(let y=.32;y<.65;y+=.11)box(cabin,[.03,.018,.35],[x*.76,y,z],metal)}}for(let z=-1.5;z<2;z+=.28)box(cabin,[.45,.014,.025],[0,.19,z],dark);label(cabin,'FLIGHT / 01',[0,.7,-2.8],.5);label(shell,'ASTER • 01',[0,1.49,.2],.72,[-Math.PI/2,0,0]);
  const spine=get('dorsal-array');for(let side of [-1,1]){const panel=box(spine,[.7,.035,.9],[side*.52,1.02,1.6],dark);for(let i=0;i<5;i++)box(spine,[.56,.016,.018],[side*.52,1.05,1.25+i*.17],copper)}
 }
 if(model==='robot'){
  for(const id of ['upper-arm','forearm']){const g=get(id),upper=id==='upper-arm',length=upper?1.6:1.1;for(const side of [-1,1]){box(g,[.055,length,.19],[side*(upper?.27:.22),.9,.03],dark);for(const y of [.35,1.25])bolt(g,[side*(upper?.3:.25),y,.08],[0,0,Math.PI/2]);tube(g,[[side*.32,.05,.18],[side*.43,.5,.26],[side*.39,1.2,.26],[side*.23,upper?1.88:1.48,.15]],.035,side<0?copper:dark)}for(let i=0;i<6;i++)box(g,[.19,.025,.025],[0,.6+i*.1,.245],metal);label(g,upper?'ATLAS / A1':'ATLAS / A2',[0,.85,.26],.32)}
  const base=get('base');ring(base,.61,.026,[0,.61,0],light,[Math.PI/2,0,0]);for(let i=0;i<16;i++){const a=i*Math.PI/8;box(base,[.055,.11,.07],[Math.cos(a)*.87,.19,Math.sin(a)*.87],metal)}const grip=get('gripper');for(let x of [-.25,.25])for(let y=1.84;y<2.12;y+=.07)box(grip,[.12,.015,.22],[x,y,0],dark);
 }
 if(model==='drone'){
  const core=get('core');for(let x of [-.53,.53])for(let z of [-.62,.62])bolt(core,[x,.61,z]);for(let i=0;i<9;i++)box(core,[.68,.035,.03],[0,.61,-.4+i*.1],metal);label(core,'AERO / 03',[0,.64,0],.68,[-Math.PI/2,0,0]);for(let i=0;i<4;i++){const g=get('arm-'+i),x=i%2?1:-1,z=i<2?1:-1;ring(g,.29,.026,[x*2,.24,z*2],copper,[Math.PI/2,0,0]);tube(g,[[x*.62,.2,z*.62],[x,.2,z],[x*1.7,.2,z*1.7]],.025,copper);for(let n=0;n<8;n++){const a=n*Math.PI/4;box(g,[.035,.14,.035],[x*2+Math.cos(a)*.23,.22,z*2+Math.sin(a)*.23],dark)}box(g,[.18,.06,.12],[x*2,.08,z*2.26],i<2?light:amber)}const sensor=get('sensor');ring(sensor,.15,.018,[0,-.67,-.94],metal);ring(sensor,.11,.016,[0,-.67,-.953],dark);
 }
 if(model==='rocket'){
  const body=get('rocket-body');for(let i=0;i<12;i++){const a=i*Math.PI/6;for(let y of [-.9,.7,2.3]){const m=box(body,[.12,.35,.035],[Math.sin(a)*.704,y,Math.cos(a)*.704],i%3?ceramic:dark);m.rotation.y=a}for(let y of [-1.05,.55,2.15])bolt(body,[Math.sin(a)*.72,y,Math.cos(a)*.72],[Math.PI/2,0,-a])}label(body,'DREAMCO',[0,.9,.733],.72);label(body,'ORBIT / 04',[0,.55,.735],.7);tube(body,[[.25,-1.6,.67],[.3,-1.3,.69],[.3,1.5,.69],[.2,1.8,.69]],.028,copper);for(let i=0;i<4;i++){const g=get('rocket-fin-'+i),a=i*Math.PI/2;for(let y of [-1.8,-1.45,-1.1])bolt(g,[Math.cos(a)*.89,y,Math.sin(a)*.89])}ring(get('rocket-base'),.74,.035,[0,-2.2,0],metal,[Math.PI/2,0,0]);
 }
 if(model==='research'){
  const base=get('research-base');for(let x of [-1.7,1.7])for(let z of [-1.2,1.2]){add(base,new T.CylinderGeometry(.15,.19,.16,20),metal,[x,-1.92,z]);bolt(base,[x,-1.51,z])}const optics=get('research-optics');for(let y=.6;y<1.5;y+=.12)ring(optics,.39,.023,[.55,y,.5],metal,[Math.PI/2,0,0]);tube(get('research-frame'),[[-1.4,-1.4,.86],[-1.6,.8,.86],[-1.1,1.6,.86],[.2,1.6,.86]],.045,dark);const stage=get('research-stage');for(let x of [-.65,1.05]){box(stage,[.05,.09,1.5],[x,-.49,.35],metal);for(let z of [-.25,.95])bolt(stage,[x,-.43,z])}for(let i=0;i<14;i++)box(stage,[.025,.017,.1],[-.4+i*.09,-.535,-.35],dark);label(get('research-control'),'SAMPLE / EMPTY',[1.45,-.82,-.815],.95,[-.3,0,0]);for(let i=0;i<5;i++)box(get('research-control'),[.1,.08,.025],[1.03+i*.2,-1.12,-.77],i===0?light:dark);
 }
 // Original template materials aren't attached to scene meshes; release them now.
 for(const material of [metal,ceramic,dark,copper,light,amber])material.dispose();
}
