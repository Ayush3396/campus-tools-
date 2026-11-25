"""
marketplace/forms.py

ModelForms for Item, LendingRequest, and ExchangeRequest.

A ModelForm automatically generates form fields from a model's fields.
We just specify which fields to include using 'fields' in Meta.
"""

from django import forms
from .models import Item, LendingRequest, ExchangeRequest


class ItemForm(forms.ModelForm):
    """
    Form for adding and editing item listings.
    Fields: name, description, category, condition, listing_type, image.
    'owner' and 'availability' are set by the view, not by the user directly.
    """

    class Meta:
        model = Item
        fields = ('name', 'description', 'category', 'condition', 'listing_type', 'image')
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the item — its use, any wear and tear, accessories included, etc.'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Casio fx-991ES Scientific Calculator'
            }),
        }
        labels = {
            'listing_type': 'Listing Type',
            'image': 'Item Photo (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image not required (it is optional)
        self.fields['image'].required = False
        # Add a helpful label to category dropdown
        self.fields['category'].empty_label = '-- Select a category --'


class LendingRequestForm(forms.ModelForm):
    """
    Form for submitting a borrowing request.
    Only 'message' and 'duration' are filled by the requester.
    item, requester, owner, status are set programmatically in the view.
    """

    class Meta:
        model = LendingRequest
        fields = ('message', 'duration')
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Explain why you need this item and how you will take care of it...'
            }),
            'duration': forms.TextInput(attrs={
                'placeholder': 'e.g. 3 days, 1 week, until Dec 20'
            }),
        }
        labels = {
            'message': 'Message to Owner',
            'duration': 'How long do you need it?',
        }


class ExchangeRequestForm(forms.ModelForm):
    """
    Form for submitting an exchange proposal.
    The requester describes what they are offering in return.
    """

    class Meta:
        model = ExchangeRequest
        fields = ('offered_item_name', 'offered_item_description', 'message')
        widgets = {
            'offered_item_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Engineering Drawing Kit'
            }),
            'offered_item_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the condition, age, and any accessories included...'
            }),
            'message': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Any additional message for the owner... (optional)'
            }),
        }
        labels = {
            'offered_item_name': 'What are you offering in exchange?',
            'offered_item_description': 'Describe your offered item',
            'message': 'Additional message (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].required = False
