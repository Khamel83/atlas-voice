#!/usr/bin/env python3
"""
Intelligent Interface for Atlas Voice
Understands natural language requests and executes appropriate actions
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class IntelligentInterface:
    """AI-powered interface that understands natural user requests"""

    def __init__(self):
        self.data_dir = Path("data")
        self.profiles_dir = Path("profiles")
        self.prompts_dir = Path("prompts")
        self.temp_dir = Path("temp")

        # Ensure directories exist
        for dir_path in [self.data_dir, self.profiles_dir, self.prompts_dir, self.temp_dir]:
            dir_path.mkdir(exist_ok=True)

        # Import our core modules
        from style_analyzer import FinalStylePreservationSystem
        from main import VoiceMatchCLI

        self.analyzer = None
        self.cli = VoiceMatchCLI()

        # Intent patterns
        self.intent_patterns = {
            'analyze_once': [
                r'analyze.*once.*delete',
                r'use.*once.*remove',
                r'one time.*analysis',
                r'temporary.*analysis',
                r'delete.*after.*process',
                r'process.*and.*delete'
            ],
            'create_voice': [
                r'create.*voice',
                r'make.*voice.*profile',
                r'generate.*voice',
                r'voice.*profile',
                r'sound like.*me',
                r'capture.*my.*voice'
            ],
            'ask_question': [
                r'ask.*question',
                r'how.*would.*i.*say',
                r'what.*would.*i.*say',
                r'in.*my.*voice',
                r'use.*my.*voice'
            ],
            'export_prompt': [
                r'export.*prompt',
                r'get.*prompt',
                r'save.*prompt',
                r'copy.*prompt',
                'give.*me.*prompt'
            ],
            'show_analysis': [
                r'show.*analysis',
                r'what.*did.*you.*find',
                r'how.*do.*i.*sound',
                r'voice.*analysis',
                'tell.*me.*about.*my.*voice'
            ],
            'list_profiles': [
                r'list.*profiles',
                r'what.*profiles',
                r'show.*voices',
                r'my.*voices'
            ],
            'delete_data': [
                r'delete.*all.*data',
                r'remove.*everything',
                r'clean.*up',
                r'start.*over',
                r'reset.*everything'
            ],
            'help': [
                r'help',
                r'what.*can.*you.*do',
                r'how.*do.*i.*use.*this',
                r'what.*are.*the.*commands'
            ]
        }

        # Contextual information extraction patterns
        self.extraction_patterns = {
            'data_source': [
                r'(?:from|using|with).*?([^.\n]+?)(?:\.|$|\n|and|then)',
                r'(?:directory|folder|data).*?([^.\n]+?)(?:\.|$|\n|and|then)',
                r'([^\s]+/[^.\n]+)(?:\.|$|\n|and|then)'
            ],
            'profile_name': [
                r'(?:named?|called?|as)\s+([^\s.,]+)',
                r'profile\s+([^\s.,]+)',
                r'voice\s+([^\s.,]+)'
            ],
            'question': [
                r'["\'](.*?)["\']',
                r'(?:ask|say|question|how|what|when|where|why)(.*?)(?:\.|$|\n|and|then)',
            ],
            'delete_after': [
                r'(?:delete|remove|clean.*up|temporary)',
                r'(?:once|one.*time|temporary)',
                r'(?:after.*process|when.*done)'
            ]
        }

    def understand_intent(self, user_input: str) -> Tuple[str, Dict]:
        """Understand user intent and extract relevant information"""
        user_input = user_input.lower().strip()

        # Determine primary intent
        intent = 'unknown'
        confidence = 0

        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input):
                    intent = intent_name
                    confidence += 1

        # Extract contextual information
        context = self._extract_context(user_input)

        # Handle special cases
        if any(phrase in user_input for phrase in ['once', 'temporary', 'delete after', 'clean up after', 'remove after']):
            context['delete_after'] = True

        # Fix data source extraction - remove "once" and similar words
        if 'data_source' in context:
            data_source = context['data_source']
            for word in ['once', 'temporary', 'and delete', 'and clean', 'after processing']:
                data_source = data_source.replace(word, '').strip()
            context['data_source'] = data_source.strip()

        return intent, context

    def _extract_context(self, user_input: str) -> Dict:
        """Extract contextual information from user input"""
        context = {}

        # Extract data source
        for pattern in self.extraction_patterns['data_source']:
            matches = re.findall(pattern, user_input)
            if matches:
                context['data_source'] = matches[0].strip()
                break

        # Extract profile name
        for pattern in self.extraction_patterns['profile_name']:
            matches = re.findall(pattern, user_input)
            if matches:
                context['profile_name'] = matches[0].strip()
                break

        # Extract question
        for pattern in self.extraction_patterns['question']:
            matches = re.findall(pattern, user_input)
            if matches:
                context['question'] = matches[0].strip().strip('"\'')
                break

        return context

    def execute_request(self, user_input: str) -> str:
        """Execute user request based on understood intent"""
        intent, context = self.understand_intent(user_input)

        # Initialize analyzer if needed
        if self.analyzer is None and intent in ['analyze_once', 'create_voice']:
            from style_analyzer import FinalStylePreservationSystem
            self.analyzer = FinalStylePreservationSystem(str(self.data_dir))

        # Execute based on intent
        try:
            if intent == 'analyze_once':
                return self._handle_analyze_once(context)
            elif intent == 'create_voice':
                return self._handle_create_voice(context)
            elif intent == 'ask_question':
                return self._handle_ask_question(context)
            elif intent == 'export_prompt':
                return self._handle_export_prompt(context)
            elif intent == 'show_analysis':
                return self._handle_show_analysis(context)
            elif intent == 'list_profiles':
                return self._handle_list_profiles(context)
            elif intent == 'delete_data':
                return self._handle_delete_data(context)
            elif intent == 'help':
                return self._handle_help(context)
            else:
                return self._handle_unknown_intent(user_input, context)

        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}\n💡 Try rephrasing your request or ask for help."

    def _handle_analyze_once(self, context: Dict) -> str:
        """Handle one-time analysis request"""
        if 'data_source' not in context:
            return "❌ I need to know where your data is located. Please specify the directory or file path."

        data_path = Path(context['data_source'])
        if not data_path.exists():
            return f"❌ I can't find data at: {data_path}"

        profile_name = context.get('profile_name', 'temp_analysis')

        # Privacy check
        self.cli._privacy_check_import_dir(str(data_path))

        response = []
        response.append(f"📥 Analyzing your data from: {data_path}")
        response.append("🔒 Privacy: I'll delete source files after processing")

        # Import and analyze
        texts_processed = 0
        for file_path in data_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.eml']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content.strip()) > 100:
                            self.analyzer.analyze_text(content)
                            texts_processed += 1
                except Exception as e:
                    response.append(f"⚠️  Skipped {file_path.name}: {e}")

        if texts_processed == 0:
            return "❌ No valid text files found to analyze"

        # Generate results
        profile = self.analyzer.generate_voice_profile()
        prompt = self.analyzer.generate_final_prompt()

        # Save temporarily
        temp_profile = self.temp_dir / f"{profile_name}.json"
        temp_prompt = self.temp_dir / f"{profile_name}.txt"

        with open(temp_profile, 'w') as f:
            json.dump(profile, f, indent=2)

        with open(temp_prompt, 'w') as f:
            f.write(prompt)

        response.append(f"✅ Analyzed {self.analyzer.total_words:,} words from {texts_processed} files")
        response.append(f"📊 Your voice profile saved to: {temp_prompt}")
        response.append(f"🎭 Average sentence length: {profile['avg_sentence_length']:.1f} words")

        # Delete source files if requested
        if context.get('delete_after', False):
            self.cli._cleanup_source_files(str(data_path), delete_files=True)
            response.append("🗑️  Source files deleted as requested")

        response.append(f"\n📄 Your voice prompt is ready! You can copy it from: {temp_prompt}")

        return "\n".join(response)

    def _handle_create_voice(self, context: Dict) -> str:
        """Handle create voice profile request"""
        if 'data_source' not in context:
            return "❌ I need to know where your data is. Please specify the directory or file path."

        data_path = Path(context['data_source'])
        if not data_path.exists():
            return f"❌ I can't find data at: {data_path}"

        profile_name = context.get('profile_name', 'my_voice')

        # Use the CLI import functionality
        os.system(f"python3 src/main.py import-data --data-dir {data_path} --profile-name {profile_name}")

        return f"✅ Created voice profile '{profile_name}'! You can now use it to sound like yourself."

    def _handle_ask_question(self, context: Dict) -> str:
        """Handle ask question in voice request"""
        if 'question' not in context:
            return "❌ What question would you like me to answer in your voice?"

        question = context['question']
        profile_name = context.get('profile_name', 'my_voice')

        # Check if profile exists
        profile_path = self.profiles_dir / f"{profile_name}.json"
        prompt_path = self.prompts_dir / f"{profile_name}.txt"

        if not profile_path.exists():
            return f"❌ Voice profile '{profile_name}' not found. Create one first."

        # Show the prompt and question
        response = []
        response.append(f"🎤 Using your voice profile '{profile_name}':")
        response.append("=" * 50)

        with open(prompt_path, 'r') as f:
            response.append(f.read())

        response.append("=" * 50)
        response.append(f"❓ Ask this: {question}")

        return "\n".join(response)

    def _handle_export_prompt(self, context: Dict) -> str:
        """Handle export prompt request"""
        profile_name = context.get('profile_name', 'my_voice')

        # Use CLI functionality
        result = os.system(f"python3 src/main.py export-prompt --profile-name {profile_name}")
        return f"✅ Exported prompt for profile '{profile_name}'"

    def _handle_show_analysis(self, context: Dict) -> str:
        """Handle show analysis request"""
        profile_name = context.get('profile_name', 'my_voice')

        # Use CLI functionality
        result = os.system(f"python3 src/main.py analyze-profile --profile-name {profile_name}")
        return f"📊 Analysis for profile '{profile_name}' shown above"

    def _handle_list_profiles(self, context: Dict) -> str:
        """Handle list profiles request"""
        profiles = list(self.profiles_dir.glob("*.json"))

        if not profiles:
            return "❌ No voice profiles found. Create one by analyzing your writing data."

        response = ["🎭 Your available voice profiles:"]
        for profile in profiles:
            prompt_file = self.prompts_dir / f"{profile.stem}.txt"
            status = "✅ Ready" if prompt_file.exists() else "⚠️  Incomplete"
            response.append(f"   {status} {profile.stem}")

        return "\n".join(response)

    def _handle_delete_data(self, context: Dict) -> str:
        """Handle delete all data request"""
        response = []

        # Delete profiles
        for profile_file in self.profiles_dir.glob("*.json"):
            profile_file.unlink()
            response.append(f"🗑️  Deleted profile: {profile_file.name}")

        # Delete prompts
        for prompt_file in self.prompts_dir.glob("*.txt"):
            prompt_file.unlink()
            response.append(f"🗑️  Deleted prompt: {prompt_file.name}")

        # Delete temp files
        for temp_file in self.temp_dir.glob("*"):
            temp_file.unlink()
            response.append(f"🗑️  Deleted temp file: {temp_file.name}")

        if not response:
            response.append("✅ No data to delete")
        else:
            response.append("✅ All data cleaned up!")

        return "\n".join(response)

    def _handle_help(self, context: Dict) -> str:
        """Handle help request"""
        return """
