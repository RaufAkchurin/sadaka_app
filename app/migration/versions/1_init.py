"""init

Revision ID: e9142a3a3399
Revises:
Create Date: 2025-10-08 11:44:02.935015
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "e9142a3a3399"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------- 1️⃣ CREATE TABLES (no FKs yet) ----------
    op.create_table(
        "countrys",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("language", sa.Enum("RU", "EN", name="language_enum"), server_default="RU", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_countrys"),
        sa.UniqueConstraint("name", name="uq_countrys_name"),
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
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_files"),
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
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_funds"),
        sa.UniqueConstraint("picture_id", name="uq_funds_picture_id"),
    )

    op.create_table(
        "regions",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("picture_id", sa.Integer(), nullable=True),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_regions"),
        sa.UniqueConstraint("name", name="uq_regions_name"),
        sa.UniqueConstraint("picture_id", name="uq_regions_picture_id"),
    )

    op.create_table(
        "projects",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "FINISHED", "ALL", name="project_status_enum"), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("goal", sa.Integer(), nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
    )

    op.create_table(
        "stages",
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("goal", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "FINISHED", "ALL", name="stage_status_enum"), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_stages"),
        sa.UniqueConstraint("project_id", "number", name="unique_stage_number_per_project"),
    )

    op.create_table(
        "citys",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_citys"),
        sa.UniqueConstraint("name", name="uq_citys_name"),
    )

    op.create_table(
        "users",
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("google_access_token", sa.String(), nullable=True),
        sa.Column("phone", sa.String(length=12), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("language", sa.Enum("RU", "EN", name="language_enum"), server_default="RU", nullable=False),
        sa.Column(
            "role",
            sa.Enum("SUPERUSER", "FUND_ADMIN", "FUND_STAFF", "USER", name="role_enum"),
            server_default="USER",
            nullable=False,
        ),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("picture_id", sa.Integer(), nullable=True),
        sa.Column("city_id", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
        sa.UniqueConstraint("picture_id", name="uq_users_picture_id"),
    )

    # op.create_table(
    #     "funds",  # уже есть, просто отмечаем чтобы понимал порядок
    # )

    op.create_table(
        "referrals",
        sa.Column("key", sa.String(length=6), nullable=False),
        sa.Column("type", sa.Enum("JOIN", "FUND", "PROJECT", name="referraltypeenum"), nullable=False),
        sa.Column("sharer_id", sa.Integer(), nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_referrals"),
        sa.UniqueConstraint("key", name="uq_referrals_key"),
    )

    op.create_table(
        "payments",
        sa.Column("provider", sa.Enum("YOOKASSA", "TBANK", name="payment_provider_enum"), nullable=False),
        sa.Column("provider_payment_id", sa.String(), nullable=False),
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
        sa.Column("referral_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_payments"),
    )

    # ---------- 2️⃣ ADD FOREIGN KEYS ----------
    op.create_foreign_key("fk_regions_country_id", "regions", "countrys", ["country_id"], ["id"])
    op.create_foreign_key("fk_regions_picture_id", "regions", "files", ["picture_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_citys_region_id", "citys", "regions", ["region_id"], ["id"])
    op.create_foreign_key("fk_users_city_id", "users", "citys", ["city_id"], ["id"])
    op.create_foreign_key("fk_users_picture_id", "users", "files", ["picture_id"], ["id"])
    op.create_foreign_key("fk_funds_region_id", "funds", "regions", ["region_id"], ["id"])
    op.create_foreign_key("fk_funds_picture_id", "funds", "files", ["picture_id"], ["id"])
    op.create_foreign_key("fk_projects_fund_id", "projects", "funds", ["fund_id"], ["id"])
    op.create_foreign_key("fk_stages_project_id", "stages", "projects", ["project_id"], ["id"])
    op.create_foreign_key("fk_files_fund_document_id", "files", "funds", ["fund_document_id"], ["id"])
    op.create_foreign_key("fk_files_project_document_id", "files", "projects", ["project_document_id"], ["id"])
    op.create_foreign_key("fk_files_project_picture_id", "files", "projects", ["project_picture_id"], ["id"])
    op.create_foreign_key("fk_files_stage_id", "files", "stages", ["stage_id"], ["id"])
    op.create_foreign_key("fk_referrals_fund_id", "referrals", "funds", ["fund_id"], ["id"])
    op.create_foreign_key("fk_referrals_project_id", "referrals", "projects", ["project_id"], ["id"])
    op.create_foreign_key("fk_referrals_sharer_id", "referrals", "users", ["sharer_id"], ["id"])
    op.create_foreign_key("fk_payments_user_id", "payments", "users", ["user_id"], ["id"])
    op.create_foreign_key("fk_payments_project_id", "payments", "projects", ["project_id"], ["id"])
    op.create_foreign_key("fk_payments_stage_id", "payments", "stages", ["stage_id"], ["id"])
    op.create_foreign_key("fk_payments_referral_id", "payments", "referrals", ["referral_id"], ["id"])


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("referrals")
    op.drop_table("users")
    op.drop_table("citys")
    op.drop_table("stages")
    op.drop_table("projects")
    op.drop_table("regions")
    op.drop_table("funds")
    op.drop_table("files")
    op.drop_table("countrys")
