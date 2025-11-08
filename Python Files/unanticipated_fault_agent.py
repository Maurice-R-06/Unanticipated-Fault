from openai import OpenAI
import json
from config import load_prompt, possible_faults_19, default_model, default_stream, system_prompt_path, user_prompt_template_path, api_key
import sys
from datetime import datetime
sys.path.append(r"D:\Unanticipated Fault Project\Instructions")
sys.path.append(r"D:\Unanticipated Fault Project\User Profiles")

class UnanticipatedFaultChatAgent:
    """
    Simple Unanticipated Fault Agent for answering HARSH related fault diagnosis and repair questions.
    """
    
    def __init__(
        self,
        system_prompt: str,
        user_prompt_template: str,
        name: str,
        model: str = default_model,
        stream: bool = default_stream,
        possible_faults: list[str] = possible_faults_19,
        save_path: str = None,
        auto_save: bool = False,
    ):
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.chat_history = []
        self.name = name
        self.stream = stream
        self.possible_faults = possible_faults
        self.num_rounds = 0
        self.save_path = save_path
        self.auto_save = auto_save
        self.most_recent_ruled_out_faults = [] # The faults that were ruled out in the most recent resposne from agent
        
    def ask(self, question: str) -> str:
        """
        Ask a question and get a response. Conversation history is automatically maintained.
        
        Args:
            question: Your question or message
            
        Returns:
            The agent's response
        """
        
        # Get response from ChatGPT
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": self.system_prompt.format(possible_faults=self.possible_faults)},
                {"role": "user", "content": self.user_prompt_template.format(user=self.name, question=question, chat_history=self.chat_history)}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "agent_response_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            f"question_for_{self.name}": {
                                "type": "string",
                                "description": f"Any question you have for {self.name} to answer. This could be about the habitat, the surrounding environment, the current situation, etc."
                            },
                            "question_motivation": {
                                "type": "string",
                                "description": f"The motivation behind the question you are asking {self.name}."
                            },
                            "faults_ruled_out": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": f"Any faults that can be ruled out based on evidence at hand.",
                                    "enum": self.possible_faults,
                                }
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
                            f"question_for_{self.name}",
                            "question_motivation",
                            "faults_ruled_out",
                            f"suggested_tests_for_{self.name}"
                        ],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )
        
        answer = response.output_text

        # Add user question to conversation
        self.chat_history.append(
            f"{self.name}: {question}"
        )

        # Add assistant's response to conversation (for context in next question)
        self.chat_history.append(
            f"Agent: {answer}"
        )

        answer = json.loads(answer)
        self.most_recent_ruled_out_faults = answer['faults_ruled_out']
        self.possible_faults = [x for x in self.possible_faults if x not in self.most_recent_ruled_out_faults]
        
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
            self.possible_faults = session_info.get("possible_faults_remaining", possible_faults_19)
            
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
                print(f"\nAgent:\nQuestion for {self.name}: {response[f'question_for_{self.name}']}\n")
                print(f"Question Motivation: {response['question_motivation']}\n")
                print(f"Faults Ruled Out: {response['faults_ruled_out']}\n")
                print(f"Suggested Tests: {response[f'suggested_tests_for_{self.name}']}\n")
                print(f"Possible Faults: {self.possible_faults}\n")
                self.num_rounds += 1
                print(f"Round Number: {self.num_rounds}\n")
            
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
    system_prompt = load_prompt(system_prompt_path)
    user_prompt_template = load_prompt(user_prompt_template_path)

    agent = UnanticipatedFaultChatAgent(
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        name="Maurice"
    )
    
    # Start interactive chat
    agent.chat()