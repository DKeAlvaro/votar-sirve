# Chart B - Does effort pay off? (ES vs NL, young vs old, 1981-2022)

Verdict: PARTIAL. All items are 1-10 scales. The effort item (E040) exists for only 4 waves per country: ES 1990-2011, NL 1990-2022.

## Data
- `data/clean/cB_wvs_age.csv` (tidy, columns per BRIEF): country, wave year, age group (`<30`, `30-49`, `50+`, `all`, `Missing Unknown`), variable `ITEM:stat` with stat = `share_1to3`, `share_8to10`, `mean_1to10`, `n_total_sample_group`. Shares are of valid answers (codes 1-10).
- `data/clean/cB_wording.csv`: English wording (and original language when available) per item and wave.
- Source: World Values Survey / EVS online analysis (worldvaluessurvey.org), crosstab item x single-year age. Scripts `scripts/cB_wvs_discover.py`, `cB_wvs_harvest.py`, `cB_wvs_clean.py`, `cB_wvs_wording.py`. Raw html in `data/raw/cB/`. No registration needed.

## Comparability table
| Item | Wording | ES waves | NL waves |
|---|---|---|---|
| E040_hardwork | 10-point scale, "Hard work brings success" vs luck/connections. The harvested wording only gives the left statement. Per WVS codebook 1 = hard work usually brings a better life, 10 = more a matter of luck and connections, so `share_1to3` = effort side. VERIFY orientation | 1990, 1995, 2007, 2011 | 1990, 2006, 2012, 2022 |
| E039_competition | Competition good / harmful | 1990, 1995, 2000, 2007, 2011, 2017 | 1990, 2006, 2012, 2017, 2022 |
| E036_ownership | Private vs state ownership of business | 1990-2017 (6 waves) | 1990, 2012, 2017, 2022 |
| E037_govresp | Government vs individual responsibility | 1990-2017 | 1990, 2006, 2012, 2017, 2022 |
| A173_freedom | Freedom of choice and control | 1981-2017 (7) | 1981, 1990, 2006, 2012, 2017, 2022 |
| A170_lifesat | Life satisfaction | 1981-2017 | 1981-2022 |

## Caveats
- Wording/translation break flagged in `source_id` (`wording_break_1990`); the E040 header wording shifts slightly between waves (see cB_wording.csv).
- Waves are not the same year in both countries (ES 2007 vs NL 2006; ES 2011 vs NL 2012). The `<30` group has roughly 190-400 respondents per cell, so margins of error are about 5-7 points.
- E040 was not harvested for the 2017 round in either country, so ES has nothing after 2011 and NL nothing between 2012 and 2022 other than 2022.
- The ES `share_8to10` drop from 28% (1990) to 6-7% (2007) is large; check for a scale or coding change before charting.
- Gap between young and 50+ is small in most waves; only 1990 ES shows young at the luck side more than old.
