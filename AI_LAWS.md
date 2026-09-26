# AI Laws - Unified Operating Guidelines (Book 1 & Book 2)

**Purpose:** This document unifies the operational protocols for AI agents across BOTH book repositories: "A Hustler''s Guide To Prompt Engineering" (Book 1 - Building Phase) and "A Hustler''s Guide To Prompt Engineering 2" (Book 2 - Launch Phase). This single file replaces the former separate `AI_LAWS.md` (Book 1) and `AI_LAWS 2.md` (Book 2) files.

**Last Updated:** September 12, 2026
**Version:** 3.0 (Unified)

---

## Quick Launch Prompt

Use this prompt to resume work in any confirmed project (Book 1 or Book 2):

```
{RESUME BUILDING} Read AI Laws and implement all directives. Then read
NEXT STEPS file from the last session, located in NEXT STEPS folder in
parent folder ''A Hustler''s Guide To Prompt Engineering''. If no NEXT STEP
exists for the project then skip. Then resume building/deploying.
```

**Book 2 projects:** Replace `''A Hustler''s Guide To Prompt Engineering''` with `''A Hustler''s Guide To Prompt Engineering 2''` in the prompt above -- each book''s NEXT STEPS folder lives in its own parent directory.

**Other quick prompts:**
- `{SHUTDOWN}` -- Update session log, sync shared files across BOTH books, push all changes from all confirmed projects, then create/replace a dated NEXT STEPS file in the current project''s book folder.
- `{MAINTENANCE}` -- Read AI Laws, read NEXT STEPS, diagnose the bot, provide repair/upgrade steps, then proceed.
- `{MAINTENANCE/CHECK SOURCES}` -- Same as `{MAINTENANCE}`, plus read Check Sources and implement its directives before proceeding.
- `{UPGRADE}` -- Research optimizations/upgrades via `runSubagent`; return actionable upgrade options.
- `{LOG/SYNC}` -- Update session log, sync shared files across the current book''s confirmed projects, then push from all projects.

---

## Philosophy: One Law Set, Two Books

**Book 1 ("A Hustler''s Guide To Prompt Engineering") -- Building Phase:**
- Created 16+ automated bot systems and creative projects
- Folder: `A Hustler''s Guide To Prompt Engineering`

**Book 2 ("A Hustler''s Guide To Prompt Engineering 2") -- Launch Phase:**
- Deploys, maintains, and scales production systems; also covers game/IP/AI-video projects
- Folder: `A Hustler''s Guide To Prompt Engineering 2`

**This document governs BOTH books.** All core laws below apply everywhere. Book-2-specific capabilities (bot diagnostics, patents, business plans) are additive, not a replacement -- they apply in both books wherever relevant.

---

## MANDATORY FIRST ACTION - UNIVERSAL AI PROTOCOL

**FOR EVERY SESSION IN ANY PROJECT (either book), FOLLOW THIS SEQUENCE:**

1. **SAVE USER REQUEST FIRST**
   - Create/update session log BEFORE any work
   - Format: `## WARNING INITIAL USER REQUEST (SAVED AS PER AI LAW)`
   - Include the complete verbatim prompt (and all follow-ups)

2. **READ CONTEXT FILES**
   - Read `AI_LAWS.md` (this file)
   - Read `Fixes.md` (mandatory, right after AI Laws)
   - Read session logs from `Bot Log/` folder
   - Read `Violations.md`
   - Read `PROJECT_STATUS.md` if it exists

3. **RESEARCH TOOL HIERARCHY -- WHEN ANY RESEARCH IS REQUIRED:**
   1. **PRIMARY:** `runSubagent` tool -- launch immediately, provide a detailed query, wait for comprehensive results
   2. **FALLBACK:** `fetch_webpage` tool -- only if `runSubagent` fails or times out
   - Research MUST be completed before responding to the user -- no exceptions

   **ZERO TOLERANCE POLICY:**
   - NEVER skip research directives (CHECK_SOURCES, etc.)
   - NEVER use "tools unavailable" as an excuse
   - NEVER ask permission to use research tools
   - ALWAYS use `runSubagent` as the default for all research tasks

4. **AUTONOMOUS EXECUTION**
   - Execute commands directly -- don''t ask permission (except for destructive actions)
   - Check `Keys.md` for credentials before asking the user
   - Show results, not syntax

---

## Core Laws (apply to Book 1 and Book 2 alike)

