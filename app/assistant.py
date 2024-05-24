import openai
import time
import json
from config import Config
from models import User,Quote,QuoteItem
from spreadsheet import Spreadsheet
from pathlib import Path

class Assistant:
    def __init__(self, phone, message):
        openai.api_key = Config.OPENAI_API_KEY
        self.gpt_id = Config.GPT_ID
        self.phone = phone
        self.message = message

    def process(self):
        thread_id = self.get_thread_id()

        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=self.message
        )

        instructions_base = Path('instructions.txt').read_text()
        known_products = Spreadsheet().get_products()

        instructions_text = instructions_base + '\n'.join(known_products)

        # print('instructions: ')
        # print( instructions_text )


        assistant_run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.gpt_id,
            instructions=instructions_text
        )

        while assistant_run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(2)
            keep_retrieving_run = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=assistant_run.id
            )
            print(f"Run status: {keep_retrieving_run.status}")

            if keep_retrieving_run.status == "completed":
                print("\n")

                # Step 6: Retrieve the Messages added by the Assistant to the Thread
                all_messages = openai.beta.threads.messages.list(
                    thread_id=thread_id
                )

                print("------------------------------------------------------------ \n")

                #print(f"User: {my_thread_message.content[0].text.value}")
                print(f"Assistant: {all_messages.data[0].content[0].text.value}")
                assistant_response = all_messages.data[0].content[0].text.value

                break
            elif keep_retrieving_run.status == 'requires_action':
                for call in keep_retrieving_run.required_action.submit_tool_outputs.tool_calls:
                    print(f"Call: {call.id}")
                    print(f"Action: {call.function.name}")
                    if call.function.name == 'create_quote':
                        parsed_arguments = json.loads(call.function.arguments)
                        order_id = self.create_quote( parsed_arguments['items'] )
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": "Pedido confirmado com o número " + str(order_id) + ". Informe esse número ao cliente para acompanhamento do pedido.",
                                },
                                ]
                            )
                    elif call.function.name == 'create_blank_quote':
                        output = self.create_blank_quote()
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": output,
                                },
                                ]
                            )
                    elif call.function.name == 'add_items_to_existing_quote':
                        parsed_arguments = json.loads(call.function.arguments)
                        output = self.add_items_to_existing_quote(parsed_arguments['quote_id'], parsed_arguments['items'])
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": output,
                                },
                                ]
                            )
                    elif call.function.name == 'update_items_in_existing_quote':
                        parsed_arguments = json.loads(call.function.arguments)
                        output = self.update_items_in_existing_quote(parsed_arguments['quote_id'], parsed_arguments['items'])
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": output,
                                },
                                ]
                            )
                    elif call.function.name == 'remove_items_from_existing_quote':
                        parsed_arguments = json.loads(call.function.arguments)
                        output = self.remove_items_from_existing_quote(parsed_arguments['quote_id'], parsed_arguments['items'])
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": output,
                                },
                                ]
                            )
                    elif call.function.name == 'list_all_quotes':
                        output = self.list_all_quotes()
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": output,
                                },
                                ]
                            )
                    elif call.function.name == 'send_quote_request':
                        parsed_arguments = json.loads(call.function.arguments)
                        output = self.send_quote_request(parsed_arguments['quote_id'])
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=keep_retrieving_run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": output,
                                },
                                ]
                            )
            elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
                pass
            else:
                print(f"Run status: {keep_retrieving_run.status}")
                break

        return assistant_response


    def get_thread_id(self):
        existing_user = User.find_by_phone(self.phone)
        if existing_user:
            return existing_user.thread_id

        # Create a new thread and user
        thread = openai.beta.threads.create()

        new_user = User.create_user(phone=self.phone, thread_id=thread.id)

        return thread.id

    def create_quote(self, items):
        items_string = ''
        for item in items:
            items_string = items_string + str(item['item_quantity']) + ' - ' + item['item_name'] + '; '

        quote_id = Quote.create_new_quote()

        QuoteItem.add_items_to_quote(quote_id, items)

        return "pedido criado com ID " + str(quote_id) + ". Itens: " + items_string + "."

    def create_blank_quote(self):

        quote_id = Quote.create_new_quote()
        return "pedido criado com ID " + str(quote_id)

    def add_items_to_existing_quote(self, quote_id, items):
        items_string = ''
        for item in items:
            items_string = items_string + str(item['item_quantity']) + ' - ' + item['item_name'] + '; '
        QuoteItem.add_items_to_quote(quote_id, items)
        return "Itens adicionado ao pedido " + str(quote_id) + ": " + items_string

    def update_items_in_existing_quote(self, quote_id, items):
        for item in items:
            items_string = items_string + str(item['item_quantity']) + ' - ' + item['item_name'] + '; '
        QuoteItem.update_item_in_quote(quote_id, items)
        return "Itens modificado no pedido " + str(quote_id) + ": " + items_string

    def remove_items_from_existing_quote(self, quote_id, item_name):
        for item in items:
            items_string = items_string + item['item_name'] + '; '
        QuoteItem.remove_items_from_quote(quote_id, item_name)
        return "Itens removido do pedido " + items_string

    def list_all_quotes(self):
        quotes = Quote.list_all_quotes()
        quotes_string = ''
        for quote in quotes:
            quotes_string = quotes_string + "Pedido " + str(quote.id) + ":\n"
            for item in quote.get_quote_items():
                quotes_string = quotes_string + str(item.quantity) + " - " + item.item_name + "\n"
            quotes_string = quotes_string + "\n"
        return quotes_string

    def send_quote_request(self, quote_id):
        print("Sending quote request for quote " + str(quote_id))
        return "Pedido de orçamento enviado para os fornecedores"

if __name__ == "__main__":

    # Run this file directly to create the assistant.
    print ("Creating assistant...")
    openai.api_key = Config.OPENAI_API_KEY
    assistant = openai.beta.assistants.create(
        name="Assistente de Cotação - Montar pedido",
        description="Você é um assistente que vai ajudar a montar uma lista de compras para que outro assistente faça uma cotação.",
        model="gpt-4-turbo-preview",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "create_quote",
                    "description": "Creates a new quote with items",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {"type": "array", "description": "The items to be added to the quote", "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": { "type": "string"},
                                    "item_quantity": { "type": "integer"},
                                }
                            }},
                        },
                        "required": ["items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_blank_quote",
                    "description": "Creates a new quote without any items",
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_items_to_existing_quote",
                    "description": "Adds a new item to an existing quote",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quote_id": { "type": "integer"},
                            "items": {"type": "array", "description": "The items to be added to the quote", "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": { "type": "string"},
                                    "item_quantity": { "type": "integer"},
                                }
                            }},
                        },
                        "required": ["quote_id", "items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_items_in_existing_quote",
                    "description": "Updates an item quantity in an existing quote",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quote_id": { "type": "integer"},
                            "items": {"type": "array", "description": "The items to be added to the quote", "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": { "type": "string"},
                                    "item_quantity": { "type": "integer"},
                                }
                            }},
                        },
                        "required": ["quote_id", "items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_items_from_existing_quote",
                    "description": "Removes an item from an existing quote",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quote_id": { "type": "integer"},
                            "items": {"type": "array", "description": "The items to be added to the quote", "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": { "type": "string"},
                                }
                            }},
                        },
                        "required": ["quote_id", "items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_all_quotes",
                    "description": "Lists all quotes created in the system",
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_quote_request",
                    "description": "Sends a given quote to the suppliers for a quote request",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quote_id": { "type": "integer"},
                        },
                        "required": ["quote_id"]
                    }
                }
            },
        ]
    )
    print( "Created")
    print(assistant.id)