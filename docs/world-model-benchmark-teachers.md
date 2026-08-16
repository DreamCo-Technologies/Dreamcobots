# World-Model Benchmark Teachers

DreamDojo is now a first-class benchmark teacher for Buddy's reality-simulation program.

DreamDojo is especially valuable because its 2026 work trains a generalist robot world model from 44,000 hours of egocentric human video, uses continuous latent actions, and evaluates open-world/contact-rich behavior. Its released setup documentation currently describes H100 80GB testing, so Buddy should treat it as a research benchmark and not assume it can run locally on every machine.

Additional teachers tracked in the registry include DreamX-World, MIRA, MMBench2, AlayaWorld, WorldFoundry, and Interactive World Simulator. Their techniques cover interactive worlds, camera/action control, multiplayer dynamics, hallucination prevention, evaluation infrastructure, and simulation.

Buddy's rule: learn the *technique*, reproduce it with an original implementation when practical, benchmark the result, and retain the benchmark as a regression test. Do not copy proprietary code, assets, characters, maps, datasets, or model weights unless the applicable license explicitly permits their use.
