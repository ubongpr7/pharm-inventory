import base64

encoded_message = "SG9wZSB5b3VyIGJpcnRoZGF5IGxvb3BzIHJ1biBzbW9vdGhseSBhbmQgdGhhdCB5b3UgZG9uJ3QgYnJlYWsgb3V0IG9mIHRoZSBmb3IgbG9vcCB0b28gc29vbi4KRnJvbSAwIHRvIDEsIGZyb20gMSB0byAxMCwgZnJvbSAxMCB0byAxMDAsIGFuZCBmcm9tIDEwMCBjb250aW51ZSDigKYgSSBsb3ZlIGl0ISBIYXBweSBiaXJ0aGRheSwgTWlzcyBFc3RoZXIhCllvdSd2ZSBiZWVuIGxlYXJuaW5nIHB5dGhvbiBmb3IgMiBtb250aHMgbm93LCBhbmQgeW91ciBlbnRodXNpYXNtIGlzIGluc3BpcmluZyEgCkxldCBtZSBzYXk6IERvbid0IGdpdmUgdXAuIFB1c2ggdGhyb3VnaCwgYW5kIG1ha2UgdGhpcyB5ZWFyIGJlIHRoZSB5ZWFyIHlvdSBiZWNvbWUgYSBQeXRob25pc3RhIQpNYXkgdGhpcyB5ZWFyIGJlIGZpbGxlZCB3aXRoIHN1Y2Nlc3MsIGpveSwgYW5kIGFtYXppbmcgUHl0aG9uIGFkdmVudHVyZXMhCklmIGl0IGlzIHlvdXIgd2lzaCB0aGF0IHlvdSBsYW5kIGEgam9iIGluIHRoZSB0ZWNoIGluZHVzdHJ5LCBTbyBiZSBpdCEKSSB3YW50IHRvIHdpc2ggeW91IGEgaGFwcHkgYmlydGhkYXkgaW4gY29kZS4KSXJvbmljYWxseSwgSSdtIG5vdCBzdXJlIGlmIEkga25vdyBob3cgdG8gc2VuZCBpdCBpbiB0aGUgYmluYXJ5IGZvcm0uCkJ1dCBpbiBteSBvd24gd2F5LCBJIHdpbGwgY29udGludWUgdG8gd2lzaCB5b3Ug4oCcSGFwcHkgQmlydGhkYXnigJ0gd2hlbiB0aGUgdGltZSBjb21lcy4=="


# Decode the message
message = """
    Hope your birthday loops run smoothly and that you don't break out of the for loop too soon.
    From 0 to 1, from 1 to 10, from 10 to 100, and from 100 continue … I love it! Happy birthday, Miss Esher!
    You've been learning python for 2 months now, and your engthusiasm is inspiriing! L
    et me say: Dont give up. Push through, and make this year be the year you become a Pythonista!
    May this year be filled with success, joy, and amazing Python adventures!
    If it is your wish that you land a job in the tech industry, So be it!
    I want to wish you a happy birthday in code.
    Ironically, I'm not sure if I know how to send it in the binary form.
    But in my own way, I will continue to wish you “Happy Birthday” when the time comes.
"""

encoded = base64.b64encode(message.encode()).decode()
print(encoded)
decoded_message = base64.b64decode(encoded_message).decode("utf-8")

print(decoded_message)
