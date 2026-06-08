This debugging session actually exposed a lot of the **real-world problems people hit when building Agentic RAG systems**. The biggest takeaway is that most failures are not in the LLM—they're in **state management, routing, and graph design**.

# 1. Treat State as the Single Source of Truth

Initially you expected:

```python
docs = state["documents"]
```

to contain retrieved documents.

But your retriever was a `create_retriever_tool()` inside a `ToolNode`, which only writes a `ToolMessage` into:

```python
state["messages"]
```

not into:

```python
state["documents"]
```

### Learning

Whenever you create a state field:

```python
documents
current_question
selected_db
```

ask:

> Which node writes this field?
>
> Which node reads this field?

If you cannot answer both immediately, you'll get bugs later.

---

# 2. Tool Messages ≠ State Variables

This was probably the biggest conceptual shift.

You assumed:

```python
ToolNode
```

would populate:

```python
state["documents"]
```

because the tool retrieved documents.

But ToolNode actually produces:

```python
AIMessage(tool_call=...)
ToolMessage(...)
```

inside:

```python
state["messages"]
```

### Learning

There are two architectures:

### Tool Calling Architecture

```text
Agent
 ↓
ToolNode
 ↓
messages
```

Information flows through messages.

### State-Based Workflow

```text
Agent
 ↓
Retriever Node
 ↓
state["documents"]
```

Information flows through state.

Don't mix the two.

---

# 3. Every State Field Needs an Owner

For example:

```python
documents
```

must have exactly one node responsible for updating it.

Good:

```python
retrieve()
    ↓
returns {"documents": docs}
```

Bad:

```python
retrieve()
generate()
rewrite()
```

all modifying documents.

### Learning

A useful question:

> Which node owns this state variable?

---

# 4. Don't Retrieve Twice

You eventually had:

```python
retrieve()
```

retrieving documents.

Then later:

```python
generate()
```

retrieving again.

This is a common RAG mistake.

### Wrong

```python
retrieve
 ↓
generate
   ↓
retrieve again
```

### Right

```python
retrieve
 ↓
state["documents"]
 ↓
generate
```

Retrieve once.
Reuse many times.

---

# 5. Type Consistency Matters

You declared:

```python
documents: str
```

but stored:

```python
List[Document]
```

inside it.

This works until some node assumes:

```python
docs.lower()
```

or:

```python
len(docs)
```

and everything explodes.

### Learning

State schema should match reality.

```python
documents: list[Document]
```

is much better.

---

# 6. Route Decisions Should Be Explicit

Initially you were using:

```python
tools_condition
```

for routing.

But your agent wasn't producing tool calls anymore.

It was producing:

```python
selected_db
```

in state.

### Learning

Use routing based on what actually exists.

Bad:

```python
tools_condition
```

when no tools are being called.

Good:

```python
def route_retriever(state):
    return state["selected_db"]
```

---

# 7. Structured Output Is Excellent for Routing

You moved to:

```python
class Route(BaseModel):
    retriever: Literal[
        "langgraph_vector_db",
        "langchain_vector_db",
        "END"
    ]
```

This is exactly how many production systems do routing.

### Learning

Use structured output whenever you need:

* routing
* classification
* decision making
* workflow branching

instead of parsing text.

Bad:

```python
if "langgraph" in response:
```

Good:

```python
response.retriever
```

---

# 8. Messages Must Contain Messages

You hit:

```python
Unsupported message type:
Route
```

because you tried:

```python
messages=[response]
```

where:

```python
response
```

was a Pydantic model.

### Learning

`messages` can only contain:

```python
HumanMessage
AIMessage
ToolMessage
SystemMessage
```

Never:

```python
Pydantic models
dicts
custom classes
```

Store those in state instead.

---

# 9. Graph Design First, Code Second

You spent a lot of time fixing code because the architecture wasn't fully settled.

A useful habit:

Draw this first.

```text
START
 ↓
init_state
 ↓
router
 ↓
retrieve
 ↓
grade
 ├─ generate
 └─ rewrite
```

Then implement.

### Learning

If you can't draw the graph on paper, coding it will be painful.

---

# 10. Query Rewriting Can Easily Loop Forever

You already saw:

```text
retrieve
 ↓
not relevant
 ↓
rewrite
 ↓
retrieve
 ↓
not relevant
 ↓
rewrite
```

This can continue forever.

### Learning

Always add:

```python
retry_count
```

or

```python
max_rewrites
```

to state.

Example:

```python
rewrite_count: int
```

Then:

```python
if rewrite_count >= 3:
    return "generate"
```

or

```python
return END
```

---

# 11. Retrieval and Routing Are Separate Problems

You originally had:

```python
LangGraph DB
LangChain DB
```

and were wondering whether to use one retriever or two.

The answer is:

### Router decides WHERE

```python
LangGraph
LangChain
```

### Retriever decides WHAT

```python
top-k chunks
```

Keep those concerns separate.

---

# 12. Production RAG Is Mostly State Machines

Before building agents, most people think:

```text
LLM
 ↓
Retriever
 ↓
Answer
```

After building agents, you realize:

```text
State
 ↓
Routing
 ↓
Memory
 ↓
Retrieval
 ↓
Evaluation
 ↓
Retry
 ↓
Generation
```

The LLM is only one component.

The hard part is orchestrating everything.

---

# 13. Your Future Agentic RAG Checklist

Before building any Agentic RAG system, ask:

### State

* What fields exist?
* Who writes them?
* Who reads them?

### Routing

* What decisions need to be made?
* Are they tool-based or state-based?

### Retrieval

* How many retrievers?
* How are they selected?

### Evaluation

* How is relevance checked?
* What happens when retrieval fails?

### Retry

* How many retries?
* How do loops terminate?

### Generation

* Which state fields are needed?
* Are documents already retrieved?

### Observability

* Print state at each node.
* Log routing decisions.
* Log retrieved documents.
* Log grader decisions.

---

If you keep these 13 lessons in mind, you'll avoid a huge percentage of the debugging pain that shows up when building more advanced systems like:

* Multi-agent RAG
* Corrective RAG (CRAG)
* Self-RAG
* Adaptive RAG
* Deep Research agents
* Multi-vector-store retrieval systems
* Production LangGraph workflows

These are exactly the kinds of issues that separate a tutorial implementation from a system that reliably works in production.
