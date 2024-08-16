from src.models import DatabaseSession
from src.models.user import User


def create_admin():
    email = input('Enter new admin email: ')

    with DatabaseSession().withSession() as session:
        user_orm = session.query(User).where(
            User.email == email
        ).one()
        user_orm.is_admin = True
        session.add(user_orm)
        session.commit()

        print(user_orm, "Is now an admin")
