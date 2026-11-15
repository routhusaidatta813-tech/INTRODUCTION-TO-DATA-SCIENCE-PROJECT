/**
 * OUTBREAK ZERO: PREDICTIVE ANALYTICS & ZOMBIE CLASSIFICATION
 * An interactive educational web game for Introduction to Data Science
 */

(function () {
  'use strict';

  // =========================================================================
  // AUDIO SYNTHESIZER (Web Audio API - Offline & Self-Contained)
  // =========================================================================
  class TacticalAudio {
    constructor() {
      this.ctx = null;
      this.enabled = true;
    }

    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();
      }
      if (this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    playTone(freq, type = 'sine', duration = 0.15, vol = 0.1) {
      if (!this.enabled) return;
      this.init();
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        gain.gain.setValueAtTime(vol, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch (e) {
        // Audio might fail if user hasn't interacted yet
      }
    }

    click() {
      this.playTone(800, 'triangle', 0.04, 0.06);
    }

    scan() {
      this.playTone(420, 'sine', 0.1, 0.04);
    }

    alarm() {
      if (!this.enabled) return;
      this.playTone(320, 'sawtooth', 0.25, 0.12);
      setTimeout(() => this.playTone(280, 'sawtooth', 0.35, 0.12), 120);
    }

    shieldDeploy() {
      if (!this.enabled) return;
      this.playTone(550, 'sine', 0.1, 0.08);
      setTimeout(() => this.playTone(880, 'sine', 0.2, 0.08), 70);
    }

    victory() {
      if (!this.enabled) return;
      [523.25, 659.25, 783.99, 1046.5].forEach((f, idx) => {
        setTimeout(() => this.playTone(f, 'triangle', 0.25, 0.09), idx * 110);
      });
    }

    defeat() {
      if (!this.enabled) return;
      [330, 293.66, 261.63, 196].forEach((f, idx) => {
        setTimeout(() => this.playTone(f, 'sawtooth', 0.3, 0.12), idx * 140);
      });
    }
  }

  const audio = new TacticalAudio();

  // =========================================================================
  // SECTORS & EPIDEMIOLOGICAL DATA MODEL
  // =========================================================================
  const DISTRICT_TEMPLATES = [
    { id: 1, name: "Downtown Metro", x: 420, y: 260, pop: 34000, density: 14200, cases: 48, rate: 2.9, hospitals: 3.2, distance: 1.5 },
    { id: 2, name: "Riverside Suburbs", x: 180, y: 380, pop: 18500, density: 3100, cases: 6, rate: 1.1, hospitals: 1.8, distance: 8.4 },
    { id: 3, name: "Medical District", x: 380, y: 150, pop: 12000, density: 5600, cases: 22, rate: 1.4, hospitals: 8.8, distance: 3.2 },
    { id: 4, name: "Harbor Industrial", x: 650, y: 390, pop: 9500, density: 2400, cases: 14, rate: 2.1, hospitals: 0.9, distance: 6.8 },
    { id: 5, name: "Tech University", x: 260, y: 180, pop: 26000, density: 11500, cases: 38, rate: 3.2, hospitals: 2.5, distance: 2.8 },
    { id: 6, name: "North Forest Haven", x: 150, y: 90, pop: 6200, density: 1100, cases: 2, rate: 0.7, hospitals: 1.2, distance: 14.5 },
    { id: 7, name: "Old Town Market", x: 490, y: 340, pop: 29000, density: 16800, cases: 54, rate: 3.4, hospitals: 1.4, distance: 1.1 },
    { id: 8, name: "South Rail Depot", x: 520, y: 460, pop: 14000, density: 6200, cases: 28, rate: 2.8, hospitals: 1.5, distance: 5.2 },
    { id: 9, name: "West End Heights", x: 140, y: 260, pop: 16500, density: 4400, cases: 11, rate: 1.3, hospitals: 4.1, distance: 7.2 },
    { id: 10, name: "Airport Cargo Hub", x: 680, y: 160, pop: 8800, density: 3800, cases: 25, rate: 3.1, hospitals: 2.0, distance: 8.9 },
    { id: 11, name: "Eastside Slums", x: 600, y: 280, pop: 31000, density: 15400, cases: 46, rate: 3.6, hospitals: 0.4, distance: 2.2 },
    { id: 12, name: "Civic Citadel", x: 330, y: 320, pop: 11500, density: 5200, cases: 15, rate: 1.5, hospitals: 5.5, distance: 3.5 }
  ];

  // Road connections between districts (for graph visualization)
  const NETWORK_EDGES = [
    [1, 3], [1, 5], [1, 7], [1, 12],
    [5, 3], [5, 6], [5, 9],
    [9, 2], [9, 12],
    [2, 12], [2, 8],
    [7, 8], [7, 11], [7, 12],
    [11, 4], [11, 10], [1, 11],
    [4, 8], [4, 10], [3, 10]
  ];

  // Scenario Wave Definitions
  const SCENARIOS = [
    {
      wave: 1,
      title: "WAVE 1: INITIAL OUTBREAK - DENSITY & PROXIMITY",
      desc: "Patient Zero escaped containment. High density zones near the city center face imminent infection. Tune your model or hit Auto-Train to deploy 5 quarantine shields.",
      budget: 5,
      survivors: 216900,
      noise: 0.12
    },
    {
      wave: 2,
      title: "WAVE 2: TRANSIT ACCELERATION - VELOCITY R₀",
      desc: "The infection jumped into the rail and cargo networks! Sectors with high infection velocity (R₀) are now at severe risk despite distance.",
      budget: 5,
      survivors: 216900,
      noise: 0.15
    },
    {
      wave: 3,
      title: "WAVE 3: HEALTHCARE COLLAPSE - HOSPITAL CAPACITY",
      desc: "Medical capacity is strained. Sectors with low hospital beds will quickly succumb. Observe how negative feature weights protect high-capacity zones.",
      budget: 6,
      survivors: 216900,
      noise: 0.18
    },
    {
      wave: 4,
      title: "WAVE 4: MUTANT STRAIN - DECISION THRESHOLD CHALLENGE",
      desc: "A stealthy airborne strain emerges. False Negatives carry catastrophic death tolls. Experiment with lowering your decision threshold (τ) to 0.35 - 0.40!",
      budget: 6,
      survivors: 216900,
      noise: 0.22
    },
    {
      wave: 5,
      title: "WAVE 5: FINAL CONTAINMENT - METRIC MASTERY",
      desc: "The entire city's fate hinges on this final batch prediction. Achieve balanced Precision and Recall to secure total containment!",
      budget: 7,
      survivors: 216900,
      noise: 0.25
    }
  ];

  // =========================================================================
  // GAME STATE
  // =========================================================================
  const state = {
    waveIndex: 0,
    survivors: 216900,
    budget: 5,
    selectedCount: 0,
    threshold: 0.50,

    // Logistic Regression Weights: z = w0 + w1*x1 + w2*x2 + w3*x3 + w4*x4 + w5*x5
    weights: {
      bias: -1.2,
      density: 2.4,
      cases: 3.1,
      rate: 2.8,
      hospitals: -2.5,
      distance: -2.0
    },

    sectors: [],
    particles: [],
    hoveredSector: null,
    selectedSector: null,

    // Cumulative stats
    historyTP: 0,
    historyFP: 0,
    historyFN: 0,
    historyTN: 0,
    latestMetrics: {
      tp: 0, fp: 0, fn: 0, tn: 0,
      accuracy: 0, precision: 0, recall: 0, f1: 0
    }
  };

  // =========================================================================
  // MACHINE LEARNING MATHEMATICS: NORMALIZATION, LOGISTIC & GRADIENT DESCENT
  // =========================================================================

  // Sigmoid activation function: 1 / (1 + e^-z)
  function sigmoid(z) {
    if (isNaN(z) || z === null || z === undefined) return 0.5;
    if (z > 40) return 1.0;
    if (z < -40) return 0.0;
    return 1.0 / (1.0 + Math.exp(-z));
  }

  // Min-Max Normalizer for features across the current dataset
  function computeFeatureRanges(sectors) {
    const ranges = {
      density: { min: Infinity, max: -Infinity },
      cases: { min: Infinity, max: -Infinity },
      rate: { min: Infinity, max: -Infinity },
      hospitals: { min: Infinity, max: -Infinity },
      distance: { min: Infinity, max: -Infinity }
    };

    sectors.forEach(s => {
      const density = s.density || 0;
      const cases = s.cases || 0;
      const rate = s.rate || 0;
      const hospitals = s.hospitals || 0;
      const distance = s.distance || 0;

      ranges.density.min = Math.min(ranges.density.min, density);
      ranges.density.max = Math.max(ranges.density.max, density);

      ranges.cases.min = Math.min(ranges.cases.min, cases);
      ranges.cases.max = Math.max(ranges.cases.max, cases);

      ranges.rate.min = Math.min(ranges.rate.min, rate);
      ranges.rate.max = Math.max(ranges.rate.max, rate);

      ranges.hospitals.min = Math.min(ranges.hospitals.min, hospitals);
      ranges.hospitals.max = Math.max(ranges.hospitals.max, hospitals);

      ranges.distance.min = Math.min(ranges.distance.min, distance);
      ranges.distance.max = Math.max(ranges.distance.max, distance);
    });

    return ranges;
  }

  function normalize(val, min, max) {
    if (val === undefined || isNaN(val)) return 0.5;
    if (max === min || isNaN(min) || isNaN(max)) return 0.5;
    return (val - min) / (max - min);
  }

  // Calculate probability P(Y=1) for a sector given current weights
  function calculateProbability(sector, ranges, weights) {
    const x1 = normalize(sector.density, ranges.density.min, ranges.density.max);
    const x2 = normalize(sector.cases, ranges.cases.min, ranges.cases.max);
    const x3 = normalize(sector.rate, ranges.rate.min, ranges.rate.max);
    const x4 = normalize(sector.hospitals, ranges.hospitals.min, ranges.hospitals.max);
    const x5 = normalize(sector.distance, ranges.distance.min, ranges.distance.max);

    const z = weights.bias +
              (weights.density * x1) +
              (weights.cases * x2) +
              (weights.rate * x3) +
              (weights.hospitals * x4) +
              (weights.distance * x5);

    return sigmoid(z);
  }

  // Ground Truth generator: simulates true epidemiological spread with physical transmission & stochastic factor
  function determineGroundTruth(sector, waveConfig) {
    // True epidemiological score:
    const rawRisk = (sector.density / 17000) * 0.35 +
                    (sector.cases / 60) * 0.35 +
                    (sector.rate / 4.0) * 0.25 -
                    (sector.hospitals / 10.0) * 0.25 -
                    (sector.distance / 16.0) * 0.20;

    // Stochastic variation representing real-world noise & unseen mutation factors
    const noise = (Math.random() - 0.5) * waveConfig.noise;
    const finalScore = rawRisk + noise;

    // Binary Ground Truth (1 = will suffer severe outbreak, 0 = will remain contained)
    return finalScore > 0.33 ? 1 : 0;
  }

  // Train Logistic Regression using Batch Gradient Descent
  function trainLogisticRegression(sectors, ranges, epochs = 250, lr = 0.45) {
    // Standardize training dataset
    const X = [];
    const Y = [];

    sectors.forEach(s => {
      X.push([
        1.0, // bias feature
        normalize(s.density, ranges.density.min, ranges.density.max),
        normalize(s.cases, ranges.cases.min, ranges.cases.max),
        normalize(s.rate, ranges.rate.min, ranges.rate.max),
        normalize(s.hospitals, ranges.hospitals.min, ranges.hospitals.max),
        normalize(s.distance, ranges.distance.min, ranges.distance.max)
      ]);
      Y.push(s.groundTruthNext);
    });

    const m = X.length;
    // Initial weights
    let w = [state.weights.bias, state.weights.density, state.weights.cases, state.weights.rate, state.weights.hospitals, state.weights.distance];

    for (let epoch = 0; epoch < epochs; epoch++) {
      const grad = [0, 0, 0, 0, 0, 0];

      for (let i = 0; i < m; i++) {
        // Compute dot product
        let z = 0;
        for (let j = 0; j < 6; j++) {
          z += w[j] * X[i][j];
        }
        const pred = sigmoid(z);
        const err = pred - Y[i];

        for (let j = 0; j < 6; j++) {
          grad[j] += (err * X[i][j]) / m;
        }
      }

      // Update weights with gradient descent step
      for (let j = 0; j < 6; j++) {
        w[j] -= lr * grad[j];
      }
    }

    return {
      bias: parseFloat(w[0].toFixed(2)),
      density: parseFloat(w[1].toFixed(2)),
      cases: parseFloat(w[2].toFixed(2)),
      rate: parseFloat(w[3].toFixed(2)),
      hospitals: parseFloat(w[4].toFixed(2)),
      distance: parseFloat(w[5].toFixed(2))
    };
  }

  // =========================================================================
  // INITIALIZATION & WAVE SETUP
  // =========================================================================
  function initWave(waveIdx) {
    const config = SCENARIOS[waveIdx];
    state.waveIndex = waveIdx;
    state.budget = config.budget;
    state.selectedCount = 0;

    // Clone base districts and perturb slightly for new wave telemetry
    state.sectors = DISTRICT_TEMPLATES.map(t => {
      const densityMod = 1 + (waveIdx * 0.05);
      const caseMod = 1 + (waveIdx * 0.18);
      const rateMod = 1 + (waveIdx * 0.12);

      const s = {
        ...t,
        density: Math.round(t.density * densityMod),
        cases: Math.round(t.cases * caseMod),
        rate: parseFloat((t.rate * rateMod).toFixed(1)),
        isQuarantined: false,
        status: 'normal',
        predictedProb: 0.5,
        predictedClass: 0,
        groundTruthNext: 0
      };

      // Calculate the objective ground truth outcome
      s.groundTruthNext = determineGroundTruth(s, config);
      return s;
    });

    // Update UI HUD
    document.getElementById('hudDay').innerText = `Wave ${config.wave}`;
    document.getElementById('hudSurvivors').innerText = state.survivors.toLocaleString();
    document.getElementById('scenarioName').innerText = config.title;
    document.getElementById('scenarioDesc').innerText = config.desc;

    updatePredictionsAndUI();
  }

  // Recompute probabilities and update UI components
  function updatePredictionsAndUI() {
    const ranges = computeFeatureRanges(state.sectors);
    let predOutbreakCount = 0;

    state.sectors.forEach(s => {
      s.predictedProb = calculateProbability(s, ranges, state.weights);
      s.predictedClass = s.predictedProb >= state.threshold ? 1 : 0;
      if (s.predictedClass === 1) predOutbreakCount++;
    });

    // Recalculate selected quarantines
    state.selectedCount = state.sectors.filter(s => s.isQuarantined).length;

    // Update DOM indicators
    document.getElementById('hudBudget').innerText = `${state.budget - state.selectedCount} Available`;
    document.getElementById('footerAllocation').innerHTML = `Selected Quarantines: <strong>${state.selectedCount} / ${state.budget}</strong>`;
    document.getElementById('lblThreshold').innerText = `Threshold (τ) = ${state.threshold.toFixed(2)}`;
    document.getElementById('predictedCounts').innerText = `Predicted: ${predOutbreakCount} Outbreak / ${state.sectors.length - predOutbreakCount} Safe`;

    // Sliders readouts
    document.getElementById('valWeightDensity').innerText = (state.weights.density >= 0 ? '+' : '') + state.weights.density.toFixed(2);
    document.getElementById('valWeightCases').innerText = (state.weights.cases >= 0 ? '+' : '') + state.weights.cases.toFixed(2);
    document.getElementById('valWeightRate').innerText = (state.weights.rate >= 0 ? '+' : '') + state.weights.rate.toFixed(2);
    document.getElementById('valWeightHospitals').innerText = (state.weights.hospitals >= 0 ? '+' : '') + state.weights.hospitals.toFixed(2);
    document.getElementById('valWeightDistance').innerText = (state.weights.distance >= 0 ? '+' : '') + state.weights.distance.toFixed(2);
    document.getElementById('valWeightBias').innerText = (state.weights.bias >= 0 ? '+' : '') + state.weights.bias.toFixed(2);

    renderDistBar();
    renderDataTable();
  }

  // Render Risk Probability Distribution Bar
  function renderDistBar() {
    const container = document.getElementById('distBarContainer');
    container.innerHTML = '';

    // Sort copy by probability
    const sorted = [...state.sectors].sort((a, b) => a.predictedProb - b.predictedProb);
    sorted.forEach(s => {
      const dot = document.createElement('div');
      dot.className = `dist-dot ${s.predictedClass === 1 ? 'pred-outbreak' : 'pred-safe'}`;
      dot.title = `${s.name}: P(Outbreak)=${(s.predictedProb * 100).toFixed(1)}%`;
      dot.addEventListener('click', () => {
        toggleQuarantine(s.id);
      });
      container.appendChild(dot);
    });
  }

  // Render Data Science Table
  function renderDataTable() {
    const tbody = document.getElementById('sectorsTableBody');
    tbody.innerHTML = '';

    state.sectors.forEach(s => {
      const tr = document.createElement('tr');
      const probPct = (s.predictedProb * 100).toFixed(1);
      const isHigh = s.predictedClass === 1;

      tr.innerHTML = `
        <td><strong>${s.name}</strong></td>
        <td>${s.density.toLocaleString()} /km²</td>
        <td>${s.cases}</td>
        <td>${s.rate}x</td>
        <td>${s.hospitals} beds</td>
        <td>${s.distance} km</td>
        <td>
          <span style="font-weight:700; color:${isHigh ? 'var(--accent-red)' : 'var(--accent-green)'}">
            ${probPct}%
          </span>
        </td>
        <td>
          <span class="tag-badge ${isHigh ? 'badge-risk-high' : 'badge-risk-low'}">
            ${isHigh ? 'PREDICT OUTBREAK (1)' : 'SAFE (0)'}
          </span>
        </td>
        <td>
          <button class="btn btn-sm ${s.isQuarantined ? 'btn-secondary' : 'btn-outline'}" data-id="${s.id}">
            ${s.isQuarantined ? '🛡️ Quarantined' : 'Target'}
          </button>
        </td>
      `;

      tr.querySelector('button').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleQuarantine(s.id);
      });

      tr.addEventListener('mouseenter', () => {
        state.hoveredSector = s;
      });
      tr.addEventListener('mouseleave', () => {
        state.hoveredSector = null;
      });

      tbody.appendChild(tr);
    });
  }

  // Target / untarget quarantine drone
  function toggleQuarantine(id) {
    const s = state.sectors.find(sec => sec.id === id);
    if (!s) return;

    if (!s.isQuarantined) {
      if (state.selectedCount >= state.budget) {
        audio.alarm();
        alert(`Resource limit reached! You only have ${state.budget} Quarantine Drones this wave. Deselect another sector first or raise the threshold.`);
        return;
      }
      s.isQuarantined = true;
      audio.shieldDeploy();
      createParticles(s.x, s.y, '#00f3ff', 12);
    } else {
      s.isQuarantined = false;
      audio.click();
    }

    updatePredictionsAndUI();
  }

  // Target all predicted high-risk sectors up to drone capacity
  function targetAllPredicted() {
    audio.click();
    // Clear first
    state.sectors.forEach(s => s.isQuarantined = false);

    // Sort by risk descending
    const highRisk = [...state.sectors]
      .filter(s => s.predictedClass === 1)
      .sort((a, b) => b.predictedProb - a.predictedProb);

    let deployed = 0;
    highRisk.forEach(s => {
      if (deployed < state.budget) {
        s.isQuarantined = true;
        deployed++;
      }
    });

    audio.shieldDeploy();
    updatePredictionsAndUI();
  }

  function clearAllTargets() {
    audio.click();
    state.sectors.forEach(s => s.isQuarantined = false);
    updatePredictionsAndUI();
  }

  // =========================================================================
  // ROUND EXECUTION & CONFUSION MATRIX EVALUATION
  // =========================================================================
  function executeSimulationStep() {
    audio.init();

    let tp = 0; // Actual Outbreak (1) & Quarantined (1)
    let fp = 0; // Actual Safe (0) & Quarantined (1)
    let fn = 0; // Actual Outbreak (1) & NOT Quarantined (0)
    let tn = 0; // Actual Safe (0) & NOT Quarantined (0)

    let roundCasualties = 0;
    let roundSaved = 0;

    state.sectors.forEach(s => {
      const actual = s.groundTruthNext;
      const protectedByPlayer = s.isQuarantined;

      if (actual === 1 && protectedByPlayer) {
        tp++;
        s.status = 'saved';
        roundSaved += Math.round(s.pop * 0.85);
        createParticles(s.x, s.y, '#10b981', 25);
      } else if (actual === 1 && !protectedByPlayer) {
        fn++;
        s.status = 'infected';
        const loss = Math.round(s.pop * 0.45);
        roundCasualties += loss;
        createParticles(s.x, s.y, '#ef4444', 35);
      } else if (actual === 0 && protectedByPlayer) {
        fp++;
        s.status = 'quarantined';
        createParticles(s.x, s.y, '#f59e0b', 12);
      } else {
        tn++;
        s.status = 'safe';
      }
    });

    state.survivors = Math.max(0, state.survivors - roundCasualties);

    // Compute Metrics
    const total = tp + fp + fn + tn;
    const accuracy = total > 0 ? (tp + tn) / total : 0;
    const precision = (tp + fp) > 0 ? tp / (tp + fp) : 0;
    const recall = (tp + fn) > 0 ? tp / (tp + fn) : 0;
    const f1 = (precision + recall) > 0 ? (2 * precision * recall) / (precision + recall) : 0;

    state.latestMetrics = { tp, fp, fn, tn, accuracy, precision, recall, f1 };

    // Update cumulative history
    state.historyTP += tp;
    state.historyFP += fp;
    state.historyFN += fn;
    state.historyTN += tn;

    // Update Matrix Cells in DOM
    document.getElementById('countTP').innerText = tp;
    document.getElementById('countFP').innerText = fp;
    document.getElementById('countFN').innerText = fn;
    document.getElementById('countTN').innerText = tn;

    document.getElementById('metricAccuracy').innerText = (accuracy * 100).toFixed(1) + '%';
    document.getElementById('metricPrecision').innerText = (precision * 100).toFixed(1) + '%';
    document.getElementById('metricRecall').innerText = (recall * 100).toFixed(1) + '%';
    document.getElementById('metricF1').innerText = f1.toFixed(3);

    document.getElementById('hudAccuracy').innerText = (accuracy * 100).toFixed(0) + '%';
    document.getElementById('hudSurvivors').innerText = state.survivors.toLocaleString();

    // Show Sound & Results Dialog
    if (fn === 0) {
      audio.victory();
    } else {
      audio.alarm();
    }

    displayEvaluationModal(roundSaved, roundCasualties, { tp, fp, fn, tn, accuracy, precision, recall, f1 });
  }

  function displayEvaluationModal(saved, casualties, m) {
    const modal = document.getElementById('roundEvalModal');
    const banner = document.getElementById('evalBanner');
    const critique = document.getElementById('evalCritique');

    document.getElementById('repTP').innerText = m.tp;
    document.getElementById('repFN').innerText = m.fn;
    document.getElementById('repFP').innerText = m.fp;
    document.getElementById('repTN').innerText = m.tn;

    if (m.fn === 0) {
      banner.className = 'report-banner victory';
      banner.innerHTML = `
        <h3 style="color:var(--accent-green)">PERFECT DEFENSE: ZERO BREACHES</h3>
        <p>Your classification model achieved 100% Recall! ${saved.toLocaleString()} citizens shielded behind quarantine perimeters.</p>
      `;
    } else {
      banner.className = 'report-banner defeat';
      banner.innerHTML = `
        <h3 style="color:var(--accent-red)">OUTBREAK CONTAINMENT BREACHED</h3>
        <p>${m.fn} sector(s) suffered surprise zombie overruns (${casualties.toLocaleString()} civilian casualties). False Negatives prove fatal in epidemiology!</p>
      `;
    }

    // Pedagogical Data Science Critique
    let critiqueText = `<strong>Data Science Diagnostic:</strong><br>`;
    if (m.fn > 0 && m.fp === 0) {
      critiqueText += `Your model was too conservative (High Precision, but <em>low Recall of ${(m.recall * 100).toFixed(0)}%</em>). In medical screening and disaster defense, try <strong>lowering the Decision Threshold (τ)</strong> to catch more potential outbreaks!`;
    } else if (m.fp > 2) {
      critiqueText += `You had ${m.fp} False Positives (wasted drones on safe sectors). Your model was overly cautious. Consider <strong>raising the threshold (τ)</strong> or increasing the weight of protective features like <em>Hospital Capacity</em>.`;
    } else if (m.f1 > 0.8) {
      critiqueText += `Outstanding classification performance! Balanced F1-Score of ${m.f1.toFixed(3)}. The model learned accurate feature representations for viral spread.`;
    } else {
      critiqueText += `Model Accuracy was ${(m.accuracy * 100).toFixed(0)}%. Remember: features like <em>Population Density</em> and <em>Active Cases</em> correlate positively with spread, whereas <em>Hospitals</em> and <em>Distance</em> have negative protective weights.`;
    }

    critique.innerHTML = critiqueText;
    modal.classList.remove('hidden');
  }

  // =========================================================================
  // CANVAS RENDERING & INTERACTIVE RADAR MAP
  // =========================================================================
  const canvas = document.getElementById('cityCanvas');
  const ctx = canvas.getContext('2d');
  let animationFrameId = null;

  function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth * window.devicePixelRatio;
    canvas.height = parent.clientHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  function getCanvasCoords(e) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }

  // Particle System
  function createParticles(x, y, color, count = 15) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 3 + 1;
      state.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color,
        life: 1.0,
        decay: Math.random() * 0.03 + 0.015,
        radius: Math.random() * 3 + 1.5
      });
    }
  }

  function updateParticles() {
    for (let i = state.particles.length - 1; i >= 0; i--) {
      const p = state.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;
      if (p.life <= 0) {
        state.particles.splice(i, 1);
      }
    }
  }

  function drawMap(timestamp) {
    const width = canvas.width / window.devicePixelRatio;
    const height = canvas.height / window.devicePixelRatio;

    ctx.clearRect(0, 0, width, height);

    // Draw Cyber Grid
    ctx.strokeStyle = 'rgba(0, 243, 255, 0.04)';
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Scale factors to fit 800x550 template onto canvas
    const scaleX = width / 820;
    const scaleY = height / 540;

    // Draw Transit Network Roads
    NETWORK_EDGES.forEach(([idA, idB]) => {
      const sA = state.sectors.find(s => s.id === idA);
      const sB = state.sectors.find(s => s.id === idB);
      if (!sA || !sB) return;

      const ax = sA.x * scaleX;
      const ay = sA.y * scaleY;
      const bx = sB.x * scaleX;
      const by = sB.y * scaleY;

      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(bx, by);

      // Warning color if either sector is high risk
      if (sA.predictedClass === 1 || sB.predictedClass === 1) {
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.25)';
        ctx.lineWidth = 2;
      } else {
        ctx.strokeStyle = 'rgba(0, 243, 255, 0.12)';
        ctx.lineWidth = 1.5;
      }
      ctx.stroke();

      // Traveling data packet animation
      const t = ((timestamp / 2000) + (idA * 0.1)) % 1;
      const px = ax + (bx - ax) * t;
      const py = ay + (by - ay) * t;
      ctx.fillStyle = sA.predictedClass === 1 ? 'rgba(239, 68, 68, 0.8)' : 'rgba(0, 243, 255, 0.8)';
      ctx.beginPath();
      ctx.arc(px, py, 2, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw Sectors
    state.sectors.forEach(s => {
      const sx = s.x * scaleX;
      const sy = s.y * scaleY;
      const radius = 22;
      const isHovered = state.hoveredSector && state.hoveredSector.id === s.id;

      // Glow Aura
      let auraColor = 'rgba(16, 185, 129, 0.2)';
      let strokeColor = '#10b981';

      if (s.status === 'infected') {
        auraColor = 'rgba(239, 68, 68, 0.5)';
        strokeColor = '#ef4444';
      } else if (s.isQuarantined) {
        auraColor = 'rgba(0, 243, 255, 0.45)';
        strokeColor = '#00f3ff';
      } else if (s.predictedClass === 1) {
        auraColor = 'rgba(245, 158, 11, 0.35)';
        strokeColor = '#f59e0b';
      }

      ctx.save();

      // Outer Aura Circle
      ctx.fillStyle = auraColor;
      ctx.beginPath();
      ctx.arc(sx, sy, radius + (isHovered ? 8 : 4), 0, Math.PI * 2);
      ctx.fill();

      // Main Node Circle
      ctx.fillStyle = '#111827';
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = isHovered ? 3 : 2;
      ctx.beginPath();
      ctx.arc(sx, sy, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Center Icon or Probability
      ctx.fillStyle = '#fff';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      if (s.isQuarantined) {
        ctx.font = '14px sans-serif';
        ctx.fillText('🛡️', sx, sy);
      } else if (s.status === 'infected') {
        ctx.font = '14px sans-serif';
        ctx.fillText('☣', sx, sy);
      } else {
        const pct = Math.round(s.predictedProb * 100);
        ctx.fillText(`${pct}%`, sx, sy);
      }

      // District Label
      ctx.font = '10px "Inter", sans-serif';
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(s.name, sx, sy + radius + 14);

      ctx.restore();
    });

    // Draw Particles
    state.particles.forEach(p => {
      ctx.save();
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x * scaleX, p.y * scaleY, p.radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    });
    updateParticles();

    animationFrameId = requestAnimationFrame(drawMap);
  }

  // Handle Canvas Interaction: Hover & Click
  function handleCanvasMouseMove(e) {
    const coords = getCanvasCoords(e);
    const width = canvas.width / window.devicePixelRatio;
    const height = canvas.height / window.devicePixelRatio;
    const scaleX = width / 820;
    const scaleY = height / 540;

    const found = state.sectors.find(s => {
      const sx = s.x * scaleX;
      const sy = s.y * scaleY;
      const dist = Math.hypot(coords.x - sx, coords.y - sy);
      return dist <= 26;
    });

    state.hoveredSector = found || null;
    const tooltip = document.getElementById('mapTooltip');

    if (found) {
      canvas.style.cursor = 'pointer';
      const probPct = (found.predictedProb * 100).toFixed(1);
      const riskClass = found.predictedClass === 1 ? 'HIGH RISK (1)' : 'LOW RISK (0)';

      tooltip.innerHTML = `
        <div style="font-weight:700; color:#fff; margin-bottom:4px; font-family:'Orbitron', sans-serif;">
          ${found.name}
        </div>
        <div style="color:${found.predictedClass === 1 ? 'var(--accent-red)' : 'var(--accent-green)'}; font-weight:700; margin-bottom:6px;">
          Risk Probability: ${probPct}% [${riskClass}]
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; font-size:0.72rem; color:var(--text-muted); font-family:monospace;">
          <span>Density: ${found.density}/km²</span>
          <span>Infected: ${found.cases}</span>
          <span>Rate (R₀): ${found.rate}x</span>
          <span>Hospitals: ${found.hospitals}</span>
          <span>Distance: ${found.distance}km</span>
          <span>Status: ${found.isQuarantined ? 'Quarantined 🛡️' : 'Unprotected'}</span>
        </div>
        <div style="margin-top:6px; font-size:0.7rem; color:var(--accent-cyan);">
          Click to toggle Quarantine Drone
        </div>
      `;
      tooltip.style.left = `${Math.min(coords.x + 15, width - 290)}px`;
      tooltip.style.top = `${Math.min(coords.y + 15, height - 160)}px`;
      tooltip.classList.remove('hidden');
    } else {
      canvas.style.cursor = 'crosshair';
      tooltip.classList.add('hidden');
    }
  }

  function handleCanvasClick(e) {
    if (state.hoveredSector) {
      toggleQuarantine(state.hoveredSector.id);
    }
  }

  // =========================================================================
  // DATA SCIENCE LAB: AUTO-TRAIN LOGISTIC REGRESSION ANIMATION
  // =========================================================================
  function autoTrainModelWithAnimation() {
    audio.init();
    audio.scan();

    const btn = document.getElementById('btnAutoTrain');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `⏳ Training Model (Gradient Descent)...`;

    const ranges = computeFeatureRanges(state.sectors);
    const optimalWeights = trainLogisticRegression(state.sectors, ranges, 300, 0.45);

    // Smoothly animate the weights shifting from current to optimal
    const startWeights = { ...state.weights };
    const duration = 1200;
    const startTime = performance.now();

    function stepAnimation(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1.0);
      const ease = 1 - Math.pow(1 - progress, 3); // cubic ease-out

      Object.keys(optimalWeights).forEach(key => {
        state.weights[key] = parseFloat((startWeights[key] + (optimalWeights[key] - startWeights[key]) * ease).toFixed(2));
      });

      // Synchronize input sliders
      document.getElementById('weightDensity').value = state.weights.density;
      document.getElementById('weightCases').value = state.weights.cases;
      document.getElementById('weightRate').value = state.weights.rate;
      document.getElementById('weightHospitals').value = state.weights.hospitals;
      document.getElementById('weightDistance').value = state.weights.distance;
      document.getElementById('weightBias').value = state.weights.bias;

      updatePredictionsAndUI();

      if (progress < 1.0) {
        requestAnimationFrame(stepAnimation);
      } else {
        btn.disabled = false;
        btn.innerHTML = originalText;
        audio.victory();
      }
    }

    requestAnimationFrame(stepAnimation);
  }

  function resetDefaultWeights() {
    audio.click();
    state.weights = {
      bias: -1.2,
      density: 2.4,
      cases: 3.1,
      rate: 2.8,
      hospitals: -2.5,
      distance: -2.0
    };
    document.getElementById('weightDensity').value = state.weights.density;
    document.getElementById('weightCases').value = state.weights.cases;
    document.getElementById('weightRate').value = state.weights.rate;
    document.getElementById('weightHospitals').value = state.weights.hospitals;
    document.getElementById('weightDistance').value = state.weights.distance;
    document.getElementById('weightBias').value = state.weights.bias;
    updatePredictionsAndUI();
  }

  // =========================================================================
  // DATASET EXPORT TO CSV (FOR COURSEWORK SUBMISSION)
  // =========================================================================
  function exportDatasetCSV() {
    audio.click();
    let csv = "District_ID,District_Name,Population_Density,Active_Infected_Cases,Infection_Velocity_R0,Hospital_Beds_Per_1k,Distance_To_Epicenter_km,Predicted_Probability,Model_Classification,Actual_Outbreak_Ground_Truth\n";
    
    state.sectors.forEach(s => {
      csv += `${s.id},"${s.name}",${s.density},${s.cases},${s.rate},${s.hospitals},${s.distance},${s.predictedProb.toFixed(4)},${s.predictedClass},${s.groundTruthNext}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `outbreak_zero_telemetry_wave_${state.waveIndex + 1}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // =========================================================================
  // DOM EVENT BINDINGS
  // =========================================================================
  function setupEventListeners() {
    // Sound Toggle
    const btnSound = document.getElementById('btnSoundToggle');
    btnSound.addEventListener('click', () => {
      audio.enabled = !audio.enabled;
      btnSound.innerText = audio.enabled ? '🔊' : '🔇';
    });

    // Title Screen & Lore Carousel Logic
    const titleScreen = document.getElementById('titleScreen');
    const loreModal = document.getElementById('loreModal');
    let currentLorePage = 1;
    const totalLorePages = 4;

    function setLorePage(pageNum) {
      if (pageNum < 1) pageNum = 1;
      if (pageNum > totalLorePages) pageNum = totalLorePages;
      currentLorePage = pageNum;

      // Update slides
      document.querySelectorAll('.lore-slide').forEach(slide => {
        const slideIdx = parseInt(slide.getAttribute('data-slide'));
        slide.classList.toggle('active', slideIdx === currentLorePage);
      });

      // Update dots
      document.querySelectorAll('.lore-dot').forEach(dot => {
        const dotIdx = parseInt(dot.getAttribute('data-dot'));
        dot.classList.toggle('active', dotIdx === currentLorePage);
      });

      // Update indicator & buttons
      document.getElementById('lorePageIndicator').innerText = `PAGE ${currentLorePage} OF ${totalLorePages}`;
      const btnPrev = document.getElementById('btnLorePrev');
      const btnNext = document.getElementById('btnLoreNext');

      btnPrev.disabled = currentLorePage === 1;
      if (currentLorePage === totalLorePages) {
        btnNext.innerHTML = `🚀 ENTER COMMAND DECK ▶`;
        btnNext.className = 'btn btn-danger pulse-glow';
      } else {
        btnNext.innerHTML = `Next Page ▶`;
        btnNext.className = 'btn btn-primary';
      }
    }

    function enterTacticalCommand() {
      loreModal.classList.add('hidden');
      titleScreen.classList.add('hidden');
      audio.victory();
    }

    // Start Button on Title Screen
    document.getElementById('btnStartGame').addEventListener('click', () => {
      audio.init();
      audio.click();
      titleScreen.classList.add('hidden');
      loreModal.classList.remove('hidden');
      setLorePage(1);
    });

    // Replay Lore from HUD
    document.getElementById('btnShowLore').addEventListener('click', () => {
      audio.click();
      loreModal.classList.remove('hidden');
      setLorePage(1);
    });

    // Lore Navigation Controls
    document.getElementById('btnLoreNext').addEventListener('click', () => {
      audio.click();
      if (currentLorePage < totalLorePages) {
        setLorePage(currentLorePage + 1);
      } else {
        enterTacticalCommand();
      }
    });

    document.getElementById('btnLorePrev').addEventListener('click', () => {
      audio.click();
      if (currentLorePage > 1) {
        setLorePage(currentLorePage - 1);
      }
    });

    document.getElementById('btnLoreSkip').addEventListener('click', () => {
      audio.click();
      enterTacticalCommand();
    });

    document.querySelectorAll('.lore-dot').forEach(dot => {
      dot.addEventListener('click', () => {
        audio.click();
        const targetPage = parseInt(dot.getAttribute('data-dot'));
        setLorePage(targetPage);
      });
    });

    // Reset Simulation
    document.getElementById('btnRestart').addEventListener('click', () => {
      if (confirm("Reset the outbreak simulation back to Wave 1?")) {
        audio.click();
        initWave(0);
      }
    });

    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        audio.click();
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        const targetId = btn.getAttribute('data-tab');
        document.getElementById(targetId).classList.add('active');
      });
    });

    // Weight Sliders
    const bindWeightSlider = (sliderId, weightKey) => {
      const slider = document.getElementById(sliderId);
      slider.addEventListener('input', (e) => {
        state.weights[weightKey] = parseFloat(e.target.value);
        updatePredictionsAndUI();
      });
    };

    bindWeightSlider('weightDensity', 'density');
    bindWeightSlider('weightCases', 'cases');
    bindWeightSlider('weightRate', 'rate');
    bindWeightSlider('weightHospitals', 'hospitals');
    bindWeightSlider('weightDistance', 'distance');
    bindWeightSlider('weightBias', 'bias');

    // Threshold Slider
    document.getElementById('thresholdSlider').addEventListener('input', (e) => {
      state.threshold = parseFloat(e.target.value);
      updatePredictionsAndUI();
    });

    // Auto-Train & Reset
    document.getElementById('btnAutoTrain').addEventListener('click', autoTrainModelWithAnimation);
    document.getElementById('btnResetWeights').addEventListener('click', resetDefaultWeights);

    // Map Action Buttons
    document.getElementById('btnSelectAllPredicted').addEventListener('click', targetAllPredicted);
    document.getElementById('btnClearTargets').addEventListener('click', clearAllTargets);
    document.getElementById('btnExportData').addEventListener('click', exportDatasetCSV);

    // Outbreak Execution
    document.getElementById('btnExecuteSimulation').addEventListener('click', executeSimulationStep);

    // Guide Modal
    const guideModal = document.getElementById('dsGuideModal');
    document.getElementById('btnDsGuide').addEventListener('click', () => {
      audio.click();
      guideModal.classList.remove('hidden');
    });

    // Playtest Evidence Button directly in Header
    document.getElementById('btnPlaytest').addEventListener('click', () => {
      audio.click();
      guideModal.classList.remove('hidden');
      const playtestTab = document.querySelector('[data-guide="g-playtest"]');
      if (playtestTab) playtestTab.click();
    });

    document.getElementById('btnCloseGuide').addEventListener('click', () => guideModal.classList.add('hidden'));
    document.getElementById('btnGotIt').addEventListener('click', () => guideModal.classList.add('hidden'));

    // Guide Sidebar Navigation
    document.querySelectorAll('.guide-link').forEach(link => {
      link.addEventListener('click', () => {
        audio.click();
        document.querySelectorAll('.guide-link').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.guide-page').forEach(p => p.classList.remove('active'));

        link.classList.add('active');
        const target = link.getAttribute('data-guide');
        document.getElementById(target).classList.add('active');
      });
    });

    // Round Result Modal
    const evalModal = document.getElementById('roundEvalModal');
    document.getElementById('btnCloseEval').addEventListener('click', () => evalModal.classList.add('hidden'));
    document.getElementById('btnReviewBoard').addEventListener('click', () => {
      evalModal.classList.add('hidden');
      // Switch to evaluation tab
      document.querySelector('[data-tab="tab-eval"]').click();
    });

    document.getElementById('btnNextWave').addEventListener('click', () => {
      evalModal.classList.add('hidden');
      if (state.waveIndex < SCENARIOS.length - 1) {
        initWave(state.waveIndex + 1);
      } else {
        alert("CONGRATULATIONS! You completed all outbreak waves and mastered Predictive Analytics & Classification!");
        initWave(0);
      }
    });

    // Canvas Events
    canvas.addEventListener('mousemove', handleCanvasMouseMove);
    canvas.addEventListener('click', handleCanvasClick);
    window.addEventListener('resize', resizeCanvas);
  }

  // =========================================================================
  // APP ENTRY POINT
  // =========================================================================
  window.addEventListener('DOMContentLoaded', () => {
    resizeCanvas();
    setupEventListeners();
    initWave(0);
    requestAnimationFrame(drawMap);
  });

})();
