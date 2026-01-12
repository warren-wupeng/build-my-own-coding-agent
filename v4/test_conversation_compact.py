#!/usr/bin/env python3
# test_conversation_compact.py - Tests for conversation compression functionality
# V4 version: Unit and integration tests for compression algorithms

import sys
import json
from agent import AgentV4
from conversation.compressor import ConversationCompressor


def create_test_messages(count):
    """Create test messages for compression testing"""
    messages = []
    
    # First message (always preserved)
    messages.append({
        "role": "user",
        "content": "Initial task: Create a complex project"
    })
    
    # Create alternating pattern of assistant and tool messages
    for i in range(1, count):
        if i % 3 == 1:
            messages.append({
                "role": "assistant",
                "content": f"Step {i}: Processing task",
                "tool_calls": [{
                    "id": f"call_{i}",
                    "type": "function",
                    "function": {"name": "write_file", "arguments": '{"path": "file' + str(i) + '.py"}'}
                }]
            })
        elif i % 3 == 2:
            messages.append({
                "role": "tool",
                "name": "write_file",
                "content": f"✅ Successfully written file file{i-1}.py"
            })
        else:
            messages.append({
                "role": "assistant",
                "content": f"Step {i}: Continuing with next task"
            })
    
    return messages


def test_compression_basic():
    """Test basic compression functionality"""
    print("🧪 Test 1: Basic Compression")
    agent = AgentV4()
    agent.messages = create_test_messages(30)
    
    print(f"   Before: {len(agent.messages)} messages")
    compacted = agent.compressor.compact_messages_conservative(agent.messages)
    print(f"   After: {len(compacted)} messages")
    
    assert len(compacted) < len(agent.messages), "Compression should reduce message count"
    assert compacted[0]["role"] == "user", "First message should be preserved"
    assert len(compacted) <= agent.compressor.max_compacted_length, "Should respect max length"
    
    print("   ✅ Basic compression test passed\n")


def test_compression_preserves_recent():
    """Test that recent messages are preserved"""
    print("🧪 Test 2: Recent Messages Preservation")
    agent = AgentV4()
    agent.messages = create_test_messages(30)
    
    original_recent = agent.messages[-agent.compressor.keep_recent_messages:]
    compacted = agent.compressor.compact_messages_conservative(agent.messages)
    compacted_recent = compacted[-agent.compressor.keep_recent_messages:]
    
    print(f"   Original recent count: {len(original_recent)}")
    print(f"   Compacted recent count: {len(compacted_recent)}")
    
    # Recent messages should be preserved (at least the structure)
    assert len(compacted_recent) == agent.compressor.keep_recent_messages, "Recent messages should be preserved"
    
    print("   ✅ Recent messages preservation test passed\n")


def test_compression_preserves_first():
    """Test that first message is always preserved"""
    print("🧪 Test 3: First Message Preservation")
    agent = AgentV4()
    agent.messages = create_test_messages(30)
    
    first_message = agent.messages[0]
    compacted = agent.compressor.compact_messages_conservative(agent.messages)
    
    print(f"   Original first: {first_message['content'][:50]}...")
    print(f"   Compacted first: {compacted[0]['content'][:50]}...")
    
    assert compacted[0]["role"] == "user", "First message should be user message"
    assert "Initial task" in compacted[0]["content"], "First message content should be preserved"
    
    print("   ✅ First message preservation test passed\n")


def test_auto_compression_trigger():
    """Test automatic compression trigger"""
    print("🧪 Test 4: Auto-Compression Trigger")
    agent = AgentV4()
    agent.messages = create_test_messages(30)
    
    initial_count = len(agent.messages)
    print(f"   Initial message count: {initial_count}")
    print(f"   Threshold: {agent.compressor.auto_compact_threshold}")
    
    # Simulate one step (which should trigger compression)
    if agent.compressor.should_compact(agent.messages):
        agent._auto_compact_conversation()
    
    final_count = len(agent.messages)
    print(f"   Final message count: {final_count}")
    
    assert final_count < initial_count, "Auto-compression should reduce messages"
    assert agent.compressor.compressed_count == 1, "Compression count should be incremented"
    
    print("   ✅ Auto-compression trigger test passed\n")


def test_message_classification():
    """Test message classification for grouping"""
    print("🧪 Test 5: Message Classification")
    agent = AgentV4()
    
    test_cases = [
        ({"role": "user", "content": "test"}, "user_request"),
        ({"role": "assistant", "content": "response"}, "ai_response"),
        ({"role": "assistant", "tool_calls": []}, "ai_tool_calls"),
        ({"role": "tool", "name": "test_tool"}, "tool_results"),
    ]
    
    for msg, expected_type in test_cases:
        msg_type = agent.compressor.classify_message(msg)
        assert msg_type == expected_type, f"Expected {expected_type}, got {msg_type}"
        print(f"   ✅ {msg.get('role')} → {msg_type}")
    
    print("   ✅ Message classification test passed\n")


def test_block_analysis():
    """Test message block analysis"""
    print("🧪 Test 6: Block Analysis")
    agent = AgentV4()
    agent.messages = create_test_messages(20)
    
    blocks = agent.compressor.analyze_message_structure(agent.messages[1:-15])
    
    print(f"   Total blocks identified: {len(blocks)}")
    for i, block in enumerate(blocks):
        print(f"   Block {i+1}: {block['type']} ({len(block['messages'])} messages)")
    
    assert len(blocks) > 0, "Should identify at least one block"
    
    print("   ✅ Block analysis test passed\n")


def test_compression_below_threshold():
    """Test that compression doesn't happen below threshold"""
    print("🧪 Test 7: Below Threshold Behavior")
    agent = AgentV4()
    agent.messages = create_test_messages(20)  # Below threshold of 25
    
    initial_count = len(agent.messages)
    compacted = agent.compressor.compact_messages_conservative(agent.messages)
    final_count = len(compacted)
    
    print(f"   Initial: {initial_count} messages")
    print(f"   Final: {final_count} messages")
    print(f"   Threshold: {agent.compressor.auto_compact_threshold}")
    
    # Should not compress if below max_compacted_length
    if initial_count <= agent.compressor.max_compacted_length:
        assert final_count == initial_count, "Should not compress if below max length"
    
    print("   ✅ Below threshold test passed\n")


def test_token_estimation():
    """Test token estimation in statistics"""
    print("🧪 Test 8: Token Estimation")
    agent = AgentV4()
    agent.messages = create_test_messages(30)
    
    total_chars = sum(len(json.dumps(msg)) for msg in agent.messages)
    estimated_tokens = total_chars // 4
    
    print(f"   Total characters: {total_chars}")
    print(f"   Estimated tokens: ~{estimated_tokens}")
    
    assert estimated_tokens > 0, "Should estimate positive token count"
    assert estimated_tokens < total_chars, "Tokens should be less than characters"
    
    print("   ✅ Token estimation test passed\n")


def run_all_tests():
    """Run all compression tests"""
    print("=" * 60)
    print("🧪 V4 Conversation Compression Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_compression_basic,
        test_compression_preserves_recent,
        test_compression_preserves_first,
        test_auto_compression_trigger,
        test_message_classification,
        test_block_analysis,
        test_compression_below_threshold,
        test_token_estimation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"   ❌ Test error: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
