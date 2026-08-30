import type { BenchmarkLevel } from './types.js';

export const COMPLEX_GAME_LEVELS: BenchmarkLevel[] = [
 { level: 1, name: 'small-playable', requiredCapabilities: ['playable loop'], metrics: ['build success','bugs','test coverage'] },
 { level: 2, name: '3d-environment', requiredCapabilities: ['3D scene'], metrics: ['runtime fps','memory','build success'] },
 { level: 3, name: 'npc-simulation', requiredCapabilities: ['NPC state','agent behavior'], metrics: ['simulation stability','recovery'] },
 { level: 4, name: 'educational-game', requiredCapabilities: ['objectives','assessments'], metrics: ['objective coverage','assessment validity'] },
 { level: 5, name: 'construction-system', requiredCapabilities: ['building','interior editing'], metrics: ['edit latency','persistence'] },
 { level: 6, name: 'persistent-economy', requiredCapabilities: ['economy','inventory','jobs'], metrics: ['state consistency','exploit rate'] },
 { level: 7, name: 'multiplayer-prototype', requiredCapabilities: ['networked sessions'], metrics: ['latency','disconnect recovery'] },
 { level: 8, name: 'persistent-world', requiredCapabilities: ['save/load','world state'], metrics: ['data integrity','recovery'] },
 { level: 9, name: 'streaming-open-world', requiredCapabilities: ['chunk streaming','procedural generation'], metrics: ['load time','memory','frame stability'] },
 { level: 10, name: 'full-educational-simulation', requiredCapabilities: ['curriculum','simulation','multiplayer','assessment'], metrics: ['end-to-end success','security','performance','learning outcomes'] },
];
