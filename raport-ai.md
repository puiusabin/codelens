# Raport despre Folosirea Toolurilor de AI în Timpul Dezvoltării Software

**Proiect**: CodeLens — AI-Powered Code Review CLI
**Echipa**: puiusabin
**Data**: Iunie 2026

---

## 1. Introducere

CodeLens este un tool CLI care analizeaza cod, detecteaza code smells, face review la Pull Request-uri GitHub si genereaza teste unitare automat — folosind o arhitectura cu doi agenti AI. Proiectul a fost construit **integral cu ajutorul AI**, de la planificarea initiala pana la implementare, testare si documentatie.

Acest raport descrie ce tooluri au fost folosite, in ce faze ale dezvoltarii, si ce impact au avut asupra vitezei si calitatii codului.

---

## 2. Tooluri AI Utilizate

| Tool | Versiune / Model | Rol in proiect |
|------|-----------------|----------------|
| **ChatGPT** | GPT-4o | Planificare produs, definire cerinte, generare user stories |
| **Claude Code** | claude-sonnet-4-6 | Implementare cod, debugging, refactorizare, documentatie |
| **Ollama** | gemma2 (local) | LLM-ul local folosit de CodeLens insusi pentru analiza codului |

---

## 3. Fazele Dezvoltarii si Rolul AI

### Faza 1: Planificare si Definire Cerinte (ChatGPT)

Primul pas a fost o sesiune de planificare cu ChatGPT pentru a defini conceptul de produs si arhitectura sistemului.

**Ce a produs AI-ul:**
- Arhitectura cu doi agenti specializati: **Context Analyzer** (Agent 1) si **QA Sentinel** (Agent 2)
- Backlog structurat in 4 Epics cu user stories si acceptance criteria masurabile
- Decizia de a folosi Ollama pentru a rula modele local (zero data leakage pentru cod proprietar)
- Structura comenzilor CLI: `init`, `auth`, `explain`, `check`, `review`, `chat`, `test`

**De ce a functionat:** ChatGPT a generat rapid un backlog complet care a putut fi folosit direct ca spec pentru implementare. Fara AI, definirea cerinterilor ar fi durat 2-3 zile de brainstorming.

**Exemplu de prompt folosit:**
> "Proiectez un CLI tool pentru code review cu AI. Am doua agente: unul care explica codul si unul care genereaza teste. Genereaza user stories structurate cu acceptance criteria clare pentru 4 epics."

---

### Faza 2: Setup CI/CD si Infrastructura (Claude Code)

Inainte de orice cod de aplicatie, pipeline-ul de CI/CD a fost configurat cu Claude Code.

**Ce a produs AI-ul:**
- GitHub Actions workflow (`ci.yml`) pentru Python: install dependente, lint cu `ruff`, teste cu `pytest`
- `.gitignore` completat pentru Python / virtualenv
- Structura initiala a proiectului (`pyproject.toml`, `requirements.txt`)

**Impact:** CI-first a insemnat ca orice cod scris ulterior era verificat automat la fiecare Pull Request. Au fost deschise 11 PR-uri pe tot parcursul proiectului, fiecare trecut prin pipeline.

---

### Faza 3: Implementare Epic cu Epic (Claude Code)

Fiecare epic a fost implementat intr-un branch separat. Claude Code a scris codul complet la fiecare pas, nu doar snippets.

#### Epic 1 — CLI Setup si Configuratie

**Branch:** `feature/epic-1-cli-setup`

Claude Code a implementat:
- `config.py`: `save_config()` si `load_config()` cu persistenta JSON la `~/.codelens_config`
- Comanda `codelens init`: selectia backend-ului AI (openai / anthropic / ollama)
- Comanda `codelens auth github`: stocare token Personal Access Token
- Teste pentru validare backend invalid, persistenta configuratiei, stocare token

#### Epic 2 — Context Analyzer Agent

**Branch:** `feature/epic-2-context-analyzer`

Claude Code a implementat:
- `agents/analyzer.py`: functii specializate pentru fiecare comanda (`explain_code`, `check_code_smells`, `analyze_diff`)
- `agents/github_api.py`: parsare URL Pull Request, fetch diff via GitHub REST API cu autentificare optionala
- Prompt engineering specific per comanda: output structurat cu sectiuni fixe (TL;DR / Major Components / Logic Flow)
- Colorare output in terminal: `[WARNING]` galben, `[CRITICAL]` rosu cu numere de linie

#### Epic 3 — QA Sentinel Agent

**Branch:** `feature/epic-3-qa-sentinel`

Claude Code a implementat:
- `agents/tester.py`: Agent 2 primeste codul + output-ul de la Agent 1 si genereaza teste
- Prompt engineering pentru structura fixa: sectiuni `Happy Path` si `Edge Cases`, comentariu `# WHY:` per test
- Post-procesare output LLM: stergere fence-uri Markdown, validare sintaxa Python cu `ast.parse()`, eliminare proza trailing prin iteratie linie cu linie
- Afisare teste generate cu syntax highlighting (Rich Syntax, tema monokai, numere de linie)

#### Epic 4 — Advanced Features

**Branch:** `feature/epic-4-advanced-cli`

Claude Code a implementat:
- Comanda `codelens chat`: sesiune interactiva multi-turn cu Agent 1 despre un fisier de cod
- Suport `codelens.yaml`: fisier de configurare per-proiect, instructiunile din el sunt injectate in system prompt-ul agentilor la fiecare apel

#### Agent Evals

**Branch:** `feature/agent-evals`

