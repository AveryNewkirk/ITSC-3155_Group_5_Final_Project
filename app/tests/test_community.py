

def test_route(client):

    response = client.get('/community')
    
    assert response.data is not None
    