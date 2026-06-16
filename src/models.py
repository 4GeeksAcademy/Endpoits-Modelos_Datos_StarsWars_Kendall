from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(16))
    last_name: Mapped[str] = mapped_column(String(16))
    subscription_date: Mapped[Date] = mapped_column(Date())
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "last_name": self.last_name,
            "subscription_date": self.subscription_date,
            
            "favorites": [favorite.serialize() for favorite in self.favorites]
        }

class Person(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    species: Mapped[str] = mapped_column(String(30))
    hair_or_skin_color: Mapped[str] = mapped_column(String(30))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "hair_or_skin_color": self.hair_or_skin_color
        }
    
class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    weather: Mapped[str] = mapped_column(String(30))
    land: Mapped[str] = mapped_column(String(30))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "weather": self.weather,
            "land": self.land
        }
    
class Favorites(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    person_id: Mapped[int | None] = mapped_column(ForeignKey("person.id"), nullable=True)
    planet_id : Mapped[int | None] = mapped_column(ForeignKey("planets.id"), nullable=True)

    user: Mapped[User] = relationship(backref="favorites") 
    person: Mapped[Person] = relationship()
    planet: Mapped[Planets] = relationship()

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "person_id": self.person_id,
            "planet_id": self.planet_id
        }