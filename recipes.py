import pandas as pd
import joblib
import random
import numpy as np


class RatingPredictor:
    def __init__(self, model_path="model.pkl", feature_file="file.csv"):

        self.model = joblib.load(model_path)

        df = pd.read_csv(feature_file)
        self.features = df.columns.drop(['title', 'rating']) if 'rating' in df.columns else df.columns.drop(['title'])

    def forecast_rating(self, ingredients):
        input_vector = {ingredient: int(ingredient in ingredients) for ingredient in self.features}
        input_df = pd.DataFrame([input_vector])

        prediction = self.model.predict(input_df)[0]

        print("I. OUR FORECAST")
        if prediction == "bad":
            return "You might find it tasty, but in our opinion, it's a bad idea to have a dish with that list of ingredients."
        elif prediction == "so-so":
            return "Sounds okay, but it's a so-so combination health- and taste-wise."
        elif prediction == "great":
            return "That's a great ingredient combination! Likely healthy and tasty."
        else:
            return f"Prediction: {prediction}"


class NutritionAnalyzer:
    def __init__(self, nutrition_file="data/nutrition_facts.csv"):
        self.df = pd.read_csv(nutrition_file)
        self.df.set_index("ingredient", inplace=True)

    def get_nutrients(self, ingredients):
        output = ""
        for ingredient in ingredients: 
            #output += f"\n{ingredient.title()} -> "
            
            matching_rows = self.df[self.df.index.str.lower() == ingredient.lower()]

            if not matching_rows.empty:
                for name, row in matching_rows.iterrows():
                    output += f"\n{name.capitalize()}\n"
                    for nutrient, val in row.items():
                        if val > 0:
                            output += f"{nutrient} - {round(val)}% of Daily Value\n"
            else:
                output += "No nutrition data found.\n"
        return output


class RecipeMatcher:
    def __init__(self, ingredients_file="ingredients_df.csv", links_file="recipe_links.csv"):
        self.ingredients_df = pd.read_csv(ingredients_file)
        
        self.ingredient_cols = self.ingredients_df.columns.drop('title')
        
        self.links_df = pd.read_csv(links_file)
        self.links_df.set_index("title", inplace=True)

    def find_similar(self, input_ingredients, top_n=3):
        query_vec = pd.Series(0, index=self.ingredient_cols)
        for ing in input_ingredients:
            if ing in self.ingredient_cols:
                query_vec[ing] = 1

        self.ingredients_df["similarity"] = self.ingredients_df[self.ingredient_cols].dot(query_vec)

        top_matches = self.ingredients_df.sort_values(by="similarity", ascending=False).head(top_n+10)
        results = []
        for _, row in top_matches.iterrows():
            title = row["title"]
            rating = self.links_df.loc[title, "rating"] if title in self.links_df.index else None
            url = self.links_df.loc[title, "url"] if title in self.links_df.index else None
            
            item = {}

            if type(title) is str:
                item["title"] = title.strip()

            if type(rating) is np.float64:
                item["rating"] = rating

            if type(url) is str:
                item["url"] = url.strip()

            if all(k in item for k in ['title', 'rating', 'url']):
                results.append(item)

        results.sort(reverse=True, key=lambda k: k['rating'])
        results = results[:top_n]
        return results



class DailyMenuGenerator:
    def __init__(self, ingredients_path, nutrition_path, links_path, ratings_path):
        self.ingredients_df = pd.read_csv(ingredients_path)
        self.nutrition_df = pd.read_csv(nutrition_path).set_index("ingredient")
        self.links_df = pd.read_csv(links_path)
        self.ratings_df = pd.read_csv(ratings_path)[["title", "rating"]]
        self.data = self._prepare_recipe_data()

    def _prepare_recipe_data(self):
        recipe_data = []

        for _, row in self.ingredients_df.iterrows():
            title = row['title']
            used_ingredients = row.drop('title')[row.drop('title') == 1].index.tolist()


            nutrition = self.nutrition_df.loc[self.nutrition_df.index.intersection(used_ingredients)]
            nutrition_total = nutrition.sum(skipna=True).fillna(0)

            nutrition_percent = nutrition_total / 100


            rating_row = self.ratings_df[self.ratings_df['title'] == title]
            rating = float(rating_row['rating'].iloc[0]) if not rating_row.empty else 0.0



            link_row = self.links_df[self.links_df['title'] == title]
            url = link_row['url'].values[0] if not link_row.empty else "URL not found"

            recipe_data.append({
                "title": title,
                "ingredients": used_ingredients,
                "nutrition": nutrition_percent.to_dict(),
                "rating": rating,
                "url": url
            })

        return recipe_data

    def _select_top_recipes(self, count=3):

        valid = []

        for recipe in self.data:
            over_nutrient = any(v > 1.0 for v in recipe['nutrition'].values())
            if not over_nutrient:
                valid.append(recipe)

        sorted_recipes = sorted(valid, key=lambda x: x['rating'], reverse=True)
        return sorted_recipes[:count]

    def generate_daily_menu(self):
        categories = ["BREAKFAST", "LUNCH", "DINNER"]
        menu = dict()

        top_recipes = self._select_top_recipes(count=9)
        random.shuffle(top_recipes)

        for i, meal in enumerate(categories):
            menu[meal] = top_recipes[i*3:(i+1)*3]

        for meal, recipes in menu.items():
            print(f"\n{meal}\n" + "-"*30)
            for r in recipes:
                print(f"{r['title']} (rating: {r['rating']})")
                print("Ingredients:")
                for ing in r['ingredients']:
                    print(f"- {ing}")
                print("Nutrients:")
                for n, v in r['nutrition'].items():
                    print(f"- {n.lower()}: {round(v*100, 1)}%")
                print(f"URL: {r['url']}\n")
