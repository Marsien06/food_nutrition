#!/usr/bin/env python3

import sys
from recipes import RatingPredictor, NutritionAnalyzer, RecipeMatcher, DailyMenuGenerator


if __name__ == "__main__":
    user_ingredients = sys.argv[1].split(',')

    predictor = RatingPredictor(model_path="data/model.pkl", feature_file="data/ingredients_df.csv")
    message = predictor.forecast_rating(user_ingredients)
    print(message)


    print("\nII. NUTRITION FACTS", end="")
    analyzer = NutritionAnalyzer()
    print(analyzer.get_nutrients(user_ingredients))

    print("\nIII. TOP-3 SIMILAR RECIPES:")
    matcher = RecipeMatcher(
        ingredients_file="data/epi_r.csv",
        links_file="data/recipe_links.csv"
    )

    results = matcher.find_similar(user_ingredients, top_n=3)

    for recipe in results:
        print(f"- {recipe['title']}, rating: {recipe['rating']}, URL: {recipe['url']}")

    print('\n(BONUS) Daily Menu')
    print("... generating daily menu, please wait ...")

    menu = DailyMenuGenerator(
        "data/ingredients_df.csv",
        "data/nutrition_facts.csv",
        "data/recipe_links.csv",
        "data/epi_r.csv"
    )

    menu.generate_daily_menu()
