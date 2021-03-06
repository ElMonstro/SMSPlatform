import factory

name = factory.Faker('sentence', nb_words=5, variable_nb_words=True)

valid_sms_data = {
    "message": "yeah mayyyne",
    "recepients": ["+254754333000"]
}

data_without_recepient_or_group = {
    "message": "yeah mayyyne"
}

data_with_both_recepient_or_group = {
    "message": "yeah mayyyne",
    "recepients": ["+254754333000"],
    "groups": [1]
}

email_data_with_both_recepient_or_group = {
    "subject": "joh",
    "message": "yeah mayyyne",
    "recepients": ["jratcher@gmail.com"],
    "groups": [1]
}

valid_sms_template_data = {
    "message": "goat ms",
    "name": "josh"
}

invalid_sms_template_data = {
    "name": "josh"
}

valid_group_data = {
    "name": name,
    "description": "name"
}

valid_member_data = {
    "first_name": "Blero",
    "second_name": "Consolero",
    "phone": "+254754333000"
}

valid_email_data = {
    "subject": "yoh",
    "message": "Come mbio",
    "recepients": ["jratcher@gmail.com"]
}

email_data_without_recepient_or_group = {
    "message": "yeah mayyyne",
    "subject": "joh"
}
