import { Router, type IRouter } from "express";
import { db, quantumProvidersTable, type InsertQuantumProvider } from "@workspace/db";
import { asc } from "drizzle-orm";
import { logger } from "../lib/logger";

const router: IRouter = Router();

/**
 * Curated directory of real, publicly known quantum-computing providers DreamCo
 * can resell access to or route client workloads toward. Factual company
 * attributes only — no fabricated capacity, pricing, or performance metrics.
 */
const PROVIDERS: InsertQuantumProvider[] = [
  { name: "Enterprise Quantum", hardware: "superconducting", accessModel: "cloud", headquarters: "Armonk, USA", url: "https://example.com/enterprise-quantum-reference", category: "hardware", summary: "Superconducting QPUs accessed via Qiskit Runtime on Enterprise Cloud." },
  { name: "Google Quantum AI", hardware: "superconducting", accessModel: "research", headquarters: "Mountain View, USA", url: "https://quantumai.google", category: "hardware", summary: "Sycamore-class superconducting processors and the Cirq framework." },
  { name: "IonQ", hardware: "trapped-ion", accessModel: "cloud", headquarters: "College Park, USA", url: "https://ionq.com", category: "hardware", summary: "Trapped-ion systems available via AWS Braket, Azure Quantum and GCP." },
  { name: "Quantinuum", hardware: "trapped-ion", accessModel: "cloud", headquarters: "Broomfield, USA / Cambridge, UK", url: "https://www.quantinuum.com", category: "hardware", summary: "High-fidelity trapped-ion H-series plus the TKET software stack." },
  { name: "Rigetti Computing", hardware: "superconducting", accessModel: "cloud", headquarters: "Berkeley, USA", url: "https://www.rigetti.com", category: "hardware", summary: "Superconducting QPUs via the Quantum Cloud Services (QCS) platform." },
  { name: "D-Wave Systems", hardware: "annealing", accessModel: "cloud", headquarters: "Burnaby, Canada", url: "https://www.dwavesys.com", category: "hardware", summary: "Quantum annealers for optimization, accessed through the Leap cloud." },
  { name: "Microsoft Azure Quantum", hardware: "simulator", accessModel: "cloud", headquarters: "Redmond, USA", url: "https://azure.microsoft.com/products/quantum", category: "cloud-access", summary: "Cloud aggregator giving access to multiple QPU providers plus simulators." },
  { name: "AWS Braket", hardware: "simulator", accessModel: "cloud", headquarters: "Seattle, USA", url: "https://aws.amazon.com/braket", category: "cloud-access", summary: "Managed access to IonQ, Rigetti, QuEra and IQM hardware plus simulators." },
  { name: "Pasqal", hardware: "neutral-atom", accessModel: "cloud", headquarters: "Palaiseau, France", url: "https://www.pasqal.com", category: "hardware", summary: "Neutral-atom processors targeting analog and digital quantum computing." },
  { name: "QuEra Computing", hardware: "neutral-atom", accessModel: "cloud", headquarters: "Boston, USA", url: "https://www.quera.com", category: "hardware", summary: "Neutral-atom Aquila machine available on AWS Braket." },
  { name: "Xanadu", hardware: "photonic", accessModel: "cloud", headquarters: "Toronto, Canada", url: "https://www.xanadu.ai", category: "hardware", summary: "Photonic quantum hardware and the PennyLane framework." },
  { name: "Atom Computing", hardware: "neutral-atom", accessModel: "cloud", headquarters: "Berkeley, USA", url: "https://atom-computing.com", category: "hardware", summary: "Neutral-atom systems scaling to 1000+ qubits." },
  { name: "PsiQuantum", hardware: "photonic", accessModel: "research", headquarters: "Palo Alto, USA", url: "https://www.psiquantum.com", category: "hardware", summary: "Building a fault-tolerant photonic quantum computer in silicon." },
  { name: "Alpine Quantum Technologies", hardware: "trapped-ion", accessModel: "cloud", headquarters: "Innsbruck, Austria", url: "https://www.aqt.eu", category: "hardware", summary: "Compact rack-mounted trapped-ion quantum computers." },
  { name: "Origin Quantum", hardware: "superconducting", accessModel: "cloud", headquarters: "Hefei, China", url: "https://qcloud.originqc.com.cn", category: "hardware", summary: "Superconducting QPUs and a domestic quantum cloud platform." },
  { name: "Baidu Quantum", hardware: "superconducting", accessModel: "cloud", headquarters: "Beijing, China", url: "https://quantum.baidu.com", category: "hardware", summary: "Quantum platform with the Qian Shi device and Paddle Quantum toolkit." },
  { name: "Fujitsu", hardware: "superconducting", accessModel: "cloud", headquarters: "Tokyo, Japan", url: "https://www.fujitsu.com/global/about/research/technology/quantum", category: "hardware", summary: "Superconducting hardware (with RIKEN) plus large quantum simulators." },
  { name: "Toshiba", hardware: "software", accessModel: "cloud", headquarters: "Tokyo, Japan", url: "https://www.global.toshiba/ww/products-solutions/ai-iot/sbm.html", category: "software", summary: "Quantum-inspired Simulated Bifurcation Machine for optimization." },
  { name: "NEC", hardware: "annealing", accessModel: "cloud", headquarters: "Tokyo, Japan", url: "https://www.nec.com/en/global/quantum-computing", category: "hardware", summary: "Quantum annealing and vector-annealing services for optimization." },
  { name: "Intel", hardware: "spin", accessModel: "research", headquarters: "Santa Clara, USA", url: "https://www.intel.com/content/www/us/en/research/quantum-computing.html", category: "hardware", summary: "Silicon spin-qubit research and the Tunnel Falls test chip." },
  { name: "NVIDIA (CUDA-Q)", hardware: "simulator", accessModel: "sdk", headquarters: "Santa Clara, USA", url: "https://developer.nvidia.com/cuda-q", category: "software", summary: "GPU-accelerated quantum simulation and hybrid QPU/GPU programming." },
  { name: "Quantum Brilliance", hardware: "spin", accessModel: "on-prem", headquarters: "Canberra, Australia", url: "https://quantumbrilliance.com", category: "hardware", summary: "Diamond nitrogen-vacancy qubits aimed at room-temperature deployment." },
  { name: "Terra Quantum", hardware: "software", accessModel: "cloud", headquarters: "St. Gallen, Switzerland", url: "https://terraquantum.swiss", category: "software", summary: "Quantum algorithms, hybrid optimization and a quantum-as-a-service cloud." },
  { name: "Classiq", hardware: "software", accessModel: "sdk", headquarters: "Tel Aviv, Israel", url: "https://www.classiq.io", category: "software", summary: "High-level quantum circuit synthesis and design automation platform." },
  { name: "QC Ware", hardware: "software", accessModel: "cloud", headquarters: "Palo Alto, USA", url: "https://www.qcware.com", category: "software", summary: "Quantum and quantum-inspired algorithms via the Forge platform." },
  { name: "Quandela", hardware: "photonic", accessModel: "cloud", headquarters: "Paris, France", url: "https://www.quandela.com", category: "hardware", summary: "Photonic quantum computers and single-photon source technology." },
  { name: "Oxford Quantum Circuits", hardware: "superconducting", accessModel: "cloud", headquarters: "Reading, UK", url: "https://oqc.tech", category: "hardware", summary: "Superconducting Coaxmon QPUs delivered as quantum computing as a service." },
  { name: "IQM Quantum Computers", hardware: "superconducting", accessModel: "on-prem", headquarters: "Espoo, Finland", url: "https://www.meetiqm.com", category: "hardware", summary: "On-premises and cloud superconducting quantum computers." },
  { name: "SpinQ", hardware: "spin", accessModel: "on-prem", headquarters: "Shenzhen, China", url: "https://www.spinquanta.com", category: "hardware", summary: "NMR-based desktop quantum computers for education and research." },
  { name: "Quantum Computing Inc (QCi)", hardware: "photonic", accessModel: "cloud", headquarters: "Hoboken, USA", url: "https://quantumcomputinginc.com", category: "hardware", summary: "Photonic and entropy-based systems for optimization workloads." },
];

