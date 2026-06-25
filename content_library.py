"""Approved short educational snippets for Vital8 AI grounding."""

from __future__ import annotations


LE8_DOMAIN_EXPLANATIONS = {
    "Daily fuel": "Eating pattern affects cholesterol, blood pressure, blood sugar, weight, and inflammation.",
    "Movement": "Regular activity supports blood pressure, insulin sensitivity, sleep, mood, and long-term heart health.",
    "Nicotine": "Avoiding nicotine and secondhand smoke exposure protects blood vessels and lowers cardiovascular risk.",
    "Sleep rhythm": "Usual sleep duration is connected with blood pressure, glucose control, appetite, and recovery.",
    "Body size": "BMI is one screening signal. It does not measure muscle, body composition, or overall health by itself.",
    "Cholesterol particles": "Non-HDL cholesterol estimates cholesterol carried by plaque-forming particles.",
    "Blood sugar": "A1c or fasting glucose helps show how the body handles energy over time.",
    "Blood pressure": "Blood pressure is common, often silent, measurable at home, and treatable.",
}


APPROVED_SCOPE = (
    "Vital8 is educational only. It can explain Life's Essential 8, prevention priorities, "
    "general lifestyle concepts, home measurement, and clinician discussion topics. It is not a diagnosis, "
    "treatment plan, emergency triage tool, or validated clinical risk calculator."
)


SCORING_METHODOLOGY = (
    "The core Vital8 score is an educational LE8-style score from 0 to 100. It averages the available domain "
    "scores across Daily fuel, Movement, Nicotine, Sleep rhythm, Body size, Cholesterol particles, Blood sugar, "
    "and Blood pressure when enough domains are entered. Missing labs can produce a partial score. Diet and "
    "nicotine are consumer-facing approximations designed to align with the spirit of AHA Life's Essential 8, "
    "not exact clinical recalls. Optional VO2max/cardiorespiratory fitness and hsCRP/Lp(a) sections are "
    "exploratory interpretive lenses that do not replace the raw LE8 score and are not validated risk calculators."
)


ADVANCED_INTERPRETATION_GUIDE = (
    "Use this high-level language when explaining the optional advanced lenses. The user's raw LE8 score is the "
    "foundation. The advanced lenses do not replace it; they ask whether biology adds extra context. "
    "Cardiorespiratory fitness/VO2max is best explained as how well the heart, lungs, blood vessels, and muscles "
    "work together during sustained effort. Physical activity is what someone reports doing; fitness is what the "
    "body can actually do. Higher fitness is consistently associated with lower long-term cardiovascular and "
    "all-cause mortality risk, so low fitness can make an otherwise decent LE8 score feel less reassuring, while "
    "high fitness can add favorable context. Keep this population-level and do not promise personal life-years. "
    "Lp(a), pronounced lipoprotein little-a, is not alpha-lipoic acid. It is a mostly inherited cholesterol-like "
    "particle. It usually does not change much with diet or exercise. If elevated, the message is not blame; it "
    "means the controllable risk factors around it matter more, especially LDL/non-HDL/ApoB, blood pressure, "
    "glucose, nicotine exposure, and fitness. hsCRP is a snapshot of inflammatory signaling. Unlike Lp(a), it can "
    "move over time and may be influenced by recent infection, injury, chronic inflammatory conditions, adiposity, "
    "sleep, smoking, activity, and cardiometabolic health. A single high hsCRP should be interpreted cautiously, "
    "especially if someone was recently sick. The practical message is to reduce avoidable inflammatory burden "
    "and discuss persistent elevation with a clinician. When explaining why these biomarkers matter, use the "
    "foundation-and-context metaphor: LE8 describes the house, while Lp(a) and hsCRP help describe whether the "
    "house is sitting on especially favorable or less favorable biological ground. Two people can have the same "
    "LE8 score but different prevention margins if one has high inherited lipid burden or persistent inflammation. "
    "Avoid frightening phrases like hidden time bomb, danger zone, or cliff. Frame the value as precision and "
    "actionability: the labs help someone know whether excellent control of LDL/non-HDL/ApoB, blood pressure, "
    "glucose, nicotine exposure, sleep, activity, body weight, and fitness should be treated as even more important. "
    "When users ask about the advanced score, describe it as biological drag or biological tailwind: inherited lipid "
    "risk, inflammation, and fitness can change how much prevention margin someone appears to have, but the main "
    "actions remain evidence-based LE8 habits plus clinician-guided risk-factor management."
)


LE8_EVIDENCE_POSITIONING = (
    "When explaining why LE8 matters, use persuasive but careful language. Describe the score as one number built "
    "from eight levers: diet, activity, nicotine exposure, sleep, body size, cholesterol, blood sugar, and blood "
    "pressure. Higher LE8 scores are associated in large cohort studies with lower risk of heart attack, stroke, "
    "heart failure, diabetes, dementia, premature death, and more years lived free from major chronic disease. "
    "When a user asks why they should care about improving the score, give a concise 3 to 4 sentence answer, not a "
    "long evidence dump. Use this evidence base without overclaiming: a meta-analysis of 34 studies and 1.8 million "
    "people found high LE8 scores associated with 63% lower cardiovascular death and 46% lower all-cause mortality. "
    "A pooled U.S. analysis of 32,896 adults followed for 642,000 person-years found each 10-point LE8 increase "
    "associated with 22-40% lower cardiovascular disease risk and 17-21% lower mortality risk. Moving from low "
    "LE8 below 50 to intermediate LE8 50-74 has been associated with 40% lower all-cause mortality and 38% lower "
    "cardiovascular death, so perfection is not required. A Chinese cohort of nearly 89,000 people found that "
    "improving from the lowest to highest LE8 category over 6 years was associated with 44% lower heart attack and "
    "stroke risk. Broader outcome data connect high LE8 with 44% lower dementia risk, 71% lower vascular dementia "
    "risk, healthier brain MRI markers, 54% lower heart failure risk, 57% lower chronic kidney disease risk, lower "
    "cancer risk in some cohorts, 35% lower odds of accelerated biological aging, and markedly lower depression "
    "risk. The average U.S. adult scores around 65/100, more than 80% of adults are less than optimal, and diet, "
    "activity, and weight are often the most modifiable weak points. Frame this as ROI: the score matters because "
    "it identifies the few modifiable levers most likely to change a person's long-term health trajectory. "
    "Score-tailor the message: for scores below 50, emphasize that the first move into the 50-74 range can carry "
    "major upside; for 50-79, emphasize the additional gains from reaching 80 or higher; for 80 or higher, emphasize "
    "maintenance, resilience, and protecting the system they have built. "
    "Do not promise that an individual user will gain a specific number of years or avoid a disease. Emphasize "
    "that the value of the score is actionability: it shows what is already strong, what is missing, and which "
    "one or two levers may be most worth improving next."
)
