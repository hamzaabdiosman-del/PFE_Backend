from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Client, Commande, DetailsCommande, Paiement, Service, Base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# postpone table creation until the app is starting so that the
# database has a chance to be reachable. In production you may manage
# migrations with Alembic instead of create_all.

app = FastAPI()

# enable CORS so React/Vite frontend on localhost can call these APIs
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # this will create sqlite file or contact the configured DB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Pydantic schemas
class ClientBase(BaseModel):
    nom: str
    email: str
    mot_de_passe: str

class ClientCreate(ClientBase):
    pass

class ClientSchema(ClientBase):
    id: int
    date_creation: datetime

    class Config:
        from_attributes = True

class CommandeBase(BaseModel):
    user_id: int
    produit_id: int
    total: Optional[float]

class CommandeCreate(CommandeBase):
    pass

class CommandeSchema(CommandeBase):
    class Config:
        from_attributes = True

class DetailsCommandeBase(BaseModel):
    cammande_id: Optional[int]
    service_id: Optional[int]
    quantite: int
    prix_unitaire: float

class DetailsCommandeCreate(DetailsCommandeBase):
    pass

class DetailsCommandeSchema(DetailsCommandeBase):
    id: int

    class Config:
        from_attributes = True

class PaiementBase(BaseModel):
    commande_id: int
    methode: str
    montant: float

class PaiementCreate(PaiementBase):
    pass

class PaiementSchema(PaiementBase):
    id: int
    date_paiement: datetime

    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    nom_service: Optional[str]
    description: str
    prix: Optional[float]

class ServiceCreate(ServiceBase):
    pass

class ServiceSchema(ServiceBase):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str

# Routes for Authentication
@app.get("/login/{email}")
def login_get(email: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.email == email).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"id": client.id, "nom": client.nom, "email": client.email}

@app.post("/login/")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.email == credentials.email).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    if client.mot_de_passe != credentials.mot_de_passe:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"id": client.id, "nom": client.nom, "email": client.email}

# Routes for Clients
@app.post("/clients/", response_model=ClientSchema)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients/", response_model=List[ClientSchema])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients

