from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    date_creation = Column(DateTime, default=func.now())

class Commande(Base):
    __tablename__ = "commandes"

    user_id = Column(Integer, primary_key=True)
    produit_id = Column(Integer, primary_key=True)
    total = Column(DECIMAL(10, 2))

class DetailsCommande(Base):
    __tablename__ = "details_commande"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cammande_id = Column(Integer)
    service_id = Column(Integer)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(DECIMAL(10, 0), nullable=False)

class Paiement(Base):
    __tablename__ = "paiements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    commande_id = Column(Integer, nullable=False)
    methode = Column(Enum('cash', 'carte', 'virement'), nullable=False)
    montant = Column(DECIMAL(10, 2), nullable=False)
    date_paiement = Column(DateTime, default=func.now())

class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom_service = Column(String(100))
    description = Column(Text, nullable=False)
    prix = Column(DECIMAL(10, 2))