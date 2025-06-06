# -*- coding: utf-8 -*-
"""A2C indi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_7MwxkcWM1zu3RmeeDY3_1W7OVAByfuw
"""

1st varient

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import f1_score, recall_score, accuracy_score
from imblearn.over_sampling import SMOTE
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import random

class IntrusionDetectionEnv:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.current_idx = 0
        self.state = None

    def reset(self):
        self.current_idx = 0
        self.state = self.X[self.current_idx]
        return self.state

    def step(self, action):
        reward = 1 if action == self.y[self.current_idx] else -1
        self.current_idx += 1
        done = self.current_idx >= len(self.X)
        next_state = self.X[self.current_idx] if not done else None
        return next_state, reward, done

class A2CAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = 0.99
        self.actor, self.critic = self._build_model()

    def _build_model(self):
        inputs = Input(shape=(self.state_size,))
        dense = Dense(64, activation='relu')(inputs)
        policy = Dense(self.action_size, activation='softmax')(dense)
        value = Dense(1, activation='linear')(dense)
        actor = Model(inputs, policy)
        critic = Model(inputs, value)
        actor.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001))
        critic.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
        return actor, critic

    def act(self, state):
        policy = self.actor.predict(state, verbose=0)[0]
        return np.random.choice(self.action_size, p=policy)

    def train(self, state, action, reward, next_state, done):
        value = self.critic.predict(state, verbose=0)
        next_value = self.critic.predict(next_state, verbose=0) if not done else 0
        target = reward + self.gamma * next_value if not done else reward
        advantage = target - value
        action_onehot = np.zeros((1, self.action_size))
        action_onehot[0][action] = 1
        self.actor.fit(state, action_onehot * advantage, verbose=0)
        self.critic.fit(state, target, verbose=0)

    def get_weights(self):
        return self.actor.get_weights(), self.critic.get_weights()

    def set_weights(self, actor_weights, critic_weights):
        self.actor.set_weights(actor_weights)
        self.critic.set_weights(critic_weights)

def federated_averaging(weights):
    actor_weights = [w[0] for w in weights]
    critic_weights = [w[1] for w in weights]
    avg_actor = [np.mean([a[i] for a in actor_weights], axis=0) for i in range(len(actor_weights[0]))]
    avg_critic = [np.mean([c[i] for c in critic_weights], axis=0) for i in range(len(critic_weights[0]))]
    return avg_actor, avg_critic

data = pd.read_csv("TON_IoT.csv")
label_encoder = LabelEncoder()
data['label'] = label_encoder.fit_transform(data['label'])
X = data.drop('label', axis=1).values
y = data['label'].values
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_resampled)
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)
X_train, X_test, y_train, y_test = train_test_split(X_pca, y_resampled, test_size=0.2, random_state=42)
num_clients = 10
X_partitions = np.array_split(X_train, num_clients)
y_partitions = np.array_split(y_train, num_clients)
state_size = X_train.shape[1]
action_size = len(np.unique(y))
global_agent = A2CAgent(state_size, action_size)
global_actor_weights, global_critic_weights = global_agent.get_weights()
clients = [A2CAgent(state_size, action_size) for _ in range(num_clients)]
num_rounds = 10
results_df = pd.DataFrame(columns=["Round", "F1-score", "Recall", "Acc (%)", "Cumulative Reward (AVG)"])

for round_num in range(num_rounds):
    local_weights = []
    cumulative_rewards = []
    for client_idx, client in enumerate(clients):
        X_client = X_partitions[client_idx]
        y_client = y_partitions[client_idx]
        env = IntrusionDetectionEnv(X_client, y_client)
        client.set_weights(global_actor_weights, global_critic_weights)
        state = env.reset().reshape(1, state_size)
        total_reward = 0
        steps = 0
        while True:
            action = client.act(state)
            next_state, reward, done = env.step(action)
            next_state = next_state.reshape(1, state_size) if next_state is not None else np.zeros((1, state_size))
            client.train(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            steps += 1
            if done:
                break
        cumulative_rewards.append(total_reward / steps)
        local_weights.append(client.get_weights())
    global_actor_weights, global_critic_weights = federated_averaging(local_weights)
    global_agent.set_weights(global_actor_weights, global_critic_weights)
    y_pred_prob = global_agent.actor.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_prob, axis=1)
    f1 = f1_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")
    acc = accuracy_score(y_test, y_pred) * 100
    results_df.loc[round_num] = [round_num + 1, f1 * 100, recall * 100, acc, np.mean(cumulative_rewards)]

print(results_df)
results_df.to_csv("a2c_training_results.csv", index=False)

2nd varient

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import f1_score, recall_score, accuracy_score
from imblearn.over_sampling import SMOTE
import tensorflow as tf
from tensorflow.keras import layers, models

