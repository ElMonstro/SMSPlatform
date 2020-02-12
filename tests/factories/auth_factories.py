import factory
from faker import Faker


from api.authentication.models import User, Company

fake = Faker()

class CompanyFactory(factory.DjangoModelFactory):
    """create test  factory"""
    class Meta:
        model =  Company

    name = factory.Faker('sentence', nb_words=3, variable_nb_words=True)

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
    company = factory.SubFactory(CompanyFactory)
