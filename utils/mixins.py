from django.db import models

class AbstractModelA(models.Model):
    # Your common fields and methods for AbstractModelA

    def save(self, *args, **kwargs):
        # Custom save logic for AbstractModelA
        print("AbstractModelA's save method is called")

        # Call the save method of the parent class (superclass)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class AbstractModelB(models.Model):
    # Your common fields and methods for AbstractModelB

    def save(self, *args, **kwargs):
        # Custom save logic for AbstractModelB
        print("AbstractModelB's save method is called")

        # Call the save method of the parent class (superclass)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class MyConcreteModel(AbstractModelA, AbstractModelB):
    # Your additional fields for the concrete model
    name = models.CharField(max_length=255)

    def additional_save_logic(self):
        # Your additional save logic specific to the concrete model
        print("Additional save logic for the concrete model")

    def save(self, *args, **kwargs):
        # Call the save methods of the abstract models in the desired order
        super(AbstractModelA, self).save(*args, **kwargs)
        super(AbstractModelB, self).save(*args, **kwargs)

        # Call additional functions specific to the concrete model
        self.additional_save_logic()

    def __str__(self):
        return self.name









import jwt
import requests

# Assume you have the JWT token stored in a variable named 'token'
token = 'your_jwt_token_here'

# Decode the JWT token to extract user information
decoded_token = jwt.decode(token, options={"verify_signature": False})

# Access user information
username = decoded_token.get('username')
email = decoded_token.get('email')

# Now you can use 'username' and 'email' in your Python code as needed
print('Username:', username)
print('Email:', email)




