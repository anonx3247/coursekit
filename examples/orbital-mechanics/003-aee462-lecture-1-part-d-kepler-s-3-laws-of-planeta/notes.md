# AEE462 Lecture 1, Part D - Kepler's 3 Laws of Planetary motion and Newton's Universal Gravitation

> Course: A Course on Orbital Mechanics and Spacecraft Dynamics · Lesson 3 · [Watch](https://www.youtube.com/watch?v=OU02qX0FcNc) · Duration 00:52:00

## TL;DR
This lesson finishes the course's historical introduction. It states Kepler's three laws of planetary motion: elliptical orbits, equal areas swept in equal times, and period squared proportional to the semi-major axis cubed. It then argues that Newton was hugely influential because he introduced differential-equation models of dynamics (his three laws and universal gravitation) and a new idea of what counts as a "solution": an iterative algorithm, Newton's method, which he developed for Kepler's equation. The lesson ends with the single model the course studies: Newton's second law combined with inverse-square gravitation, from which all of Kepler's laws can be derived.

## Outline
- [00:00:02] Lesson roadmap {skip: short overview of the part}
- [00:00:45] Kepler's first law: elliptical orbits
- [00:04:39] Second law: equal areas, equal times
- [00:09:04] Third law: period and semi-major axis
- [00:11:59] Kepler's legacy and reception
- [00:15:40] Newton and differential-equation modeling
- [00:20:07] Newton anecdotes and the Principia {skip: biographical digression}
- [00:29:39] Newton's three laws of motion
- [00:33:59] Law of universal gravitation
- [00:38:23] Newton's other contributions: optics, calculus, series
- [00:42:39] Newton's method: algorithms as solutions
- [00:47:02] Kepler's equation and two millennia of technology
- [00:49:55] The course model: Newtonian gravitation
- [00:51:22] Preview of Lecture 2 {skip: preview of next lecture}

## Key points
- **Kepler I:** planets move on ellipses. One focus is occupied (by the Sun; see the note in Detailed notes) and the other focus is vacant. This is a small step from Ptolemy's vacant equant plus eccentric. [00:00:45]
- **Ellipse basics:** the sum of distances from the two foci is constant. Key quantities are the semi-major axis $a$, the semi-minor axis $b$ and the eccentricity $0 \le e < 1$. The center-to-focus distance is $ae$. [00:01:31]
- **Kepler II:** the line from the focus to the planet sweeps equal areas in equal times. Speed is not constant, but the areal rate $\dot A$ is. This law gives predictive power, and the speaker calls it the most important. [00:05:24]
- Kepler made predictions (the Rudolphine Tables) by adding small triangles of area step by step. The speaker calls this "almost a differential equation". [00:06:52]
- **Kepler III:** $T^2 \propto a^3$. It follows from II, because over one period the whole ellipse area is swept. Elegant and universal, but of little use before artificial satellites. [00:09:04]
- Newton's key contribution was modeling dynamics quantitatively with differential equations. Today's technology rests on this. [00:17:56]
- **Newton's laws:** (1) inertia; (2) $F = m\ddot{r}$, "the universal model which governs all motion"; (3) equal and opposite, collinear action and reaction. [00:30:24]
- **Universal gravitation:** force is proportional to the product of the masses and inversely proportional to the square of the distance. Inertial mass equals gravitational mass, which is "still shocking". The inverse square could be checked from planetary periods and distances. The individual masses could not be measured at the time. [00:34:44]
- Once you have gravitation plus $F = ma$, Kepler's laws can be derived. This is everything needed for the first half of the course. [00:37:40]
- Newton redefined "solution" as a sequence of computations that converges to the answer, which is the idea of an algorithm. Newton's method is still used for optimization. [00:44:51]
- Newton developed his method to solve Kepler's (transcendental) equation, which predicts position as a function of time. The course will use it for the same purpose. [00:47:02]
- **Course model:** $\ddot{\mathbf r}_i$ is set by $G$ times the masses, acting along the line between the bodies. The course stops there: no relativity, black holes or dark matter. [00:49:55]

## Detailed notes

### [00:00:02] Lesson roadmap
- Part D concludes Lecture 1. It introduces Kepler's three laws, then Newton, who used them to arrive at the law of universal gravitation.

### [00:00:45] Kepler's first law: elliptical orbits
- These laws are used "throughout the entire first half of this course".
- **First law:** "the planets move in elliptic orbits". The ellipse was well understood geometrically since the ancient Greeks.
- String construction: pin a string at the two foci, pull it taut and trace the curve. The defining property is that the sum of the distances from the two foci to any point on the ellipse is constant ($a_1 + a_2$).
- Key quantities:
  - semi-major axis $a$, "which we'll be talking about in great depth";
  - semi-minor axis $b$;
  - eccentricity, "a number between 0 and 1".
- There are no epicycles: the motion is purely elliptical.
- One focus is occupied and the other focus is vacant.
  - **Note:** in the transcript the speaker says the occupied focus is "the planet itself". The correct statement is that the Sun sits at the occupied focus and the planet moves along the ellipse.
- **Comparison with Ptolemy:** Ptolemy's model had an eccentric (the center), the Earth offset to one side, and a vacant equant on the other side. Turning the equant into a vacant focus and setting the offset to $ae$ is "not that huge a leap".
- The law is "buried" in Kepler's treatise "among all the mystical rantings". It is observation-based: with careful Copernican-frame data, the elliptic motion is "fairly obvious".

### [00:04:39] Second law: equal areas, equal times
- The second law is what gave Kepler **predictive power**: where the planet will be as a function of time.
- The difficulty is that planetary speeds are not constant. They speed up and slow down, and there is no easy formula for velocity as a function of time.
- Kepler's "real genius" was to find the quantity that *is* constant: the **rate at which area is swept** from the focus to the planet. Planets sweep equal areas in equal times.
- The speaker considers this "probably the most important" law. Ellipses were not a huge stretch from the data, but the constant areal rate was "particularly shocking".
- **Prediction procedure:** a known time interval corresponds to a known swept area. Add small triangles of area one by one and locate the planet after each step. Repeat as a function of date.
  - Smaller triangles give more accurate predictions. This is "almost a differential equation", although differential equations did not exist yet.
  - Kepler used this to build the **Rudolphine Tables**. The speaker guesses he used steps of about one day and kept going for about 20 years.
- The catch: the area swept from position 1 to position 2 as a function of position is "quite complicated". The course will spend a lot of time on it.

### [00:09:04] Third law: period and semi-major axis
- The third law is an "easy to calculate corollary" of the second.
- The area of the whole ellipse is easy to compute from $a$ and $e$. Because $\dot A$ is constant, one full revolution (2π, or 360°) sweeps the full area.
- Result: the square of the period is proportional to the cube of the semi-major axis. In the speaker's words, the proportionality constant "depends on the planet" (see Equations for the modern view).
- All three laws will be derived "in the next lecture or two".
- The speaker says the law was "not particularly" useful at the time, because all planetary periods were already known and there were no satellites. It matters now that we have satellites. It is still "a very clean, very elegant statement of a universal law", and Kepler was very fond of it.

### [00:11:59] Kepler's legacy and reception
- Laws I and II were experimentally derived. Law III comes out of them.
- Kepler had an intuitive notion of force, including a central-force hypothesis and inertia, but did not quantify it. Speeding up and slowing down fits a central force.
- "He got almost everything right." His is the first model that is fundamentally based on physics. Tycho, by contrast, had "no idea of forces". Kepler also had the correct model of tides.
- The course uses Kepler more than Newton directly.
- Reception: the Rudolphine predictions were used, but the claim that elliptic motion is physically what happens was "really not believed until the time of Newton". The Tychonic system was still widely treated as true until Newton.

### [00:15:40] Newton and differential-equation modeling
- The speaker admires Newton and calls him "probably the most influential person in history" because of his influence on society and technology. (Aside: the squint in period portraits.)
- **Calculus:** Newton invented differential and integral calculus. He kept it to himself, then disputed priority with Leibniz. The speaker notes Gauss had the same problem.
- The speaker traces a progression in how nature was described mathematically:
  - Galileo: nature is mathematics, but "triangles and circles";
  - Kepler: ellipses;
  - Newton: **differential equations, dynamics**.
- Before Newton, ideas of force and acceleration were qualitative. Galileo had phenomenological models but no quantitative predictive models. Newton gave quantitative predictive models of dynamics: forces that you integrate to get velocities and positions, plus inertia and gravity.
- This modeling technology "is now behind all of our technology: controls, dynamics, everything". Newton's method is also still used in optimization.

### [00:20:07] Newton anecdotes and the Principia
- **Priority dispute with Leibniz:** never fully resolved.
- **Enlightenment hero:** a single equation governing all planetary motion inspired the search for basic laws of economics and government (e.g. John Locke).
  - Alexander Pope's epitaph: "Nature and Nature's laws lay hid in night; God said, *Let Newton be!* and all was light." (Transcribed loosely in the video.)
- Generally considered modest: "If I have seen further it is by standing on the shoulders of giants." The giants are perhaps Kepler and Galileo, "not sure he would credit Tycho".
- **Poor teacher:** he held a distinguished chair at Cambridge. His assistant reported that when no students came, he "lectured to the walls".
- ***Philosophiæ Naturalis Principia Mathematica*:** written in Latin. It sets out his laws but avoids calculus notation and uses very small triangles and limits instead. The speaker calls it correct but "impossible to read" and says Leibniz's notation was better.
- Personal anecdotes:
  - on his deathbed he named lifelong celibacy as his greatest accomplishment;
  - in 1693 he had a breakdown and accused people, including John Locke, of sending women to seduce him;
  - he had unorthodox religious views, was considered a heretic, and in later life became a biblical scholar;
  - as Warden of the Royal Mint he went undercover in taverns. 28 coiners and forgers were convicted, and forgery was high treason.

### [00:29:39] Newton's three laws of motion
- The speaker considers differential-equation modeling probably Newton's most important accomplishment: "we wouldn't have airplanes without differential equations". Forces and accelerations were not new ideas, but modeling them was.
- **First law (inertia):** "every body continues in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impressed upon it". The modern statement has barely changed. It makes Galileo's ideas concrete and applies them to everything, planets included.
- **Second law:** a body of mass $m$ subject to force $F$ accelerates according to $F = ma$, with $a$ the second derivative of position. "The big one", the universal model of motion that the Enlightenment took up.
- **Third law:** mutual forces of action and reaction are equal, opposite and collinear. "To every action there is always opposed an equal reaction." If the Sun pulls on the Earth, the Earth pulls on the Sun, and likewise for the Earth and Moon. This builds on Kepler's tide idea.
- The first and third laws crystallize earlier ideas. The second is the most novel.

### [00:33:59] Law of universal gravitation
- Apple-and-Moon story: the same force makes the apple fall and the Moon "fall" around the Earth. Whether it happened is unclear, but it states the idea. Everything exerts a force on everything else.
- **Refinement 1: proportional to mass.** It is the same mass as in $F = ma$. "That is still shocking; we still don't know why." Einstein's curved spacetime offers an explanation, but the equality of inertial and gravitational mass remains surprising.
  - Newton could not verify this, because no planetary mass was known. It was "somewhat inspired, maybe even a guess".
- **Refinement 2: inverse-square law.** The force is proportional to $1/d^2$ (the transcript says "proportional to the square of the distance", meaning inversely). This can be verified: from planet distances and periods, the force needed for the centripetal acceleration falls off as $1/r^2$.
- Because the masses were unknown, the numerator can be replaced by an unknown constant $\alpha$ for each planet. Kepler's three laws can still be derived; this will be done in a later lecture.
- With gravitation and $F = ma$, "we don't even need Kepler". All the modeling technology for the first half of the course is now in place.

### [00:38:23] Newton's other contributions: optics, calculus, series
- The speaker frames orbital mechanics as about 2,000 years of mathematical technology, from 600 BC to Newton's *Principia*.
  - The speaker says "1780 or 1750"; the *Principia* was actually published in 1687 (context).
- **Reflecting telescope:** Galileo's telescope was a refracting tube with lenses. Newton's design reflects light to a focal point and out through an eyepiece. The speaker's own Dobsonian reflector uses essentially the same design.
- **Optics and color:** theory of color, prisms, rainbows. The speaker attributes a wave view of color to Newton.
  - Newton actually favored a corpuscular theory of light (context).
- **Sound:** a wave model of sound.
- **Calculus:** "how can you come up with $F = ma$ without differential and integral calculus".
- **Infinite sequences and series:** the binomial theorem (generalized) and the concept of convergence.

### [00:42:39] Newton's method: algorithms as solutions
- The problem: nonlinear equations such as $x^5 + x^3 + 3x + 1 = 0$ generally have no closed-form solution. A quadratic has a formula; higher-order or transcendental equations generally do not.
- "Part of technology is changing the definition of solution":
  - ancient tables;
  - Greek circles and epicycles;
  - Kepler's ellipses;
  - Newton's differential equations;
  - finally, **a sequence of calculations converging to $x$**.
- This is what an algorithm or numerical computation is, as in simulating PDEs: you never reach the exact solution, but you can get arbitrarily close.
- The speaker argues this new notion of solution is perhaps more profound than the dynamics, and "as consequential" now that "computation is everything".
- Variants of Newton's method still power optimization: compute a derivative, follow it a bit, repeat until reaching the minimum or maximum.

### [00:47:02] Kepler's equation and two millennia of technology
- Newton built the method to solve **Kepler's equation**, which converts time into position along the orbit (predict $r_2$ from $r_1$). It will be covered later.
- Kepler propagated the orbit step by step. Newton wanted positions "hundreds of years in the future" without the intermediate steps. That leads to a transcendental equation with no analytic solution.
- Newton's method converges very fast. "There hasn't been much improvement on it", and the course will use it on this same equation.
- Thesis: much of today's technology was developed to predict the motion of planets and satellites. This continues with Einstein and Mercury's orbit.
  - The speaker says "special relativity", then corrects to general relativity. Mercury's perihelion precession is a classic test of general relativity (context).

### [00:49:55] The course model: Newtonian gravitation
- Universal gravitation plus the second law gives the course's model in vector form. The acceleration of body $i$ is set by $G$ times the masses and points along the vector between the bodies.
- The model took "two thousand years" of effort and technology to develop.
- Scope:
  - the course studies orbital mechanics, a part of celestial mechanics;
  - it covers no black holes, Big Bang, dark matter or relativistic mechanics: "we're sticking to orbits".

### [00:51:22] Preview of Lecture 2
- Lecture 2 extends the model using momentum and invariants: geometric invariants of elliptic orbits, the orbital elements, and a derivation of Kepler's first law.

## Key terms
- **Ellipse** — the set of points whose distances to two foci sum to a constant ($2a$).
- **Focus (foci)** — the two defining points of an ellipse. In planetary orbits the Sun is at one focus and the other is vacant.
- **Semi-major axis ($a$)** — half the longest diameter of the ellipse. It sets the orbit size and the period.
- **Semi-minor axis ($b$)** — half the shortest diameter.
- **Eccentricity ($e$)** — shape parameter, $0 \le e < 1$ for ellipses. The center-to-focus distance is $ae$.
- **Areal velocity ($\dot A$)** — the rate at which the focus–planet line sweeps area. Constant according to Kepler II.
- **Period ($T$)** — time for one complete orbit.
- **Equant / eccentric** — Ptolemaic constructs. The vacant equant foreshadows the vacant focus.
- **Rudolphine Tables** — Kepler's planetary position tables, computed with the area-sweep method.
- **Inertia** — the tendency of a body to keep its state of rest or uniform straight-line motion (Newton I).
- **Inertial vs gravitational mass** — the $m$ in $F = ma$ and the $m$ in gravitation. They are empirically equal.
- **Inverse-square law** — gravitational force $\propto 1/r^2$.
- **Kepler's equation** — the transcendental equation linking time to position on an orbit.
- **Newton's method** — an iterative root-finding algorithm $x_{k+1} = x_k - f(x_k)/f'(x_k)$.
- **Algorithm** — a sequence of computations whose limit is the solution.
- **Principia** — *Philosophiæ Naturalis Principia Mathematica*, Newton's main work on motion and gravitation.

## Equations

**Ellipse focal property** [00:01:31]
$$r_1 + r_2 = 2a$$
- $r_1, r_2$ are the distances from a point on the ellipse to the two foci.

**Ellipse relations** [00:02:23] (standard forms, context)
$$b = a\sqrt{1-e^2}, \qquad c = ae, \qquad A_{\text{ellipse}} = \pi a b = \pi a^2\sqrt{1-e^2}$$
- $c$ is the distance from the center to a focus (the speaker's "$ae$").

**Kepler's second law** [00:05:24]
$$\frac{dA}{dt} = \text{const} \;\left(= \tfrac{h}{2},\ h = |\mathbf r \times \dot{\mathbf r}| \text{ in modern notation (context)}\right)$$

**Kepler's third law** [00:09:49]
$$T^2 \propto a^3 \qquad\text{Newtonian form (context): } T = 2\pi\sqrt{\frac{a^3}{\mu}},\ \ \mu = G(M+m) \approx GM_\odot$$
- $T$ in s, $a$ in m, $\mu$ in m³/s².
- The speaker says the constant "depends on the planet". In the Newtonian form it depends on the masses through $\mu$, so it is nearly the same for all planets of the Sun (context).

**Newton's second law** [00:31:51]
$$\mathbf F = m\,\ddot{\mathbf r}$$

**Newton's third law** [00:32:33]
$$\mathbf F_{12} = -\mathbf F_{21}, \text{ collinear}$$

**Universal gravitation** [00:34:44]
$$F = \frac{G m_1 m_2}{r^2}$$
- $G \approx 6.674\times10^{-11}$ N·m²/kg² (context; not measurable in Newton's time).
- In the lesson, the unknown numerator can be lumped into a per-planet constant $\alpha$: $F = \alpha/r^2$ [00:37:40].

**Course model (n-body form)** [00:49:55]
$$m_i\,\ddot{\mathbf r}_i = \sum_{j\neq i} \frac{G\, m_i m_j}{\|\mathbf r_j - \mathbf r_i\|^3}\,(\mathbf r_j - \mathbf r_i)$$
- The force on body $i$ points along the vector toward body $j$.
- Assumptions: point masses, Newtonian (non-relativistic) mechanics.

**Newton's method** [00:44:51] (explicit iteration, context)
$$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}$$

**Kepler's equation** [00:47:02] (mentioned, formula given later in the course; context)
$$M = E - e\sin E, \qquad M = \sqrt{\mu/a^3}\,(t - t_p)$$
- $M$ is the mean anomaly, $E$ the eccentric anomaly, $t_p$ the time of periapsis passage.

## Derivations

**Kepler III from Kepler II** [00:09:04–00:10:33]
1. Kepler II: $\dot A = \text{const} \equiv C$.
2. Over one full period $T$ (2π of travel), the swept area is the whole ellipse: $C\,T = \pi a b = \pi a^2\sqrt{1-e^2}$.
3. Therefore $T = \pi a^2\sqrt{1-e^2}/C$.
4. Context: Kepler found the link to $a^3$ empirically. Newtonian dynamics gives $C = \tfrac12\sqrt{\mu a(1-e^2)}$, so $T = 2\pi\sqrt{a^3/\mu}$ and $T^2 \propto a^3$. The full derivation is in upcoming lectures.

**Checking the inverse-square law from observations** [00:36:13–00:37:40] (circular approximation)
1. Centripetal acceleration on a circular orbit: $a_c = v^2/r = 4\pi^2 r/T^2$.
2. By Kepler III, $T^2 = k\,r^3$, so $a_c = 4\pi^2/(k r^2) \propto 1/r^2$.
3. With $F = ma$, the required force falls off as $1/r^2$. This can be verified from planetary distances and periods alone, without knowing any mass.

**Kepler's prediction method (discrete area integration)** [00:06:52–00:07:36]
1. Choose a time step $\Delta t$. The swept area per step is $\Delta A = C\,\Delta t$.
2. From the current position, add a thin triangle (focus, current point, next point) whose area is $\Delta A$, and solve for the next point.
3. Repeat. Smaller triangles give higher accuracy. This is effectively forward integration of an ODE before ODEs existed.

## Worked example
(context) This example applies Kepler III in Newtonian form, plus Newton's method on Kepler's equation, to real orbits.

```python
import numpy as np
from scipy.optimize import newton

MU_SUN = 1.32712440018e20  # m^3/s^2, heliocentric gravitational parameter
AU = 1.495978707e11        # m
DAY = 86400.0

# Kepler III: T = 2*pi*sqrt(a^3/mu)
planets = {"Earth": (1.000, 0.0167), "Mars": (1.524, 0.0934), "Jupiter": (5.203, 0.0484)}
for name, (a_au, e) in planets.items():
    a = a_au * AU
    T = 2 * np.pi * np.sqrt(a**3 / MU_SUN)
    print(f"{name:8s} a={a_au:.3f} AU  T={T/DAY:8.1f} days  T^2/a^3={((T/DAY/365.25)**2)/a_au**3:.4f} yr^2/AU^3")

# Kepler II/equation: where is Mars 200 days after perihelion?
a_au, e = planets["Mars"]
a = a_au * AU
n = np.sqrt(MU_SUN / a**3)       # mean motion, rad/s
M = n * 200 * DAY                # mean anomaly
f  = lambda E: E - e*np.sin(E) - M
fp = lambda E: 1 - e*np.cos(E)
E = newton(f, M, fprime=fp)      # Newton's method, as Newton intended
nu = 2*np.arctan2(np.sqrt(1+e)*np.sin(E/2), np.sqrt(1-e)*np.cos(E/2))
r = a*(1 - e*np.cos(E))
print(f"Mars after 200 d: M={np.degrees(M):.2f} deg, E={np.degrees(E):.2f} deg, "
      f"true anomaly={np.degrees(nu):.2f} deg, r={r/AU:.4f} AU")
```

Expected output, approximately:
- Earth: 365.3 days. Mars: 687 days. Jupiter: 4,335 days.
- $T^2/a^3 \approx 1.000$ yr²/AU³ for all three, which is Kepler III.
- For Mars, Newton's method converges in a few iterations. The true anomaly is about 113°.

## Historical notes & resources
- **Johannes Kepler:** three laws of planetary motion; *Rudolphine Tables*, computed by stepwise area sweep over about 20 years [00:07:36]; intuitive central force and correct tide theory.
- **Ptolemy:** eccentric and equant model, the precursor to the vacant focus [00:03:07].
- **Tycho Brahe:** the Tychonic system was still widely treated as true until Newton [00:14:57].
- **Galileo:** inertia ideas, Galilean relativity, refracting telescope [00:14:12, 00:39:51].
- **Ancient Greeks:** geometry of the ellipse, including the string construction [00:00:45].
- **Isaac Newton:**
  - calculus; laws of motion; universal gravitation;
  - the *Principia* (Latin, written in terms of triangles and limits);
  - reflecting telescope; optics and color; series and the binomial theorem; Newton's method;
  - Lucasian chair at Cambridge (context: the speaker says "a distinguished chair");
  - Warden of the Royal Mint.
- **Gottfried Leibniz:** co-inventor of calculus, priority dispute, better notation [00:17:08, 00:26:00].
- **Gauss:** also slow to publish, similar priority problems [00:17:08].
- **Alexander Pope:** epitaph on Newton [00:22:20].
- **John Locke:** Enlightenment philosopher influenced by Newtonian first principles; target of Newton's 1693 accusations [00:21:36, 00:27:29].
- **Einstein:** spacetime curvature explains the equality of inertial and gravitational mass; Mercury's orbit as a test of relativity [00:35:29, 00:49:13].
- **Date correction (context):** the speaker gives "1780 or 1750" for the *Principia*; it was published in 1687.

## Review questions
1. What are Kepler's three laws, and which one gave predictive power?
2. Where are the Sun and the vacant focus in Kepler's first law, and how does this relate to Ptolemy's equant?
3. How did Kepler predict planetary positions with the second law before calculus existed?
4. Why is the third law a corollary of the second, and why was it of little practical use in Kepler's time?
5. Which part of universal gravitation could Newton verify from observations, and which part was "somewhat a guess"?
6. What is surprising about the mass in Newton's law of gravitation?
7. In what sense did Newton change the definition of a "solution", and what problem motivated it?
8. Write the course's governing model in vector form.

<details>
<summary>Answers</summary>

1. (I) Orbits are ellipses with the Sun at one focus. (II) Equal areas are swept in equal times. (III) $T^2 \propto a^3$. The second law gave predictive power because it gives position as a function of time [00:04:39].
2. The Sun occupies one focus and the other is empty. The vacant equant is like the vacant focus, and the offset of the eccentric is like the $ae$ offset [00:03:07].
3. He added small triangles of equal area for each time step, which effectively integrated numerically. Smaller steps gave more accuracy [00:06:52].
4. Over one period the whole ellipse area $\pi ab$ is swept at a constant rate, which ties $T$ to the orbit size. All planetary periods were already known and there were no satellites [00:09:04, 00:11:16].
5. The inverse-square law could be verified from planetary distances and periods. The proportionality to mass could not, because no planetary masses were known [00:36:13].
6. It is the same inertial mass that appears in $F = ma$, and why the two are equal is still not fully explained [00:34:44].
7. He accepted a convergent sequence of computations (an algorithm, Newton's method) instead of a closed-form expression. The motivating problem was the transcendental Kepler's equation for position as a function of time [00:44:51, 00:47:02].
8. $m_i\ddot{\mathbf r}_i = \sum_j G m_i m_j (\mathbf r_j - \mathbf r_i)/\|\mathbf r_j - \mathbf r_i\|^3$ [00:49:55].

</details>
