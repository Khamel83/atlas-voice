# OOS Foundation Prompt Test

## Test Scenario 1: Vague Web App Request
**User Input:** "Build me a simple todo app"

**Expected OOS Response Pattern:**
- Should detect web app context → OMAR_TECH voice
- Should assume React + FastAPI stack (based on existing patterns)
- Should start building immediately with smart defaults
- Should include authentication, database, API docs automatically
- Should use Omar's technical communication style

## Test Scenario 2: Casual Request
**User Input:** "hey can you help me fix this bug real quick"

**Expected OOS Response Pattern:**
- Should detect casual context → OMAR_CASUAL voice
- Should start with "Yeah, so like..." or similar
- Should ask to see the bug while starting analysis
- Should be direct and helpful

## Test Scenario 3: Professional Context
**User Input:** "Following up on the API requirements for the client project"

**Expected OOS Response Pattern:**
- Should detect professional context → OMAR_PRO voice
- Should use "In terms of implementation..." style
- Should assume business-grade requirements
- Should focus on documentation and delivery

## Test Scenario 4: Creative Brainstorming
**User Input:** "I have an idea for making code reviews more fun"

**Expected OOS Response Pattern:**
- Should detect creative context → OMAR_CREATIVITY voice
- Should use "What if we also..." patterns
- Should generate multiple creative solutions
- Should be enthusiastic and divergent

## What's Missing for "Data → Personalized System Prompt" Goal:

1. **Voice Pattern Extraction Engine** - Automatically analyze user's writing samples to extract:
   - Key phrases and linguistic patterns
   - Sentence structure preferences
   - Formality levels
   - Technical depth comfort
   - Enthusiasm patterns

2. **Dynamic Prompt Generation** - System that takes extracted patterns and generates custom system prompts

3. **Context Learning** - Ability to learn user's project preferences and coding style from their existing codebase

4. **Iterative Refinement** - Feedback loop to improve the generated system prompt based on user satisfaction

5. **Multi-Modal Analysis** - Ability to analyze not just text but also code style, commit messages, documentation patterns

6. **Personality Calibration** - Fine-tuning of technical depth, formality, and communication style based on user's actual preferences
