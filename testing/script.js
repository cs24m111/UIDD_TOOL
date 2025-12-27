// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    initializePosts();
});

function initializePosts() {
    const posts = document.querySelectorAll('.post');

    posts.forEach(post => {
        setupLikeButton(post);
        setupDoubleClickLike(post);
        setupCommentInput(post);
        setupSaveButton(post);
    });
}

// Like button functionality
function setupLikeButton(post) {
    const likeBtn = post.querySelector('.like-btn');
    const likesCountElement = post.querySelector('.likes-count');
    let isLiked = false;
    let likesCount = parseInt(likesCountElement.textContent);

    likeBtn.addEventListener('click', function() {
        toggleLike();
    });

    function toggleLike() {
        isLiked = !isLiked;

        if (isLiked) {
            likeBtn.classList.add('liked');
            likesCount++;
            // Add animation
            likeBtn.style.transform = 'scale(1.2)';
            setTimeout(() => {
                likeBtn.style.transform = 'scale(1)';
            }, 200);
        } else {
            likeBtn.classList.remove('liked');
            likesCount--;
        }

        likesCountElement.textContent = likesCount;
    }

    // Expose toggleLike for double-click functionality
    post.toggleLike = toggleLike;
    post.isLiked = () => isLiked;
}

// Double-click on image to like
function setupDoubleClickLike(post) {
    const postImage = post.querySelector('.post-image');
    const postImageContainer = post.querySelector('.post-image-container');
    let lastTap = 0;

    // Desktop double-click
    postImage.addEventListener('dblclick', function(e) {
        e.preventDefault();
        if (!post.isLiked()) {
            post.toggleLike();
            showHeartAnimation(postImageContainer);
        }
    });

    // Mobile double-tap
    postImage.addEventListener('touchend', function(e) {
        const currentTime = new Date().getTime();
        const tapLength = currentTime - lastTap;

        if (tapLength < 300 && tapLength > 0) {
            e.preventDefault();
            if (!post.isLiked()) {
                post.toggleLike();
                showHeartAnimation(postImageContainer);
            }
        }

        lastTap = currentTime;
    });
}

// Show heart animation on double-click
function showHeartAnimation(container) {
    const heart = document.createElement('div');
    heart.innerHTML = `
        <svg width="100" height="100" viewBox="0 0 24 24" fill="#fff" stroke="#fff" stroke-width="2" style="filter: drop-shadow(0 0 10px rgba(0,0,0,0.3));">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
    `;

    heart.style.position = 'absolute';
    heart.style.top = '50%';
    heart.style.left = '50%';
    heart.style.transform = 'translate(-50%, -50%) scale(0)';
    heart.style.zIndex = '10';
    heart.style.pointerEvents = 'none';
    heart.style.transition = 'all 0.5s ease-out';

    container.style.position = 'relative';
    container.appendChild(heart);

    // Trigger animation
    setTimeout(() => {
        heart.style.transform = 'translate(-50%, -50%) scale(1)';
        heart.style.opacity = '1';
    }, 10);

    setTimeout(() => {
        heart.style.transform = 'translate(-50%, -50%) scale(1.3)';
        heart.style.opacity = '0';
    }, 300);

    setTimeout(() => {
        container.removeChild(heart);
    }, 800);
}

// Comment input functionality
function setupCommentInput(post) {
    const commentInput = post.querySelector('.comment-input');
    const postBtn = post.querySelector('.post-btn');
    const commentsContainer = post.querySelector('.post-comments');

    // Enable/disable post button based on input
    commentInput.addEventListener('input', function() {
        if (commentInput.value.trim().length > 0) {
            postBtn.disabled = false;
        } else {
            postBtn.disabled = true;
        }
    });

    // Post comment on button click
    postBtn.addEventListener('click', function() {
        postComment();
    });

    // Post comment on Enter key
    commentInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && commentInput.value.trim().length > 0) {
            postComment();
        }
    });

    function postComment() {
        const commentText = commentInput.value.trim();

        if (commentText.length > 0) {
            const comment = document.createElement('div');
            comment.className = 'comment';
            comment.innerHTML = `
                <span class="comment-username">you</span>
                <span class="comment-text">${escapeHtml(commentText)}</span>
            `;

            commentsContainer.appendChild(comment);
            commentInput.value = '';
            postBtn.disabled = true;

            // Smooth scroll to new comment
            comment.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}

// Save button functionality
function setupSaveButton(post) {
    const saveBtn = post.querySelector('.save-btn');
    let isSaved = false;

    saveBtn.addEventListener('click', function() {
        isSaved = !isSaved;

        if (isSaved) {
            saveBtn.classList.add('saved');
        } else {
            saveBtn.classList.remove('saved');
        }

        // Add animation
        saveBtn.style.transform = 'scale(1.2)';
        setTimeout(() => {
            saveBtn.style.transform = 'scale(1)';
        }, 200);
    });
}

// Utility function to escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Initialize post button as disabled
document.addEventListener('DOMContentLoaded', function() {
    const postButtons = document.querySelectorAll('.post-btn');
    postButtons.forEach(btn => {
        btn.disabled = true;
    });
});
