# Dashboard Notes

**User and decision:** A Mariners advertising sales manager evaluating potential in-stadium audience exposure and deciding which games warrant closer review for advertising opportunities. Attendance is not a measure of verified advertising impressions or revenue.

**Page questions:** Page 1: What do historical attendance patterns show? Page 2: How accurate are the predictions, and where does the model miss? Page 3: What actions should the manager consider, and what attendance does the model predict for a future-game scenario?

**AI feature:** `ai/generate_summaries.py` sends one request per test game to Claude Haiku 4.5. Summaries are stored in PostgreSQL and displayed on Page 3 without dashboard API calls.

**Prompt used:** The following template is filled with each game's facts; Python calculates the error direction and size.

> Write exactly two short, plain-language sentences for a Mariners advertising sales manager reviewing a historical attendance prediction. Return only the two sentences, without a heading, bullets, or Markdown.
>
> Sentence 1: Identify the game date and opponent, then report predicted and actual attendance. Sentence 2: State whether the model overpredicted, underpredicted, or matched attendance, using the supplied size of the miss.
>
> Use the supplied rounded numbers exactly. Do not calculate or add percentages, ratios, or other statistics. Do not invent promotions, special events, causes, advertising impressions, or revenue. Missing values mean unknown. Feature values alone do not establish why the model made its prediction.
>
> Game ID: {game_id}; Game date: {game_date}; Opponent: {team_name}; Day/night: {day_night}; Month: {month}; Weekend: {is_weekend}; U.S. holiday: {is_holiday}; Historical attendance average before cutoff: {rolling_avg_attendance_5}; Mariners winning percentage before cutoff: {mariners_win_pct_at_prediction}; Predicted attendance, rounded: {predicted_rounded}; Actual attendance: {actual}; Error direction: {direction}; Size of miss, rounded: {absolute_error_rounded} fans.

**Three saved summaries checked:**

| Game | Saved summary |
|---|---|
| 778547 | The Mariners played the Athletics on March 27, 2025 at night, with predicted attendance of 27,928 fans and actual attendance of 42,871 fans. The model underpredicted attendance by 14,943 fans. |
| 778541 | The Mariners played the Athletics on March 28, 2025 at night, with predicted attendance of 27928 and actual attendance of 25061. The model overpredicted attendance by 2867 fans. |
| 778521 | The Mariners played the Athletics on March 29, 2025, at night, with predicted attendance of 32191 and actual attendance of 35264. The model underpredicted attendance by 3073 fans. |

**Validation findings:** These three summaries matched the supplied dates, opponents, attendance values, and error directions and sizes. An earlier version added an incorrect percentage. I revised the script to calculate errors in Python and instructed Claude not to add statistics. The final examples used two sentences without headings or unsupported causes. Other summaries may still contain errors.

**Estimated full-run cost:** The latest 81-game run used 22,814 input tokens and 4,618 output tokens. At $1/million input tokens and $5/million output tokens: (22,814 / 1,000,000 × $1) + (4,618 / 1,000,000 × $5) = $0.045904, approximately 4.6 cents. This excludes earlier tests; subsequent runs may differ. Pricing: https://platform.claude.com/docs/en/about-claude/pricing

**With more time:** I would like to add verified promotional schedules to investigate large attendance misses and evaluate whether they improve predictions.