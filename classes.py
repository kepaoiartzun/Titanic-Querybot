from dataclasses import dataclass
import gradio as gr

@dataclass
class Table:
    table_name : str
    table_description: str
    table_columns: str

class chatgpt_class:
    import openai
    def __init__(self, api_key):
        self.openai.api_key = api_key
    
    def get_completion_from_messages(self, messages, model="gpt-3.5-turbo", temperature=0):
        try:
            response = self.openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature, # this is the degree of randomness of the model's output
            )
            return response.choices[0].message["content"]
        except self.openai.error.AuthenticationError:
            raise gr.Error("There has been an authentication error, try entering the OpenAI API key correctly. Then, click the 'send' button of the chat tab again.")
        except Exception as err:
            raise gr.Error(err)



class Conversation:
    def __init__(self, table: Table, chatgpt: chatgpt_class):
        self.context = [{
            'role':'system', 
            'content':f"""
                You are QueryBot, an automated service that writes SQL querys.
                The user will describe what they want to select from the table, and you will write an SQL query to solve it.
                This is the name of the table: {table.table_name}
                This is the description of the table: {table.table_description}
                The columns of the table with their definitions are listed below, delimited by triple backticks.
                ```{table.table_columns}```
                If the user asks you something that is not related to the task of analyzing the table {table.table_name}, you will ask them to ask something related to analyzing the table {table.table_name}.
                The output should be a markdown code snippet with the SQL code only, including the leading and trailing "\`\`\`sql" and "\`\`\`"
                """
        }]
        self.explain_context = [{
            'role':'system', 
            'content':"""
                You are ExplanationBot, a service that explains the results obtained in a SQL query.
                The user asked for information in a database, and after running a query, obtained a numeric result. Your task is to explain this result to the user.
                The result must be simple and dynamic, the user is not interested in why you came to the conclusion in question.
                VERY IMPORTANT: You have to explain the result in the same language the user used.

                For example, if the user asked what is the price of a pizza, and the query result is 12.5, your response should be the following: 'The price of a pizza is 12.5'
                If the user asked information in spanish, you must answer in spanish.
                """
        }]
        self.chatgpt = chatgpt
    
    def explain_the_result(self, user_request, query_result):
        prompt = f"""
            This is the information the user asked for: {user_request}
            This is the numeric result obtained after running the query: {query_result}.
            """
        self.explain_context.append(
            {'role':'user', 'content':prompt}
        )
        response = self.chatgpt.get_completion_from_messages(self.explain_context)
        self.explain_context.append(
            {'role':'system', 'content':response}
        )
        return response

    
    def get_querybot_response(self, r):
        import re
        import sqlite3
        self.context.append(
            {'role':'user', 'content':r}
        )
        response = self.chatgpt.get_completion_from_messages(self.context)
        self.context.append(
            {'role':'system', 'content':response}
        )
        query = re.findall("```sql\n([\w\W]*?)\n```", response)
        if len(query) == 0:
            return {'query':None, 'query_result':None, "response":response}
        else:
            query = query[0]
            connection_object = sqlite3.connect('data.db')
            query_result = connection_object.execute(query).fetchall()
            connection_object.close()
            explained_result = self.explain_the_result(r, query_result)
        return {'query':query, 'query_result':query_result, "response":explained_result}
    

        