class A2C:
    def __init__(self, input_shape, action_space):
        self.state_size = input_shape
        self.action_size = action_space
        self.gamma = 0.99
        self.actor = self.build_actor()
        self.critic = self.build_critic()
        self.actor_opt = tf.keras.optimizers.Adam(0.001)
        self.critic_opt = tf.keras.optimizers.Adam(0.002)

    def build_actor(self):
        inputs = layers.Input(shape=(self.state_size,))
        x = layers.Dense(128, activation='relu')(inputs)
        x = layers.Dense(64, activation='relu')(x)
        outputs = layers.Dense(self.action_size, activation='softmax')(x)
        return models.Model(inputs, outputs)

    def build_critic(self):
        inputs = layers.Input(shape=(self.state_size,))
        x = layers.Dense(128, activation='relu')(inputs)
        x = layers.Dense(64, activation='relu')(x)
        outputs = layers.Dense(1)(x)
        return models.Model(inputs, outputs)

    def act(self, state):
        prob = self.actor(state, training=False).numpy()[0]
        return np.random.choice(self.action_size, p=prob)

    def train(self, state, action, reward, next_state, done):
        state = tf.convert_to_tensor(state)
        next_state = tf.convert_to_tensor(next_state)
        with tf.GradientTape(persistent=True) as tape:
            value = self.critic(state)
            next_value = self.critic(next_state)
            target = reward + (1 - int(done)) * self.gamma * next_value
            advantage = target - value
            probs = self.actor(state)
            action_mask = tf.one_hot([action], self.action_size)
            selected_prob = tf.reduce_sum(probs * action_mask, axis=1)
            actor_loss = -tf.math.log(selected_prob + 1e-10) * advantage
            critic_loss = tf.square(advantage)
        actor_grads = tape.gradient(actor_loss, self.actor.trainable_variables)
        critic_grads = tape.gradient(critic_loss, self.critic.trainable_variables)
        self.actor_opt.apply_gradients(zip(actor_grads, self.actor.trainable_variables))
        self.critic_opt.apply_gradients(zip(critic_grads, self.critic.trainable_variables))

    def get_weights(self):
        return self.actor.get_weights(), self.critic.get_weights()

    def set_weights(self, actor_weights, critic_weights):
        self.actor.set_weights(actor_weights)
        self.critic.set_weights(critic_weights)

class Env:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.idx = 0

    def reset(self):
        self.idx = 0
        return self.X[self.idx]

    def step(self, action):
        reward = 1 if action == self.y[self.idx] else -1
        self.idx += 1
        done = self.idx >= len(self.X)
        state = self.X[self.idx] if not done else np.zeros_like(self.X[0])
        return state, reward, done

def average_weights(weights):
    actor_weights = [w[0] for w in weights]
    critic_weights = [w[1] for w in weights]
    avg_actor = [np.mean([a[i] for a in actor_weights], axis=0) for i in range(len(actor_weights[0]))]
    avg_critic = [np.mean([c[i] for c in critic_weights], axis=0) for i in range(len(critic_weights[0]))]
    return avg_actor, avg_critic

data = pd.read_csv("TON_IoT.csv")
label_encoder = LabelEncoder()
data['label'] = label_encoder.fit_transform(data['label'])
X = data.drop('label', axis=1).values
y = data['label'].values
sm = SMOTE(random_state=42)
X, y = sm.fit_resample(X, y)
sc = StandardScaler()
X = sc.fit_transform(X)
pca = PCA(n_components=0.95)
X = pca.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clients_X = np.array_split(X_train, 10)
clients_y = np.array_split(y_train, 10)
state_dim = X_train.shape[1]
action_dim = len(np.unique(y))
agent = A2C(state_dim, action_dim)
clients = [A2C(state_dim, action_dim) for _ in range(10)]

results = pd.DataFrame(columns=["Round", "F1-score", "Recall", "Acc (%)", "Cumulative Reward (AVG)"])

for rnd in range(10):
    weights = []
    rewards = []
    for i in range(10):
        clients[i].set_weights(*agent.get_weights())
        env = Env(clients_X[i], clients_y[i])
        state = env.reset().reshape(1, -1)
        total_reward = 0
        step = 0
        while True:
            action = clients[i].act(state)
            next_state, reward, done = env.step(action)
            next_state = next_state.reshape(1, -1)
            clients[i].train(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            step += 1
            if done:
                break
        rewards.append(total_reward / step)
        weights.append(clients[i].get_weights())
    avg_actor, avg_critic = average_weights(weights)
    agent.set_weights(avg_actor, avg_critic)
    pred = agent.actor.predict(X_test, verbose=0)
    pred_label = np.argmax(pred, axis=1)
    f1 = f1_score(y_test, pred_label, average='weighted') * 100
    recall = recall_score(y_test, pred_label, average='weighted') * 100
    acc = accuracy_score(y_test, pred_label) * 100
    results.loc[rnd] = [rnd + 1, f1, recall, acc, np.mean(rewards)]

print(results)
results.to_csv("a2c_advanced_results.csv", index=False)