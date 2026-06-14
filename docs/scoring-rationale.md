# Vital8 Scoring Rationale

This document extracts the scoring system currently implemented in the Vital8 prototype. It is intended as a working methods note for future analysis, validation, and white-paper writing.

## Model structure

Vital8 has two layers:

1. A foundational Life's Essential 8-style cardiovascular health score.
2. An optional Vital8 Advanced biomarker layer that applies a conceptual biological-drag adjustment using hsCRP and Lp(a).

The biomarker layer does not replace or modify the raw LE8 score. The app presents the raw LE8 score first, then displays the biomarker-adjusted estimate as a separate exploratory lens.

## Foundational LE8 score

The foundational score uses eight domains:

- Daily fuel
- Movement
- Nicotine
- Sleep rhythm
- Body size
- Cholesterol particles
- Blood sugar
- Blood pressure

Each entered domain receives a score from 0 to 100. The total score is the rounded mean of all known component scores. Missing lab or blood pressure domains are excluded from the denominator, so the app can calculate a partial score when some measurements are unavailable.

If no domains are known, no score is calculated. The user-facing app asks for at least 5 of 8 areas before presenting the score as a useful snapshot.

Formula:

```text
Raw LE8 score = round(sum(known domain scores) / count(known domain scores))
```

Total score categories:

| Score | Category |
| --- | --- |
| 80-100 | High LE8 cardiovascular health |
| 50-79 | Moderate LE8 cardiovascular health |
| 0-49 | Low LE8 cardiovascular health |
| Missing | More information needed |

Individual domain status labels:

| Domain score | App label |
| --- | --- |
| 80-100 | Strong |
| 50-79 | Opportunity |
| 0-49 | Priority |
| Missing | Not entered |

## 1. Daily fuel / diet

The diet score is an adapted consumer-facing estimate based on eight food-pattern inputs. It is not a full 24-hour dietary recall or the full AHA diet algorithm. The purpose is to approximate whether the user's usual eating pattern is heart-protective enough to support the broader LE8 framework while capturing more of the food groups emphasized by LE8-aligned dietary guidance.

The maximum raw sum is 100, so no cap is needed.

Formula:

```text
Diet score = fruit/vegetable points + whole grain points + sugary drink points + processed food points + healthy protein points + fish/seafood points + nuts/legumes points + sodium points
```

Fruit and vegetable intake, typical day:

| Response | Points |
| --- | --- |
| Less than 1 serving | 0 |
| 1-2 servings | 5 |
| 3-4 servings | 15 |
| 5+ servings | 25 |

Whole grain choice:

| Response | Points |
| --- | --- |
| Rarely or never | 0 |
| Sometimes, a few times a week | 5 |
| Most of the time | 10 |
| Almost always | 15 |

Sugary drinks, typical week:

| Response | Points |
| --- | --- |
| None | 10 |
| 1-3 | 7 |
| 4-7 | 3 |
| More than 7 | 0 |

Fast food, fried food, or heavily processed meals, typical week:

| Response | Points |
| --- | --- |
| 0-1 | 10 |
| 2-3 | 7 |
| 4-6 | 3 |
| 7+ | 0 |

Usual protein sources:

| Response | Points |
| --- | --- |
| Mostly plant-based proteins and/or fish | 15 |
| Mix of plant-based foods, fish, poultry, and some red meat | 10 |
| Mostly poultry or lean meat, limited red or processed meat | 5 |
| Mostly red or processed meat | 0 |

Fish and seafood:

| Response | Points |
| --- | --- |
| 2 or more times per week | 10 |
| About once a week | 7 |
| A few times a month | 3 |
| Rarely or never | 0 |

Nuts, seeds, beans, or lentils:

| Response | Points |
| --- | --- |
| Most days, 5+ times per week | 10 |
| A few times a week | 7 |
| About once a week | 3 |
| Rarely or never | 0 |

Salty and high-sodium foods:

