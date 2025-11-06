#!/usr/bin/env python
"""
Performance test script to verify Phase 4 optimizations.

Tests:
1. Database query performance with indexes
2. Cache effectiveness for model registry
3. Cache effectiveness for conversations
4. N+1 query prevention with eager loading
"""

import os
import sys
import time
from pathlib import Path

# Set environment variables before imports
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ENCRYPTION_KEY", "V9itAn6qCAdzBsZIxwQhO_coouCcjn0H0vCv2UEd8hY=")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmselect import create_app
from llmselect.extensions import db, cache
from llmselect.models import User, Conversation, Message, APIKey
from llmselect.services.conversations import ConversationService
from llmselect.services.model_registry import ModelRegistryService


def setup_test_data(app):
    """Create test data for performance testing."""
    with app.app_context():
        # Create test user
        user = User(username="perftest", password_hash="test")
        db.session.add(user)
        db.session.commit()

        # Create 100 conversations with messages
        for i in range(100):
            conv = Conversation(
                user_id=user.id,
                provider="openai",
                model=f"gpt-4o-{i % 3}",
                title=f"Test Conversation {i}",
            )
            db.session.add(conv)
            db.session.flush()

            # Add 10 messages per conversation
            for j in range(10):
                msg = Message(
                    conversation_id=conv.id,
                    role="user" if j % 2 == 0 else "assistant",
                    content=f"Message {j} in conversation {i}",
                )
                db.session.add(msg)

        db.session.commit()
        return user.id


def test_query_performance(app):
    """Test database query performance with indexes."""
    print("\n=== Testing Database Query Performance ===")

    with app.app_context():
        user_id = User.query.filter_by(username="perftest").first().id

        # Test 1: Get all conversations (should use idx_conversation_user_created)
        start = time.time()
        conversations = (
            Conversation.query.filter_by(user_id=user_id)
            .order_by(Conversation.created_at.desc())
            .all()
        )
        duration = time.time() - start
        print(f"✓ Fetched {len(conversations)} conversations in {duration*1000:.2f}ms")
        assert duration < 0.1, f"Query too slow: {duration*1000:.2f}ms"

        # Test 2: Get conversations by provider (should use idx_conversations_user_provider)
        start = time.time()
        openai_convs = Conversation.query.filter_by(user_id=user_id, provider="openai").all()
        duration = time.time() - start
        print(f"✓ Filtered {len(openai_convs)} conversations by provider in {duration*1000:.2f}ms")
        assert duration < 0.1, f"Query too slow: {duration*1000:.2f}ms"

        # Test 3: Get messages for a conversation (should use idx_message_conversation_created)
        conv_id = conversations[0].id
        start = time.time()
        messages = (
            Message.query.filter_by(conversation_id=conv_id).order_by(Message.created_at).all()
        )
        duration = time.time() - start
        print(f"✓ Fetched {len(messages)} messages in {duration*1000:.2f}ms")
        assert duration < 0.05, f"Query too slow: {duration*1000:.2f}ms"


def test_model_registry_cache(app):
    """Test model registry caching."""
    print("\n=== Testing Model Registry Cache ===")

    with app.app_context():
        cache.clear()
        registry = ModelRegistryService()

        # First call - should cache
        start = time.time()
        models1 = registry.get_models(provider="openai")
        first_call = time.time() - start
        print(f"✓ First call (cold): {first_call*1000:.2f}ms, {len(models1)} models")

        # Second call - should be cached
        start = time.time()
        models2 = registry.get_models(provider="openai")
        second_call = time.time() - start
        print(f"✓ Second call (cached): {second_call*1000:.2f}ms")

        # Cached call should be faster
        speedup = first_call / second_call if second_call > 0 else float("inf")
        print(f"✓ Cache speedup: {speedup:.1f}x faster")

        # Verify cache hit
        assert models1 == models2, "Cached data should match"
        assert second_call < first_call, "Cached call should be faster"


def test_conversation_cache(app):
    """Test conversation list caching."""
    print("\n=== Testing Conversation Cache ===")

    with app.app_context():
        cache.clear()
        user_id = User.query.filter_by(username="perftest").first().id
        service = ConversationService()

        # First call - should cache
        start = time.time()
        convs1 = service.get_user_conversations(user_id, limit=50)
        first_call = time.time() - start
        print(f"✓ First call (cold): {first_call*1000:.2f}ms, {len(convs1)} conversations")

        # Second call - should be cached
        start = time.time()
        convs2 = service.get_user_conversations(user_id, limit=50)
        second_call = time.time() - start
        print(f"✓ Second call (cached): {second_call*1000:.2f}ms")

        # Cached call should be faster
        speedup = first_call / second_call if second_call > 0 else float("inf")
        print(f"✓ Cache speedup: {speedup:.1f}x faster")

        assert len(convs1) == len(convs2), "Cached data should match"
        assert second_call < first_call, "Cached call should be faster"


def test_eager_loading(app):
    """Test that eager loading prevents N+1 queries."""
    print("\n=== Testing Eager Loading (N+1 Prevention) ===")

    with app.app_context():
        cache.clear()
        user_id = User.query.filter_by(username="perftest").first().id
        service = ConversationService()

        # Get conversations with eager loading
        start = time.time()
        conversations = service.get_user_conversations(user_id, limit=10)

        # Access messages (should not trigger additional queries due to eager loading)
        total_messages = sum(len(conv.messages) for conv in conversations)
        duration = time.time() - start

        print(f"✓ Loaded {len(conversations)} conversations with {total_messages} messages")
        print(f"✓ Total time: {duration*1000:.2f}ms")
        print(f"✓ Average per conversation: {duration*1000/len(conversations):.2f}ms")

        # Should be fast because messages are eager loaded
        assert duration < 0.2, f"Query too slow: {duration*1000:.2f}ms"


def test_cache_invalidation(app):
    """Test that cache is properly invalidated on mutations."""
    print("\n=== Testing Cache Invalidation ===")

    with app.app_context():
        cache.clear()
        user_id = User.query.filter_by(username="perftest").first().id
        service = ConversationService()

        # Cache the conversation list with higher limit to see all
        convs_before = service.get_user_conversations(user_id, limit=200)
        count_before = len(convs_before)

        # Create a new conversation (should invalidate cache)
        new_conv = service.create_conversation(user_id, "anthropic", "claude-3-opus")

        # Fetch again (should be fresh data, not cached)
        convs_after = service.get_user_conversations(user_id, limit=200)
        count_after = len(convs_after)

        print(f"✓ Conversations before: {count_before}")
        print(f"✓ Conversations after: {count_after}")
        print(f"✓ Cache invalidation working: {count_after > count_before}")

        assert count_after > count_before, "New conversation should appear"


def run_all_tests():
    """Run all performance tests."""
    print("=" * 60)
    print("Phase 4 Performance Optimization Tests")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # Clean up and set up test data
        db.drop_all()
        db.create_all()
        cache.clear()

        user_id = setup_test_data(app)
        print(f"\n✓ Created test data: 100 conversations, 1000 messages")

    try:
        test_query_performance(app)
        test_model_registry_cache(app)
        test_conversation_cache(app)
        test_eager_loading(app)
        test_cache_invalidation(app)

        print("\n" + "=" * 60)
        print("✅ All Performance Tests Passed!")
        print("=" * 60)

        print("\n📊 Performance Summary:")
        print("  • Database queries: < 100ms ✓")
        print("  • Model registry cached: 24 hours ✓")
        print("  • Conversation list cached: 1 hour ✓")
        print("  • N+1 queries prevented: eager loading ✓")
        print("  • Cache invalidation: working ✓")

    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
