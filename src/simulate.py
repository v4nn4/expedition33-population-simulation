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
        "75-84": range(75, 85),
        "85+": range(85, 101),
    }

    # Age-specific annual mortality rates (probability of dying each year)
    mortality_by_age = np.zeros(MAX_AGE + 1)

    mortality_by_age[0:15] = 0.02209
    mortality_by_age[15:30] = 0.006764
    mortality_by_age[30:45] = 0.009585
    mortality_by_age[45:60] = 0.017221
    mortality_by_age[60:75] = 0.051096
    mortality_by_age[75:] = 0.159804

    TFR = 2.89
    fertility_by_age = np.zeros(MAX_AGE + 1)
    band_fractions = {
        (15, 20): 0.05,
        (20, 25): 0.26,
        (25, 30): 0.29,
        (30, 35): 0.20,
        (35, 40): 0.13,
        (40, 45): 0.06,
    }
    for (start, end), frac in band_fractions.items():
        fertility_by_age[start:end] = frac * TFR / (end - start)

    real_age_bracket_population = {
        "0-14": 0.259785505858112,
        "15-29": 0.25013423134903,
        "30-44": 0.204211636324971,
        "45-59": 0.160892327037594,
        "60-74": 0.0993535462142421,
        "75-84": 0.0225770829827583,
        "85+": 0.00304567023329202,
    }

    # Initialize population per individual age using uniform distribution within each bracket
    population_by_age = pd.DataFrame(0.0, index=years, columns=range(MAX_AGE + 1))
    for label, total in real_age_bracket_population.items():
        ages = list(age_brackets[label])
        if label == "85+":
            # linearly decreasing from age 85 -> 100
            # weight 1 at age 85, weight 0 at age 100
            weights = np.linspace(1, 0, len(ages))
            # normalize so they sum to 1, then multiply by total
            per_age = total * (weights / weights.sum())
        else:
            # uniform split
            per_age = np.full(len(ages), total / len(ages))
        # assign into your dataframe
        for age, pop_frac in zip(ages, per_age):
            population_by_age.loc[1900, age] = pop_frac

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
        new_row = pd.Series(0.0, index=population_by_age.columns)
        new_row[1:] = current[:-1].values

        # Compute total births (from age-specific fertility rates)
        births = np.sum(current * fertility_by_age * 0.5)
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

    # Print total population at the end of the simulation
    total_population = df_pop.sum(axis=1)
    print(f"Total population in {END_YEAR}: {total_population.iloc[-1]:,.0f}")

    # Print the population by age bracket for the last year, in percentage
    df_pop.iloc[-1] = df_pop.iloc[-1] / df_pop.iloc[-1].sum()
    print("Population by age bracket in percentage for the last year:")
    print(df_pop.iloc[-1])