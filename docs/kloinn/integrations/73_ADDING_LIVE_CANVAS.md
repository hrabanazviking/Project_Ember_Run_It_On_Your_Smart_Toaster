# 73 — Adding Live Canvas

Concrete implementation guidance for adding a Canvas-equivalent
(OdinUI) to Ember. Phase 5 work.

---

## Prerequisites

- Stofa shipped (Phase 2).
- Auga sibling exists (V5 plan).
- Web companion (V5).
- Funi can be prompted to emit structured output.

---

## Step 1: define OdinUI spec

`docs/odinui/SPEC.md`:

The spec defines:
- JSON shape for each component.
- Validation rules.
- Renderer requirements.
- Backward-compat rules.

V1 components:
- `form` (with field list).
- `list` (selectable items).
- `card` (content presentation).
- `chart` (basic types).
- `button` (action trigger).
- `progress` (long-running indicator).

V2 adds: `editor`, `image`, `audio`, `map`.

---

## Step 2: spec validation

`src/ember/odinui/validation.py`:

```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class FormField(BaseModel):
    name: str
    label: str
    type: Literal["text", "number", "date", "select", "checkbox", "radio"]
    required: bool = False
    options: list[str] | None = None  # for select/radio
    placeholder: str | None = None

class FormSpec(BaseModel):
    type: Literal["form"]
    title: str
    fields: list[FormField]
    submit_label: str = "Submit"

class ListSpec(BaseModel):
    type: Literal["list"]
    items: list[dict]
    selectable: bool = True

# ... etc

class OdinUI(BaseModel):
    spec: Union[FormSpec, ListSpec, ...]  # discriminated union
    version: Literal[1] = 1
```

Pydantic validates incoming JSON. Invalid spec → error;
renderer skips.

---

## Step 3: agent prompt to emit OdinUI

In TOOLS.md (or system prompt):

```markdown
## OdinUI

You can render interactive UI elements in your responses
when appropriate.

To render OdinUI, wrap a JSON spec in an `odinui` code fence:

    ```odinui
    {
      "type": "form",
      "title": "...",
      "fields": [...]
    }
    ```

Use OdinUI for:
- Multi-field input (forms).
- Selection from finite lists.
- Confirmation of consequential actions.

Use plain text for:
- Conversational replies.
- Long-form explanations.
- Open-ended questions.

The current surface supports: form, list, card, chart, button.
```

---

## Step 4: detect + parse OdinUI in response

In response streaming:

```python
def parse_response(text: str) -> ResponseParts:
    """Split text into text segments and OdinUI specs."""
    parts = []
    
    for chunk in split_by_odinui_fence(text):
        if chunk.is_odinui:
            try:
                spec = OdinUI.parse_raw(chunk.content)
                parts.append(OdinUIPart(spec=spec))
            except ValidationError as e:
                parts.append(TextPart(text=f"[OdinUI error: {e}]"))
        else:
            parts.append(TextPart(text=chunk.content))
    
    return ResponseParts(parts=parts)
```

---

## Step 5: TUI renderer (Stofa)

`src/ember/spark/munnr/stofa/odinui_renderer.py`:

```python
class TUIOdinUIRenderer:
    def render(self, spec: OdinUI, container: Container):
        if isinstance(spec.spec, FormSpec):
            self._render_form(spec.spec, container)
        elif isinstance(spec.spec, ListSpec):
            self._render_list(spec.spec, container)
        # ...
    
    def _render_form(self, form: FormSpec, container: Container):
        widgets = []
        widgets.append(Label(form.title, classes="form-title"))
        
        for field in form.fields:
            if field.type == "text":
                widgets.append(Input(name=field.name, placeholder=field.placeholder))
            elif field.type == "number":
                widgets.append(Input(name=field.name, type="number"))
            elif field.type == "date":
                widgets.append(Input(name=field.name, type="date"))
            # ...
        
        widgets.append(Button(form.submit_label, classes="form-submit"))
        
        container.mount(*widgets)
```

When operator submits form: form data captured; pushed back to
chat as next operator turn (with metadata noting it's a form
submission).

---

## Step 6: web renderer (web companion)

In `companion-pwa/js/odinui.js`:

