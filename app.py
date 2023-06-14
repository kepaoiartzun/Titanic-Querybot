import gradio as gr
from classes import chatgpt_class, Conversation, Table

table_name = "titanic"
table_description = "The table contains information about the passengers in the Titanic. Each row has de data of one passanger."
columns = """
1- Column: pclass. Definition: the ticket class of the passanger. Key: 1 = first class, 2 = second class, 3 = third class.
2- Column: survived. Definition: either the passenger survived or not. Key: 0 = No, 1 = Yes.
3- Column: sex. Definition: the sex of the passanger.
4- Column: Age. Definition: the age of the passanger in years.
5- Column: sibsp. Definition: number of siblings or spouses aboard the Titanic.
6- Column: parch. Definition: number of parents or children aboard the Titanic.
7- Column: ticket. Definition: the number of the ticket.
8- Column: fare, Definition: passenger fare.
9- Column: cabin, Definition: cabin number.
10- Column: embarked. Definition: the port of embarkation of the passanger. Key: C = Cherbourg, Q = Queenstown, S = Southampton.
"""

table = Table(table_name=table_name, table_description=table_description, table_columns=columns)
chatgpt = chatgpt_class(api_key=None)
conversation = Conversation(table=table, chatgpt=chatgpt)

with gr.Blocks() as demo:
    with gr.Tab("Chat"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox(placeholder="What do you want to know about the Titanic dataset?")
        send = gr.Button("Send", variant="primary")
        query = gr.Textbox(label="Generated SQL query")
        query_result = gr.Textbox(label="Query result")
        clear = gr.Button("New Conversation")
    
    with gr.Tab("OpenAI Api Key"):
        key_box = gr.Textbox(label="API Key", placeholder="Place your OpenAI API key here")
        send_key = gr.Button("Send", variant="primary")


    def respond(message, chat_history):
        response = conversation.get_querybot_response(message)
        bot_message = response["response"]
        query = response["query"]
        query_result = response["query_result"]
        chat_history.append((message, bot_message))
        return "", chat_history, query, query_result
    
    def setup(key):
        chatgpt.__init__(api_key=key)
        conversation.__init__(table=table, chatgpt=chatgpt)
    
    send.click(respond, [msg, chatbot], [msg, chatbot, query, query_result])
    clear.click(lambda: (conversation.__init__(table=table, chatgpt=chatgpt), None, None), 
                None, 
                [chatbot, query, query_result], 
                queue=False)
    send_key.click(setup, key_box, None)

demo.launch()
