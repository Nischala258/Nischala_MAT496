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

## Video 3
**Types of Runs:** 
1.	LLM : invokes an llm 
2.	Retriever: Retrieves documents from external sources
3.	Tool : Executes actions with function calls
4.	Chain : Combines multiple runs into a larger process
5.	Prompt: to create a prompt 
6.	Parse: Extracts structured data

**Code:** 

We give an input and output to the llm mentioning the role and command. First we run it without specifying run type , later we run specifying the run type. We can compare these two runs in Langsmith and see the difference. When we specify the run type, we can get access to playground feature where we can make changes. Then we add ls_model and ls_provider to specify which model we want to be used. 

Next is to see how llm runs are handled during streaming. We will run the code. Then add the reduce function. We will compare them in Langsmith. The code with reduce functions gives a rendered outcome.

Next we run the code for document retrieval using doc_type. Then change it to just type. The second one gives a neat list of the documents used for data retrieval. The first one gives a raw code. 

Then we, run the tool call. In Langsmith we can see that, first it recognises that the tool has to be used. Then, the tool is called and finally the output is produced. 

## Video 4:
Default way for tracing is using @traceable, it is also the most simple way of doing it. 

If we are using langchain / langraph, it automatically set ups trace in the website. 

**Code:** 

In the first code, we use LangGraph to set up tracing. When we use the graph builder, we can see the same data in the LangSmith that we saw when we used @traceable. 

In the next part, we use trace context to log just a part of the code. Here, we use with trace() , give a name to this run, run type, inputs and metadata. Then, we can log our response using ls_trace.end . This will patch our output to LangSmith so that it shows up in the trace. 
In LangSmith, we can see that in the code with trace context, we can see the question and the formatted doc string in the input. 

Wrap_openai() lets any calls done through openAI be directly traced to LangSmith. Because, I am not using openAI, I delegate the task to wrap to Gemini. 

Then we have Runtree API. This gives us more control as it lets us decide where the runs are to be formed. 

## Video 5:
**Conversational threads:**

 Threads are a series of traces. These threads re important because they contain information, that can be used for answering further questions. 
 Usually, most LLMs are conversational i.e., the user asks a question and the LLM gives the output. 
To associate traces, we need to pass metadata keys. Key name can be one of session_id , thread_id, and conversation_id.

**Code:** 
	
We run the usual RAG code. 

Then we run two other codes with the same thread id (uuid). 

Now, in LangSmith we can see it in the threads feature. Here both the codes are saved like a conversation just like all the llms we use. This is useful of we want to debug a full conversation. 


# Module 2:

## Datasets video: 
Datasets are a part of offline evaluation. It let’s us evaluate if the application is getting better or worse when changes ( new prompts, different model or new architecture) are made. 

Data sets are just a list of examples (input and optional output).

We got to LangSmith and create a dataset from the scratch. We give it a name and description. 

**CODE:**

We give a few input and output statements. Put our data set id in the code and create these as examples using client.create_examples() . 

In LangSmith, now we have a set of examples with input and ouput json files. Then we tag this, so that we can come back and work on this later. 

 We can add individual traces also to the dataset from LangSmith. 
We can also create separate datasets for document retrieved and response generated. 

We can edit the examples in the dataset in LangSmith. 

We can add input scheme (type, and format). 

We can examples manually in the dataset in LangSmith

We can add AI generated examples also, the AI generates similar examples to what we added. 

We can also add splits (like subsets) and include whatever questions we want in it. 

## Evaluators video : 
Evaluators run the application over an example in dataset . It can have metrices like accuracy and hallucination. We can attach multiple evaluators to a single application. 

In our examples, we can run the input through the version of application we are using. Now, we have 2 outputs: one which was generated by the application and our reference output. 

Now, the Evaluator takes the input, our reference output and the output generated through the run to calculate the metrices. 

**Code:**  
In the example we define a function, with input, reference output and output generated. From the reference output we get the label field and the from the run output we get the output field. Then compare the two. If both of them have the same value, then the score is 1 or else it is zero. 

Now we see LLM Judge Evaluators. We test the semantic similarity between  our generated output and the reference output. 

We define the class Similarity_score() . It returns a semantic score where 1 is unrelated and 10 is identical. Then we define a function just like the previous example and assign the LLM role of comparing the outputs and giving a semantic score. 

Then we give an input, and the outputs to check if it’s working correctly. 

In LangSmith, we can add Evaluators by selecting the Auto-Evaluators option. 

We name the Evaluator, select provider and Model. We need our API key to generate this. Then we can, use suggested Evaluator prompts or create our own.

 When we select to create our own evaluator, we can see three variables: input, submission and reference. These variables can be changed. In the schema, we can define what our evaluation should look like (In our case it is a score between 1 to 10). 
