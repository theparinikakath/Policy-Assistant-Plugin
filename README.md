# Policy-Assistant-Plugin

The Policy Assistant Chatbot is an internal AI-powered assistant that allows employees to ask questions about security and IT policies and receive accurate, grounded responses based only on approved policy documents.

Example questions the system can answer:
  What is the password policy?
  What should I do if I receive a phishing email?
  What is EDR?
  What is the 3rd-party risk policy?
  
The system uses a Retrieval-Augmented Generation (RAG) architecture — meaning the chatbot does not rely on the LLM's general knowledge. Instead, it retrieves relevant sections directly from approved DPW policy documents and generates an answer grounded strictly in that content.
