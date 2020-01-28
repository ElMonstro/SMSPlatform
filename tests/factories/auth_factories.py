import factory
from faker import Faker


from api.authentication.models import User, Role

fake = Faker()


class RoleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Role

    title = factory.LazyAttribute(lambda _: "user")


class UserFactory(factory.DjangoModelFactory):
    """This class will create test users"""

    class Meta:
        model = User

    full_name = factory.LazyAttribute(
        lambda _: fake.first_name() + " " + fake.last_name()
    )
    password = factory.PostGenerationMethodCall("set_password", "password")
    email = factory.LazyAttribute(lambda _: fake.email())
    phone = "+254" + fake.msisdn()[:9]
    role = factory.SubFactory(RoleFactory)
