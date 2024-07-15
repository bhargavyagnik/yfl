import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import google.generativeai as genai
from api_keys import GEMINI_API_KEY
from tqdm import tqdm
import os 

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


class RecipeInfo(BaseModel):
    recipe_name: str = Field(description="Name of the recipe (in English), concise like Dal bati, Red Curry, Rajma Chawal, Rasam wada")
    ingredents: dict = Field(description="Combined single key:value based dict of vegetables,pulses,meat used with quantities like {{'TOMATOES':4,'CHICKEN':'500g'}} do not include spices and condiments, give 0 if quantity is not mentioned")
    preparation_time: int = Field(default=0,description="Preparation time in minutes like 15, 25, 40, give 0 if not mentioned")
    cooking_time: int= Field(default=0,description="Cooking time in minutes like 10, 45, 1hr should be 60, give 0 if not mentioned")

parser = PydanticOutputParser(pydantic_object=RecipeInfo)
prompt_template = PromptTemplate(
    template=
    """Extract the following information in JSON formal: \n{format_instructions}\n\n
    from the below text: {text}. \n\n
    Links are not required to be extracted. \n\n Return in JSON object only.
    """,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)


def query_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None  # Or return a specific error message


def process_recipe(text):
    # Use Gemini instead of Ollama
    prompt = prompt_template.format(text=text)
    response = query_gemini(prompt)
    if response:
        try:
            parsed_response = parser.parse(response)
            return parsed_response
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None  # Or return a specific error message
    else:
        return None  # Handle no response from Gemini

new_cols = ["recipe_name", "ingredients", "preparation_time", "cooking_time"]

def extract_recipe_info(text):
    parsed_data = process_recipe(text)
    if parsed_data:
        return [parsed_data.recipe_name, parsed_data.ingredents, parsed_data.preparation_time, parsed_data.cooking_time]
    else:
        return [None] * len(new_cols)  # Return a list of None for all columns if parsing fails
    
    
def handle_apply_error(error):
    # Log the error or take appropriate action for specific exceptions
    print(f"Error applying process_recipe: {error}")
    return None  # Or return a default value

def save_files(data):
    opath = 'data/channel_data_parsed_g.csv'
    outputpath = os.path.join(os.path.dirname(__file__), opath)
    data.to_csv(outputpath, index=False)

    opath_1 = 'data/channel_data_parsed.csv'
    outputpath1 = os.path.join(os.path.dirname(__file__), opath_1)
    data[new_cols].to_csv(outputpath1, index=False)
    return outputpath

def main():
    file_path = os.path.join(os.path.dirname(__file__), 'data/channel_data_parsed_g.csv')
    data = pd.read_csv(file_path)
    data[['description']] = data[['description']].fillna('')
    if new_cols[0] not in data.columns:
        for col in new_cols:
            data[col] = None
    for i,row in  tqdm(data.iterrows(),total=len(data)):
        if pd.isna(row[new_cols[:2]]).any():
            x = extract_recipe_info(row["description"])
            for j, col in enumerate(new_cols):
                data.at[i,col] = x[j]
        else:
            print(f"Skipping row {i} as it already has values")
        if i>0 and i%100 == 0:
            save_files(data)

    outputpath = save_files(data)
    print(f"Data has been saved to {outputpath}")
    #print count of rows with missing values
    print(f"Number of rows with missing values: {data.isnull().any(axis=1).sum()}")

if __name__ == '__main__':
    main()