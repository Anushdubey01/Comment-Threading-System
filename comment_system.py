import threading
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class Comment:
    id: int
    user: str
    content: str
    timestamp: float
    parent_comment_id: Optional[int] = None
    replies: List['Comment'] = field(default_factory=list)
    vote_count: int = 0
    collapsed: bool = field(default=False)

class Post:
    def __init__(self, id: int, title: str, comment_system):
        self.id = id
        self.title = title
        self.comment_system = comment_system
        self.comments: List[Comment] = []

class CommentSystem:
    def __init__(self):
        self.posts: Dict[int, Post] = {}
        self.comments: Dict[int, Comment] = {}
        self.user_comments: Dict[str, List[int]] = {}
        self.next_comment_id = 1
        self.next_post_id = 1
        self.lock = threading.Lock()
    
    def create_post(self, title: str) -> Post:
        """Create a new post and return it"""
        with self.lock:
            post_id = self.next_post_id
            self.next_post_id += 1
            
            post = Post(post_id, title, self)
            self.posts[post_id] = post
            return post
    
    def _get_comment_depth(self, comment_id: int) -> int:
        """Calculate the depth of a comment (0 for top-level comments)"""
        depth = 0
        current_id = comment_id
        
        while current_id is not None and current_id in self.comments:
            current_comment = self.comments[current_id]
            current_id = current_comment.parent_comment_id
            if current_id is not None:
                depth += 1
        
        return depth
    
    def _count_total_replies(self, comment: Comment) -> int:
        """Count total replies in the entire thread"""
        count = len(comment.replies)
        for reply in comment.replies:
            count += self._count_total_replies(reply)
        return count
    
    def should_collapse_thread(self, comment: Comment) -> bool:
        """Check if a thread should be auto-collapsed"""
        return self._count_total_replies(comment) > 10
    
    def add_comment(self, post_id: int, user: str, content: str, 
                   parent_comment_id: Optional[int] = None) -> Optional[Comment]:
        """Add a comment to a post, optionally as a reply to another comment"""
        if not user or not content.strip():
            return None
            
        with self.lock:
            if post_id not in self.posts:
                return None
            
            if parent_comment_id is not None:
                if parent_comment_id not in self.comments:
                    return None
                
                parent_depth = self._get_comment_depth(parent_comment_id)
                if parent_depth >= 4:
                    return None
            
            comment_id = self.next_comment_id
            self.next_comment_id += 1
            
            new_comment = Comment(
                id=comment_id,
                user=user,
                content=content,
                timestamp=time.time(),
                parent_comment_id=parent_comment_id
            )
            
            self.comments[comment_id] = new_comment
            
            if user not in self.user_comments:
                self.user_comments[user] = []
            self.user_comments[user].append(comment_id)
            
            if parent_comment_id is None:
                self.posts[post_id].comments.append(new_comment)
            else:
                parent_comment = self.comments[parent_comment_id]
                parent_comment.replies.append(new_comment)
                
                if self.should_collapse_thread(parent_comment):
                    parent_comment.collapsed = True
            
            return new_comment
    
    def get_comments_view(self, post_id: int, view_type: str = "tree") -> List[Comment]:
        """Get comments for a post in either tree or flat view"""
        with self.lock:
            if post_id not in self.posts:
                return []
            
            post = self.posts[post_id]
            
            if view_type == "tree":
                return post.comments
            elif view_type == "flat":
                return self._flatten_comments(post.comments)
            else:
                raise ValueError("view_type must be 'tree' or 'flat'")
    
    def _flatten_comments(self, comments: List[Comment]) -> List[Comment]:
        """Flatten a tree of comments into a list"""
        flat_list = []
        for comment in comments:
            flat_list.append(comment)
            if not comment.collapsed:
                flat_list.extend(self._flatten_comments(comment.replies))
        return flat_list
    
    def upvote_comment(self, comment_id: int) -> bool:
        """Upvote a comment"""
        with self.lock:
            if comment_id in self.comments:
                self.comments[comment_id].vote_count += 1
                return True
            return False
    
    def downvote_comment(self, comment_id: int) -> bool:
        """Downvote a comment"""
        with self.lock:
            if comment_id in self.comments:
                self.comments[comment_id].vote_count -= 1
                return True
            return False
    
    def toggle_collapse(self, comment_id: int) -> bool:
        """Toggle the collapsed state of a comment thread"""
        with self.lock:
            if comment_id in self.comments:
                self.comments[comment_id].collapsed = not self.comments[comment_id].collapsed
                return True
            return False
    
    def get_user_comments(self, user: str) -> List[Comment]:
        """Get all comments by a specific user"""
        with self.lock:
            if user not in self.user_comments:
                return []
            return [self.comments[comment_id] for comment_id in self.user_comments[user]]
    
    def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment and all its replies"""
        with self.lock:
            if comment_id not in self.comments:
                return False
            
            comment = self.comments[comment_id]
            
            if comment.parent_comment_id is None:
                for post in self.posts.values():
                    if comment in post.comments:
                        post.comments.remove(comment)
                        break
            else:
                parent = self.comments[comment.parent_comment_id]
                if comment in parent.replies:
                    parent.replies.remove(comment)
            
            if comment.user in self.user_comments and comment_id in self.user_comments[comment.user]:
                self.user_comments[comment.user].remove(comment_id)
            
            replies_to_delete = comment.replies.copy()
            for reply in replies_to_delete:
                self.delete_comment(reply.id)
            
            del self.comments[comment_id]
            
            return True