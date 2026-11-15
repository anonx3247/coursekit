# CS 285: Lecture 1, Introduction. Part 1

> Course: CS 285: Deep RL, 2023 · Lesson 1 · [Watch](https://www.youtube.com/watch?v=SupFHGbytvA) · Duration 00:10:10

## TL;DR
The lecture opens with a robot grasping example. Grasping has too many special cases to engineer by hand, and supervised learning doesn't fit because nobody can reliably label good grasps. Reinforcement learning instead lets the robot collect its own trials labeled with success or failure (a reward) and learn a policy that beats its own data-collection behavior. Recent generative AI (image models, LLMs) is scaled-up density estimation, so it learns to imitate the data, meaning what humans produce. Deep RL combines ideas from classical RL (psychology) with large-scale optimization and control (evolutionary methods). It can discover new, emergent solutions, such as AlphaGo's move 37, that go beyond human behavior.

## Outline
- [00:00:01] Robotic grasping as a motivating problem
- [00:01:28] RL: learning from trials and rewards
- [00:02:55] Recent AI advances as density estimation
- [00:05:51] Historical roots of reinforcement learning
- [00:08:04] Deep RL and emergent behavior

## Key points
- Hand-engineering grasping is hard because of many special cases: rigid, awkwardly shaped (center of mass), and soft or deformable objects (pinching). Problems with many exceptions are a natural fit for machine learning. [00:00:01]
- Supervised learning needs (image, grasp location) pairs. Humans can't label these well because good grasps depend on the physical interaction between robot and world, not on human intuition. [00:01:28]
- The core RL idea is to let the robot collect its own trials and label them with outcomes (success or failure), which generalizes to a **reward function**. [00:01:28]
- An RL algorithm doesn't copy the data. It uses reward labels to work out what to do to **maximize reward**, and it can produce a policy *better than the average behavior* in the data. [00:02:12]
- Image generation models and LLMs are massively scaled-up **density estimation**: $p(x)$ or the conditional $p(y \mid x)$. [00:04:24]
- Density estimation learns the distribution in the data, so where the data comes from matters. Web images teach what people photograph and post, and text teaches what people type. This is great for generating human-like content, but it isn't everything we want from autonomous systems. [00:05:07]
- Modern RL has two lineages. The first is psychology and animal behavior (Skinner): an agent adapting to its environment in response to rewards. The second is control, optimization and evolutionary algorithms (Karl Sims, 1994), which produce behaviors humans didn't design. [00:05:51]
- Deep RL = large-scale optimization + the algorithmic foundations of classical RL. Scaling these up produces **emergent behavior**. [00:08:04]
- AlphaGo's **move 37** surprised experts because human players would not have made it. Generative AI impresses because it looks human. The best RL results impress because no person thought of them. [00:08:04]
- Flexible, human-like intelligence probably won't come from merely copying human behavior. We need algorithms that discover the *best* solution so they can respond intelligently in novel situations. [00:09:31]

## Detailed notes

### [00:00:01] Robotic grasping as a motivating problem
- Setup: a robot sees images from its camera and must output coordinates in space so that it picks up objects successfully.
- It looks easy ("localize the object and output its position"), but grasping has many special cases and exceptions:
  - **Rigid objects**: fairly straightforward; put the fingers on either side.
  - **Awkwardly shaped objects with a complex mass distribution**: grasp near the center of mass so the object doesn't fall out of the gripper.
  - **Soft or deformable objects**: different strategies entirely, e.g. pinching.
- "Anytime we have a situation that has so many special cases, exceptions and little details", machine learning becomes very appealing. One option is a general-purpose procedure, e.g. convolutional neural networks that extract grasp locations from images automatically.

### [00:01:28] RL: learning from trials and rewards
- **The problem with supervised learning**: it needs a dataset of images paired with suitable grasp locations, and even people can't determine grasp locations well. Good grasps are "a property of the physical interaction between the robot and its environment". As Levine puts it, "we don't have a lot of experience picking things up with robot fingers."
- **The RL idea**: have the robots run many trials, attempting different grasps and seeing what works. This is "in essence … the main idea behind reinforcement learning."
- The robot collects the data itself. The data doesn't need to contain *good* examples, only examples **labeled with outcomes**: image, action taken, and success or failure.
- More generally, this label is a **reward function**: the robot is rewarded for success and not for failure.
- The RL algorithm is "doing something very different from a supervised learning algorithm". Instead of copying the data, it uses reward labels to work out what to do to maximize successes or reward.
- Result: a policy that can be **better than the average behavior** the robot showed while collecting data, because it uses experience to improve on what it would typically do.

### [00:02:55] Recent AI advances as density estimation
- Recent advances mentioned:
  - Text-to-image **diffusion models**, e.g. "a vibrant portrait painting of Salvador Dalí with a half robot face".
  - **Language models** that hold conversations and tell jokes (cows going to study bovine sciences at Harvard).
  - **LLM assistants** that explain jokes and answer complex coding prompts.
  - **Biology**: generative models that design proteins binding to certain viruses.
- These advances rest on the same idea as the supervised "straw man" from the robotics example: **density estimation**.
  - Estimate $p(x)$, or conditionally $p(y \mid x)$.
  - LLMs estimate the distribution of natural-language sentences. Image models are conditional distributions over images given a prompt.
  - They are "massively scaled up versions of the kind of density estimation that we learn about in statistics class."
- **Key caveat** [00:05:07]: you learn the *distribution in the data*, so think about where the data comes from.
  - Web images with text labels teach "the kind of images that people put on the web".
  - Text teaches "what people tend to type on keyboards".
  - This is excellent if the goal is human-like content: paintings humans would draw, text humans would write. But "that's not the only thing that we want from our autonomous systems."

### [00:05:51] Historical roots of reinforcement learning
- Modern RL traces its lineage to **two disciplines**:
  1. **Reinforcement learning proper**, rooted in **psychology and animal behavior**. B. F. Skinner studied animal behavior in response to reinforcement. This line of work "forms the bedrock" of computational RL, which models an agent interacting with and adapting to its environment in response to rewards.
  2. **Controls and optimization**, including **evolutionary algorithms**. Karl Sims' 1994 virtual creatures had both form and behavior optimized by an evolutionary procedure (Sims didn't call it RL, but the principles are similar). The creatures learned to locomote, swim, run and even fight.
