import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


ALLOWED_BOOKING_TRANSITIONS = {
    BookingStatus.PENDING: {
        BookingStatus.CONFIRMED,
        BookingStatus.FAILED,
        BookingStatus.CANCELLED,
    },
    BookingStatus.CONFIRMED: set(),
    BookingStatus.FAILED: set(),
    BookingStatus.CANCELLED: set(),
}


def can_transition_booking(current_status: BookingStatus, target_status: BookingStatus) -> bool:
    return target_status in ALLOWED_BOOKING_TRANSITIONS.get(current_status, set())


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    diagnostic_centre_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_centres.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    diagnostic_test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_tests.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    appointment_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status", native_enum=False),
        default=BookingStatus.PENDING,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="bookings")
    centre = relationship("DiagnosticCentre", back_populates="bookings")
    test = relationship("DiagnosticTest", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
