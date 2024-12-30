RAG Workflow Steps:
1. Input Processing:
The user can upload PDF file via the gr.Files Gradio component.
The initialize_database() function processes the uploaded files wherein 
	The File paths are extracted and documents are loaded using the PyPDFLoader package
	The Text is split into chunks with overlap using RecursiveCharacterTextSplitter package.

2. Creating Vector Database:
The create_db() function generates document embeddings using the HuggingFaceEmbeddings package.
They are stored in a FAISS(Facebook AI Similarity Search) based vector Database which makes retrieval more efficient.

3. Initializing the LLM.
We can choose from the preloaded LLMs i.e. Meta-Llama 3 and the Mistral 7B and set parameters such as maximum tokens, temperature and top-k sampling.
Then the initialize_llmchain() function configures the selected LLM via HuggingFaceEndpoint, integrates conversation memory and links the vector database to ConversationalRetrievalChain to retrieve from.

4. Querying:
When the user asks the questions the conversation() function formats the chat history and passes the input to qa_chain which retrieves relevant document chunks and generates the answers via the LLM.
Answers and references (source text and page numbers) are extracted from the LLM response and displayed.

5. Output:
The Gradio UI updates in real time and shows the chatbots response and the relevant references. 


UI Description:
PDF Upload:
The users can upload multiple documents in the upload PDF documents section which calls gr.Files component.
Database Creation:
The user can create a vector database by clicking the Create Vector Database which is connected to db_btn which in turn triggers the initialize_database() function.
Adjusting LLM parameters:
There is a Radio button gr.Radio which lets users choose the LLM of their preference.
The gr.Slider component lets users adjust the LLM parameters such as Temperature, Max New Tokens and top-k.
Querying:
Users can query (ask questions) to the chatbots in the Textbox gr.Textbox and then submit their question via submit_btn
The gr.Chatbot component displays the conservations which contains the response from the chatbot.  
The gr.Accordian component displays 3 Relevant sources from the document and their references with their corresponding page numbers using gr.Textbox and gr.Number
The user can use the submit and the clear button to submit and clear the conversation as required. 
Note: the clear button only clears the conversations from the gr.Chatbot component but they are stored in the Conversation Memory in the qa_chain component thus the stored conversations remain intact. 