/** Idempotent reference-data seed run once at startup. */
export async function seedQuantumProviders(): Promise<void> {
  try {
    for (const p of PROVIDERS) {
      await db
        .insert(quantumProvidersTable)
        .values(p)
        .onConflictDoUpdate({
          target: quantumProvidersTable.name,
          set: {
            hardware: p.hardware ?? null,
            accessModel: p.accessModel ?? null,
            headquarters: p.headquarters ?? null,
            url: p.url ?? null,
            summary: p.summary ?? null,
            category: p.category ?? "hardware",
          },
        });
    }
    logger.info({ count: PROVIDERS.length }, "quantum providers directory seeded");
  } catch (err) {
    logger.warn({ err }, "could not seed quantum providers directory");
  }
}

// GET the curated quantum-providers directory (LIVE — from the DB).
router.get("/quantum", async (_req, res): Promise<void> => {
  const rows = await db.select().from(quantumProvidersTable).orderBy(asc(quantumProvidersTable.name));
  const byCategory: Record<string, number> = {};
  const byHardware: Record<string, number> = {};
  for (const r of rows) {
    byCategory[r.category] = (byCategory[r.category] ?? 0) + 1;
    if (r.hardware) byHardware[r.hardware] = (byHardware[r.hardware] ?? 0) + 1;
  }
  res.json({ total: rows.length, byCategory, byHardware, providers: rows });
});

export default router;
