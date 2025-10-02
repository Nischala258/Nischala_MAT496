## Module 0: Set up (calling API Keys and setting up tracing)
I have used Gemini and GoogleAI both to replace OPENAI.
We set up the environment variables and wrote a basic RAG function.  


# Module 1: Tracing

## Video 1
**Tracing:** To help debug and understand better how each part of the code is working.  

## Video 2 
**Project :** This is our RAG application. It has a collection of traces.
**Trace:** Record of events when the application was run. 
**Run :** execution of each logic. 
In RAG we have 2 runs: retrieve information and generate answer. 
**Code:** 
First set up the environment variables. 
Using the same RAG function as in the initial module, we apply traceable decorator. This creates a run tree for all the functions.
We can check all these traces in the langsmith website. We can see each run with the inputs and outputs. We can also see the documents that were retrieved to generate the response. 
Now, we attach meta data. It is a dictionary of key values which we can attach to run to store additional information (like the model provider used, version of the application) about the run. 
These runs can be shared.