Claude Code a scris teste de evaluare automata pentru calitatea output-ului agentilor:
- Agent 1 trebuie sa identifice un bug cunoscut intr-un fisier dummy
- Agent 2 trebuie sa produca cod Python sintactic valid
- Stergerea prozei trailing din output-ul tester-ului (bug descoperit in timpul evals)

---

### Faza 4: Bugfix — Config Corupt (Claude Code)

**Branch:** `fix/corrupt-config-crash`

Dupa ce aplicatia crapa fara mesaj clar la citirea unui `~/.codelens_config` corupt (JSON invalid), Claude Code a:

1. Identificat locul exact: `json.JSONDecodeError` in `load_config()` nu era prins
2. Adaugat handling cu mesaj de eroare specific:
   ```
   Error: ~/.codelens_config is corrupted. Run 'codelens init' to reset it.
   ```
3. Scris un test de regresie care reproduce exact scenariul (fisier corupt → `SystemExit` cu mesajul corect)

**Timp total:** sub 10 minute de la descrierea bug-ului pana la commit.

---

### Faza 5: Suport Multi-Provider LLM (Claude Code)

**Branch:** `fix/corrupt-config-crash` (continuare)

Problema: ambii agenti hardcodau `ollama` cu modelul `gemma2`, ignorand complet backend-ul ales in `codelens init`. Claude Code a rezolvat prin:

**Creare `agents/llm.py`** — strat de abstractizare cu doua functii publice:
```python
def chat(system_prompt: str, user_content: str) -> str: ...
def chat_messages(messages: list[dict]) -> str: ...  # pentru chat multi-turn
```

Dispatch pe baza config-ului la runtime catre:
- **Ollama**: `ollama.chat(model=model, messages=[...])`
- **OpenAI**: `openai.OpenAI(api_key=...).chat.completions.create(...)`
- **Anthropic**: `anthropic.Anthropic(api_key=...).messages.create(...)` — necesita tratare separata: Anthropic primeste `system` ca parametru top-level, nu in lista de mesaje

**Actualizare `codelens init`**: acum solicita si numele modelului (default per provider: `gpt-4o`, `claude-sonnet-4-6`, `gemma2`) si API key-ul (doar pentru cloud providers).

**Actualizare teste**: mock-urile `agents.analyzer.ollama` inlocuite cu `agents.llm.chat`.

---

## 4. Impact Masurat

| Metrica | Valoare |
|---------|---------|
| Linii de cod generate cu AI | ~100% |
| Pull Requests deschise | 11 |
| Commits totale | 25+ |
| Durata totala implementare | ~1 saptamana |
| Timp estimat fara AI | 3-4 saptamani |
| Teste scrise | 18, toate trec |
| Timp mediu bugfix cu AI | sub 15 minute |

---

## 5. Ce a Functionat Bine

**Planificarea structurata** — ChatGPT a generat un backlog complet cu acceptance criteria clare care a servit direct ca spec. Fara ambiguitati, implementarea a urmat natural.

**Separarea responsabilitatilor** — AI-ul a sugerat natural arhitectura cu doi agenti specializati in loc de un singur prompt monolitic. Aceasta decizie a imbunatatit calitatea testelor generate (Agent 2 are mai mult context).

**Test-first** — Claude Code a scris testele odata cu codul, nu dupa. Acoperirea a ramas consistenta pe tot parcursul proiectului.

**Iteratia rapida pe buguri** — descrierea clara a unui bug a produs in mod constant fix complet + test de regresie in sub 15 minute.

**Post-procesare LLM output** — Claude Code a identificat singur ca modelele ignora uneori instructiunile din prompt si a adaugat post-procesare defensiva (stergere fence-uri, validare `ast.parse()`, eliminare proza trailing).

---

## 6. Limitari si Unde a Fost Necesara Judecata Umana

**Alegerea modelului local** — decizia de a folosi `gemma2` via Ollama pentru a garanta zero data leakage a fost o alegere deliberata de produs, nu o sugestie AI. AI-ul nu cunoaste contextul de business (cod proprietar, politici de securitate).

**Validarea evals** — testele de evaluare au aratat ca Agent 2 produce uneori proza dupa blocul de cod Python. AI-ul a scris fix-ul, dar problema a fost descoperita prin rulare manuala a evals-urilor, nu prin cod.

**Reviewul PR-urilor** — fiecare PR a fost revizuit inainte de merge. Codul generat de AI era corect functional dar uneori supraabundent; cateva simplificari au fost facute manual.

**Arhitectura initiala vs. realitate** — README-ul initial mentiona LangChain/LlamaIndex pentru orchestrare. In implementare, agentii comunica direct (output Agent 1 → input Agent 2) fara un framework de orchestrare, ceea ce s-a dovedit mai simplu si mai usor de testat. Aceasta decizie a fost luata in timpul implementarii.

---

## 7. Concluzie

Folosirea AI pe tot parcursul ciclului de dezvoltare — de la planificare la implementare, testare si debugging — a redus timpul de livrare de la estimat 3-4 saptamani la aproximativ 1 saptamana. Calitatea codului a fost consistenta: 18 teste automate trec, CI ruleaza la fiecare PR, si fiecare comanda are comportament verificat.

Cel mai mare castig nu a fost viteza de scriere a codului in sine, ci **eliminarea timpului petrecut pe decizii de design la nivel jos**: structura functiilor, formate de output, handling-ul erorilor. AI-ul a propus solutii rezonabile instant, lasand judecata umana sa se concentreze pe deciziile de produs si arhitectura.
