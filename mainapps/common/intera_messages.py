
from django.http import HttpResponse


class InteraMessages:

    def __init__(self,hx_request=None, hx_trigger='revealed', target=None,) -> None:
        self.hx_request=hx_request
        self.hx_trigger=hx_trigger
        self.target=target

    def success(self,messages):

        return
    def send_request(self):
        if self.hx_request and self.target:
            hx_request=f"""hx-request='{self.hx_request}' hx-target='#{self.target}' hx-trigger='{self.hx_trigger}' """

            return hx_request
        return
    def compile_message(self,messages):
        return HttpResponse(
            f"""
            <div hx-tart='#d'></div>
"""
        )                         

    
            