import uuid
from datetime import datetime
from sqlalchemy import String,DateTime,Integer,Float,Text
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.sql import func
from app.db import Base
def uid(): return uuid.uuid4()
class SimulationRun(Base):
    __tablename__="simulation_runs"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    tenant_id:Mapped[str]=mapped_column(String(128),index=True)
    journey_name:Mapped[str]=mapped_column(String(256))
    journey:Mapped[dict]=mapped_column(JSONB)
    status:Mapped[str]=mapped_column(String(32),index=True,default="PENDING")
    summary:Mapped[dict|None]=mapped_column(JSONB,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class SimulatedUser(Base):
    __tablename__="simulated_users"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    run_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    persona:Mapped[str]=mapped_column(String(128))
    attributes:Mapped[dict]=mapped_column(JSONB)
    current_node:Mapped[str|None]=mapped_column(String(128),nullable=True)
    status:Mapped[str]=mapped_column(String(32),default="READY")
class Traversal(Base):
    __tablename__="traversals"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    run_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    user_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    node_id:Mapped[str]=mapped_column(String(128))
    event_type:Mapped[str]=mapped_column(String(64))
    detail:Mapped[dict]=mapped_column(JSONB,default=dict)
    seq:Mapped[int]=mapped_column(Integer)
class Finding(Base):
    __tablename__="findings"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    run_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    kind:Mapped[str]=mapped_column(String(64),index=True)
    severity:Mapped[str]=mapped_column(String(16))
    message:Mapped[str]=mapped_column(Text)
    evidence:Mapped[dict]=mapped_column(JSONB,default=dict)
