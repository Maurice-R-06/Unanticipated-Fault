from openai import OpenAI
import json
from config import load_prompt, possible_faults, default_model, default_stream, system_prompt_path, system_prompt_no_possible_faults_listed_path, user_prompt_template_path, api_key
import sys
from datetime import datetime
sys.path.append(r"C:\Users\Lmcoo\Downloads\Unanticipated-Fault\Instructions")
sys.path.append(r"C:\Users\Lmcoo\Downloads\Unanticipated-Fault\User Info")
user_info = json.load(open(r"C:\Users\Lmcoo\Downloads\Unanticipated-Fault\User Info\trial_user_info.json"))

class UnanticipatedFaultChatAgent:
    """
    Simple Unanticipated Fault Agent for answering HARSH related fault diagnosis and repair questions.
    """
    
    def __init__(
        self,
        system_prompt: str,
        user_prompt_template: str,
        model: str = default_model,
        stream: bool = default_stream,
        possible_faults: list[str] = possible_faults["22"],
        user_info: dict = user_info,
        save_path: str = None,
        auto_save: bool = False,
        max_rounds: int = 10,
        anticipated = True
    ):
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.chat_history = []
        self.name = user_info["user_name"]
        self.stream = stream
        self.possible_faults = possible_faults if anticipated else []
        self.num_rounds = 0
        self.save_path = save_path
        self.auto_save = auto_save
        self.most_recent_ruled_out_faults = [] # The faults that were ruled out in the most recent resposne from agent
        self.user_info = user_info
        self.max_rounds = max_rounds
        self.anticipated = anticipated

    def get_function_definitions(self):
        """Returns the function calling schema for OpenAI."""
        if self.anticipated:
            return [
                {
                    "type": "function",
                    "name": "diagnose_fault",
                    "function": {
                        "name": "diagnose_fault",
                        "description": f"Call this function when you have gathered enough evidence to confidently diagnose the fault. This will end the conversation with {self.name}.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "fault_diagnosis": {
                                    "type": "string",
                                    "description": "The specific fault you are diagnosing from the possible_faults list",
                                    "enum": self.possible_faults
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Detailed explanation of the evidence and logic that led to this diagnosis"
                                },
                                "confidence": {
                                    "type": "integer",
                                    "enum": [1, 2, 3, 4, 5],
                                    "description": "Your confidence level in this diagnosis on a scale of 1 to 5, where 1 is the lowest confidence and 5 is the highest confidence."
                                }
                            },
                            "required": ["fault_diagnosis", "reasoning", "confidence"],
                            "additionalProperties": False
                        }
                    }
                }
            ]
        else:
            return [
                {
                    "type": "function",
                    "name": "diagnose_fault",
                    "function": {
                        "name": "diagnose_fault",
                        "description": f"Call this function when you have gathered enough evidence to confidently diagnose the fault. This will end the conversation with {self.name}.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "fault_diagnosis": {
                                    "type": "string",
                                    "description": "The specific fault you are diagnosing",
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Detailed explanation of the evidence and logic that led to this diagnosis"
                                },
                                "confidence": {
                                    "type": "integer",
                                    "enum": [1, 2, 3, 4, 5],
                                    "description": "Your confidence level in this diagnosis on a scale of 1 to 5, where 1 is the lowest confidence and 5 is the highest confidence."
                                }
                            },
                            "required": ["fault_diagnosis", "reasoning", "confidence"],
                            "additionalProperties": False
                        }
                    }
                }
            ]
    def ask(self, question: str) -> str:
        """
        Ask a question and get a response. Conversation history is automatically maintained.
        
        Args:
            question: Your question or message
            
        Returns:
            The agent's response
        """

        if self.anticipated:
            system_prompt = self.system_prompt.format(possible_faults=self.possible_faults, user_info=self.user_info, max_rounds=self.max_rounds)
            text_format={
                "format": {
                    "type": "json_schema",
                    "name": "agent_response_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            f"message_for_{self.name}": {
                                "type": "string",
                                "description": f"Any message you have for {self.name} to answer. This could be a question, a response to a previous message, or a request for information. Also, this could be about the habitat, the surrounding environment, the current situation, etc."
                            },
                            "message_motivation": {
                                "type": "string",
                                "description": f"The motivation behind the message you are sending to {self.name}."
                            },
                            "faults_ruled_out": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": f"Any faults that can be ruled out based on evidence at hand.",
                                    "enum": self.possible_faults,
                                },
                            },
                            "faults_ruled_out_reasoning": {
                                "type": "string",
                                "description": f"The reasoning behind the faults that were ruled out this round. If none were ruled out, say 'NA'."
                            },
                            f"suggested_tests_for_{self.name}": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": f"Any tests that can be suggested to {self.name} to help diagnose the fault.",
                                }
                            }
                        },
                        "required": [
                            f"message_for_{self.name}",
                            "message_motivation",
                            "faults_ruled_out",
                            "faults_ruled_out_reasoning",
                            f"suggested_tests_for_{self.name}"
                        ],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        else:
            system_prompt = self.system_prompt.format(user_info=self.user_info, max_rounds=self.max_rounds, hypothesized_faults=self.possible_faults)
            text_format = {
            "format": {
                    "type": "json_schema",
                    "name": "agent_response_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            f"message_for_{self.name}": {
                                "type": "string",
                                "description": f"Any message you have for {self.name} to answer. This could be a question, a response to a previous message, or a request for information. Also, this could be about the habitat, the surrounding environment, the current situation, etc."
                            },
                            "message_motivation": {
                                "type": "string",
                                "description": f"The motivation behind the message you are sending to {self.name}."
                            },
                            "hypothesized_faults": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": f"Any faults that you believe might be happening in the habitat based on the evidence at hand.",
                                }
                            },
                            "hypothesized_faults_reasoning": {
                                "type": "string",
                                "description": f"The reasoning behind the faults that you have hypothesized. If none were hypothesized, say 'NA'."
                            },
                            f"suggested_tests_for_{self.name}": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": f"Any tests that can be suggested to {self.name} to help diagnose the fault.",
                                }
                            }
                        },
                        "required": [
                            f"message_for_{self.name}",
                            "message_motivation",
                            "hypothesized_faults",
                            "hypothesized_faults_reasoning",
                            f"suggested_tests_for_{self.name}"
                        ],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }

        # Get response from ChatGPT
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.user_prompt_template.format(user=self.name, question=question, chat_history=self.chat_history)}
            ],
            text=text_format,
            tools=self.get_function_definitions(),
        )
        
        for item in response.output:
            if item.type == 'function_call':
                function_call = item.function_call
                function_name = function_call.name
                function_arguments = function_call.arguments
                if function_name == 'diagnose_fault':
                    answer = function_arguments
                self.func_call = True
            else: 
                answer = response.output_text
                self.func_call = False
                break

        # Add user question to conversation
        self.chat_history.append(
            f"{self.name}: {question}"
        )

        # Add assistant's response to conversation (for context in next question)
        self.chat_history.append(
            f"Agent: {answer}"
        )

        answer = json.loads(answer)
        if not(self.func_call):
            if self.anticipated:
                self.most_recent_ruled_out_faults = answer['faults_ruled_out']
                self.possible_faults = [x for x in self.possible_faults if x not in self.most_recent_ruled_out_faults]
            else:
                self.possible_faults = answer['hypothesized_faults']
        self.num_rounds += 1
        
        # Auto-save if enabled
        if self.auto_save and self.save_path:
            self.save_chat()

        return answer

    def save_chat(self, filepath: str = None):
        """
        Save the chat history to a JSON file.
        
        Args:
            filepath: Optional path to save the chat. If not provided, uses self.save_path
        """
        save_location = filepath or self.save_path
        
        if not save_location:
            print("\n✗ No save path specified.")
            return
        
        try:
            chat_data = {
                "session_info": {
                    "user_name": self.name,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "num_rounds": self.num_rounds,
                    "possible_faults_remaining": self.possible_faults
                },
                "chat_history": self.chat_history
            }
            
            with open(save_location, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Chat saved to: {save_location}\n")
            
        except Exception as e:
            print(f"\n✗ Error saving chat: {e}\n")
    
    def load_chat(self, filepath: str):
        """
        Load a chat history from a JSON file.
        
        Args:
            filepath: Path to the saved chat file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            
            self.chat_history = chat_data.get("chat_history", [])
            session_info = chat_data.get("session_info", {})
            self.num_rounds = session_info.get("num_rounds", 0)
            self.possible_faults = session_info.get("possible_faults_remaining", possible_faults["22"])
            
            print(f"\n✓ Chat loaded from: {filepath}")
            print(f"  Rounds: {self.num_rounds}")
            print(f"  Faults remaining: {len(self.possible_faults)}\n")
            
        except FileNotFoundError:
            print(f"\n✗ File not found: {filepath}\n")
        except Exception as e:
            print(f"\n✗ Error loading chat: {e}\n")

    def reset(self):
        """Clear conversation history and start fresh."""
        self.chat_history = []

    def delete_last_message(self):
        """Remove the last interaction from conversation history."""
        if len(self.chat_history) >= 2:
            # Note: You'd need to store faults ruled out per turn to restore them properly
            self.chat_history = self.chat_history[:-2]
            if self.num_rounds > 0:
                self.num_rounds -= 1
            self.possible_faults.extend(self.most_recent_ruled_out_faults)
        else:
            print("\nNo messages to delete.")

    def chat(self):
        """
        Start an interactive chat session with the agent.
        Type 'quit' or 'exit' to end the session.
        Type 'reset' to clear conversation history.
        Type 'history' to see the conversation history.
        Type 'back' to remove the last user and agent messages.
        """
        print(f"\n{'='*60}")
        print(f"  HARSH Fault Diagnosis Agent - Interactive Chat")
        print(f"{'='*60}")
        print(f"User: {self.name}")
        print(f"Model: {self.model}")
        print("\nCommands:")
        print("  - Type your question to get a response")
        print("  - 'quit' or 'exit' to end session")
        print("  - 'reset' to clear conversation history")
        print("  - 'history' to view conversation")
        print("  - 'back' to remove the last user and agent messages.")
        print(f"{'='*60}\n")
        
        while True:
            try:
                # Get user input
                question = input(f"{self.name}: ")
                
                # Handle empty input
                if not question:
                    continue
                
                # Handle commands
                if question.lower() in ['quit', 'exit']:
                    print("\nEnding chat session. Goodbye!")
                    break
                
                elif question.lower() == 'reset':
                    self.reset()
                    print("\n✓ Conversation history cleared.\n")
                    continue
                
                elif question.lower() == 'history':
                    self._show_history()
                    continue

                elif question.lower() == 'back':
                    self.delete_last_message()
                    print("\n✓ Last user and agent messages deleted, possible faults restored, num_rounds restored.\n")
                    continue

                # Get response from agent
                response = self.ask(question)
                if not(self.func_call):
                    print(f"\nAgent:\nMessage for {self.name}: {response[f'message_for_{self.name}']}\n")
                    print(f"Message Motivation: {response['message_motivation']}\n")
                    if self.anticipated:
                        print(f"Faults Ruled Out: {response['faults_ruled_out']}\n")
                        print(f"Faults Ruled Out Reasoning: {response['faults_ruled_out_reasoning']}\n")
                    else:
                        print(f"Hypothesized Faults: {response['hypothesized_faults']}\n")
                        print(f"Hypothesized Faults Reasoning: {response['hypothesized_faults_reasoning']}\n")
                    print(f"Suggested Tests: {response[f'suggested_tests_for_{self.name}']}\n")
                    print(f"Possible Faults: {self.possible_faults}\n")
                    print(f"Round Number: {self.num_rounds}\n")
                else:
                    print(f"\nAgent:\n{response}\n")
            except KeyboardInterrupt:
                print("\n\nChat interrupted.")
                continue
            except Exception as e:
                print(f"\n✗ Error: {e}\n")
    
    def _show_history(self):
        """Display the conversation history."""
        if not self.chat_history:
            print(f"\n(No conversation history yet)\n")
            return
        
        print(f"\n{'='*60}")
        print("Conversation History")
        print(f"{'='*60}")
        for i, message in enumerate(self.chat_history, 1):
            print(f"{i}. {message}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    anticipated = True
    if anticipated:
        system_prompt = load_prompt(system_prompt_path)
    else:
        system_prompt = load_prompt(system_prompt_no_possible_faults_listed_path)
    user_prompt_template = load_prompt(user_prompt_template_path)

    agent = UnanticipatedFaultChatAgent(
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        user_info=user_info,
        max_rounds=5,
        possible_faults=possible_faults["22"],
        anticipated=anticipated
    )
    
    # Start interactive chat
    agent.chat()