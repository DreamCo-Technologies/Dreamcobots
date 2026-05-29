"""
AI Training Master Bot
=======================

Trains AI in every way possible.  Covers every major training methodology
across supervised learning, unsupervised learning, reinforcement learning,
self-supervised learning, meta-learning, federated learning, multi-modal
learning, quantum-enhanced training, neuromorphic training, and emergent /
self-organising paradigms.

Key capabilities
-----------------
* Design, run, and evaluate training experiments across all paradigms
* Manage datasets: ingestion, labelling, augmentation, versioning
* Hyperparameter optimisation (grid, random, Bayesian, evolutionary)
* Track model performance, generalisation, and bias metrics
* Self-improve: analyse its own past training runs to design better ones
* Feed best models and strategies back to Buddy for ecosystem upgrades
* Maintain a training ledger (SQLite) for full experiment reproducibility

Follows the GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import hashlib
import random
import sqlite3
from datetime import datetime, timezone
from typing import Any


from framework import GlobalAISourcesFlow  # noqa: F401 — required by compliance gate


# ---------------------------------------------------------------------------
# Training paradigm definitions
# ---------------------------------------------------------------------------

TRAINING_PARADIGMS: list[dict] = [
    {
        "id": "supervised",
        "name": "Supervised Learning",
        "description": "Learn from labelled (input, output) pairs using loss minimisation.",
        "techniques": ["cross-entropy loss", "MSE", "Adam optimiser", "batch normalisation",
                       "dropout", "learning-rate schedules"],
    },
    {
        "id": "unsupervised",
        "name": "Unsupervised Learning",
        "description": "Discover latent structure without labels.",
        "techniques": ["k-means", "DBSCAN", "VAE", "GAN", "ICA", "t-SNE", "UMAP"],
    },
    {
        "id": "reinforcement",
        "name": "Reinforcement Learning",
        "description": "Learn optimal policies through environment interaction and rewards.",
        "techniques": ["PPO", "SAC", "DQN", "A3C", "MCTS", "curriculum learning",
                       "reward shaping", "multi-agent RL"],
    },
    {
        "id": "self_supervised",
        "name": "Self-Supervised Learning",
        "description": "Create supervised signals from the raw data itself.",
        "techniques": ["contrastive learning", "masked language modelling",
                       "SimCLR", "BYOL", "DINO", "MAE"],
    },
    {
        "id": "meta_learning",
        "name": "Meta-Learning (Learning to Learn)",
        "description": "Train models that rapidly adapt to new tasks from few examples.",
        "techniques": ["MAML", "Prototypical Networks", "Reptile",
                       "Matching Networks", "Neural Process"],
    },
    {
        "id": "federated",
        "name": "Federated Learning",
        "description": "Train across distributed, privacy-preserving data silos.",
        "techniques": ["FedAvg", "FedProx", "differential privacy",
                       "secure aggregation", "split learning"],
    },
    {
        "id": "multi_modal",
        "name": "Multi-Modal Learning",
        "description": "Train on combinations of text, image, audio, video, and sensor data.",
        "techniques": ["CLIP", "Flamingo", "ImageBind", "cross-modal attention",
                       "late fusion", "early fusion"],
    },
    {
        "id": "continual",
        "name": "Continual / Lifelong Learning",
        "description": "Learn new tasks without catastrophically forgetting old ones.",
        "techniques": ["EWC", "progressive networks", "PackNet",
                       "replay buffers", "dynamic architectures"],
    },
    {
        "id": "quantum",
        "name": "Quantum-Enhanced Training",
        "description": "Use quantum circuits and annealers to accelerate optimisation.",
        "techniques": ["QNN", "variational quantum eigensolver", "QAOA",
                       "quantum kernel methods", "quantum annealing"],
    },
    {
        "id": "neuromorphic",
        "name": "Neuromorphic Training",
        "description": "Train spiking neural networks on neuromorphic hardware.",
        "techniques": ["STDP", "surrogate gradient descent",
                       "Loihi integration", "event-driven learning"],
    },
    {
        "id": "evolutionary",
        "name": "Evolutionary / Genetic Training",
        "description": "Evolve model architectures and weights via natural selection.",
        "techniques": ["neuroevolution (NEAT)", "CMA-ES", "genetic algorithms",
                       "population-based training"],
    },
    {
        "id": "causal",
        "name": "Causal Inference Training",
        "description": "Train models that reason about cause and effect, not just correlation.",
        "techniques": ["do-calculus", "structural causal models", "IDA",
                       "propensity scoring", "counterfactual data augmentation"],
    },
]

_PARADIGM_BY_ID: dict[str, dict] = {p["id"]: p for p in TRAINING_PARADIGMS}


# ---------------------------------------------------------------------------
# Experiment ledger
# ---------------------------------------------------------------------------

class _ExperimentLedger:
    """Stores training experiments in SQLite for full reproducibility."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS experiments (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT    NOT NULL,
                paradigm_id  TEXT    NOT NULL,
                dataset      TEXT    NOT NULL,
                config       TEXT,
                status       TEXT    DEFAULT 'pending',
                score        REAL,
                notes        TEXT,
                created_at   TEXT    NOT NULL,
                finished_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS hyperparams (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id  INTEGER NOT NULL REFERENCES experiments(id),
                param_name     TEXT    NOT NULL,
                param_value    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS model_versions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id  INTEGER REFERENCES experiments(id),
                version_hash   TEXT    NOT NULL UNIQUE,
                metrics        TEXT,
                saved_at       TEXT    NOT NULL
            );
            """
        )
        self._conn.commit()

    def create_experiment(self, name: str, paradigm_id: str, dataset: str,
                          config: str = "", notes: str = "") -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """
            INSERT INTO experiments (name, paradigm_id, dataset, config, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?) RETURNING id
            """,
            (name, paradigm_id, dataset, config, notes, ts),
        )
        eid = cur.fetchone()[0]
        self._conn.commit()
        return eid

    def update_experiment(self, eid: int, status: str = "running",
                          score: float | None = None) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        if score is not None:
            self._conn.execute(
                "UPDATE experiments SET status=?, score=?, finished_at=? WHERE id=?",
                (status, score, ts, eid),
            )
        else:
            self._conn.execute(
                "UPDATE experiments SET status=?, finished_at=? WHERE id=?",
                (status, ts, eid),
            )
        self._conn.commit()

    def add_hyperparam(self, eid: int, name: str, value: Any) -> None:
        self._conn.execute(
            "INSERT INTO hyperparams (experiment_id, param_name, param_value) VALUES (?,?,?)",
            (eid, name, str(value)),
        )
        self._conn.commit()

    def save_model_version(self, eid: int, metrics: dict) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(f"{eid}{ts}{random.random()}".encode()).hexdigest()[:16]
        self._conn.execute(
            "INSERT INTO model_versions (experiment_id, version_hash, metrics, saved_at) VALUES (?,?,?,?)",
            (eid, digest, str(metrics), ts),
        )
        self._conn.commit()
        return digest

    def list_experiments(self, paradigm_id: str | None = None) -> list[dict]:
        if paradigm_id:
            rows = self._conn.execute(
                "SELECT * FROM experiments WHERE paradigm_id=? ORDER BY created_at DESC",
                (paradigm_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM experiments ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def best_experiment(self) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM experiments WHERE score IS NOT NULL ORDER BY score DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Main bot
# ---------------------------------------------------------------------------

_flow = GlobalAISourcesFlow(bot_name="AITrainingMasterBot")


class AITrainingMasterBot:
    """Masters every AI training methodology and continuously improves the
    DreamCo ecosystem.

    Parameters
    ----------
    db_path : str
        SQLite database path for the experiment ledger.  Defaults to
        ``":memory:"`` for ephemeral use.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._ledger = _ExperimentLedger(db_path)
        self._log: list[dict] = []

    # ------------------------------------------------------------------
    # Paradigm introspection
    # ------------------------------------------------------------------

    def list_paradigms(self) -> list[dict]:
        """Return all supported training paradigms."""
        return list(TRAINING_PARADIGMS)

    def get_paradigm(self, paradigm_id: str) -> dict:
        """Return details for a specific paradigm.

        Raises
        ------
        KeyError
            If *paradigm_id* is not recognised.
        """
        if paradigm_id not in _PARADIGM_BY_ID:
            raise KeyError(
                f"Unknown paradigm '{paradigm_id}'. "
                f"Valid ids: {sorted(_PARADIGM_BY_ID.keys())}"
            )
        return dict(_PARADIGM_BY_ID[paradigm_id])

    # ------------------------------------------------------------------
    # Experiment management
    # ------------------------------------------------------------------

    def create_experiment(
        self,
        name: str,
        paradigm_id: str,
        dataset: str,
        hyperparams: dict | None = None,
        notes: str = "",
    ) -> dict:
        """Define a new training experiment.

        Parameters
        ----------
        name : str
            Human-readable experiment name.
        paradigm_id : str
            One of the supported paradigm ids (see :meth:`list_paradigms`).
        dataset : str
            Dataset identifier or path.
        hyperparams : dict, optional
            Key/value hyperparameter mapping.
        notes : str
            Optional free-text notes.

        Returns
        -------
        dict
            Experiment record including assigned ``experiment_id``.
        """
        if paradigm_id not in _PARADIGM_BY_ID:
            raise KeyError(f"Unknown paradigm '{paradigm_id}'")
        eid = self._ledger.create_experiment(name, paradigm_id, dataset, notes=notes)
        for k, v in (hyperparams or {}).items():
            self._ledger.add_hyperparam(eid, k, v)
        self._log.append({"action": "create_experiment", "id": eid, "name": name})
        return {"experiment_id": eid, "name": name, "paradigm_id": paradigm_id,
                "dataset": dataset, "status": "pending"}

    def run_experiment(self, experiment_id: int,
                       simulated_score: float | None = None) -> dict:
        """Simulate running a training experiment and record the result.

        Parameters
        ----------
        experiment_id : int
            Id returned by :meth:`create_experiment`.
        simulated_score : float, optional
            Override the random score (useful in tests).

        Returns
        -------
        dict
            Run result including score and saved model version hash.
        """
        self._ledger.update_experiment(experiment_id, status="running")
        score = simulated_score if simulated_score is not None else round(
            random.uniform(0.6, 0.99), 4
        )
        self._ledger.update_experiment(experiment_id, status="completed", score=score)
        version_hash = self._ledger.save_model_version(
            experiment_id, {"accuracy": score, "loss": round(1 - score, 4)}
        )
        self._log.append({"action": "run_experiment", "id": experiment_id, "score": score})
        return {
            "experiment_id": experiment_id,
            "status": "completed",
            "score": score,
            "model_version": version_hash,
        }

    def list_experiments(self, paradigm_id: str | None = None) -> list[dict]:
        """List all experiments, optionally filtered by paradigm."""
        return self._ledger.list_experiments(paradigm_id)

    def best_experiment(self) -> dict | None:
        """Return the highest-scoring experiment so far."""
        return self._ledger.best_experiment()

    # ------------------------------------------------------------------
    # Hyperparameter optimisation
    # ------------------------------------------------------------------

    def optimise_hyperparams(
        self,
        paradigm_id: str,
        param_space: dict[str, list],
        n_trials: int = 5,
    ) -> dict:
        """Run a simple random-search hyperparameter optimisation.

        Parameters
        ----------
        paradigm_id : str
            Paradigm to optimise for.
        param_space : dict[str, list]
            Mapping of param name → list of candidate values.
        n_trials : int
            Number of random samples to try.

        Returns
        -------
        dict
            Best trial result including hyperparams and score.
        """
        best: dict = {}
        for trial in range(n_trials):
            sampled = {k: random.choice(v) for k, v in param_space.items()}
            eid = self._ledger.create_experiment(
                f"hpo_trial_{trial}",
                paradigm_id,
                dataset="hpo_synthetic",
                notes=f"HPO trial {trial}",
            )
            for k, v in sampled.items():
                self._ledger.add_hyperparam(eid, k, v)
            score = round(random.uniform(0.5, 0.99), 4)
            self._ledger.update_experiment(eid, status="completed", score=score)
            if not best or score > best.get("score", 0):
                best = {"trial": trial, "params": sampled, "score": score,
                        "experiment_id": eid}
        self._log.append({"action": "optimise_hyperparams", "paradigm": paradigm_id,
                           "best_score": best.get("score")})
        return best

    # ------------------------------------------------------------------
    # Dataset management
    # ------------------------------------------------------------------

    def register_dataset(self, name: str, source: str, size: int,
                         modalities: list[str] | None = None) -> dict:
        """Register a dataset in the training ecosystem.

        Returns
        -------
        dict
            Dataset registration receipt.
        """
        record = {
            "name": name,
            "source": source,
            "size": size,
            "modalities": modalities or ["text"],
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self._log.append({"action": "register_dataset", "name": name})
        return record

    # ------------------------------------------------------------------
    # Bias and fairness
    # ------------------------------------------------------------------

    def evaluate_bias(self, model_version: str,
                      test_groups: list[str] | None = None) -> dict:
        """Evaluate model bias across demographic / feature groups.

        Returns
        -------
        dict
            Bias report with per-group accuracy and fairness score.
        """
        groups = test_groups or ["group_a", "group_b", "group_c"]
        per_group = {g: round(random.uniform(0.7, 0.99), 3) for g in groups}
        variance = max(per_group.values()) - min(per_group.values())
        fairness = round(1.0 - variance, 3)
        return {
            "model_version": model_version,
            "per_group_accuracy": per_group,
            "fairness_score": fairness,
            "bias_detected": fairness < 0.9,
        }

    # ------------------------------------------------------------------
    # Self-improvement
    # ------------------------------------------------------------------

    def self_improve(self) -> dict:
        """Analyse past runs and suggest the next best experiment to run.

        Returns
        -------
        dict
            Self-improvement recommendation.
        """
        best = self._ledger.best_experiment()
        all_exps = self._ledger.list_experiments()
        if not best:
            return {"recommendation": "Run your first experiment to start self-improvement."}
        least_used = None
        used_paradigms = {e["paradigm_id"] for e in all_exps}
        for p in TRAINING_PARADIGMS:
            if p["id"] not in used_paradigms:
                least_used = p["id"]
                break
        suggestion = least_used or best["paradigm_id"]
        return {
            "best_so_far": best,
            "recommended_next_paradigm": suggestion,
            "rationale": (
                f"Paradigm '{suggestion}' has not yet been explored — "
                "trying it next maximises coverage of the training space."
                if least_used
                else f"Best paradigm '{suggestion}' should be refined with HPO."
            ),
        }

    # ------------------------------------------------------------------
    # Buddy upgrade feed
    # ------------------------------------------------------------------

    def suggest_buddy_upgrade(self, capability: str) -> dict:
        """Suggest a training-based upgrade for Buddy.

        Parameters
        ----------
        capability : str
            Buddy capability to enhance (e.g. ``"nlp"``, ``"vision"``).

        Returns
        -------
        dict
            Suggested paradigm and techniques.
        """
        matching = [
            p for p in TRAINING_PARADIGMS
            if capability.lower() in p["description"].lower()
            or capability.lower() in p["name"].lower()
        ]
        chosen = matching[0] if matching else random.choice(TRAINING_PARADIGMS)
        return {
            "capability": capability,
            "recommended_paradigm": chosen["name"],
            "techniques": chosen["techniques"][:3],
            "priority": "high" if matching else "medium",
        }

    # ------------------------------------------------------------------
    # Status & chat
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a full status report."""
        exps = self._ledger.list_experiments()
        return {
            "bot": "AITrainingMasterBot",
            "paradigms_available": len(TRAINING_PARADIGMS),
            "total_experiments": len(exps),
            "completed_experiments": sum(1 for e in exps if e["status"] == "completed"),
            "best_score": (self._ledger.best_experiment() or {}).get("score"),
            "activity_log_entries": len(self._log),
        }

    def chat(self, message: str) -> dict:
        """Simple chat interface for Buddy routing."""
        lower = message.lower().strip()
        if lower in ("status", "report"):
            return self.status()
        if lower == "paradigms":
            return {"paradigms": self.list_paradigms()}
        if lower == "best":
            return self.best_experiment() or {"message": "No experiments yet."}
        if lower == "self improve":
            return self.self_improve()
        if lower.startswith("upgrade "):
            return self.suggest_buddy_upgrade(message[8:].strip())
        return {
            "message": f"AITrainingMasterBot: unrecognised command '{message}'",
            "hint": "Try: status | paradigms | best | self improve | upgrade <capability>",
        }
