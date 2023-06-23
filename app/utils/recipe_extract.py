import re

def extract_recipe_name(recipe):
    match = re.search(r"Recipe Name:\s*(.*?)\n", recipe)
    return match.group(1) if match else None


def extract_ingredients(recipe):
    ingredients_regex = r"Ingredients:(.*?)\n\n(?:Steps|Total time)"
    ingredients_match = re.search(ingredients_regex, recipe, re.DOTALL)
    if ingredients_match:
        ingredients_raw = ingredients_match.group(1).strip().split('\n')
        return [ingredient.strip() for ingredient in ingredients_raw if ingredient.strip()]
    return []


def extract_times(recipe):
    cook_time_match = re.search(r"Cook time:\s*(\d+)\s*minutes?", recipe)
    prep_time_match = re.search(r"Prep time:\s*(\d+)\s*minutes?", recipe)
    total_time_match = re.search(r"Total time:\s*(\d+)\s*minutes?", recipe)
    
    cook_time = int(cook_time_match.group(1)) if cook_time_match else None
    prep_time = int(prep_time_match.group(1)) if prep_time_match else None
    total_time = int(total_time_match.group(1)) if total_time_match else None


    return cook_time, prep_time, total_time



def extract_steps(recipe):
    steps_regex = r"Steps:(.*?)\n\n(?:Total time|Cook time|Prep time)"
    steps_match = re.search(steps_regex, recipe, re.DOTALL)
    if steps_match:
        steps_raw = steps_match.group(1).strip().split('\n')
        return [step.strip() for step in steps_raw if step.strip()]
    return []


def is_valid_recipe(recipe):
    cook_time, prep_time, total_time = extract_times(recipe)
    return (
        recipe is not None
        and extract_recipe_name(recipe) is not None
        and extract_ingredients(recipe)
        and cook_time is not None
        and prep_time is not None
        and total_time is not None
        and extract_steps(recipe)
    )