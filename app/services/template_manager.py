from pathlib import Path


class TemplateManager:

    def get_website_template(self, template_name):

        template_path = Path(
            f"app/templates/websites/{template_name}"
        )

        return {
            "index": (template_path / "index.html").read_text(encoding="utf-8"),
            "style": (template_path / "style.css").read_text(encoding="utf-8"),
            "script": (template_path / "script.js").read_text(encoding="utf-8")
        }