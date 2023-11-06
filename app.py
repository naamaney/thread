import os
from dotenv import load_dotenv

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from twit import tweeter

import streamlit as st

load_dotenv()


template = """
% INSTRUCTIONS
    - Vous êtes un Bot IA très doué pour écrire des tweets en suivant une description de ton.
    - Tu reçois des informations ci-dessous, tu dois à partir de ces informations écrire un thread twitter informatif en suivant la description du ton.
    - Votre objectif est d'écrire des tweets à partir d'informations en suivant le ton décrit ci-dessous.
    - Ne dépassez pas les instructions de ton ci-dessous.
    - Un tweet ne dépasse pas 280 caractères par tweet.
    - N'utilise pas de hashtags.
    - Ne mentionne pas le mot thread.
    - Ne dis pas bonjour.
    - N'utilise pas d'émoticone.
    - Fais en sorte que chaque tweet apporte une information et donne envie de voir le suivant.



% Description du ton
    Ton : Le ton du texte est motivant, encourageant, et informatif. Il cherche à inspirer le lecteur.
    Ambiance : L'ambiance est positive, encourageante, et introspective. Le texte encourage la réflexion et l'introspection.
    Rythme : Fluide et progressif, avec une cadence qui augmente à mesure que l'on approche de la résolution.
    Voix : La voix de l'auteur est assertive, persuasif et motivante.
    Perspective : Le texte est écrit à la deuxième personne, s'adressant directement au lecteur.
    Langage : Le langage est clair et accessible, sans être trop complexe, rendant le contenu compréhensible pour un large public.
    Imaginaire : Le texte incite le lecteur à imaginer sa propre situation.
    Diction : Moderne et inclusive, adaptée à un public large.
    Syntaxe : Phrases courtes et concises pour un impact maximum.
    Allusion : Fait référence à des comportements et habitudes communs.
    Métaphore : Le texte peut utiliser des métaphores.


% Informations à utiliser pour écrire le thread
    {info}
    """

prompt = PromptTemplate(
    input_variables=["info"], template=template
)

openai_api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key, model='gpt-4')
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    
)



  
twitapi = tweeter()

def tweetertweet(thread):

    tweets = thread.split("\n\n")
    #check each tweet is under 280 chars
    for i in range(len(tweets)):
        if len(tweets[i]) > 280:
            prompt = f"Raccourci ce tweet pour qu'il soit en dessous de 280 caractères : {tweets[i]}"
            tweets[i] = llm.predict(prompt)[:280]
    #give some spacing between sentances
    tweets = [s.replace('. ', '.\n\n') for s in tweets]

    for tweet in tweets:
        tweet = tweet.replace('**', '')

    response = twitapi.create_tweet(text=tweets[0])
    id = response.data['id']
    tweets.pop(0)
    for i in tweets:
        print("tweeting: " + i)
        reptweet = twitapi.create_tweet(text=i, 
                                    in_reply_to_tweet_id=id, 
                                    )
        id = reptweet.data['id']

def main():
    
    # Set page title and icon
    st.set_page_config(page_title="FRAMATOME research agent Thread", page_icon=":bird:")

    # Display header 
    st.header("FRAMATOME research agent :bird:")
    
    # Get user's research goal input
    query = st.text_input("Informations")

    # Initialize result and thread state if needed
    if not hasattr(st.session_state, 'thread'):
        st.session_state.thread = None

    # Do research if query entered and no prior result
    if query and (st.session_state.thread is None):
        
        # Generate thread from result
        st.session_state.thread = llm_chain.predict(info=query)

        # Display generated thread and result if available
        if st.session_state.thread:
            st.markdown(st.session_state.thread)
        
            # Allow tweeting thread
            tweet = st.button("Tweeeeeet")
        
            # Display info on result 
            st.markdown("Twitter thread Generated from the below research")
    
            if tweet:
                # Tweet thread
                tweetertweet(st.session_state.thread)
            
 

if __name__ == '__main__':
    main()
