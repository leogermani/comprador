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

        print('instructions: ')
        print( instructions_text )


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
        for item in items:
            QuoteItem.add_item_to_quote(quote_id, item['item_quantity'], item['item_name'])

        return "pedido criado com ID " + str(quote_id) + ". Itens: " + items_string + "."

if __name__ == "__main__":

    # Run this file directly to create the assistant.
    print ("Creating assistant...")
    openai.api_key = Config.OPENAI_API_KEY
    assistant = openai.beta.assistants.create(
        name="Assistente de Cotação - Montar pedido",
        description="Você é um assistente que vai ajudar a montar uma lista de compras para que outro assistente faça uma cotação.",
        model="gpt-4-turbo-preview",
        tools=[{
            "type": "function",
            "function": {
                "name": "create_quote",
                "description": "Creates a new quote",
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
        }]
    )
    print( "Created")
    print(assistant.id)