- The contrast with today's mainstream ML: there, the goal is to reproduce human behavior. Here the goal was to "produce behaviors that did not need to be designed by humans."
- Fast-forward a couple of decades: more sophisticated optimization and control methods let a simulated humanoid robot figure out walking and running automatically. The speaker credits this to a name the auto-subs garble, likely Yuval Tassa (context).

### [00:08:04] Deep RL and emergent behavior
- **Deep RL** = large-scale optimization + the algorithmic ideas and foundations of classical RL. Scaling classical RL with modern computation gives "very powerful emergent behaviors".
- **AlphaGo, move 37**: during the championship match, AlphaGo played a move that surprised expert observers because human players would not likely have made it. It was emergent behavior.
- **Contrast** [00:08:48]:
  - Generative AI is impressive "precisely because they look like something that a person might produce."
  - The most impressive RL results are impressive "precisely because no person had thought of it."
- Why it matters [00:09:31]: "we probably won't get the kinds of flexible intelligence that we associate with humans if we merely copy human behavior." We need algorithms that find the *best* solution to the task, not just the one a person would take, so they can respond intelligently in novel situations.
- Preview: the rest of the lecture covers the course structure and more motivation for studying deep RL today.

## Key terms
- **Reinforcement learning (RL)**: learning behavior from the agent's own experience labeled with rewards, aiming to maximize reward rather than imitate data.
- **Reward function**: a signal that scores outcomes, e.g. 1 for a successful grasp and 0 for failure.
- **Policy**: the learned mapping from observations (e.g. camera images) to actions (e.g. grasp coordinates).
- **Supervised learning**: learning from (input, correct label) pairs. Requires someone to provide correct labels.
- **Density estimation**: estimating a data distribution $p(x)$ or a conditional $p(y \mid x)$. This is the principle behind generative models.
- **Emergent behavior**: a solution found by an optimization or learning algorithm that wasn't designed or anticipated by humans (e.g. move 37).
- **Evolutionary algorithm**: optimization by mutating and selecting candidate solutions according to their performance.
- **Deep RL**: classical RL ideas combined with large-scale optimization and deep neural networks.