🤖 Atlas Voice - Intelligent Interface

I can understand natural requests like:

📊 **Analysis:**
• "Analyze my data once and delete it after"
• "Process all my emails and clean up"
• "Create a temporary voice profile from my texts"

🎭 **Voice Profiles:**
• "Create a voice profile from my data"
• "Make me sound like myself using these documents"
• "Generate my voice pattern from my writing"

❓ **Questions:**
• "How would I say 'hello' in my voice?"
• "Ask 'what do you think about AI' in my voice"
• "Use my voice to answer this question"

📄 **Export:**
• "Give me my voice prompt"
• "Export my voice profile"
• "Show me my voice template"

🔍 **Analysis:**
• "Show my voice analysis"
• "What did you find in my writing?"
• "How do I sound according to the analysis?"

🗑️ **Cleanup:**
• "Delete all my data"
• "Clean up everything"
• "Remove all profiles"

💡 **Just ask naturally what you want to do!**
"""

    def _handle_unknown_intent(self, user_input: str, context: Dict) -> str:
        """Handle unknown or unclear intent"""
        response = [
            "❌ I'm not sure what you want me to do.",
            "💡 Here are some things I can help you with:",
            "",
            "📊 Analyze your writing data",
            "🎭 Create voice profiles",
            "❓ Answer questions in your voice",
            "📄 Export voice prompts",
            "🔍 Show voice analysis",
            "🗑️ Clean up data",
            "",
            "💬 Try asking in a different way, or type 'help' for more options."
        ]
        return "\n".join(response)

    def interactive_session(self):
        """Start an interactive session with the user"""
        print("🤖 Atlas Voice - Intelligent Interface")
        print("💬 Ask me anything naturally! Type 'quit' to exit.")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n💭 What would you like to do? ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break

                if not user_input:
                    continue

                response = self.execute_request(user_input)
                print(f"\n{response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Something went wrong: {e}")
                print("💡 Try asking in a different way.")