| Response | Points |
| --- | --- |
| Rarely; actively limits salt | 5 |
| Sometimes | 3 |
| Often; most meals are salty or restaurant-prepared | 0 |

Implemented rationale:

- Plants, whole grains, fish/seafood, nuts, seeds, and legumes are treated as positive dietary inputs.
- Sugary drinks and ultra-processed or fast-food meals are treated as negative dietary inputs.
- Sodium exposure is included as a simplified proxy for salty food patterns and frequent restaurant or packaged-food intake.
- Usual protein source quality is included to distinguish plant/fish-forward patterns from red or processed meat-heavy patterns.
- The score is intentionally simple for consumer use and should be described as an estimated diet score, not a validated diet instrument.

## 2. Movement / physical activity

Physical activity is converted into moderate-equivalent minutes per week.

Formula:

```text
Moderate-equivalent minutes = moderate minutes + (2 * vigorous minutes)
```

Scoring:

| Moderate-equivalent minutes/week | Score |
| --- | --- |
| 0 | 0 |
| 1-29 | 20 |
| 30-59 | 40 |
| 60-89 | 60 |
| 90-149 | 80 |
| 150+ | 100 |

Implemented rationale:

- Vigorous activity receives double credit.
- The top score begins at 150 moderate-equivalent minutes per week, aligning with common public-health physical activity targets.
- The app frames movement as beneficial for blood pressure, insulin sensitivity, sleep, mood, and long-term cardiovascular health.

## 3. Nicotine

Nicotine scoring is based on four dimensions: current combustible tobacco use, current non-combustible nicotine or smokeless tobacco use, former regular use and time since quitting, and regular secondhand smoke or vapor exposure.

Base score:

| Status | Base score |
| --- | --- |
| Never or no regular nicotine/tobacco use | 100 |
| Quit less than 1 year ago | 50 |
| Quit 1-2 years ago | 60 |
| Quit 3-4 years ago | 70 |
| Quit 5-9 years ago | 80 |
| Quit 10 or more years ago | 90 |
| Current e-cigarettes, vapes, nicotine pouches, or smokeless tobacco only | 20 |
| Current combustible tobacco | 0 |
| Current combustible tobacco plus another nicotine product | 0 |

Secondhand exposure adjustment:

| Exposure | Adjustment |
| --- | --- |
| No regular secondhand exposure | No change |
| Regular exposure to tobacco smoke or e-cigarette vapor | Subtract 5 points, floor of 0 |

Formula:

```text
Nicotine score = max(0, base score - 5) if regular secondhand exposure is reported
Nicotine score = base score if no regular secondhand exposure is reported
```

Implemented rationale:

- Current combustible tobacco receives the lowest score.
- Current non-combustible nicotine or smokeless tobacco exposure is still heavily penalized.
- Former use is scored progressively higher with longer time since quitting, reflecting declining risk after cessation.
- Secondhand smoke or vapor exposure is captured as a simplified penalty.
- The app treats avoiding nicotine and secondhand exposure as one of the highest-impact cardiovascular choices.

## 4. Sleep rhythm

Sleep scoring is based on usual nightly sleep duration.

| Usual sleep duration | Score |
| --- | --- |
| 7 to <9 hours | 100 |
| 6 to <7 hours or 9 to <10 hours | 70 |
| 5 to <6 hours or >=10 hours | 40 |
| <5 hours | 20 |

Implemented rationale:

- The optimal range is 7 to under 9 hours.
- Both short and long sleep are penalized, with more severe penalties at the extremes.
- The app explains sleep as connected to blood pressure, hunger signaling, glucose control, and stress physiology.

## 5. Body size

Body size is estimated using BMI.

Formula:

```text
BMI = round((weight_lbs / height_inches^2) * 703, 1)
```

Scoring:

| BMI | Score |
| --- | --- |
| <18.5 | 70 |
| 18.5 to <25 | 100 |
| 25 to <30 | 70 |
| 30 to <35 | 30 |
| 35 to <40 | 15 |
| >=40 | 0 |