## Math

Density estimation, the principle behind generative models [00:04:24]:
$$\hat{p}(x) \quad\text{or}\quad \hat{p}(y \mid x)$$
- $x$ is the data (e.g. a sentence or an image), $y$ is the output conditioned on input $x$ (e.g. an image given a text prompt), and $\hat{p}$ is the model's estimate of the data distribution.

(context) Maximum-likelihood form of what such models optimize, consistent with "learning the distribution in the data" [00:05:07]:
$$\theta^\star = \arg\max_\theta \; \mathbb{E}_{(x,y)\sim \mathcal{D}} \big[\log p_\theta(y \mid x)\big]$$
- $\theta$ is the model parameters, $\mathcal{D}$ is the dataset (whatever humans put on the web), and $p_\theta$ is the model distribution. The optimum reproduces $\mathcal{D}$, not something better.

(context) The RL objective, formalized later in the course, matching "maximize the number of successes or maximize the reward" [00:02:55]:
$$\pi^\star = \arg\max_\pi \; \mathbb{E}_{s \sim p(s),\, a \sim \pi(a \mid s)} \big[r(s, a)\big]$$
- $s$ is the observation (camera image), $a$ is the action (grasp), $\pi(a \mid s)$ is the policy, and $r(s,a)$ is the reward (1 = success, 0 = failure). The optimum can beat the behavior that collected the data.

## Code examples

### 1. Copying the data vs. maximizing reward on a toy grasping bandit (context) [00:02:12]
```python
import numpy as np

rng = np.random.default_rng(0)
n_objects, n_grasps = 5, 8
# Hidden success probability of each grasp strategy on each object type
p_success = rng.uniform(0.05, 0.95, size=(n_objects, n_grasps))

# 1) The robot collects its own trials with a random exploratory policy
N = 20_000
obj = rng.integers(n_objects, size=N)
grasp = rng.integers(n_grasps, size=N)
reward = (rng.random(N) < p_success[obj, grasp]).astype(float)  # success/failure label

# 2) "Supervised" baseline: imitate the data-collection behaviour (uniform random)
copy_rate = p_success.mean()

# 3) RL-style: estimate success per (object, grasp) and act greedily on it
counts = np.zeros((n_objects, n_grasps))
wins = np.zeros_like(counts)
np.add.at(counts, (obj, grasp), 1)
np.add.at(wins, (obj, grasp), reward)
q_hat = wins / np.maximum(counts, 1)
policy = q_hat.argmax(axis=1)
rl_rate = p_success[np.arange(n_objects), policy].mean()

print(f"imitating the data:       {copy_rate:.2f}")
print(f"reward-maximising policy: {rl_rate:.2f}")
print(f"best possible:            {p_success.max(axis=1).mean():.2f}")
```
*Try:* shrink `N` to 200 and watch the greedy policy get worse as its estimates get noisy. This is the exploration problem.

### 2. Density estimation reproduces the data, not the goal (context) [00:05:07]
```python
import numpy as np

rng = np.random.default_rng(0)
# "Web data": what people tend to produce
data = rng.normal(loc=3.0, scale=0.5, size=5_000)

# Maximum-likelihood fit of a Gaussian = density estimation
mu, sigma = data.mean(), data.std()
print(f"fitted p(x): mu={mu:.2f}, sigma={sigma:.2f}")

# Suppose the task's true reward peaks at x = 6
reward = lambda x: -(x - 6.0) ** 2
model_samples = rng.normal(mu, sigma, size=1_000)
print("avg reward of generative model:", reward(model_samples).mean().round(2))
print("reward of optimal action x=6:   ", reward(6.0))
```
*Try:* add a few data points near 6. The fitted model barely moves because it matches the data's bulk, not the reward.

