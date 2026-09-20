from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomerPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, customer, timestamp):
        password = customer.password or ""

        return (
            str(customer.pk)
            + str(timestamp)
            + password
        )


customer_password_reset_token = (
    CustomerPasswordResetTokenGenerator()
)