@app.get("/clients/{client_id}", response_model=ClientSchema)
def read_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.put("/clients/{client_id}", response_model=ClientSchema)
def update_client(client_id: int, client: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in client.dict().items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted"}

# Routes for Commandes
@app.post("/commandes/", response_model=CommandeSchema)
def create_commande(commande: CommandeCreate, db: Session = Depends(get_db)):
    db_commande = Commande(**commande.dict())
    db.add(db_commande)
    db.commit()
    db.refresh(db_commande)
    return db_commande

@app.get("/commandes/", response_model=List[CommandeSchema])
def read_commandes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    commandes = db.query(Commande).offset(skip).limit(limit).all()
    return commandes

@app.get("/commandes/{user_id}/{produit_id}", response_model=CommandeSchema)
def read_commande(user_id: int, produit_id: int, db: Session = Depends(get_db)):
    commande = db.query(Commande).filter(Commande.user_id == user_id, Commande.produit_id == produit_id).first()
    if commande is None:
        raise HTTPException(status_code=404, detail="Commande not found")
    return commande

@app.put("/commandes/{user_id}/{produit_id}", response_model=CommandeSchema)
def update_commande(user_id: int, produit_id: int, commande: CommandeCreate, db: Session = Depends(get_db)):
    db_commande = db.query(Commande).filter(Commande.user_id == user_id, Commande.produit_id == produit_id).first()
    if db_commande is None:
        raise HTTPException(status_code=404, detail="Commande not found")
    for key, value in commande.dict().items():
        setattr(db_commande, key, value)
    db.commit()
    db.refresh(db_commande)
    return db_commande

@app.delete("/commandes/{user_id}/{produit_id}")
def delete_commande(user_id: int, produit_id: int, db: Session = Depends(get_db)):
    commande = db.query(Commande).filter(Commande.user_id == user_id, Commande.produit_id == produit_id).first()
    if commande is None:
        raise HTTPException(status_code=404, detail="Commande not found")
    db.delete(commande)
    db.commit()
    return {"message": "Commande deleted"}

# Routes for DetailsCommande
@app.post("/details_commande/", response_model=DetailsCommandeSchema)
def create_details_commande(details: DetailsCommandeCreate, db: Session = Depends(get_db)):
    db_details = DetailsCommande(**details.dict())
    db.add(db_details)
    db.commit()
    db.refresh(db_details)
    return db_details

@app.get("/details_commande/", response_model=List[DetailsCommandeSchema])
def read_details_commandes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    details = db.query(DetailsCommande).offset(skip).limit(limit).all()
    return details

@app.get("/details_commande/{details_id}", response_model=DetailsCommandeSchema)
def read_details_commande(details_id: int, db: Session = Depends(get_db)):
    details = db.query(DetailsCommande).filter(DetailsCommande.id == details_id).first()
    if details is None:
        raise HTTPException(status_code=404, detail="DetailsCommande not found")
    return details

@app.put("/details_commande/{details_id}", response_model=DetailsCommandeSchema)
def update_details_commande(details_id: int, details: DetailsCommandeCreate, db: Session = Depends(get_db)):
    db_details = db.query(DetailsCommande).filter(DetailsCommande.id == details_id).first()
    if db_details is None:
        raise HTTPException(status_code=404, detail="DetailsCommande not found")
    for key, value in details.dict().items():
        setattr(db_details, key, value)
    db.commit()
    db.refresh(db_details)
    return db_details

@app.delete("/details_commande/{details_id}")
def delete_details_commande(details_id: int, db: Session = Depends(get_db)):
    details = db.query(DetailsCommande).filter(DetailsCommande.id == details_id).first()
    if details is None:
        raise HTTPException(status_code=404, detail="DetailsCommande not found")
    db.delete(details)
    db.commit()
    return {"message": "DetailsCommande deleted"}

# Routes for Paiements
@app.post("/paiements/", response_model=PaiementSchema)
def create_paiement(paiement: PaiementCreate, db: Session = Depends(get_db)):
    db_paiement = Paiement(**paiement.dict())
    db.add(db_paiement)
    db.commit()
    db.refresh(db_paiement)
    return db_paiement

@app.get("/paiements/", response_model=List[PaiementSchema])
def read_paiements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    paiements = db.query(Paiement).offset(skip).limit(limit).all()
    return paiements

@app.get("/paiements/{paiement_id}", response_model=PaiementSchema)
def read_paiement(paiement_id: int, db: Session = Depends(get_db)):
    paiement = db.query(Paiement).filter(Paiement.id == paiement_id).first()
    if paiement is None:
        raise HTTPException(status_code=404, detail="Paiement not found")
    return paiement

@app.put("/paiements/{paiement_id}", response_model=PaiementSchema)
def update_paiement(paiement_id: int, paiement: PaiementCreate, db: Session = Depends(get_db)):
    db_paiement = db.query(Paiement).filter(Paiement.id == paiement_id).first()
    if db_paiement is None:
        raise HTTPException(status_code=404, detail="Paiement not found")
    for key, value in paiement.dict().items():
        setattr(db_paiement, key, value)
    db.commit()
    db.refresh(db_paiement)
    return db_paiement

@app.delete("/paiements/{paiement_id}")
def delete_paiement(paiement_id: int, db: Session = Depends(get_db)):
    paiement = db.query(Paiement).filter(Paiement.id == paiement_id).first()
    if paiement is None:
        raise HTTPException(status_code=404, detail="Paiement not found")
    db.delete(paiement)
    db.commit()
    return {"message": "Paiement deleted"}

# Routes for Services
@app.post("/services/", response_model=ServiceSchema)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.post("/services/bulk", response_model=List[ServiceSchema])
def create_services_bulk(services: List[ServiceCreate], db: Session = Depends(get_db)):
    db_services = [Service(**service.dict()) for service in services]
    db.add_all(db_services)
    db.commit()
    for service in db_services:
        db.refresh(service)
    return db_services

@app.get("/services/", response_model=List[ServiceSchema])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services = db.query(Service).offset(skip).limit(limit).all()
    return services

@app.get("/services/{service_id}", response_model=ServiceSchema)
def read_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.put("/services/{service_id}", response_model=ServiceSchema)
def update_service(service_id: int, service: ServiceCreate, db: Session = Depends(get_db)):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in service.dict().items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.delete("/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return {"message": "Service deleted"}