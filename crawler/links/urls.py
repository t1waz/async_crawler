from starlette.routing import Route
from links import views


routes = [
    Route('/add_link', endpoint=views.AddLinkView, methods=['POST']),
    Route('/get_link_info', endpoint=views.GetLinkView, methods=['GET']),
    Route('/get_link_info/{id}', endpoint=views.GetLinkView, methods=['GET']),
]