### 3. Evolution-style policy search (Karl Sims lineage) on CartPole (context) [00:06:34]
```python
import numpy as np
import gymnasium as gym

env = gym.make("CartPole-v1")

def fitness(w, seeds=(0, 1, 2)):
    total = 0.0
    for seed in seeds:
        obs, _ = env.reset(seed=seed)
        for _ in range(500):
            obs, r, term, trunc, _ = env.step(int(obs @ w > 0))  # linear policy
            total += r
            if term or trunc:
                break
    return total / len(seeds)

rng = np.random.default_rng(0)
best_w = rng.normal(size=4)
best = fitness(best_w)
for gen in range(50):
    population = best_w + 0.5 * rng.normal(size=(16, 4))   # mutate
    scores = [fitness(w) for w in population]               # evaluate
    i = int(np.argmax(scores))
    if scores[i] >= best:                                   # select
        best, best_w = scores[i], population[i]
    if gen % 10 == 0:
        print(f"gen {gen:2d}  best return {best:.1f}")
print("final best return:", best)
```
*Try:* change the mutation scale `0.5` or the population size `16` and see how fast the search reaches the 500 cap. No human ever specifies how to balance the pole.

## Papers & resources
- **B. F. Skinner**: behaviorist psychologist whose studies of animal behavior under reinforcement are the root of the RL lineage. [00:06:34]
- **Karl Sims (1994)**, *Evolving Virtual Creatures* (SIGGRAPH '94): evolution of both morphology and behavior of virtual creatures. [00:06:34] https://www.karlsims.com/evolved-virtual-creatures.html
- **Simulated humanoid walking and running via optimization and control**: the speaker's attribution is garbled in the auto-subs, likely Yuval Tassa et al. (context: e.g. Tassa, Erez & Todorov, 2012, "Synthesis and stabilization of complex behaviors through online trajectory optimization"). [00:07:19]
- **AlphaGo** (Silver et al., 2016, *Nature*, "Mastering the game of Go with deep neural networks and tree search"). Move 37 came in game 2 against Lee Sedol, March 2016 (context). [00:08:04]
- **Diffusion models** for text-to-image generation (context: e.g. DALL·E 2, Stable Diffusion). [00:03:40]
- **Large language models** as conversational and coding assistants. [00:03:40]
- **Generative protein design**: proteins that bind to viruses (context: e.g. RFdiffusion, Watson et al., 2023). [00:03:40]

## Review questions
1. Why is robotic grasping a poor fit for standard supervised learning?
2. What does the dataset look like in the RL version of the grasping problem, and what makes it different from a supervised dataset?
3. How can an RL policy end up better than the behavior that generated its training data?
4. What statistical principle underlies modern image generators and LLMs, and what is its key limitation?
5. Name the two intellectual lineages of modern RL and give one example of each from the lecture.
6. Why does the lecturer single out AlphaGo's move 37?
7. Why does the lecturer argue that copying human behavior isn't enough for flexible intelligence?

<details>
<summary>Answers</summary>

1. You would need (image, good grasp) pairs, and humans can't label them reliably. Good grasps depend on the physical robot–environment interaction, and people have no experience grasping with robot fingers. [00:01:28]
2. The robot collects it itself: images, the action taken, and a success/failure (reward) label. The examples don't have to be good, only labeled with their outcome. [00:02:12]
3. The algorithm doesn't imitate the data. It uses reward labels to work out which actions maximize reward, so it can keep the successful behaviors and drop the failures. [00:02:55]
4. Density estimation, $p(x)$ or $p(y \mid x)$, scaled up massively. It learns the distribution of the data, so it reproduces what humans post or type rather than discovering better solutions. [00:04:24, 00:05:07]
5. (a) Psychology and animal behavior: Skinner, reinforcement. (b) Controls, optimization and evolutionary algorithms: Karl Sims' 1994 virtual creatures, and later the optimized simulated humanoid. [00:06:34]
6. It is emergent behavior: a strong move experts found surprising because humans wouldn't have played it. RL results impress because no person thought of them, while generative AI impresses because it looks human. [00:08:04]
7. Merely copying humans caps the system at human solutions. To act intelligently in novel situations, algorithms must discover the best solution to the task. [00:09:31]
</details>
