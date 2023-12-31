from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# configurations
app.config['UPLOAD_FOLDER'] = 'static/images'

#Load the recipes data from into pandas DataFrame
csv_file = 'CookeryHub.csv'
df_recipes = pd.read_csv(csv_file)


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/recipes')

def recipes():
    return render_template('recipes.html',recipes=df_recipes.to_dict(orient='records'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_form():
    global df_recipes  # Declare df_recipes as global to modify the global variable within the function

    if request.method == 'POST':
        recipe_name = request.form['recipe_name']
        ingredients = request.form['ingredients']
        preparation_instructions = request.form['preparation_instructions']
        serving_instructions = request.form['serving_instructions']
        image = request.files['image']

        # Validate the form data and process the image upload
        if recipe_name and ingredients and preparation_instructions and serving_instructions and image:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

            # Append new recipe to the DataFrame and save it back to the CSV
            new_recipe = {
                'Recipe_Name': recipe_name,
                'Ingredients': ingredients,
                'Preparation_Instructions': preparation_instructions,
                'Serving_Instructions': serving_instructions,
                'Image_URL': f'images/{image.filename}'
            }
            new_recipe_df = pd.DataFrame([new_recipe])
            df_recipes =pd.concat([df_recipes,new_recipe_df],ignore_index=True)

            df_recipes.to_csv(csv_file, index=False)

            return redirect(url_for('recipes'))
        else:
            return "Please fill all the required fields and upload an image."

    return render_template('upload_form.html')


@app.route('/remove/<int:index>',methods=['GET','POST'])
def remove_recipe(index):
    if request.method =='POST':
      #Remove the recipe with given index from DateFrame
        df_recipes.drop(index, inplace=True)
        df_recipes.to_csv(csv_file, index=False)
        return redirect(url_for('recipes'))
    recipe_dict = df_recipes.loc[index].to_dict()
    return render_template('remove_recipes.html', recipes=df_recipes.to_dict(orient='records'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        #Read data from the CSV file using pandas
        df = pd.read_csv(csv_file)

        #Perform search operation using pandas query
        search_results = df[df['Recipe_Name'].str.contains(search_query, case=False) |
                           df['Ingredients'].str.contains(search_query, case=False)]

        return render_template('search.html', search_results=search_results.to_dict(orient='records'))
    return render_template('search.html', search_results=[])



if __name__ == '__main__':
    app.run(debug=True)
