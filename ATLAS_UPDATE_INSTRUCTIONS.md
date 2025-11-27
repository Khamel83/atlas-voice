# 🚀 Update Atlas Project to Latest OOS

## **One Command Update:**

```bash
# In your Atlas project directory, run:
curl -sSL https://raw.githubusercontent.com/khamel83/oos/main/update-oos.sh | bash
```

## **Or Local Update (if you have OOS source):**

```bash
# Copy the updater to your Atlas project
cp /path/to/oos/update_oos.py /path/to/atlas/
cd /path/to/atlas/
python3 update_oos.py
```

## **Or Manual Update (from this Speech directory):**

```bash
# From your Atlas project directory:
python3 /Users/khamel83/dev/atlas-voice/update_oos.py --project .
```

## **What It Does:**

✅ **Analyzes your Atlas project** - Checks what's already there
✅ **Backs up existing files** - Safe, non-destructive update
✅ **Updates only what's needed** - Smart file comparison
✅ **Adds strategic consultant** - Full `/consultant` command
✅ **Enhances existing commands** - Keeps your Atlas functionality
✅ **Tests installation** - Verifies everything works
✅ **Shows summary** - Clear report of changes

## **After Update:**

1. **Restart Claude Code**
2. **Test with:** `/consultant "How can we improve Atlas?"`
3. **Check status:** `/consultant status`
4. **View dashboard:** `/consultant dashboard`

## **Example Atlas Usage:**

```bash
# Strategic analysis for Atlas
/consultant "How do we scale Atlas to handle 1M requests?"
/consultant "Should we migrate Atlas from Python to Go?"
/consultant "What's the fastest way to add real-time features to Atlas?"

# Project management
/consultant status
/consultant monitor atlas_scaling_project
/consultant dashboard

# Enhanced creation (if Atlas has project creation)
/create "microservice for Atlas data processing"
```

## **What Gets Updated:**

- ✅ **Strategic Consultant Brain** (`src/strategic_consultant.py`)
- ✅ **Archon Integration** (`src/archon_integration.py`)
- ✅ **Execution Monitoring** (`src/execution_driver.py`)
- ✅ **Adaptive Planning** (`src/adaptive_planner.py`)
- ✅ **Enhanced Commands** (`src/commands/consultant_command.py`)
- ✅ **Configuration** (`config/consultant.yaml`)
- ✅ **Templates** (`templates/*.j2`)
- ✅ **Command Handler** (enhanced, not replaced)

## **What Stays The Same:**

- ✅ **All your Atlas code** - Unchanged
- ✅ **Existing functionality** - Fully preserved
- ✅ **Project structure** - Maintained
- ✅ **Dependencies** - Only adds what's needed

**Your Atlas project gets strategic intelligence without breaking anything.**

---

**Ready to make Atlas smarter? Run the one-command update!**