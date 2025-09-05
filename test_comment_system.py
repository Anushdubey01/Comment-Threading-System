from comment_system import CommentSystem

def create_post(comment_system, title):
    return comment_system.create_post(title)

def add_comment(post, user, content, parent_comment_id=None):
    return post.comment_system.add_comment(post.id, user, content, parent_comment_id)

def get_comments_view(post, view_type="tree"):
    return post.comment_system.get_comments_view(post.id, view_type)

def test_add_comment_and_reply():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    comment = add_comment(post, "User1", "This is a comment.")
    reply = add_comment(post, "User2", "This is a reply.", parent_comment_id=comment.id)
    
    comments_tree = get_comments_view(post, view_type="tree")
    
    assert len(comments_tree) == 1, "There should be one top-level comment."
    assert len(comments_tree[0].replies) == 1, "The comment should have one reply."
    print("Test 1 passed: Adding comment and reply works correctly")

def test_max_reply_depth():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    comment = add_comment(post, "User1", "This is a comment.")
    
    parent_comment_id = comment.id
    # Create 4 replies (depths 1, 2, 3, 4) - this should work
    for depth in range(4):
        reply = add_comment(post, f"User{depth+2}", f"Reply {depth+1}", parent_comment_id=parent_comment_id)
        assert reply is not None, f"Reply at depth {depth+1} should be created successfully"
        parent_comment_id = reply.id
    
    # Try to create a 5th reply (depth 5) - this should fail
    reply = add_comment(post, "User6", "This is a 5th-level reply.", parent_comment_id=parent_comment_id)
    
    assert reply is None, "Replies should not be allowed beyond depth 4 (5 levels total)."
    print("Test 2 passed: Maximum reply depth enforcement works correctly")

def test_flat_comments_view():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    comment1 = add_comment(post, "User1", "First comment.")
    comment2 = add_comment(post, "User2", "Second comment.")
    reply1 = add_comment(post, "User3", "Reply to first comment.", parent_comment_id=comment1.id)
    
    flat_view = get_comments_view(post, view_type="flat")
    
    assert len(flat_view) == 3, "There should be 3 comments in the flat view."
    assert flat_view[0].parent_comment_id is None, "Top-level comments should have None as parent_comment_id."
    print("Test 3 passed: Flat view works correctly")

def test_voting():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    comment = add_comment(post, "User1", "This is a comment.")
    
    system.upvote_comment(comment.id)
    assert system.comments[comment.id].vote_count == 1, "Upvote should increase vote count to 1"
    
    system.downvote_comment(comment.id)
    assert system.comments[comment.id].vote_count == 0, "Downvote should decrease vote count to 0"
    print("Test 4 passed: Voting system works correctly")

def test_auto_collapse():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    comment = add_comment(post, "User1", "This is a comment.")
    
    for i in range(11):
        add_comment(post, f"User{i+2}", f"Reply {i+1}", parent_comment_id=comment.id)
    
    assert system.comments[comment.id].collapsed, "Thread should be auto-collapsed after 11 replies"
    print("Test 5 passed: Auto-collapse works correctly")

def test_user_index():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    
    add_comment(post, "User1", "First comment.")
    add_comment(post, "User2", "Second comment.")
    add_comment(post, "User1", "Another comment from User1.")
    
    user1_comments = system.get_user_comments("User1")
    assert len(user1_comments) == 2, "User1 should have 2 comments"
    
    user2_comments = system.get_user_comments("User2")
    assert len(user2_comments) == 1, "User2 should have 1 comment"
    print("Test 6 passed: User indexing works correctly")

def test_delete_comment():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    
    comment1 = add_comment(post, "User1", "First comment.")
    comment2 = add_comment(post, "User2", "Second comment.")
    reply1 = add_comment(post, "User3", "Reply to first comment.", parent_comment_id=comment1.id)
    
    result = system.delete_comment(comment1.id)
    assert result, "Comment deletion should succeed"
    
    assert comment1.id not in system.comments, "Comment should be removed from system"
    assert len(post.comments) == 1, "Post should have only one comment left"
    print("Test 7 passed: Comment deletion works correctly")

def test_input_validation():
    system = CommentSystem()
    post = create_post(system, "Post Title")
    
    comment = add_comment(post, "", "This is a comment.")
    assert comment is None, "Should reject comment with empty user"
    
    comment = add_comment(post, "User1", "   ")
    assert comment is None, "Should reject comment with empty content"
    print("Test 8 passed: Input validation works correctly")

if __name__ == "__main__":
    test_add_comment_and_reply()
    test_max_reply_depth()
    test_flat_comments_view()
    test_voting()
    test_auto_collapse()
    test_user_index()
    test_delete_comment()
    test_input_validation()
    print("All tests passed!")
    