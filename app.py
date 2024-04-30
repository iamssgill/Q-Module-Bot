#   IMPORTS
from flask import Flask, request, render_template
import openai
import pandas as pd
import numpy as np
from config import OPENAI_API_KEY
from scipy import spatial
import ast
import tiktoken

#   OPEN AI CONFIG
openai.api_key = OPENAI_API_KEY
COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

# Initialize Flask application
app = Flask(__name__)

# Read data from the previously created embedding CSV file and convert the 'embedding' column to NumPy arrays
df = pd.read_csv('msc-embeddings.csv')
df['embedding'] = df['embedding'].apply(ast.literal_eval).apply(np.array) #apply transformations to the embeddings column, convert string arrays into python lists then Numpy arrays of vector embeddings

# Function to calculate the number of tokens in a string. It helps ensure that the token budget is not exceeded when generating a message for GPT
def num_tokens(text: str, model: str = GPT_MODEL) -> int: # Calculates the number of tokens in a given text.
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Function to rank strings based on relatedness to a given query
#* This function is the core and is used in several places:
#        * It's used within the query_message function to obtain the most relevant strings based on the user's query.
#        * It's used in the ask function to rank relevant data points (strings) based on their relatedness to the user's query.
#        * It's also used in the ask function to retrieve the most relevant chunks of text from the 'embedding' column for further analysis and inclusion in the response.

def strings_ranked_by_relatedness( 
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    # Get the embedding of the input query using the OpenAI Embedding API
    query_embedding_response = openai.Embedding.create( 
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"] #extract vector embedding

    # Calculate the relatedness of each string in the DataFrame to the query
    strings_and_relatednesses = [
        (row["content"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]

    # Sort the strings (second element in tuple) based on relatedness in descending order
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)

    return strings[:top_n], relatednesses[:top_n]

# Function to generate a query message for GPT, including relevant source texts from the DataFrame and what question we want GPT to answer
#    * This function is used within the ask function to generate a message for GPT. The message includes relevant source texts (strings) from the DataFrame.
def query_message( 
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    # Get strings and relatednesses ranked by relatedness to the query
    strings, relatednesses = strings_ranked_by_relatedness(query, df)

    # Introduction message for GPT
    introduction = 'Use the below articles on the QMUL Computer Science Msc Project Thesis Module to answer the subsequent question. If the answer cannot be found in the articles, write "I\'m sorry, I could not find an appropriate answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction

    # Include relevant source texts from the DataFrame until the token budget is exceeded
    for string in strings:
        next_article = f'\n\nQMUL MSc Project Thesis Information section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article

    return message + question

# Function to interact with GPT and generate an answer for the query
#The ask function is the main function responsible for processing user queries, interacting with the GPT model, and providing answers to users.
# It utilizes several other functions, including query_message and strings_ranked_by_relatedness, to accomplish these tasks
def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    # Generate the message for GPT
    message = query_message(query, df, model=model, token_budget=token_budget)

    # Print the generated message if print_message is set to True
    if print_message:
        print(message)

    # Prepare GPT messages with system and user roles
    messages = [
        {"role": "system", "content": "You answer questions about the QMUL MSc Project Thesis."},
        {"role": "user", "content": message},
    ]

    # Request response from GPT model using the OpenAI Chat API
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )

    # Extract the response message from the API response, response variable holds the entire JSON response from the API
    response_message = response["choices"][0]["message"]["content"]

    # Get the most relevant chunks of text and their relatedness values
    relevant_chunks, relatednesses = strings_ranked_by_relatedness(query, df)

    # Format the most relevant chunks with relatedness values
    relevant_chunks_formatted = ""
    for chunk, relatedness in zip(relevant_chunks, relatednesses):
        relevant_chunks_formatted += f"- Relatedness: {relatedness:.3f}\n  Chunk: {chunk}\n\n"

    # Format the answer message
    answer_message = f"{response_message}"
    chunks = f"Most relevant chunks: {relevant_chunks_formatted}"

    # Get the most relevant chunks of text and their relatedness values for further analysis
    strings, relatednesses = strings_ranked_by_relatedness(query, df, top_n=5)

    # Create a list of dictionaries containing relevant chunk information
    relevant_chunks_info = []
    for string, relatedness in zip(strings, relatednesses):
        if relatedness >= 0.8:
            relevant_chunks_info.append({'relatedness': relatedness, 'chunk': string, 'is_relevant': True})
        else:
            relevant_chunks_info.append({'relatedness': relatedness, 'chunk': string, 'is_relevant': False})

        # Print relevantness and chunks if print_message is set to True
        if print_message:
            print(f"{relatedness=:.3f}")
            print(string)

    # Return the answer message and relevant chunk information
    return answer_message, relevant_chunks_info

# Route to display the search form
@app.route('/')
def search_form():
    return render_template('search.html')

# Route to handle the search query and display the search results
@app.route('/search')
def search():
    # Get the search query from the URL query string
    query = request.args.get('query')

    # Get the GPT response for the query and relevant chunk information
    response_message, relevant_chunks = ask(query, print_message=True)  # Set print_message to True

    # Render the search results template, passing in the search query, GPT response, and relevant chunks
    return render_template('response.html', query=query, response_message=response_message, relevant_chunks=relevant_chunks)

# Route to serve static files (styling)
@app.route('/static/<path:filename>/')
def serve_static(filename):
    return app.send_static_file(filename) 

# Run the Flask application
if __name__ == '__main__':
    #app.run(port=8000)
    app.run()