Implemented rationale:

- BMI is used as an accessible screening signal, not as a complete measure of health.
- The app explicitly notes that BMI does not measure muscle, body composition, or overall health by itself.
- Higher BMI categories are penalized because body size can influence blood pressure, glucose, cholesterol, sleep apnea risk, and inflammation.

## 6. Cholesterol particles

The cholesterol domain uses non-HDL cholesterol.

Formula:

```text
Non-HDL cholesterol = max(0, total cholesterol - HDL cholesterol)
```

Scoring:

| Non-HDL cholesterol | Score |
| --- | --- |
| <130 mg/dL | 100 |
| 130 to <160 mg/dL | 60 |
| 160 to <190 mg/dL | 40 |
| 190 to <220 mg/dL | 20 |
| >=220 mg/dL | 0 |

Implemented rationale:

- Non-HDL cholesterol is used because it captures cholesterol carried by plaque-forming particles.
- The app uses total cholesterol minus HDL because those values are commonly available on standard lipid panels.

## 7. Blood sugar

The blood sugar domain accepts either hemoglobin A1c or fasting glucose. The scoring differs depending on whether the user reports known diabetes.

### If using A1c and no diabetes

| A1c | Score |
| --- | --- |
| <5.7% | 100 |
| 5.7 to <6.5% | 60 |
| >=6.5% | 40 |

### If using A1c and diabetes

| A1c | Score |
| --- | --- |
| <7.0% | 40 |
| 7.0 to <8.0% | 30 |
| 8.0 to <9.0% | 20 |
| >=9.0% | 10 |

### If using fasting glucose and no diabetes

| Fasting glucose | Score |
| --- | --- |
| <100 mg/dL | 100 |
| 100 to <126 mg/dL | 60 |
| >=126 mg/dL | 40 |

### If using fasting glucose and diabetes

| Fasting glucose | Score |
| --- | --- |
| <130 mg/dL | 40 |
| 130 to <160 mg/dL | 30 |
| 160 to <200 mg/dL | 20 |
| >=200 mg/dL | 10 |

Implemented rationale:

- A1c is framed as a marker of average blood sugar over approximately three months.
- Fasting glucose is framed as an overnight-fasting measurement.
- Diabetes status changes the scoring ceiling, reflecting that established diabetes carries residual cardiometabolic risk even when glycemia is well controlled.

## 8. Blood pressure

Blood pressure scoring is based on systolic and diastolic pressure, with an additional penalty if the user reports taking blood pressure medication.

Untreated scoring:

| Blood pressure | Untreated score |
| --- | --- |
| SBP <120 and DBP <80 | 100 |
| SBP 120 to <130 and DBP <80 | 75 |
| SBP 130 to <140 or DBP 80 to <90 | 50 |
| SBP 140 to <160 or DBP 90 to <100 | 25 |
| SBP >=160 or DBP >=100 | 0 |

Medication adjustment:

```text
Final BP score = max(0, untreated score - 20) if treated
Final BP score = untreated score if untreated
```

Implemented rationale:

- Blood pressure is treated as common, often silent, measurable at home, and highly modifiable.
- The medication penalty reflects that treated blood pressure implies underlying hypertension burden even if the measured value is controlled.

## Vital8 Advanced biomarker layer

The Vital8 Advanced layer is intentionally separate from the standard LE8 score. The code describes it as a conceptual translation of published risk gradients into an exploratory score modifier. It is not a validated clinical calculator.

The biomarker layer uses two optional inputs:

- hsCRP in mg/L, representing inflammatory burden.
- Lp(a) in nmol/L, representing largely inherited lipid risk.

Each biomarker is converted into a multiplier. If both are entered, the multipliers are multiplied together.

Formula:

```text
Combined biomarker multiplier = hsCRP multiplier * Lp(a) multiplier
Adjusted estimate = round(raw LE8 score / combined biomarker multiplier)
Biomarker penalty percent = round((1 - (1 / combined biomarker multiplier)) * 100)
```

