# Fix ModuleNotFoundError in scripts/start_system.py

## Steps:

- [x] Step 1: Edit scripts/start_system.py to add sys.path fix
- [x] Step 2: Edit agents/master_agent.py to fix import paths for ContextAgent and SafetyAgent
- [x] Step 3: Test `python scripts/start_system.py`
- [x] Done: Use attempt_completion
