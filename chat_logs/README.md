# Chat Logs Directory

This directory contains automatically saved conversation logs from the HARSH Fault Diagnosis Agent.

## File Types

### 1. JSON Files (`session_YYYYMMDD_HHMMSS.json`)
- **Purpose**: Machine-readable format with complete session data
- **Contents**: 
  - Session metadata (user, model, timestamp, rounds)
  - Complete chat history
  - Remaining possible faults
- **Use**: For programmatic analysis or reloading sessions

### 2. Readable Transcripts (`session_YYYYMMDD_HHMMSS_readable.txt`)
- **Purpose**: Human-readable conversation transcript
- **Contents**:
  - Formatted conversation with clear sections
  - Messages, motivations, and reasoning
  - Faults ruled out with explanations
  - Suggested tests for user
  - Final list of remaining possible faults
- **Use**: For easy reading, sharing, or documentation

## Auto-Save Behavior

When `auto_save=True` is enabled (default):
- Both files are saved after **every conversation round**
- Files are timestamped to avoid overwriting
- Directory is created automatically if it doesn't exist

## Manual Save

You can also save manually during a session by typing `save` in the interactive chat.

## Example Output Structure

```
chat_logs/
├── session_20251112_143045.json          (machine-readable)
├── session_20251112_143045_readable.txt  (human-readable)
├── session_20251112_155230.json
└── session_20251112_155230_readable.txt
```

## Tips

- Readable transcripts are perfect for copying/pasting into reports
- JSON files can be loaded back into the agent using `agent.load_chat(filepath)`
- Old logs can be archived or deleted to keep this directory clean

