from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class LabValue(Base):
    """Individual lab test value within a report."""

    __tablename__ = "lab_values"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    ref_low = Column(Float, nullable=True)
    ref_high = Column(Float, nullable=True)
    status = Column(String(20), nullable=False)  # "normal", "low", "high", "critical_low", "critical_high"

    # Relationship
    report = relationship("Report", back_populates="lab_values")

    def __repr__(self):
        return f"<LabValue(test={self.test_name}, value={self.value}, status={self.status})>"
