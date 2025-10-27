import json
from pathlib import Path
from services.api.app.main import app
out = Path("docs/api/openapi.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(app.openapi(), indent=2))
print(f"Wrote {out}")
