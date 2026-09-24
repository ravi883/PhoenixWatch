from django import forms

class TrackOrderForm(forms.Form):
    order_id = forms.CharField(max_length=30,label="Order ID",required=False)
    email = forms.EmailField(label="Email",required=False)

    