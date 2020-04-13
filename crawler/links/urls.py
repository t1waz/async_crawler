from starlette.routing import (
    Route,
    Mount
)

from links import views


routes = [
    Mount('/links', routes=[
        Route('/', views.LinkView, methods=['GET', 'POST']),
        Route('/{id}', views.LinkView, methods=['GET', 'PATCH', 'DELETE'])
    ]),
    Mount('/link_data', routes=[
        Route('/', views.LinkDataView, methods=['GET', 'POST']),
        Route('/{id}', views.LinkDataView, methods=['GET', 'PATH', 'DELETE'])
    ])
]
