# Project Plan: Intrinsically Motivated Cobot

## 1. Project Overview

### What this is

An always on, task free, intrinsically motivated learning system running on a personal 4 DOF cobot arm. The robot generates its own behavior from curiosity signals derived from a learned world model. There are no tasks, no hand written reward functions describing desired behavior, no episodes, and no discrete skill dispatch. Behaviors (reaching, tracking, self inspection) should emerge as attractors of a continuously running policy, not be invoked as pre built functions.

The developmental analogy is an infant: a small set of hardwired reflexes and safety limits, pretrained low level perception, and everything above that learned through self generated experience (motor babbling, then curiosity driven exploration).

### Strategy: single repo first

All work happens in this one cobot project repo. A generic, pip installable IMOL library is a possible FUTURE project that would be extracted from this codebase after the research core is proven on hardware. To keep that extraction mechanical rather than a rewrite:

* Respect the module boundaries below (M1 through M6) as real package boundaries.
* Modules M2 through M5 must never import robot specific code, drivers, or ROS2 message types. They operate on normalized tensors and specs only.
* All robot specific knowledge lives in M1 (embodiment adapter config) and the ROS2/hardware layer.

Do not build library packaging, public APIs, or PyPI infrastructure now. That is explicitly deferred.

### Explicitly rejected approaches

Do not implement these, even as temporary scaffolding:

* A high level policy dispatching to a menu of pre trained discrete skills or options with termination conditions.
* Hand written reward functions describing what the robot should do.
* Task or episode boundaries anywhere above the reflex layer (training in imagination may use rollout horizons; the deployed act loop never resets).
* Goal conditioning inputs to the policy.
* Curiosity from raw prediction error alone with no correction for irreducible randomness (the noisy TV problem).
* Adding new drive scalars to force a behavior the owner wants to see. That is hand design through the back door.

## 2. Prior Art Context

This project sits inside the intrinsically motivated open ended learning (IMOL) field, active since Schmidhuber 1991 and Oudeyer's developmental robotics work. Key references for implementation decisions:

* Oudeyer et al.: learning progress as a curiosity signal robust to the noisy TV problem.
* Pathak et al.: Intrinsic Curiosity Module (ICM).
* Burda et al.: Random Network Distillation (RND).
* Hafner et al.: DreamerV3, the world model plus imagination training architecture this project builds on.
* Explauto (Inria, 2014): prior open source Python library for intrinsic motivation and exploration, pre deep learning era, low dimensional spaces only.
* PILLAR Robots (EU Horizon, 2022 to 2026): domain independent intrinsically motivated cognitive architecture. No public code found as of mid 2026; check for releases before locking major design decisions.
* LeRobot (Hugging Face): the dominant open source robot learning stack. Not used directly in this repo, but a future library extraction would target LeRobot compatibility, so avoid design choices that would make that impossible.

The contribution of this project: the IMOL concept rebuilt on a modern self supervised deep world model, from raw sensors, on cheap accessible hardware, in usable code. The concept is not new; the modern accessible implementation is.

## 3. Hardware and Environment

