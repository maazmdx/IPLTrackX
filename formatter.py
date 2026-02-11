import json
import textwrap

# ------------ LOAD BRAIN OUTPUT ------------
with open("brain_output.json", "r") as f:
    design = json.load(f)

headline = design.get("headline", "")
sub = design.get("sub_headline", "")
facts = design.get("facts", [])

# ------------ CLEAN TEXT ------------

def clean_text(text):
    text = text.replace("*", "")
    text = text.replace("•", "")
    text = text.strip()
    return text

headline = clean_text(headline)
sub = clean_text(sub)
facts = [clean_text(f) for f in facts]

# ------------ TEXT WRAPPING ------------

def wrap_text(text, width):
    return "\n".join(textwrap.wrap(text, width=width))

headline_wrapped = wrap_text(headline, 28)
sub_wrapped = wrap_text(sub, 32)
facts_wrapped = [wrap_text(f, 36) for f in facts]

# ------------ FORMAT OUTPUT ------------

formatted = {
    "headline": headline_wrapped,
    "sub": sub_wrapped,
    "facts": facts_wrapped
}

# Save for renderer
with open("formatted_content.json", "w") as f:
    json.dump(formatted, f, indent=2)

print(json.dumps(formatted, indent=2))
