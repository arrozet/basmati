import pytest
import pytest_asyncio
from httpx import AsyncClient
from main import app
from core.database import Database
from core.config import settings
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for the session"""
    import asyncio
    return asyncio.get_event_loop_policy()


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Setup and teardown database connection for tests"""
    logger.info("🔧 Setting up database for tests...")
    await Database.connect_db()
    yield
    logger.info("🧹 Cleaning up database after tests...")
    await Database.close_db()


@pytest.mark.asyncio
async def test_database_connection(setup_database):
    """Test that database connection is established"""
    # Verify client exists
    assert Database.client is not None, "Database client should be initialized"
    
    # Verify we can ping the database
    try:
        result = await Database.client.admin.command('ping')
        assert result.get('ok') == 1.0, "Database ping should return ok=1.0"
        logger.info("✅ Database connection test passed")
    except Exception as e:
        pytest.fail(f"Failed to ping database: {e}")


@pytest.mark.asyncio
async def test_get_database(setup_database):
    """Test getting database instance"""
    db = Database.get_db()
    assert db is not None, "Database instance should not be None"
    assert db.name == settings.mongodb_db_name, f"Database name should be {settings.mongodb_db_name}"
    logger.info("✅ Get database test passed")


@pytest.mark.asyncio
async def test_database_operations(setup_database):
    """Test basic database operations (insert, find, delete)"""
    db = Database.get_db()
    test_collection = db["test_connection"]
    
    # Test insert
    test_doc = {"test": "connection_test", "timestamp": "2025-10-21"}
    result = await test_collection.insert_one(test_doc)
    assert result.inserted_id is not None, "Insert should return an ID"
    logger.info(f"✅ Inserted test document with ID: {result.inserted_id}")
    
    # Test find
    found_doc = await test_collection.find_one({"_id": result.inserted_id})
    assert found_doc is not None, "Should find the inserted document"
    assert found_doc["test"] == "connection_test", "Document content should match"
    logger.info("✅ Found test document")
    
    # Test delete (cleanup)
    delete_result = await test_collection.delete_one({"_id": result.inserted_id})
    assert delete_result.deleted_count == 1, "Should delete one document"
    logger.info("✅ Deleted test document")


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200, "Health endpoint should return 200"
        data = response.json()
        assert data["status"] == "healthy", "Status should be healthy"
        logger.info("✅ Health endpoint test passed")


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200, "Root endpoint should return 200"
        data = response.json()
        assert data["status"] == "online", "Status should be online"
        assert "version" in data, "Response should include version"
        logger.info("✅ Root endpoint test passed")


@pytest.mark.asyncio
async def test_api_v1_users_endpoint(setup_database):
    """Test users API endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/")
        assert response.status_code == 200, "Users endpoint should return 200"
        data = response.json()
        assert "users" in data, "Response should include users list"
        assert "total" in data, "Response should include total count"
        assert "page" in data, "Response should include page number"
        assert "page_size" in data, "Response should include page_size"
        logger.info("✅ API v1 users endpoint test passed")


@pytest.mark.asyncio
async def test_list_collections(setup_database):
    """Test listing collections in database"""
    db = Database.get_db()
    collections = await db.list_collection_names()
    assert isinstance(collections, list), "Collections should be a list"
    logger.info(f"✅ Found {len(collections)} collections: {collections}")


@pytest.mark.asyncio
async def test_database_stats(setup_database):
    """Test getting database statistics"""
    db = Database.get_db()
    stats = await db.command("dbstats")
    assert "collections" in stats, "Stats should include collections count"
    assert "dataSize" in stats, "Stats should include data size"
    assert "storageSize" in stats, "Stats should include storage size"
    logger.info(f"✅ Database stats: {stats.get('collections')} collections, "
                f"{stats.get('dataSize')} bytes data")


@pytest.mark.asyncio
async def test_users_crud_api(setup_database):
    """Test complete CRUD operations for users API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. CREATE - Create a test user
        logger.info("Testing CREATE user...")
        new_user = {
            "name": "Test User",
            "email": "test_crud@example.com",
            "pwd": "test1234"
        }
        response = await client.post("/api/v1/users/", json=new_user)
        assert response.status_code == 201, f"Create should return 201, got {response.status_code}"
        created_user = response.json()
        assert created_user["name"] == new_user["name"]
        assert created_user["email"] == new_user["email"]
        assert "_id" in created_user, "Response should include user ID"
        user_id = created_user["_id"]
        logger.info(f"✅ User created with ID: {user_id}")
        
        # 2. READ - Get the created user
        logger.info("Testing READ user by ID...")
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200, "Get user should return 200"
        user = response.json()
        assert user["_id"] == user_id
        assert user["email"] == new_user["email"]
        logger.info("✅ User retrieved successfully")
        
        # 3. UPDATE - Update the user
        logger.info("Testing UPDATE user...")
        update_data = {"name": "Updated Test User"}
        response = await client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200, "Update should return 200"
        updated_user = response.json()
        assert updated_user["name"] == "Updated Test User"
        logger.info("✅ User updated successfully")
        
        # 4. DELETE - Delete the user
        logger.info("Testing DELETE user...")
        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 200, "Delete should return 200"
        logger.info("✅ User deleted successfully")
        
        # 5. Verify deletion
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404, "Deleted user should return 404"
        logger.info("✅ Complete CRUD cycle test passed")
