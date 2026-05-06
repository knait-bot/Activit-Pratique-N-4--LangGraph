# Base de connaissances LangGraph

## Concepts de base

LangGraph est un framework d'orchestration pour construire des applications LLM sous forme de graphes. Un graphe contient un etat partage, des noeuds qui executent du code Python, et des aretes qui determinent l'ordre d'execution.

`StateGraph` sert a declarer le schema de l'etat. Chaque noeud recoit l'etat courant et retourne uniquement les champs a mettre a jour. LangGraph fusionne ensuite ces mises a jour dans l'etat.

`START` represente le point d'entree du graphe et `END` represente la fin de l'execution. Les aretes simples connectent deux noeuds. Les aretes conditionnelles permettent de choisir dynamiquement la prochaine etape selon le contenu de l'etat.

## Agentic RAG

Un systeme RAG classique recupere des documents puis genere une reponse. Un Agentic RAG ajoute des decisions explicites : faut-il recuperer des documents, les documents sont-ils pertinents, faut-il reformuler la question, et comment citer les sources.

Dans ce projet, l'agent commence par router la question. Les salutations ou petites questions generales peuvent recevoir une reponse directe. Les questions sur LangGraph, RAG, Studio, Streamlit ou les graphes passent par la recuperation.

Le noeud de recuperation cherche les passages les plus proches de la question dans cette base de connaissances. Le noeud de grading evalue si les documents retrouves sont suffisamment pertinents. Si la pertinence est faible, le noeud de rewrite enrichit la question avec des mots-cles utiles et relance la recuperation.

## LangGraph Studio

LangGraph Studio permet d'inspecter visuellement le graphe, de lancer des executions, de voir l'etat entre les noeuds et de deboguer les transitions. Pour l'utiliser localement, le projet doit fournir un fichier `langgraph.json` qui declare les dependances, les graphes exposés et le fichier d'environnement.

La commande `langgraph dev` demarre un serveur API local. Le graphe compile devient accessible par Studio et par API.

## Streamlit

Streamlit permet de creer rapidement une interface web Python. Dans cette application, Streamlit conserve l'historique de conversation dans `st.session_state`, envoie la derniere question au graphe LangGraph, puis affiche la reponse, les sources et les etapes d'execution.

## Bonnes pratiques

Un chatbot RAG doit citer ses sources, signaler quand les documents ne suffisent pas, eviter d'inventer une reponse non fondee, et separer clairement la logique de recuperation, de jugement et de generation.

Pour un projet de production, il est recommande d'utiliser une vraie base vectorielle, des embeddings, une evaluation systematique, LangSmith pour les traces, et une strategie de securite pour les cles API.
