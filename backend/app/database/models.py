from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    created_groups = relationship("Group", back_populates="creator", foreign_keys="Group.created_by")
    memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    expenses_paid = relationship("Expense", back_populates="payer", foreign_keys="Expense.paid_by")
    expense_splits = relationship("ExpenseSplit", back_populates="user", cascade="all, delete-orphan")
    settlements_paid = relationship("Settlement", back_populates="payer", foreign_keys="Settlement.paid_by")
    settlements_received = relationship("Settlement", back_populates="recipient", foreign_keys="Settlement.paid_to")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(100), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    invite_code = Column(String(10), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    creator = relationship("User", back_populates="created_groups", foreign_keys=[created_by])
    memberships = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group")
    settlements = relationship("Settlement", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="memberships")


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
        CheckConstraint("split_type IN ('equal', 'percentage', 'exact')", name="ck_expenses_split_type"),
        CheckConstraint("version > 0", name="ck_expenses_version_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    paid_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    split_type = Column(String(20), nullable=False)
    expense_date = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    version = Column(Integer, nullable=False, server_default=text("1"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid", foreign_keys=[paid_by])
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"
    __table_args__ = (UniqueConstraint("expense_id", "user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount_owed = Column(Numeric(10, 2), nullable=False)

    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")


class Settlement(Base):
    __tablename__ = "settlements"
    __table_args__ = (CheckConstraint("paid_by <> paid_to", name="ck_settlements_different_users"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    paid_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paid_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    settled_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    group = relationship("Group", back_populates="settlements")
    payer = relationship("User", back_populates="settlements_paid", foreign_keys=[paid_by])
    recipient = relationship("User", back_populates="settlements_received", foreign_keys=[paid_to])


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user = relationship("User", back_populates="refresh_tokens")