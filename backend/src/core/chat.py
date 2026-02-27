import ollama
 
class ChatSession:
    def __init__(self, model="llama3"):
        self.conversation_history = []
        self.system_prompt = ""
        self.current_persona = None
        self.current_subject = None
        self.model = model

    def set_system_prompt(self, prompt):
        """Set the system prompt for this session"""
        self.system_prompt = prompt
    
    def set_subject_info(self, persona, subject):
        """Store current persona and subject information"""
        self.current_persona = persona
        self.current_subject = subject
    
    def add_message(self, role, content):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_full_context(self):
        """Get the full context for API call
        Returns system prompt + conversation history"""
        return {
            "system_prompt": self.system_prompt,
            "history": self.conversation_history
        }
    
    def send_message(self, user_message):
        """Send a message to Ollama and get response"""
        self.add_message("user", user_message)
        
        # Build messages for Ollama with system prompt
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.conversation_history)
        
        try:
            response = ollama.chat(model=self.model, messages=messages)
            response_content = response['message']['content']
            self.add_message("assistant", response_content)
            return response_content
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            print(f"✗ {error_msg}")
            return error_msg
    
    def send_message_stream(self, user_message):
        """Send a message to Ollama and stream the response"""
        self.add_message("user", user_message)
        
        # Build messages for Ollama with system prompt
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.conversation_history)
        
        try:
            full_response = ""
            for chunk in ollama.chat(model=self.model, messages=messages, stream=True):
                content = chunk['message']['content']
                full_response += content
                yield content
            
            # Add complete assistant response to history
            self.add_message("assistant", full_response)
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            print(f"✗ {error_msg}")
            yield error_msg
    
    def clear_history(self):
        """Clear conversation history (useful when switching subjects)"""
        self.conversation_history = []
    
    def load_history(self, conversation_history):
        """Load conversation history from a saved chat file"""
        self.conversation_history = conversation_history
    
    def get_history_for_logging(self):
        """Format conversation history for logging"""
        log_text = []
        for msg in self.conversation_history:
            role = msg['role'].capitalize()
            content = msg['content']
            log_text.append(f"{role}:\n{content}\n")
        return "\n".join(log_text)

    def set_model(self, model_name: str):
        """Swap the underlying Ollama model."""
        self.model = model_name
        print(f"[info] Model switched to: {model_name}") 