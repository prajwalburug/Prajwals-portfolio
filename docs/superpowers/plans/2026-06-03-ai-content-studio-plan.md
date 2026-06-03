# AI Content Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a brand-aligned AI content generation system with Obsidian vault foundation, swipe file, portable `writing-skills.md`, and generation agents for LinkedIn, email, and blog.

**Architecture:** Three layers — research (Firecrawl) → swipe file (Obsidian) → generation (Python agents). All agents read `writing-skills.md` for brand context. Output lands in both Obsidian (review) and n8n (publish).

**Tech Stack:** Python 3 · OpenAI/Anthropic · Firecrawl · Obsidian · n8n

**Location:** `gtm-portfolio/ai-content-studio/` (new project alongside `wati-gtm-engine/`)

---

### Phase 1: Foundation — Vault, Swipe File, Compiler

**Task 1: Scaffold project structure**

```
ai-content-studio/
├── code/
├── automation/
├── swipe-file/
│   ├── hooks.md
│   ├── frameworks.md
│   ├── subject-lines.md
│   ├── cta-library.md
│   └── channel-rules/
│       ├── linkedin.md
│       ├── email.md
│       └── blog.md
├── brands/awesome-hires/
│   ├── brand-kit.md
│   └── writing-skills.md
└── README.md
```

- [ ] Create directories and empty placeholder files
- [ ] Add `.gitkeep` in `code/` and `automation/`
- [ ] Commit: `git add ai-content-studio/ && git commit -m "feat: scaffold ai-content-studio project"`

---

**Task 2: Write brand-kit.md for Awesome Hires**

- [ ] Create `brands/awesome-hires/brand-kit.md` with the content the user provided

---

**Task 3: Write swipe-file samples**

- [ ] Create `swipe-file/hooks.md` with 20+ proven hook patterns
- [ ] Create `swipe-file/frameworks.md` with 5 content frameworks
- [ ] Create `swipe-file/subject-lines.md` with 30 subject lines
- [ ] Create `swipe-file/cta-library.md` with CTAs organized by intent
- [ ] Create `swipe-file/channel-rules/linkedin.md`
- [ ] Create `swipe-file/channel-rules/email.md`
- [ ] Create `swipe-file/channel-rules/blog.md`
- [ ] Commit

---

**Task 4: Write compile_skills.py**

- [ ] Create `code/compile_skills.py`
- [ ] Test: `python code/compile_skills.py --brand awesome-hires --output brands/awesome-hires/writing-skills.md`
- [ ] Test dry-run: `python code/compile_skills.py --brand awesome-hires --dry-run`
- [ ] Commit

---

### Phase 2: Generation Agents

**Task 5: Write generate_linkedin.py**

- [ ] Create `code/generate_linkedin.py`
- [ ] Test: `python code/generate_linkedin.py --brand awesome-hires --topic "AI bias in hiring" --demo`
- [ ] Test dry-run: `python code/generate_linkedin.py --brand awesome-hires --topic "AI voice interviews" --demo --dry-run`
- [ ] Commit

---

**Task 6: Write generate_email.py**

- [ ] Create `code/generate_email.py`
- [ ] Test: `python code/generate_email.py --brand awesome-hires --topic "30-min screening" --type cold --demo`
- [ ] Test dry-run: `python code/generate_email.py --brand awesome-hires --topic "fair hiring" --type newsletter --demo --dry-run`
- [ ] Commit

---

**Task 7: Write generate_blog.py**

- [ ] Create `code/generate_blog.py`
- [ ] Test: `python code/generate_blog.py --brand awesome-hires --topic "Why AI interviews are fairer" --seo-keyword "AI interview bias" --outline-only --demo`
- [ ] Test: `python code/generate_blog.py --brand awesome-hires --topic "Why AI interviews are fairer" --demo`
- [ ] Commit

---

### Phase 3: Repurposing + Research

**Task 8: Write repurpose.py**

- [ ] Create `code/repurpose.py`
- [ ] Test: `python code/repurpose.py --brand awesome-hires --channels linkedin,email --demo`
- [ ] Test dry-run: `python code/repurpose.py --brand awesome-hires --demo --dry-run`
- [ ] Commit

---

**Task 9: Write research_scout.py**

- [ ] Create `code/research_scout.py`
- [ ] Test: `python code/research_scout.py --brand awesome-hires --source linkedin --demo`
- [ ] Test dry-run: `python code/research_scout.py --brand awesome-hires --source all --demo --dry-run`
- [ ] Commit

---

### Phase 4: Automation + Polish

**Task 10: Write n8n workflows**

- [ ] Create `automation/research-scan.json`
- [ ] Create `automation/content-studio.json`
- [ ] Commit

---

**Task 11: Write project README**

- [ ] Create `ai-content-studio/README.md`
- [ ] Update root `gtm-portfolio/README.md`
- [ ] Commit

---

**Task 12: Verify end-to-end**

- [ ] Run full pipeline
- [ ] Verify all agents support `--demo` and `--dry-run`
- [ ] Verify Obsidian `generated/` outputs
- [ ] Push