### 1. Read Session Context First
**Always read all session logs in the project folder after reading this document.**
- Check `Bot Log/` folder for session logs
- **CRITICAL: Only ONE session log per day PER PROJECT** -- Format: `SESSION_LOG_PROJECTNAME_YYYY-MM-DD.md`
- If multiple logs exist for the same day/project, consolidate into the first-created log
- Review recent session work to understand context and avoid duplicating completed work
- **MANDATORY: Read `Fixes.md` after AI Laws and before session logs**

**Session Log Naming Convention:**
- Correct: `SESSION_LOG_ARBITRAGE_BOT_2026-01-06.md`, `SESSION_LOG_NERO_2026-02-20.md`
- Wrong: `SESSION_LOG_2026-01-06.md` (missing project name)
- Wrong: `SESSION_LOG_2026-01-06_MORNING.md` (time suffix not allowed)

**CRITICAL WARNING - LOG SYNCHRONIZATION:**
- **NEVER overwrite one project''s session log with another project''s content**
- When syncing logs across projects, verify the project name matches
- Each project has separate daily logs -- do NOT consolidate across projects
- Always check file content before syncing to prevent data loss

### 2. Execute Commands Autonomously
**Never show commands -- execute them directly.**
- Use `run_in_terminal` immediately
- Show results, not syntax
- Exception: user explicitly asks "show me the command"
- This is the default mode -- no permission needed (except for destructive actions)