```javascript
function renderOdinUI(spec, container) {
  if (spec.type === 'form') {
    renderForm(spec, container);
  } else if (spec.type === 'list') {
    renderList(spec, container);
  }
  // ...
}

function renderForm(form, container) {
  const formEl = document.createElement('form');
  formEl.innerHTML = `<h3>${form.title}</h3>`;
  
  form.fields.forEach(field => {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <label for="${field.name}">${field.label}</label>
      <input
        id="${field.name}"
        name="${field.name}"
        type="${field.type}"
        ${field.required ? 'required' : ''}
        placeholder="${field.placeholder || ''}"
      />
    `;
    formEl.appendChild(wrapper);
  });
  
  const submit = document.createElement('button');
  submit.textContent = form.submit_label;
  submit.type = 'submit';
  formEl.appendChild(submit);
  
  formEl.onsubmit = (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(formEl));
    sendFormSubmission(data);
  };
  
  container.appendChild(formEl);
}
```

Standard HTML; renders natively in browser.

---

## Step 7: handling submission

When operator submits a form:

```python
async def handle_form_submission(form_data: dict, session: Session):
    # Construct chat-turn input with form data as structured input
    chat_input = f"[Form submission: {json.dumps(form_data)}]\n\nProceed."
    
    # Process as normal chat-turn
    await chat.process_turn(session, chat_input)
```

Agent receives form data as part of the next prompt; can
acknowledge + use the values.

---

## Step 8: Munnr (CLI) fallback

Munnr is text-only; can't render UI. If response contains
OdinUI:

```python
def render_odinui_for_cli(spec: OdinUI) -> str:
    """Convert OdinUI to text description for CLI."""
    if isinstance(spec.spec, FormSpec):
        lines = [
            f"[Form: {spec.spec.title}]",
            "Please provide:",
        ]
        for field in spec.spec.fields:
            lines.append(f"  {field.label}: ?")
        lines.append("(Reply with each field on a line as: name=value)")
        return "\n".join(lines)
    # ...
```

Operator can respond with field=value lines; parsed and
treated as form submission.

---

## Step 9: tests

```python
# tests/unit/test_odinui_renderer.py

def test_form_renders_correctly():
    spec = OdinUI(spec=FormSpec(
        type="form",
        title="Test",
        fields=[FormField(name="x", label="X", type="text")],
    ))
    
    container = MockContainer()
    renderer = TUIOdinUIRenderer()
    renderer.render(spec, container)
    
    assert len(container.children) == 3  # label + input + button

def test_form_submission_captures_values():
    # ... simulate form submission ...
    assert captured_data == {"x": "value"}
```

---

## Step 10: configuration

```yaml
ember:
  odinui:
    enabled: false                 # opt-in V5
    
    spec_version: 1
    max_widgets_per_response: 5
    
    surfaces:
      stofa:
        enabled: true
        fallback_to_text: true
      web_companion:
        enabled: true
      munnr:
        text_fallback: true
    
    cache_widget_state_in_episode: true
```

---

## Step 11: documentation

`docs/odinui/`:
- `SPEC.md` — spec definition.
- `OPERATOR_GUIDE.md` — what operators see + can do.
- `AUTHORING_GUIDE.md` — for agent prompting + custom skills.
- `RENDERER_GUIDE.md` — for implementing new renderers.

---

## Step 12: rollout in V5

V5a release: spec + Stofa renderer for `form` + `list`.
V5b: web companion renderer.
V5c: more components (chart, button, etc.).
V5d: agent prompt fine-tuning.

Each ships incrementally.

---

## What about backward compat across versions

OdinUI spec versions matter. Agent prompts include current
spec version. Renderers support known versions.

Future version 2: backward-compat shim translates V1 specs
correctly.

---

## What we explicitly skip

🔴 **Reject for V5**:

### 1. Drag-and-drop interactivity

Complex; defer to V6+ if demand.

### 2. Custom CSS in agent responses

Agent doesn't choose visual styling; renderer applies
operator's theme. Safe + sovereign.

### 3. Embedded code execution

OdinUI is *declarative*; not Turing-complete. No code in
specs.

### 4. Cross-widget binding

Each OdinUI widget is independent. No global state binding
across widgets in V5.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Agent over-uses OdinUI | Prompt discipline + max per response |
| Operator confused by widgets | Stofa shows text-equivalent below |
| Spec ambiguity | Pydantic validation strict |
| Widget submission lost | Persistent storage per session |

---

## Closing

Adding Live Canvas is **V5 work** — define OdinUI spec; build
renderers for Stofa + web + Munnr-fallback; teach Funi to
emit; document.

Implementation: ~1500 lines (spec + 3 renderers + agent
prompting).

Critical: open spec (anyone can implement); operator can
disable; defaults sane.

This is the *most ambitious Klóinn adoption* — but also the
most operator-empowering UI feature in Ember V5.
