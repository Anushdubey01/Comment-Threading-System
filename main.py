from comment_system import CommentSystem

def demo():
    system = CommentSystem()
    
    post = system.create_post("Welcome to our platform!")
    print(f"Created post: {post.title}")
    
    comment1 = system.add_comment(post.id, "Alice", "Great platform!")
    comment2 = system.add_comment(post.id, "Bob", "I agree with Alice!")
    
    reply1 = system.add_comment(post.id, "Charlie", "Thanks Alice!", comment1.id)
    
    print("\n--- Tree View ---")
    tree_view = system.get_comments_view(post.id, "tree")
    for comment in tree_view:
        print(f"{comment.user}: {comment.content}")
        for reply in comment.replies:
            print(f"  └─ {reply.user}: {reply.content}")
    
    print("\n--- Flat View ---")
    flat_view = system.get_comments_view(post.id, "flat")
    for comment in flat_view:
        indent = "  " * (system._get_comment_depth(comment.id))
        print(f"{indent}{comment.user}: {comment.content}")

if __name__ == "__main__":
    demo()