* Arm: 4 DOF, Feetech STS3215 serial bus servos, FE URT 1 USB servo interface.
* Compute (training and inference): Ubuntu 22.04 desktop, RTX 3070, 8 GB VRAM. Size all models to fit training plus inference concurrently in 8 GB. Use small DreamerV3 configs.
* Distributed node: Raspberry Pi 4 running servo IO, camera capture, microphone capture, and the safety layer.
* Sensors: USB or CSI camera on or near the arm; USB microphone (audio is a later phase).
* Middleware: ROS2 Humble over DDS between Pi and desktop.
* Existing assets from the owner's prior cobot work, ask for entry points rather than rebuilding:
  * A swappable sim/real backend for the arm.
  * A shared observation builder node.
  * An FSM orchestrator and ONNX skill server (NOT used by this project's learned behavior, but their process management and ROS2 patterns are reference material).
* Servo telemetry available over the bus and already exposed via ROS2 topics: position, velocity, load, temperature, voltage. The drive system uses load and temperature for homeostatic signals.

## 4. System Architecture

Six modules, three asynchronous loops.

```
                    [Pi: camera, mic, servo IO]
                              |
                     ROS2 DDS topics
                              |
   M1 embodiment adapter (normalize obs, denormalize actions)
                              |
   M2 sensory encoders (frozen) -> fused latent z_t
                              |
   M3 world model (RSSM + ensemble)
        |                     |
   M4 drive system      M5 policy (actor critic, trained in imagination)
        |_____________________|
                              |
   M6 reflex and safety layer (on Pi, non overridable)
                              |
                        servo commands
```

### M1. Embodiment Adapter

The only module containing robot specific code. A per robot YAML config defines:

* Observation schema: camera resolution and rate, mic sample rate, joint count, per joint ranges for position, velocity, load, temperature.
* Action schema: dimensionality, per joint limits, control rate.
* Kinematic description (URDF or equivalent).

M1 converts raw ROS2 messages into normalized tensors matching the schema and converts policy outputs back into servo commands. Everything above M1 is embodiment agnostic by construction. Generalize the existing shared observation builder as the starting point.

### M2. Sensory Encoders (Frozen)

* Vision: pretrained frozen DINOv2 ViT S class model at roughly 10 Hz, patch latents pooled per frame.
* Audio (later phase): frozen pretrained audio embedding model (PANNs or YAMNet, both trained on AudioSet, general sound, not speech specific like Whisper), gated by Silero VAD so silence is not processed. Only add a small trainable projection layer on top if the frozen model underperforms on the real mic and environment; never train the full encoder from scratch.
* Proprioception: small MLP over joint position, velocity, load, temperature.
* Outputs fused into a single latent vector z_t per timestep.

Frozen for two reasons: prevents latent collapse while the rest of the system is unstable, and mirrors the fact that biological perception arrives substantially prewired. In simulation phases, a low dimensional state vector may bypass the vision encoder entirely; prove the loop on simple inputs first.

### M3. World Model

RSSM (recurrent state space model) following DreamerV3: predicts next latent given hidden state, current latent, and action.

* Ensemble of ~5 prediction heads with independent initializations.
* Ensemble disagreement = epistemic uncertainty (learnable unknowns, worth exploring).
* Distinct from aleatoric uncertainty (irreducible noise, not worth exploring). This split is the structural defense against the noisy TV problem.
* Start from an existing open source DreamerV3 implementation, adapted to consume M2 latents rather than raw pixels. Do not write an RSSM from scratch. Cite the adapted source in comments.

### M4. Drive System (the novel research core)

This section is written as an implementable algorithm, not just a concept. Treat every parameter value below as a starting point to tune, not a fixed requirement.

**Data structure: the codebook.**
A fixed size table of N=256 entries (start here, tunable). Each entry holds:
* `centroid`: a vector the same size as the fused latent from M2, representing one region of latent space.
* `fast_error`: a scalar EMA of recent prediction error for this region.
* `slow_error`: a scalar EMA of longer term prediction error for this region.
* `count`: how many times this region has been visited, used only for initialization logic below.

Initialize all 256 centroids from the first batch of babbling data (random sample of observed latents), fast_error and slow_error both at zero, count at zero.

**Per timestep algorithm, runs once every act loop tick:**

1. Take the current fused latent z_t from M2 and the world model's prediction error e_t from M3 (the distance between predicted and actual latent, e.g. mean squared error).
2. Find the nearest codebook centroid to z_t (nearest neighbor by distance, standard k means style lookup).
3. Update that centroid's EMAs:
   `fast_error = 0.9 * fast_error + 0.1 * e_t`
   `slow_error = 0.99 * slow_error + 0.01 * e_t`
   (these two decay rates are the tunable knob: fast_error should visibly react within tens of steps, slow_error should drift over hundreds to thousands of steps. Adjust the 0.9 and 0.99 coefficients if that is not happening.)
4. Occasionally re center that centroid slightly toward z_t (standard streaming k means update, e.g. `centroid += 0.01 * (z_t - centroid)`), so the codebook keeps adapting to where the robot actually spends time.
5. Compute learning progress for that region: `LP = slow_error - fast_error`. Positive means error is currently dropping (getting better here), negative or near zero means either already mastered or not improving.
6. Pull epistemic novelty directly from M3's ensemble: the variance or spread across the 5 prediction heads' outputs for this timestep. No separate bookkeeping needed, this comes straight from M3's forward pass.
7. Combine into the drive vector for this timestep, starting with 2 scalars:
   `drive = [w_lp * LP, w_novelty * disagreement]`
   `w_lp` and `w_novelty` are scalar weights, start both at 1.0, tune later.
8. Once hardware phases begin (Phase 3 onward), add two more scalars read directly from ROS2 servo telemetry, no learning involved, just simple threshold math:
   `fatigue = clip((current_temp - safe_temp) / (max_temp - safe_temp), 0, 1)`, subtract this from the drive vector's total magnitude, or feed it as a negative bias term, either is fine to start.
   `boredom = 1.0 if max(LP across all codes) < boredom_threshold else 0.0`, used only to raise the policy's entropy floor for that timestep (see M5), not concatenated into the drive vector itself.
9. Output the drive vector to M5 as a conditioning input, alongside z_t.

**Debugging and tuning guidance:**
* The single most useful plot in this entire project: a heatmap of LP across all 256 codes, updated over training time. Uniform noise means something is broken (fast_error and slow_error decay rates are too close together, or the codebook is not separating regions meaningfully). Visible structure, some codes lighting up then fading as they get mastered, means it is working.
* If behavior fixates on one thing forever (the noisy TV problem): check whether epistemic novelty (step 6) is actually distinct from fast_error. If the ensemble heads agree even in the fixated region, disagreement should be near zero there and LP should also be near zero once mastered, so persistent fixation despite low LP and low disagreement means a bug in the drive computation, not a fundamental flaw.
* If the robot goes inert (nothing seems interesting anywhere): check `boredom_threshold`, it is likely set too high, and check the entropy floor in M5 is actually wired up to respond to the boredom flag.

Hard constraint, regardless of how the above is tuned: drives are continuous conditioning inputs to the policy network. There is no arbiter, switch statement, or mode selection keyed on drive values. The mapping from drive state to behavior must be learned by M5, not branched in code.

### M5. Policy

**Runtime inputs, every tick:** the fused latent z_t from M2, the world model's hidden state from M3 (its running internal summary of the situation, not just the instantaneous prediction), and the drive vector from M4. All three concatenated into one input to the actor network.

**Runtime output:** joint position or velocity deltas at 20 to 50 Hz, continuous, no resets, no goal input. One forward pass through the already trained actor network, nothing more, every tick.

**Training, offline, separate from the runtime loop:** actor critic trained inside the world model's imagined rollouts (standard DreamerV3 machinery). The critic only exists during this offline training process, it estimates expected future drive signal from a given state purely to stabilize the actor's gradient updates. The critic never runs at runtime and never gates, filters, or parses the actor's output; by deployment time its job is already finished and only the trained actor remains in the live loop.

**Reward signal used during that offline training:** the drive weighted sum of LP and disagreement from M4, computed inside imagined rollouts. No external reward exists anywhere in this system.

* Entropy floor so the policy can never collapse into stillness or a fixed loop.
* Learned policy, not MPC/CEM planning: online planning at control rate does not fit the compute budget.

**Pipeline shape, for reference:** there are two threads converging on M5. The direct thread is M1, M2, M5, raw state straight through to the actor. The evaluative thread is M1, M2, M3, M4, then into M5, where M3 must run first since M4's computation depends on M3's prediction error and ensemble disagreement. M3's hidden state also feeds M5 directly alongside these two threads, so M5's actual input is state (from M2 and M3's hidden state) plus a small evaluation of how interesting that state currently is (from M4).

### M6. Reflex and Safety Layer

The only hand engineered behavior. Runs on the Pi, downstream of the policy, high rate, non overridable:

* Joint position, velocity, and torque clamps.
* Temperature throttle and shutdown thresholds.
* Current spike detection for collision or jam stop.
* Watchdog: if policy commands stop arriving, hold or go limp safely.
* Optional, only if emergence stalls in late phases: one or two central pattern generator (CPG) oscillators as modulatable raw material, analogous to newborn rhythmic reflexes. Do not front load.

If emergent behavior stalls, M6 is the only layer permitted to be enriched with primitives. Everything above it stays learned.

### Runtime loops

1. Act loop, 20 to 50 Hz: obs -> M1 -> M2 -> M3 latent update -> M4 drives -> M5 action -> M6 -> servos.
2. World model training loop: continuous background training from the replay buffer.
3. Policy training loop: imagined rollouts in the current world model, interleaved with loop 2.

Simple alternation of loops 2 and 3 is acceptable early; true async is a later optimization.

### Replay buffer

Disk backed ring buffer with reservoir sampling for long horizon retention plus a recent window. An always on system with no resets will otherwise catastrophically forget anything not recently seen. In memory buffer is acceptable for early sim phases only.

## 5. Build Phases

Each phase ends with a postable artifact (plot, video, or writeup). There is no external benchmark; dashboards are the only ground truth and are deliverables from Phase 0 onward.

### Phase 0: Sim babbling and infrastructure

* Repo skeleton per Section 7. Sim wrapper over the existing backend with a gym style interface (reset used only for training convenience).
* Ornstein Uhlenbeck (temporally correlated) noise driving joint targets.
* Replay buffer and logging pipeline. Dashboards for action and state distributions.
* Acceptance: 100k+ transitions collected and stored; dashboards live.

### Phase 1: Sim world model

* Adapt DreamerV3 to the sim observation space (low dimensional state first). Add the 5 head ensemble.
* Acceptance: prediction error visibly decreasing; imagined vs real trajectory plots qualitatively sane; disagreement higher on rare states than common ones.

### Phase 2: Sim closed loop

* M4 and M5 wired in. Policy drives the sim arm from drives alone; new experience flows back into training.
* Acceptance: 1+ hour of continuous sim operation without crashes; state visitation heatmap visibly different from babbling; LP heatmap over the codebook shows structure (codes rising then falling as they get learned). The LP heatmap is the single most important diagnostic in the project. If it shows uniform noise, stop and debug here.

### Phase 3: Real arm babbling and world model

* M1 config for the real arm. M6 safety layer on the Pi, tested with babbling before any learned policy touches hardware.
* 24+ hours of real babbling data. Retrain M3 on real data (real noise, backlash, occlusion).
* Acceptance: Phase 1 diagnostics reproduced on hardware data; M6 demonstrably clamps and stops correctly (test deliberately).

### Phase 4: Real arm closed loop

* Full M1 through M6 running continuously. Vision encoder (frozen DINOv2 class) enters the fused latent here if not already.
* Acceptance: multi hour continuous operation; recorded video where behavior reads as exploratory and attractor like rather than random; the stated project benchmark is qualitative, whether an outside observer reads the behavior as alive.

### Phase 5: Audio

* Microphone into the fused latent via a frozen pretrained audio embedding model (PANNs or YAMNet), Silero VAD gated.
* Optional: treat sound output (speaker) as additional action dimensions driven by the same drive signals (vocal babbling).
* Acceptance: demonstrable behavioral response to novel sounds without any hand coded sound handling.

### Phase 6: Second embodiment (portability proof)

* New M1 config for a structurally different robot (different DOF or morphology). Retrain M3 through M5 from scratch. Zero code changes above M1 permitted.
* Acceptance: the same emergent behavior pipeline runs on the second embodiment. Only after this phase may genericity be claimed publicly. This phase is also the go/no go gate for extracting the standalone IMOL library as a separate project.

## 6. Known Failure Modes and Mitigations

* Noisy TV fixation on unlearnable randomness: LP instead of raw error, plus epistemic/aleatoric split via ensemble.
* Boredom lockup (LP flat, robot inert): entropy floor plus boredom drive.
* Runaway or self damaging motion: M6 clamps, temperature throttle, current spike stop, watchdog. M6 is never bypassed, including during debugging.
* Catastrophic forgetting from always on operation: reservoir sampling replay.
* Latent collapse: frozen encoders.
* Drive weight tuning becoming disguised task design: drive vector stays at 4 to 8 scalars maximum; new drives require explicit owner sign off and a written rationale in DECISIONS.md.
* VRAM overrun on the 3070: small model configs, memory check before long runs, mixed precision where stable.
* The least de risked element in the whole plan is the M4 to M5 coupling: producing legible structured behavior from a small continuous drive signal with no scaffolding. Expect the majority of research debugging time there. Everything else is assembled from proven components.

## 7. Repository Structure

```
cobot_imol/
  configs/
    embodiments/
      arm_sim.yaml
      arm_real.yaml
    training/
      world_model_small.yaml
      policy_default.yaml
  m1_embodiment_adapter/
  m2_sensory_encoders/
  m3_world_model/
  m4_drive_system/
  m5_policy/
  m6_reflex_safety/        (deploys to the Pi)
  replay_buffer/
  ros2_nodes/              (Pi and desktop nodes, launch files)
  sim/                     (wrapper over existing sim backend)
  scripts/
    run_babbling.py
    train_world_model.py
    train_policy.py
    run_closed_loop.py
  dashboards/
  docs/
    projectplan.md         (this file)
    DECISIONS.md
    progress_journal.md
```

M2 through M5 must not import from ros2_nodes, m1, m6, or any driver code. Enforce with import linting if convenient.

## 8. Tech Stack

* Python 3.10+, PyTorch, type hints on public functions.
* Existing open source DreamerV3 implementation as the M3/M5 foundation.
* ROS2 Humble for all interprocess and cross device communication.
* Weights and Biases (or TensorBoard fallback) for all runs, no unlogged training.
* Existing sim backend from the owner's cobot stack for Phases 0 through 2; minimal MuJoCo or PyBullet scene only as a fallback if adaptation exceeds half a day.
* OpenCV where camera plumbing is needed; DINOv2 via torch hub or HF; Silero VAD for audio gating in Phase 5; PANNs or YAMNet (torch hub or HF) as the frozen audio embedding model.

## 9. Working Agreement for the Agent

* Read this entire file before writing code.
* Build in phase order. Never run a learned policy on hardware before M6 is tested. Never build Phase N+1 machinery while Phase N acceptance criteria are unmet.
* Working and instrumented beats clever. Every training loop logs from its first run.
* Small commits, one concern each, imperative messages.
* Ambiguous decisions: choose the simpler option, record it in DECISIONS.md with the non shortcut alternative, keep moving. Exception: anything touching the core premise (no tasks, no hand rewards, no modes, continuous operation) or hardware safety requires asking the owner first.
* Prefer adapting cited open source implementations over writing from scratch.
* Never add task definitions, success criteria for specific behaviors, scripted behavior modes, or goal conditioning. Architecture violations, not style choices.
* Ask the owner for existing code entry points (sim backend, observation builder, ROS2 launch patterns) before rebuilding anything that already exists.
