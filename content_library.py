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
    "Do not promise that an individual user will gain a specific number of years or avoid a disease. Emphasize "
    "that the value of the score is actionability: it shows what is already strong, what is missing, and which "
    "one or two levers may be most worth improving next."
)
