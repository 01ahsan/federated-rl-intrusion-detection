---

## 🔐 Federated Reinforcement Learning for Network Intrusion Detection

### A modular framework with DQN, DDQN, and A2C across NSL-KDD, TON-IoT, and UNSW-NB15 datasets

---

### 📌 Overview

This project explores the integration of **Federated Learning** with **Reinforcement Learning (RL)** for intrusion detection in network systems. The framework supports multiple RL agents (DQN, Double DQN, A2C) and runs on three widely-used cybersecurity datasets:

* NSL-KDD
* TON-IoT
* UNSW-NB15

Our system simulates decentralized training using federated averaging, enabling distributed IDS development without central data aggregation.

---

### ⚙️ Features

* ✅ **RL Models**: Deep Q-Network (DQN), Double DQN, Advantage Actor-Critic (A2C)
* ✅ **Federated Setup**: Simulated 10-client environment with IID data splits
* ✅ **Multi-dataset Support**: Load, preprocess, and train on NSL-KDD, TON-IoT, UNSW-NB15
* ✅ **Advanced RL Agents**: Includes basic and enhanced A2C logic with entropy regularization
* ✅ **Results Logging**: Round-wise tracking of Q-values, F1-score, Recall, Accuracy, Rewards
* ✅ **Cleaned Data Export**: CSV outputs of preprocessed datasets for direct model use

---

### 🧠 Architectures

* `IntrusionDetectionEnv`: Custom RL environment wrapper for each dataset
* `DQNAgent`, `DDQNAgent`, `A2CAgent`: Modular RL agent classes
* `federated_averaging`: Weight aggregation for collaborative learning
* `results_df`: DataFrame for training metric exports (`training_results.csv`)

---

### 🧪 Datasets

Each dataset has a standalone Python script:

* `download_ksl_kdd.py`
* `download_ton_iot.py`
* `download_unsw_nb15.py`

Each script:

* Downloads the dataset
* Encodes categorical labels
* Applies scaling and saves as a cleaned `.csv`

---

### 🚀 Getting Started

1. Clone the repo:

   ```bash
   git clone https://github.com/MahirHossain12/federated-rl-intrusion-detection.git
   cd federated-rl-intrusion-detection
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Download and preprocess datasets:

   ```bash
   python download_ksl_kdd.py
   python download_ton_iot.py
   python download_unsw_nb15.py
   ```

4. Run your desired model:

   ```bash
   python federated_dqn.py       # DQN version
   python federated_ddqn.py      # DDQN version
   python federated_a2c.py       # Basic A2C
   python federated_a2c_advanced.py  # Advanced A2C
   ```

---

### 📊 Outputs

* Cleaned dataset CSVs
* Training logs: Q-values, accuracy, F1, recall, cumulative reward
* Exported model weights (optional)

---


