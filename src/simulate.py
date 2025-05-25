from pathlib import Path
import numpy as np
import pandas as pd


START_YEAR = 1900
END_YEAR = 1967
MAX_AGE = 100
INITIAL_TOTAL_POPULATION = 2_714_068  # Population of Paris in 1901


def simulate_population(output_dir: Path):
    years = np.arange(START_YEAR, END_YEAR + 1)
    age_brackets = {
        "0-14": range(0, 15),
        "15-29": range(15, 30),
        "30-44": range(30, 45),
        "45-59": range(45, 60),
        "60-74": range(60, 75),
        "75+": range(75, 101),
    }

    # Age-specific annual mortality rates (probability of dying each year)
    mortality_by_age = np.zeros(MAX_AGE + 1)
    mortality_by_age[0:15] = 0.05  # 5% for ages 0–14
    mortality_by_age[15:30] = 0.01  # 1% for ages 15–29
    mortality_by_age[30:45] = 0.02  # 2% for ages 30–44
    mortality_by_age[45:60] = 0.04  # 4% for ages 45–59
    mortality_by_age[60:75] = 0.10  # 10% for ages 60–74
    mortality_by_age[75:] = 0.20  # 20% for ages 75+

    # Age-specific annual fertility rates for ages 15–44
    # Based on TFR of 2.8 children per woman (1901 data), distributed across age bands
    fertility_by_age = np.zeros(MAX_AGE + 1)
    fertility_by_age[15:20] = 0.056  # 10% of births over 5 years
    fertility_by_age[20:25] = 0.14  # 25% over 5 years
    fertility_by_age[25:30] = 0.168  # 30% over 5 years
    fertility_by_age[30:35] = 0.112  # 20% over 5 years
    fertility_by_age[35:40] = 0.056  # 10% over 5 years
    fertility_by_age[40:45] = 0.028  # 5% over 5 years
    fertility_by_age *= 0.5  # Assuming 50% of the population is female

    # Initial population per bracket based on 1901 census proportions
    real_age_bracket_population = {
        "0-14": INITIAL_TOTAL_POPULATION * 0.2533,
        "15-29": INITIAL_TOTAL_POPULATION * 0.2439,
        "30-44": INITIAL_TOTAL_POPULATION * 0.1991,
        "45-59": INITIAL_TOTAL_POPULATION * 0.1569,
        "60-74": INITIAL_TOTAL_POPULATION * 0.1219,
        "75+": INITIAL_TOTAL_POPULATION * 0.0249,
    }

    # Initialize population per individual age using uniform distribution within each bracket
    population_by_age = pd.DataFrame(0, index=years, columns=range(MAX_AGE + 1))
    for label, total in real_age_bracket_population.items():
        ages = list(age_brackets[label])
        per_age = total / len(ages)
        for age in ages:
            population_by_age.loc[1900, age] = per_age

    # Normalize the population to exactly match the target population
    population_by_age.loc[1900] *= (
        INITIAL_TOTAL_POPULATION / population_by_age.loc[1900].sum()
    )

    # Simulate population evolution year by year
    for i, year in enumerate(years[1:], start=1):
        prev_year = years[i - 1]
        current = population_by_age.loc[prev_year].copy()

        # Apply age-specific mortality
        current *= 1 - mortality_by_age

        # Age the population
        new_row = pd.Series(0, index=population_by_age.columns)
        new_row[1:] = current[:-1].values

        # Compute total births (from age-specific fertility rates)
        births = np.sum(current * fertility_by_age)
        new_row[0] = births

        # Apply Paintress effect: remove all individuals of the painted age or older
        painted_age = MAX_AGE - i + 1
        if painted_age in new_row.index:
            new_row[painted_age:] = 0

        population_by_age.loc[year] = new_row

    # Aggregate results by age brackets
    df_pop = pd.DataFrame(index=years)
    df_pop.index.name = "year"
    for label, age_range in age_brackets.items():
        df_pop[label] = population_by_age[age_range].sum(axis=1)

    # Export to CSV
    df_pop.to_csv(output_dir / "population.csv")
