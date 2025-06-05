from admin.views.base.picture_preview import BaseAdminView
from markupsafe import Markup


class DocumentsPreviewAdmin(BaseAdminView):
    column_list = ["id", "documents_preview"]

    # 👇 Исключаем реальное поле, если оно не маппится напрямую
    form_excluded_columns = ["documents"]

    @staticmethod
    def _documents_preview(self, model):
        items = getattr(self, "documents", [])
        if not items:
            return "—"

        previews = []
        for doc in items:
            if doc.url:
                previews.append(
                    f'<img src="{doc.url}" width="40" height="40" style="object-fit:cover;'
                    f' margin-right: 4px; border-radius: 4px;" />'
                )

        return Markup(" ".join(previews))

    column_formatters = {
        "documents_preview": _documents_preview,
    }

    column_labels = {
        "documents_preview": "Документы",
    }
