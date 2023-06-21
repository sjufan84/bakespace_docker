# bakespace_fastapi

## FastAPI backend to be integrated with Bakespace website.  The app should have the following functions

**The app should have the following functions:**

1 -- It should be able to allow the user to input specifications and the front end to receive other variables 
that will be passed to the model and then a recipe will be generated as a Recipe object

2 -- Chat Features -- The user should be able to chat with a large language model about their recipe after it 
is generated.  This is achieved by passing the recipe and the chat history to the model so that it can have
context when answering the questions.  The function or functions related to chat should allow the user to chat
over a specific recipe or other context depending on what section of the website they are on.

3 -- Recipe text extraction -- The app should be able to extract text from a user uploaded recipe -- this could 
be in the form of a text document, pdf document, word document, copy and paste text, or a picture of a recipe.
We will use the Google Vision API to extract the text from the picture, and then will pass the result to a large 
language model to parse the recipe and format in a way that is legible and can be leveraged in the website.
The user should have the ability to edit the recipe after the text is extracted before saving to ensure that
it is correct and that the API or other text loaders did not make a mistake in extracting the text.

4 -- Image generation -- the app should be able to leverage Stability AI's image generation feature by initially passing
it the value of the recipe_name after the recipe is generated to create the initial image.  It should then allow the user to 
pass in their own prompt if they wish to generate a new image.

5 -- Pairings Generator -- the app should allow the user to choose a type of pairing i.e. wine, beer, coffee, tea
for their recipe.  This will take in the recipe text and pairing type text and then should output the pairing as a string.

6 -- The app should be able to interact with the Bakespace API and have the same attributes for the objects, particularly the
objects that exist in both existing applications, i.e. recipes, etc.  

7 -- The app will be deployed and tested via an Azure Linux VM, so any code written should be able to be translated onto the 
virtual machine.


