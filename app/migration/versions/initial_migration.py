from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f88841f79d03"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создание таблиц без внешних ключей
    op.create_table(
        "countrys",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("language", sa.Enum("RU", "EN", name="language_enum"), server_default="RU", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "funds",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("hot_line", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("region_id", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("picture_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("picture_id"),
    )

    op.create_table(
        "files",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("type", sa.Enum("DOCUMENT", "REPORT", "PICTURE", name="file_type_enum"), nullable=False),
        sa.Column("mime", sa.Enum("PDF", "PNG", "JPEG", name="file_mime_enum"), nullable=False),
        sa.Column("fund_document_id", sa.Integer(), nullable=True),
        sa.Column("project_document_id", sa.Integer(), nullable=True),
        sa.Column("project_picture_id", sa.Integer(), nullable=True),
        sa.Column("stage_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projects",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "FINISHED", "ALL", name="project_status_enum"), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("goal", sa.Integer(), nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "stages",
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("goal", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "FINISHED", "ALL", name="stage_status_enum"), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "number", name="unique_stage_number_per_project"),
    )

    op.create_table(
        "regions",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("picture_id", sa.Integer(), nullable=True),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countrys.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("picture_id"),
    )

    op.create_table(
        "citys",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("google_access_token", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("language", sa.Enum("RU", "EN", name="language_enum"), server_default="RU", nullable=False),
        sa.Column(
            "role",
            sa.Enum("SUPERUSER", "FUND_ADMIN", "FUND_STAFF", "USER", name="role_enum"),
            server_default="USER",  # Изменено на верхний регистр
            nullable=False,
        ),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("picture_id", sa.Integer(), nullable=True),
        sa.Column("city_id", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["citys.id"]),
        sa.ForeignKeyConstraint(["picture_id"], ["files.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("picture_id"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("captured_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("income_amount", sa.Float(), nullable=True),
        sa.Column("test", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "CANCELED", "WAITING_FOR_CAPTURE", "SUCCEEDED", name="payment_status_enum"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("stage_id", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["stage_id"], ["stages.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_fund_access",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("fund_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

    # Добавление внешних ключей после создания всех таблиц
    op.create_foreign_key("fk_files_fund_document_id", "files", "funds", ["fund_document_id"], ["id"])
    op.create_foreign_key("fk_files_project_document_id", "files", "projects", ["project_document_id"], ["id"])
    op.create_foreign_key("fk_files_project_picture_id", "files", "projects", ["project_picture_id"], ["id"])
    op.create_foreign_key("fk_files_stage_id", "files", "stages", ["stage_id"], ["id"])
    op.create_foreign_key("fk_funds_picture_id", "funds", "files", ["picture_id"], ["id"])
    op.create_foreign_key("fk_regions_picture_id", "regions", "files", ["picture_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_users_picture_id", "users", "files", ["picture_id"], ["id"])


def downgrade() -> None:
    # Удаление внешних ключей и таблиц
    op.drop_constraint("fk_files_fund_document_id", "files", type_="foreignkey")
    op.drop_constraint("fk_files_project_document_id", "files", type_="foreignkey")
    op.drop_constraint("fk_files_project_picture_id", "files", type_="foreignkey")
    op.drop_constraint("fk_files_stage_id", "files", type_="foreignkey")
    op.drop_constraint("fk_funds_picture_id", "funds", type_="foreignkey")
    op.drop_constraint("fk_regions_picture_id", "regions", type_="foreignkey")
    op.drop_constraint("fk_users_picture_id", "users", type_="foreignkey")

    op.drop_table("user_fund_access")
    op.drop_table("payments")
    op.drop_table("users")
    op.drop_table("citys")
    op.drop_table("regions")
    op.drop_table("stages")
    op.drop_table("projects")
    op.drop_table("funds")
    op.drop_table("files")
    op.drop_table("countrys")