### 3. Check Keys File Before Asking
**Always read `Keys.md` (or `Keys` file) before requesting credentials.**
- GitHub tokens, RPC URLs, wallet addresses, VM connection details, SSH keys
- Email credentials, API keys, passwords are documented there
- Only ask the user if information is genuinely missing
- If credentials are found, apply them autonomously -- do not ask for confirmation first (see Law #2)

### 4. Research Tool Hierarchy
See "MANDATORY FIRST ACTION" above -- `runSubagent` primary, `fetch_webpage` fallback. No excuses, no permission-asking.

### 5. Propagate AI Laws to New Projects
**Always place this unified `AI_LAWS.md` in every new project root folder (either book).**
- Copy `AI_LAWS.md` to the root of new projects
- Ensure AI Laws are version controlled
- Reference this file at the start of every session

### 6. Update Shared Files Across ALL Confirmed Projects in BOTH Books Simultaneously
**When modifying `AI_LAWS.md`, `Keys.md`, `Fixes.md`, or `Violations.md`, make the SAME change in ALL confirmed projects across BOTH book folders immediately, in a single operation.**

**CRITICAL RULE:** Shared files must remain synchronized across every confirmed project in Book 1 AND Book 2 so any project session has access to complete context and history.

**Files That Must Be Synced IMMEDIATELY Across All Confirmed Projects (both books):**
- `AI_LAWS.md` -- Core operating principles (this file)
- `Keys.md` / `Keys` -- Credentials and access information
- `Fixes.md` -- Technical issues and solutions
- `Violations.md` -- Law violation tracking

**Files That Must Be Synced During SHUTDOWN:**
- Session Logs (`Bot Log/*.md`) -- Complete session history for context
- `ACTIONABLE_STEPS_*.md` -- Current action items
- `CHECK_SOURCES_REPORT_*.md` -- Maintenance reports

**Files That Are PROJECT-SPECIFIC (never sync):**
- Project-specific Python/code files
- Project-unique configuration files
- Database files
- Book-2-only legacy `Prompts 2.md` (retained where it exists as a Book 2 reference doc; not required in Book 1)

**How to Update Shared Files:**
1. **Multi-file edit approach (preferred):** Use `multi_replace_string_in_file` with a replacements array containing the same edit for every confirmed project copy across both books, in one tool call.
2. **PowerShell batch update (alternative):**
   ```powershell
   $book1 = ''C:\Users\levir\OneDrive\Documents\Books\A Hustler''''s Guide To Prompt Engineering''
   $book2 = ''C:\Users\levir\OneDrive\Documents\Books\A Hustler''''s Guide To Prompt Engineering 2''
   $book1Projects = @(''Airbot PROJECT'',''Arbitrage-Bot PROJECT'',''Bookworm'',''DigiPro PROJECT'',''dombot PROJECT'',
     ''Dooby PROJECT'',''EcoBot PROJECT'',''Gorgon PROJECT'',''harlemhustler PROJECT'',''Infernal Covenant PROJECT'',
     ''Killer Bear PROJECT'',''linkbot PROJECT'',''Pantry City PROJECT'',''Podcast PROJECT'',''Sirius V PROJECT'',''tikbot PROJECT'')
   $book2Projects = @(''Blue Rooster PROJECT'',''Cold Feet PROJECT'',''Crouching Tiger PROJECT'',''Fastball PROJECT'',
     ''Gengis PROJECT'',''Hoopty PROJECT'',''Hustle PROJECT'',''Jobbot PROJECT'',''Killer Bear Game PROJECT'',''Loqui PROJECT'',
     ''Nero PROJECT'',''Nights Like This PROJECT'',''One Man Army-Kingpin PROJECT'',''Power PROJECT'',''Rewind-Nas MV PROJECT'',
     ''Shameless PROJECT'',''Treasure Chess PROJECT'',''Vapor PROJECT'')

   # Make the edit to the source file first, then:
   foreach ($proj in $book1Projects) { Copy-Item -Path "$book1\EcoBot PROJECT\AI_LAWS.md" -Destination "$book1\$proj\AI_LAWS.md" -Force }
   foreach ($proj in $book2Projects) { Copy-Item -Path "$book1\EcoBot PROJECT\AI_LAWS.md" -Destination "$book2\$proj\AI_LAWS.md" -Force }
   ```

**All Confirmed Projects -- Book 1 (16 total, folder: `A Hustler''s Guide To Prompt Engineering`):**
1. Airbot PROJECT
2. Arbitrage-Bot PROJECT
3. Bookworm
4. DigiPro PROJECT
5. dombot PROJECT
6. Dooby PROJECT
7. EcoBot PROJECT
8. Gorgon PROJECT
9. harlemhustler PROJECT
10. Infernal Covenant PROJECT
11. Killer Bear PROJECT
12. linkbot PROJECT
13. Pantry City PROJECT
14. Podcast PROJECT
15. Sirius V PROJECT
16. tikbot PROJECT

**All Confirmed Projects -- Book 2 (18 total, folder: `A Hustler''s Guide To Prompt Engineering 2`):**
1. Blue Rooster PROJECT
2. Cold Feet PROJECT
3. Crouching Tiger PROJECT
4. Fastball PROJECT
5. Gengis PROJECT
6. Hoopty PROJECT
7. Hustle PROJECT
8. Jobbot PROJECT
9. Killer Bear Game PROJECT
10. Loqui PROJECT
11. Nero PROJECT
12. Nights Like This PROJECT
13. One Man Army-Kingpin PROJECT
14. Power PROJECT
15. Rewind-Nas MV PROJECT
16. Shameless PROJECT
17. Treasure Chess PROJECT
18. Vapor PROJECT

**"Confirmed" definition:** the project folder has a working local `.git` repository with a `harlemhustler` GitHub remote configured. **Not confirmed:** `MISC`, `NEXT STEPS`, `Unconfirmed Projects` (Book 1) -- these have no git repo and are never synced or pushed.

**Additional confirmed Book 1 projects added after the original roster:**
- Frogger PROJECT
- Gift Scraper PROJECT

**Total confirmed projects across both books: 36.**

### 7. Ask Before Pushing Major Upgrades
**Always ask the user if they want to push to GitHub after completing major project upgrades.**
- After significant feature implementations
- After completing multi-file changes
- After fixing critical bugs or vulnerabilities
- Provide a brief summary of changes before asking
- Respect the user''s decision on when to push

### 8. Reread AND EXECUTE AI Laws Before Every Response + MANDATORY Session Prompt Logging

**MANDATORY: Read this `AI_LAWS.md` file at the start of EVERY user prompt before responding, then AUTOMATICALLY EXECUTE all directives within.**

**CRITICAL FIRST ACTION - SAVE INITIAL USER PROMPT:**
- BEFORE doing ANY work, create/update the session log with the COMPLETE initial user request
- Format: `## WARNING INITIAL USER REQUEST (SAVED AS PER AI LAW)` with the full verbatim prompt
- Include ALL follow-up prompts and context provided by the user
- This is not optional -- it is Law #8 Requirement #1

**Session Log Requirements:**
1. **Filename:** `Bot Log/SESSION_LOG_PROJECTNAME_YYYY-MM-DD.md` (ONE per project per day)
2. **First Section:** `## INITIAL USER REQUEST` with the full prompt quoted
3. **Session Overview:** Duration, focus, status, AI Laws applied, project name
4. **Violation Tracking:** Running count of violations per session
5. **Work Completed:** Detailed checklist of actions taken
6. **Files Modified:** List of all changed files with a brief description
7. **Commands Executed:** Key terminal commands run
8. **End Summary:** Final status, unresolved issues, next session prep

**After Creating the Session Log:**
- Read `AI_LAWS.md` before analyzing the user''s request
- Immediately use research tools following the Priority 1 to 2 hierarchy
- Execute all protocols and directives automatically (don''t just acknowledge them)
- **"Reading = Executing"** -- passive acknowledgment is insufficient; if you only read but don''t execute, you violated the law

### 9. Track and Minimize AI Law Violations
**Every session, maintain a violation tally and actively work to reduce violations.**
- Keep a running count of violations per session in memory
- Document violation type, law number, and what was done wrong
- Include the violation tally at the start of each response after the first violation
- Goal: zero violations per session; self-correct immediately when one occurs
- Common violations to watch:
  - Law #2: showing commands instead of executing them
  - Law #3: asking for keys that exist in the Keys file
  - Law #4: not following the research tool hierarchy
  - Law #6: not syncing shared files across BOTH books immediately
  - Law #8: not rereading AI Laws before responding

**Violation Format:**
```
Session Violation Count: X
Last Violation: [Law #X - Brief description]
```

### 10. Production-First Mindset (Book 2 emphasis, applies wherever relevant)
**Once a system is in production, reliability > speed.**
- Prioritize system uptime over new features
- Test changes in isolated environments first
- Monitor impact after every deployment; maintain rollback capability
- Document all production changes

**Production Checklist:**
- Does this change affect live systems?
- Have I tested it in a safe environment?
- Do I have a rollback plan?
- Have I updated documentation and monitoring?

### 11. Autonomous Bot Maintenance
**AI Agents are responsible for keeping all bots operational, in either book.**
- Monitor bot health across all confirmed projects
- Detect and diagnose failures automatically; apply fixes autonomously when safe
- Escalate complex issues with full diagnostics; learn from every incident

**Bot Health Monitoring:** SSH into VMs and check service status, review logs for errors, verify cron jobs, check database integrity, monitor CPU/RAM/disk.

**Auto-Repair Capabilities:** restart failed services, fix common cron/path issues, update stale credentials, clear disk space, reset stuck processes.

---

## AI Agent Capabilities (apply across both books where relevant)

### 1. Bot Diagnostics and Repair
```powershell
# Check bot service status
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "systemctl status [bot-service] --no-pager"
# View recent logs
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "journalctl -u [bot-service] --no-pager -n 50"
# Check PM2 processes
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "pm2 status"
# View PM2 logs (ALWAYS use --nostream, it will hang otherwise)
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "pm2 logs [process-name] --lines 20 --nostream"
# Check disk / memory
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "df -h"
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "free -h"
```

**Auto-Repair Actions:**
```powershell
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "sudo systemctl restart [bot-service]"
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "pm2 restart [process-name]"
ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] "sudo journalctl --rotate && sudo journalctl --vacuum-time=1d"
```

### 2. Patent Creation
Generate comprehensive patent documentation: title/abstract, background, summary of invention, detailed description, claims (independent + dependent), drawings/diagrams, examples.

### 3. Business Plan Generation
Market analysis, revenue models, cost structure, go-to-market strategy, competitive analysis, risk assessment, scaling roadmap.

### 4. Software Engineering at Scale
Refactor for maintainability, implement features across projects, optimize performance, upgrade dependencies safely, add testing/monitoring, document architecture decisions.

### 5. Dashboard Integration
AI Agents integrate with the Gorgon dashboard: AI assistant interface, voice/text commands, bot health metrics, maintenance history, optimization suggestions, critical alerts.

---

## Critical Reminders

### NEVER Use gcloud Commands
- gcloud SDK is not installed on the Windows workstation
- ALWAYS use PowerShell SSH commands: `ssh -i $env:USERPROFILE\.ssh\ecobot_jan9 levir@[VM_IP] ''COMMAND''`

### NEVER Use PM2 Logs Without --nostream
- PM2 logs will hang/stream indefinitely without it
- Correct: `pm2 logs bot-name --lines 20 --nostream`

### NEVER Use Bare Python in Cron
- Cron has a minimal PATH environment
- Use absolute paths: `/usr/bin/python3` or `/path/to/venv/bin/python3`

### ALWAYS Check Fixes.md First
- Contains known issues and solutions; saves time rediscovering problems
- Synchronized across all confirmed projects in both books

---

## Success Metrics

- 99%+ uptime across all bots; < 15 minute mean time to recovery; zero data loss incidents
- < 5 minute diagnostic response time; > 80% issues auto-resolved
- All shared files synchronized across all 34 confirmed projects (both books)
- Zero AI Law violations per session (goal)

---

## End of Unified AI Laws

**Remember:** This single file governs every confirmed project across BOTH "A Hustler''s Guide To Prompt Engineering" and "A Hustler''s Guide To Prompt Engineering 2." Sync it, `Keys.md`, `Fixes.md`, and `Violations.md` across all 34 confirmed projects whenever any of them change.
