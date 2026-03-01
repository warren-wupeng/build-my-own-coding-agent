"""Conversation compression module for AgentV4"""


class ConversationCompressor:
    """Handles conversation compression to manage context size"""
    
    def __init__(self,
                 auto_compact_threshold=25,
                 keep_recent_messages=15,
                 max_compacted_length=18,
                 compression_block_size=6):
        """Initialize compressor with configuration"""
        self.auto_compact_threshold = auto_compact_threshold
        self.keep_recent_messages = keep_recent_messages
        self.max_compacted_length = max_compacted_length
        self.compression_block_size = compression_block_size
        self.compressed_count = 0
    
    def should_compact(self, messages):
        """Check if conversation should be compacted"""
        return len(messages) > self.auto_compact_threshold
    
    def auto_compact(self, messages):
        """Automatically compact conversation using conservative approach"""
        print(f"📦 Auto-compacting conversation ({len(messages)} messages → preserving context)")
        
        compacted = self.compact_messages_conservative(messages)
        if compacted:
            if len(compacted) < len(messages):
                old_count = len(messages)
                self.compressed_count += 1
                print(f"   ✅ Conservative compression: {old_count} → {len(compacted)} messages")
                return compacted, True
            else:
                print(f"   ℹ️  Compression resulted in same or more messages ({len(messages)} → {len(compacted)})")
                return compacted, False
        else:
            print(f"   ℹ️  No compression needed - context preserved")
            return messages, False
    
    def classify_message(self, msg):
        """Classify message for grouping"""
        role = msg.get("role")
        
        if role == "user":
            return "user_request"
        elif role == "assistant":
            # Check for tool_calls - if tool_calls key exists, it's a tool call message
            # (even if empty list, it indicates intent to call tools)
            if "tool_calls" in msg:
                return "ai_tool_calls"
            return "ai_response"
        elif role == "tool":
            return "tool_results"
        else:
            return "other"
    
    def analyze_message_structure(self, messages):
        """Analyze message structure to identify compressible blocks"""
        blocks = []
        current_block = []
        current_type = None
        
        for i, msg in enumerate(messages):
            msg_type = self.classify_message(msg)
            
            # Group similar types together, but allow larger blocks
            if msg_type != current_type:
                if current_block:
                    blocks.append({
                        'type': current_type,
                        'messages': current_block,
                        'start_idx': i - len(current_block),
                        'end_idx': i - 1
                    })
                current_block = [msg]
                current_type = msg_type
            else:
                current_block.append(msg)
                # Only split if block gets very large (allow up to 12 messages per block)
                if len(current_block) >= 12:
                    blocks.append({
                        'type': current_type,
                        'messages': current_block,
                        'start_idx': i - len(current_block) + 1,
                        'end_idx': i
                    })
                    current_block = []
        
        if current_block:
            blocks.append({
                'type': current_type,
                'messages': current_block,
                'start_idx': len(messages) - len(current_block),
                'end_idx': len(messages) - 1
            })
        
        return blocks
    
    def compress_block(self, block):
        """Compress a block of messages"""
        messages = block['messages']
        block_type = block['type']
        
        if block_type == "tool_results":
            return self.compress_tool_results_block(messages)
        elif block_type == "ai_response":
            # Summarize AI responses
            contents = [msg.get("content", "") for msg in messages if msg.get("content")]
            if contents:
                summary = "[AI Response Summary] " + "; ".join([
                    content[:100] + ("..." if len(content) > 100 else "")
                    for content in contents
                ])
                return {
                    "role": "assistant",
                    "content": summary
                }
        elif block_type == "user_request":
            # Summarize user requests
            contents = [msg.get("content", "") for msg in messages if msg.get("content")]
            if contents:
                summary = "[User Request Summary] " + "; ".join([
                    content[:100] + ("..." if len(content) > 100 else "")
                    for content in contents
                ])
                return {
                    "role": "user",
                    "content": summary
                }
        
        # Default: return first message with summary note
        if messages:
            first_msg = messages[0].copy()
            first_msg["content"] = f"[Compressed {len(messages)} messages] " + str(first_msg.get("content", ""))[:200]
            return first_msg
        
        return None
    
    def compress_tool_results_block(self, messages):
        """Compress tool execution results"""
        tools_summary = {}
        
        for msg in messages:
            tool_name = msg.get("name", "unknown")
            result = msg.get("content", "")
            
            # Analyze result success/failure
            if "✅" in result or "successfully" in result.lower():
                status = "✅ Success"
            elif "❌" in result or "error" in result.lower():
                status = "❌ Error"
            else:
                status = "⚠️  Completed"
            
            # Summarize result
            result_summary = result[:100].replace("\n", " ")
            if len(result) > 100:
                result_summary += "..."
            
            tools_summary[tool_name] = f"{status}: {result_summary}"
        
        # Create compressed message
        summary_content = "[Tool Summary] " + "; ".join([
            f"{tool}: {summary}" for tool, summary in tools_summary.items()
        ])
        
        return {
            "role": "tool",
            "name": "conversation_compactor",
            "content": summary_content
        }
    
    def compact_messages_conservative(self, messages, keep_recent=None, max_total=None):
        """Conservative main compression logic"""
        if keep_recent is None:
            keep_recent = self.keep_recent_messages
        if max_total is None:
            max_total = self.max_compacted_length
        
        if len(messages) <= max_total:
            return messages  # No compression needed
        
        # Always keep first message (initial user request)
        first_message = messages[0] if messages else None
        
        # Keep recent messages
        recent_messages = messages[-keep_recent:] if len(messages) > keep_recent else messages
        
        # Messages to compress (middle section)
        compress_start = 1 if first_message else 0
        compress_end = len(messages) - keep_recent
        
        if compress_end <= compress_start:
            return messages  # Nothing to compress
        
        messages_to_compress = messages[compress_start:compress_end]
        
        # Analyze and group messages
        blocks = self.analyze_message_structure(messages_to_compress)
        
        # Compress each block - be more aggressive when we have many messages
        compressed_blocks = []
        total_to_compress = len(messages_to_compress)
        
        # If we have many messages to compress, compress smaller blocks too
        # Lower threshold when we have many messages overall
        min_block_size = 2 if total_to_compress > 8 else self.compression_block_size
        
        # Group small blocks together for compression
        small_blocks = []
        for block in blocks:
            block_size = len(block['messages'])
            if block_size >= min_block_size:
                # Compress large enough blocks immediately
                compressed_msg = self.compress_block(block)
                if compressed_msg:
                    compressed_blocks.append(compressed_msg)
            else:
                # Collect small blocks to compress together
                small_blocks.extend(block['messages'])
        
        # Compress collected small blocks together if we have enough
        if len(small_blocks) >= 2:
            # Create a synthetic block for small messages
            synthetic_block = {
                'type': 'mixed',
                'messages': small_blocks
            }
            compressed_msg = self.compress_block(synthetic_block)
            if compressed_msg:
                compressed_blocks.append(compressed_msg)
        elif small_blocks:
            # If only 1 small block, just add it
            compressed_blocks.extend(small_blocks)
        
        # Assemble final message list
        final_messages = []
        
        if first_message:
            final_messages.append(first_message)
        
        final_messages.extend(compressed_blocks)
        final_messages.extend(recent_messages)
        
        # If still too long, compress more aggressively
        if len(final_messages) > max_total and len(compressed_blocks) > 1:
            # Further compress the middle compressed blocks
            middle_compressed = []
            for i, block_msg in enumerate(compressed_blocks):
                if i < len(compressed_blocks) - 2:  # Keep last 2 compressed blocks
                    # Further summarize
                    content = block_msg.get("content", "")
                    if len(content) > 150:
                        block_msg = block_msg.copy()
                        block_msg["content"] = content[:150] + "..."
                middle_compressed.append(block_msg)
            
            final_messages = []
            if first_message:
                final_messages.append(first_message)
            final_messages.extend(middle_compressed)
            final_messages.extend(recent_messages)
        
        return final_messages
