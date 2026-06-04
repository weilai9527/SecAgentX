"""Response action API routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.session import get_db

router = APIRouter(prefix="/api/incidents", tags=["actions"])


@router.get("/{incident_id}/actions", response_model=List[schemas.ResponseActionOut])
def list_actions(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return db.query(models.ResponseAction).filter(models.ResponseAction.incident_id == incident_id).all()


@router.post("/{incident_id}/actions/{action_id}/approve")
def approve_action(incident_id: int, action_id: int, payload: schemas.ActionApproval, db: Session = Depends(get_db)):
    action = db.query(models.ResponseAction).filter(
        models.ResponseAction.id == action_id,
        models.ResponseAction.incident_id == incident_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action.status = "approved"
    action.approved_by = payload.approved_by
    db.commit()
    return {"ok": True, "status": action.status}


@router.post("/{incident_id}/actions/{action_id}/reject")
def reject_action(incident_id: int, action_id: int, payload: schemas.ActionApproval, db: Session = Depends(get_db)):
    action = db.query(models.ResponseAction).filter(
        models.ResponseAction.id == action_id,
        models.ResponseAction.incident_id == incident_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action.status = "rejected"
    action.approved_by = payload.approved_by
    db.commit()
    return {"ok": True, "status": action.status}


@router.post("/{incident_id}/actions/{action_id}/simulate")
def simulate_action(incident_id: int, action_id: int, db: Session = Depends(get_db)):
    action = db.query(models.ResponseAction).filter(
        models.ResponseAction.id == action_id,
        models.ResponseAction.incident_id == incident_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action.status = "simulated"
    db.commit()
    return {"ok": True, "status": action.status, "message": f"模拟执行: {action.action_type}"}
