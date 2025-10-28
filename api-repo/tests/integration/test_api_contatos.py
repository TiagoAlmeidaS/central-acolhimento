"""Integration tests for contact API endpoints."""



def test_create_contato_manual(client, sample_contato_data):
    """Test creating a contact via API with explicit fields."""
    response = client.post("/api/v1/contatos", json=sample_contato_data)

    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Maria Silva"
    assert data["telefone"] == "11-9999-8888"
    assert data["email"] == "maria@example.com"
    assert data["motivo"] == "apoio emocional"


def test_create_contato_missing_required_fields(client):
    """Test creating contact with missing required fields."""
    response = client.post("/api/v1/contatos", json={"nome": "Test"})

    # Should fail validation or request explicit fields
    assert response.status_code in [422, 400]


def test_list_contatos(client):
    """Test listing contacts via API."""
    # Create some contacts first
    for i in range(3):
        client.post(
            "/api/v1/contatos",
            json={
                "nome": f"User {i}",
                "telefone": f"11-9999-{1000+i}",
                "motivo": "test",
            },
        )

    # List them
    response = client.get("/api/v1/contatos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_contato_by_id(client, sample_contato_data):
    """Test getting a contact by ID via API."""
    # Create a contact
    create_response = client.post("/api/v1/contatos", json=sample_contato_data)
    assert create_response.status_code == 201
    contato_id = create_response.json()["id"]

    # Get it
    response = client.get(f"/api/v1/contatos/{contato_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contato_id
    assert data["nome"] == "Maria Silva"


def test_get_contato_not_found(client):
    """Test getting non-existent contact returns 404."""
    response = client.get("/api/v1/contatos/99999")
    assert response.status_code == 404


def test_update_contato(client, sample_contato_data):
    """Test updating a contact via API."""
    # Create a contact
    create_response = client.post("/api/v1/contatos", json=sample_contato_data)
    contato_id = create_response.json()["id"]

    # Update it
    update_data = {"nome": "Maria Silva Updated"}
    response = client.put(f"/api/v1/contatos/{contato_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Maria Silva Updated"


def test_delete_contato(client, sample_contato_data):
    """Test deleting a contact via API."""
    # Create a contact
    create_response = client.post("/api/v1/contatos", json=sample_contato_data)
    contato_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/contatos/{contato_id}")

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/contatos/{contato_id}")
    assert get_response.status_code == 404


def test_list_contatos_with_pagination(client):
    """Test listing contacts with pagination."""
    # Create 5 contacts
    for i in range(5):
        client.post(
            "/api/v1/contatos",
            json={
                "nome": f"User {i}",
                "telefone": f"11-9999-{1000+i}",
                "motivo": "test",
            },
        )

    # Test pagination
    response = client.get("/api/v1/contatos?skip=2&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_contatos_with_filter(client):
    """Test listing contacts with filters."""
    # Create contacts with different motivos
    client.post(
        "/api/v1/contatos",
        json={
            "nome": "User A",
            "telefone": "11-1111-1111",
            "motivo": "apoio emocional",
        },
    )
    client.post(
        "/api/v1/contatos",
        json={
            "nome": "User B",
            "telefone": "11-2222-2222",
            "motivo": "orientação jurídica",
        },
    )

    # Filter by motivo
    response = client.get("/api/v1/contatos?motivo=apoio+emocional")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["motivo"] == "apoio emocional"