If only one biomarker is entered, the combined multiplier is that biomarker's multiplier. If neither biomarker is entered, no adjusted estimate is calculated.

## hsCRP biological-drag multiplier

| hsCRP | Category | Multiplier |
| --- | --- | --- |
| Not entered | Not entered | None |
| <1 mg/L | Low inflammation | 1.00 |
| 1 to <2 mg/L | Mild inflammation | 1.12 |
| 2 to <3 mg/L | Moderate inflammation | 1.18 |
| 3 to <5 mg/L | High inflammation | 1.30 |
| 5 to <=10 mg/L | Very high inflammation | 1.45 |
| >10 mg/L | Extreme if persistent | 1.75 |

Implemented rationale:

- hsCRP is treated as a cross-sectional inflammatory signal.
- Lower hsCRP is favorable, but low hsCRP does not prove absence of inflammation.
- Mild to high elevations are interpreted as possible biological drag, particularly if persistent.
- hsCRP is framed as partly modifiable through sleep, activity, weight, nicotine exposure, oral health, diet quality, and inflammatory disease context.
- Values above 10 mg/L are flagged as potentially reflecting acute infection, injury, or inflammatory disease and needing clinical interpretation or repeat testing.

## Lp(a) biological-drag multiplier

| Lp(a) | Category | Multiplier |
| --- | --- | --- |
| Not entered | Not entered | None |
| <75 nmol/L | Lower Lp(a) | 1.00 |
| 75 to <125 nmol/L | Mildly elevated Lp(a) | 1.20 |
| 125 to <250 nmol/L | Elevated Lp(a) | 1.40 |
| 250 to <350 nmol/L | High Lp(a) | 2.00 |
| 350 to <430 nmol/L | Very high Lp(a) | 3.00 |
| >=430 nmol/L | Extreme Lp(a) | 4.00 |

Implemented rationale:

- Lp(a) is treated as a largely genetic, inherited lipid-risk signal.
- Because Lp(a) is not very responsive to lifestyle, the practical response is tighter control of modifiable risk factors around it.
- Those surrounding targets include LDL-C, non-HDL cholesterol, ApoB, blood pressure, glucose, nicotine exposure, and maintaining a high LE8 foundation.

## Advanced adjusted categories

The adjusted estimate is categorized using the same 80 and 50 thresholds, but the label changes to biological drag:

| Adjusted estimate | Category |
| --- | --- |
| 80-100 | Low biological drag |
| 50-79 | Moderate biological drag |
| 0-49 | High biological drag |
| Missing | Advanced layer not calculated |

Interpretation:

- Low biological drag: entered biomarkers do not substantially change the LE8 story.
- Moderate biological drag: the same LE8 score may require tighter control of LDL/non-HDL/ApoB, blood pressure, glucose, sleep, activity, and nicotine exposure.
- High biological drag: the standard LE8 score may understate risk; the response is precision and aggressive management of modifiable risk factors, not panic.

## Target raw LE8 calculation

The app estimates what raw LE8 score would be required to reach adjusted targets of 65 or 80.

Formula:

```text
Required raw LE8 = round(target adjusted score * combined biomarker multiplier)
```

If the required raw LE8 is above 100, the app states that the target is not achievable by LE8 alone. In that situation, the message is to pair excellent LE8 habits with clinician-guided lipid and risk-factor management.

## Important methodological caveats

- The foundational score is an LE8-style educational implementation, not a certified clinical calculator.
- The diet score is an adapted consumer-facing dietary pattern estimate that now captures more LE8-aligned dietary features than the original five-question prototype.
- The biomarker layer is explicitly conceptual and exploratory.
- The adjusted biomarker score is cross-sectional and should not be used to diagnose, treat, or replace clinician-guided risk assessment.
- hsCRP can be transiently elevated by acute illness, injury, inflammatory conditions, and other context.
- Lp(a) is mostly genetic; the intervention logic is currently focused on lowering surrounding modifiable risk.
