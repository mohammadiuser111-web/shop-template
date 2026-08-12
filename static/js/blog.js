/**
 * Shop Template - Blog JavaScript
 * ===============================
 * Blog-specific JavaScript functionality
 */

// ============================================
// Blog Management
// ============================================
class Blog {
    constructor() {
        this.posts = [];
        this.categories = [];
        this.tags = [];
        this.currentCategory = null;
        this.currentTag = null;
        this.currentSearch = null;
        this.init();
    }
    
    init() {
        this.loadPosts();
        this.loadCategories();
        this.loadTags();
        this.parseURLParams();
        this.initFilters();
        this.initSearch();
        this.initSocialSharing();
        this.initNewsletter();
    }
    
    loadPosts() {
        // In a real app, these would be fetched from the API
        // For demo purposes, we'll use placeholder data
        this.posts = [
            {
                id: 1,
                title: '10 Essential Tips for Online Shopping Safety',
                slug: '10-essential-tips-for-online-shopping-safety',
                excerpt: 'Learn how to protect yourself while shopping online with these essential safety tips.',
                content: '<p>Online shopping has become an integral part of our daily lives...</p>',
                image: '/static/images/blog/blog-1.jpg',
                category: { id: 1, name: 'Shopping Tips', slug: 'shopping-tips' },
                author: { id: 1, name: 'John Doe', avatar: '/static/images/avatars/avatar-1.jpg' },
                date: '2024-01-15',
                tags: ['online shopping', 'safety', 'tips'],
                comments: 12,
                views: 1560,
                readingTime: 8
            },
            {
                id: 2,
                title: 'The Ultimate Guide to Choosing the Perfect Smartphone',
                slug: 'the-ultimate-guide-to-choosing-the-perfect-smartphone',
                excerpt: 'Find your perfect smartphone match with our comprehensive buying guide.',
                content: '<p>Choosing a new smartphone can be overwhelming with so many options...</p>',
                image: '/static/images/blog/blog-2.jpg',
                category: { id: 2, name: 'Technology', slug: 'technology' },
                author: { id: 2, name: 'Jane Smith', avatar: '/static/images/avatars/avatar-2.jpg' },
                date: '2024-01-10',
                tags: ['smartphone', 'technology', 'buying guide'],
                comments: 8,
                views: 2340,
                readingTime: 12
            },
            {
                id: 3,
                title: 'How to Style Your Outfits for Any Occasion',
                slug: 'how-to-style-your-outfits-for-any-occasion',
                excerpt: 'Master the art of styling with our expert fashion advice.',
                content: '<p>Fashion is all about expressing your personality through what you wear...</p>',
                image: '/static/images/blog/blog-3.jpg',
                category: { id: 3, name: 'Fashion', slug: 'fashion' },
                author: { id: 3, name: 'Sarah Johnson', avatar: '/static/images/avatars/avatar-3.jpg' },
                date: '2024-01-05',
                tags: ['fashion', 'style', 'outfits'],
                comments: 18,
                views: 3120,
                readingTime: 10
            },
            {
                id: 4,
                title: 'The Benefits of Using Wireless Headphones',
                slug: 'the-benefits-of-using-wireless-headphones',
                excerpt: 'Discover why wireless headphones are becoming everyone\'s favorite audio accessory.',
                content: '<p>Wireless headphones have revolutionized the way we listen to music...</p>',
                image: '/static/images/blog/blog-4.jpg',
                category: { id: 2, name: 'Technology', slug: 'technology' },
                author: { id: 1, name: 'John Doe', avatar: '/static/images/avatars/avatar-1.jpg' },
                date: '2024-01-01',
                tags: ['headphones', 'wireless', 'technology'],
                comments: 5,
                views: 890,
                readingTime: 6
            }
        ];
    }
    
    loadCategories() {
        // Extract unique categories from posts
        const categoryMap = new Map();
        this.posts.forEach(post => {
            if (post.category) {
                if (!categoryMap.has(post.category.id)) {
                    categoryMap.set(post.category.id, {
                        ...post.category,
                        count: 0
                    });
                }
                categoryMap.get(post.category.id).count++;
            }
        });
        
        this.categories = Array.from(categoryMap.values());
    }
    
    loadTags() {
        // Extract unique tags from posts
        const tagMap = new Map();
        this.posts.forEach(post => {
            (post.tags || []).forEach(tag => {
                if (!tagMap.has(tag)) {
                    tagMap.set(tag, { name: tag, count: 0 });
                }
                tagMap.get(tag).count++;
            });
        });
        
        this.tags = Array.from(tagMap.values());
    }
    
    parseURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        this.currentCategory = urlParams.get('category');
        this.currentTag = urlParams.get('tag');
        this.currentSearch = urlParams.get('q');
    }
    
    getFilteredPosts() {
        return this.posts.filter(post => {
            // Filter by category
            if (this.currentCategory && post.category?.slug !== this.currentCategory) {
                return false;
            }
            
            // Filter by tag
            if (this.currentTag && !post.tags?.includes(this.currentTag)) {
                return false;
            }
            
            // Filter by search
            if (this.currentSearch) {
                const searchLower = this.currentSearch.toLowerCase();
                const titleMatch = post.title.toLowerCase().includes(searchLower);
                const excerptMatch = post.excerpt.toLowerCase().includes(searchLower);
                const contentMatch = post.content.toLowerCase().includes(searchLower);
                const tagMatch = post.tags?.some(tag => tag.toLowerCase().includes(searchLower));
                
                if (!titleMatch && !excerptMatch && !contentMatch && !tagMatch) {
                    return false;
                }
            }
            
            return true;
        });
    }
    
    getPostBySlug(slug) {
        return this.posts.find(post => post.slug === slug);
    }
    
    getCategoryBySlug(slug) {
        return this.categories.find(category => category.slug === slug);
    }
    
    getTagByName(name) {
        return this.tags.find(tag => tag.name === name);
    }
    
    // ============================================
    // Filters
    // ============================================
    initFilters() {
        // Category filters
        const categoryFilters = document.querySelectorAll('.blog-category');
        categoryFilters.forEach(filter => {
            filter.addEventListener('click', () => {
                const categorySlug = filter.dataset.categorySlug;
                this.filterByCategory(categorySlug);
            });
        });
        
        // Tag filters (in sidebar)
        const tagFilters = document.querySelectorAll('.tag-item a');
        tagFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                const tagName = filter.textContent.trim();
                this.filterByTag(tagName);
            });
        });
        
        // Category filters (in sidebar)
        const sidebarCategoryFilters = document.querySelectorAll('.categories-widget-item a');
        sidebarCategoryFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                const categorySlug = filter.closest('.categories-widget-item').dataset.categorySlug;
                this.filterByCategory(categorySlug);
            });
        });
        
        // Archive filters
        const archiveFilters = document.querySelectorAll('.archive-widget-item a');
        archiveFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                e.preventDefault();
                const date = filter.dataset.date;
                this.filterByDate(date);
            });
        });
    }
    
    filterByCategory(categorySlug) {
        const url = new URL(window.location);
        url.searchParams.delete('tag');
        url.searchParams.delete('q');
        
        if (categorySlug && categorySlug !== 'all') {
            url.searchParams.set('category', categorySlug);
        } else {
            url.searchParams.delete('category');
        }
        
        window.location.href = url.toString();
    }
    
    filterByTag(tagName) {
        const url = new URL(window.location);
        url.searchParams.delete('category');
        url.searchParams.delete('q');
        
        if (tagName && tagName !== 'all') {
            url.searchParams.set('tag', tagName);
        } else {
            url.searchParams.delete('tag');
        }
        
        window.location.href = url.toString();
    }
    
    filterByDate(date) {
        const url = new URL(window.location);
        url.searchParams.delete('category');
        url.searchParams.delete('tag');
        url.searchParams.delete('q');
        url.searchParams.set('date', date);
        
        window.location.href = url.toString();
    }
    
    // ============================================
    // Search
    // ============================================
    initSearch() {
        const searchForm = document.querySelector('.blog-search');
        if (!searchForm) return;
        
        const searchInput = searchForm.querySelector('input');
        if (!searchInput) return;
        
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const searchTerm = searchInput.value.trim();
            this.search(searchTerm);
        });
        
        // Also search on input for instant results
        searchInput.addEventListener('input', ShopTemplate.debounce(() => {
            const searchTerm = searchInput.value.trim();
            this.search(searchTerm);
        }, 500));
    }
    
    search(term) {
        const url = new URL(window.location);
        url.searchParams.delete('category');
        url.searchParams.delete('tag');
        
        if (term) {
            url.searchParams.set('q', term);
        } else {
            url.searchParams.delete('q');
        }
        
        window.location.href = url.toString();
    }
    
    // ============================================
    // Social Sharing
    // ============================================
    initSocialSharing() {
        const shareButtons = document.querySelectorAll('.share-btn');
        shareButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const platform = btn.dataset.platform;
                const url = btn.dataset.url || window.location.href;
                const title = btn.dataset.title || document.title;
                
                this.shareOnPlatform(platform, url, title);
            });
        });
    }
    
    shareOnPlatform(platform, url, title) {
        const shareUrls = {
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
            linkedin: `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`,
            pinterest: `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(url)}&media=${encodeURIComponent(url)}&description=${encodeURIComponent(title)}`,
            whatsapp: `https://wa.me/?text=${encodeURIComponent(`${title} - ${url}`)}`,
            email: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`${title} - ${url}`)}`
        };
        
        const shareUrl = shareUrls[platform];
        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }
    }
    
    // ============================================
    // Newsletter
    // ============================================
    initNewsletter() {
        const newsletterForms = document.querySelectorAll('.newsletter-widget .newsletter-form');
        newsletterForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const email = form.querySelector('input[type="email"]').value;
                const checkbox = form.querySelector('input[type="checkbox"]');
                
                if (email) {
                    // In a real app, this would submit to your backend
                    ShopTemplate.showToast('Thank you for subscribing!', 'success');
                    form.reset();
                    if (checkbox) checkbox.checked = false;
                } else {
                    ShopTemplate.showToast('Please enter a valid email address', 'error');
                }
            });
        });
    }
}

// ============================================
// Blog Post
// ============================================
class BlogPost {
    constructor(postElement) {
        this.post = postElement;
        this.init();
    }
    
    init() {
        this.initReadingTime();
        this.initTableOfContents();
        this.initSyntaxHighlighting();
        this.initImageLightbox();
    }
    
    initReadingTime() {
        const readingTimeElement = this.post.querySelector('.blog-post-reading-time');
        if (!readingTimeElement) return;
        
        const content = this.post.querySelector('.blog-post-detail-body');
        if (!content) return;
        
        const text = content.textContent || '';
        const words = text.trim().split(/\s+/).length;
        const readingTime = Math.max(1, Math.ceil(words / 200));
        
        readingTimeElement.textContent = `${readingTime} min read`;
    }
    
    initTableOfContents() {
        const tocContainer = this.post.querySelector('.blog-post-toc');
        if (!tocContainer) return;
        
        const headings = this.post.querySelectorAll('.blog-post-detail-body h2, .blog-post-detail-body h3');
        if (headings.length === 0) return;
        
        let tocHTML = '<ul>';
        headings.forEach((heading, index) => {
            const level = heading.tagName.toLowerCase() === 'h2' ? 2 : 3;
            const id = heading.id || `heading-${index}`;
            const indent = level === 3 ? '&nbsp;&nbsp;&nbsp;&nbsp;' : '';
            
            heading.id = id;
            tocHTML += `<li><a href="#${id}">${indent}${heading.textContent}</a></li>`;
        });
        tocHTML += '</ul>';
        
        tocContainer.innerHTML = tocHTML;
        
        // Smooth scroll for TOC links
        tocContainer.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                if (target) {
                    ShopTemplate.scrollToElement(target, -20);
                }
            }
        });
    }
    
    initSyntaxHighlighting() {
        const codeBlocks = this.post.querySelectorAll('.blog-post-detail-body pre code');
        codeBlocks.forEach(block => {
            // In a real app, you would use a syntax highlighting library here
            // For demo purposes, we'll just add a class
            block.classList.add('syntax-highlighted');
        });
    }
    
    initImageLightbox() {
        const images = this.post.querySelectorAll('.blog-post-detail-body img');
        images.forEach(img => {
            img.addEventListener('click', () => {
                this.openLightbox(img.src, img.alt);
            });
        });
    }
    
    openLightbox(src, alt) {
        // In a real app, you would open a lightbox here
        // For demo purposes, we'll just show the image in a new tab
        window.open(src, '_blank');
    }
}

// ============================================
// Comments
// ============================================
class Comments {
    constructor(container) {
        this.container = container;
        this.comments = [];
        this.init();
    }
    
    init() {
        this.loadComments();
        this.initCommentForm();
        this.initReplyButtons();
        this.initLikeButtons();
    }
    
    loadComments() {
        // In a real app, these would be fetched from the API
        // For demo purposes, we'll use placeholder data
        this.comments = [
            {
                id: 1,
                author: 'John Doe',
                avatar: '/static/images/avatars/avatar-1.jpg',
                email: 'john@example.com',
                content: 'Great article! Very informative and well-written.',
                date: '2024-01-16',
                likes: 5,
                replies: [
                    {
                        id: 2,
                        author: 'Jane Smith',
                        avatar: '/static/images/avatars/avatar-2.jpg',
                        email: 'jane@example.com',
                        content: 'I agree, this is a really useful guide.',
                        date: '2024-01-17',
                        likes: 2
                    }
                ]
            },
            {
                id: 3,
                author: 'Mike Johnson',
                avatar: '/static/images/avatars/avatar-3.jpg',
                email: 'mike@example.com',
                content: 'Thanks for sharing these tips. I learned a lot!',
                date: '2024-01-18',
                likes: 3,
                replies: []
            }
        ];
        
        this.renderComments();
    }
    
    renderComments() {
        const commentsList = this.container.querySelector('.comments-list');
        if (!commentsList) return;
        
        commentsList.innerHTML = this.comments.map(comment => `
            <div class="comment-item" data-comment-id="${comment.id}">
                <div class="comment-avatar">
                    ${comment.avatar ? `<img src="${comment.avatar}" alt="${comment.author}">` : `<span>${comment.author.charAt(0)}</span>`}
                </div>
                <div class="comment-content">
                    <div class="comment-header">
                        <div class="comment-author">${comment.author}</div>
                        <div class="comment-date">${this.formatDate(comment.date)}</div>
                    </div>
                    <div class="comment-text">${comment.content}</div>
                    <div class="comment-actions">
                        <button class="comment-action comment-like" data-comment-id="${comment.id}">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                            </svg>
                            <span>${comment.likes}</span>
                        </button>
                        <button class="comment-action comment-reply" data-comment-id="${comment.id}">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                                <polyline points="10 9 15 14 10 19"/>
                            </svg>
                            <span>Reply</span>
                        </button>
                    </div>
                    ${this.renderReplies(comment.replies)}
                </div>
            </div>
        `).join('');
    }
    
    renderReplies(replies) {
        if (replies.length === 0) return '';
        
        return `
            <div class="comment-replies">
                ${replies.map(reply => `
                    <div class="comment-reply" data-comment-id="${reply.id}">
                        <div class="comment-avatar">
                            ${reply.avatar ? `<img src="${reply.avatar}" alt="${reply.author}">` : `<span>${reply.author.charAt(0)}</span>`}
                        </div>
                        <div class="comment-content">
                            <div class="comment-header">
                                <div class="comment-author">${reply.author}</div>
                                <div class="comment-date">${this.formatDate(reply.date)}</div>
                            </div>
                            <div class="comment-text">${reply.content}</div>
                            <div class="comment-actions">
                                <button class="comment-action comment-like" data-comment-id="${reply.id}">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                                    </svg>
                                    <span>${reply.likes}</span>
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
        
        if (diffInDays === 0) {
            return 'Today';
        } else if (diffInDays === 1) {
            return 'Yesterday';
        } else if (diffInDays < 7) {
            return `${diffInDays} days ago`;
        } else if (diffInDays < 30) {
            const weeks = Math.floor(diffInDays / 7);
            return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
        } else if (diffInDays < 365) {
            const months = Math.floor(diffInDays / 30);
            return `${months} month${months > 1 ? 's' : ''} ago`;
        } else {
            const years = Math.floor(diffInDays / 365);
            return `${years} year${years > 1 ? 's' : ''} ago`;
        }
    }
    
    initCommentForm() {
        const commentForm = this.container.querySelector('.comment-form');
        if (!commentForm) return;
        
        commentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = commentForm.querySelector('input[name="name"]').value;
            const email = commentForm.querySelector('input[name="email"]').value;
            const content = commentForm.querySelector('textarea[name="content"]').value;
            
            if (name && email && content) {
                this.addComment(name, email, content);
                commentForm.reset();
                ShopTemplate.showToast('Comment submitted for approval', 'success');
            } else {
                ShopTemplate.showToast('Please fill in all fields', 'error');
            }
        });
    }
    
    addComment(name, email, content) {
        const newComment = {
            id: this.comments.length + 1,
            author: name,
            email: email,
            content: content,
            date: new Date().toISOString().split('T')[0],
            likes: 0,
            replies: []
        };
        
        this.comments.push(newComment);
        this.renderComments();
    }
    
    initReplyButtons() {
        const replyButtons = this.container.querySelectorAll('.comment-reply');
        replyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const commentId = parseInt(btn.dataset.commentId);
                const comment = this.findComment(commentId);
                
                if (comment) {
                    this.showReplyForm(commentId);
                }
            });
        });
    }
    
    findComment(commentId) {
        const findInComments = (comments) => {
            for (const comment of comments) {
                if (comment.id === commentId) {
                    return comment;
                }
                if (comment.replies && comment.replies.length > 0) {
                    const foundInReplies = findInComments(comment.replies);
                    if (foundInReplies) {
                        return foundInReplies;
                    }
                }
            }
            return null;
        };
        
        return findInComments(this.comments);
    }
    
    showReplyForm(commentId) {
        // In a real app, you would show a reply form here
        // For demo purposes, we'll just show a toast
        ShopTemplate.showToast(`Reply form for comment ${commentId} would open here`, 'info');
    }
    
    initLikeButtons() {
        const likeButtons = this.container.querySelectorAll('.comment-like');
        likeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const commentId = parseInt(btn.dataset.commentId);
                const comment = this.findComment(commentId);
                
                if (comment) {
                    comment.likes++;
                    this.renderComments();
                }
            });
        });
    }
}

// ============================================
// Related Posts
// ============================================
class RelatedPosts {
    constructor(container) {
        this.container = container;
        this.posts = [];
        this.currentPostId = null;
        this.init();
    }
    
    init() {
        this.currentPostId = parseInt(this.container.dataset.currentPostId) || null;
        this.loadRelatedPosts();
    }
    
    loadRelatedPosts() {
        // In a real app, these would be fetched based on the current post
        // For demo purposes, we'll use placeholder data
        if (window.blog) {
            // Get posts from the same category, excluding the current post
            const currentPost = window.blog.getPostBySlug(window.location.pathname.split('/').pop());
            if (currentPost) {
                this.posts = window.blog.posts.filter(post => {
                    return post.id !== currentPost.id && 
                           post.category?.id === currentPost.category?.id;
                }).slice(0, 3);
            } else {
                this.posts = window.blog.posts.slice(0, 3);
            }
        }
        
        this.renderRelatedPosts();
    }
    
    renderRelatedPosts() {
        const postsList = this.container.querySelector('.related-posts-list');
        if (!postsList) return;
        
        postsList.innerHTML = this.posts.map(post => `
            <div class="related-post-card">
                <a href="/blog/${post.slug}/" class="related-post-link">
                    <div class="related-post-image">
                        ${post.image ? `<img src="${post.image}" alt="${post.title}">` : ''}
                    </div>
                    <div class="related-post-content">
                        ${post.category ? `<div class="related-post-category">${post.category.name}</div>` : ''}
                        <h3 class="related-post-title">${post.title}</h3>
                        <div class="related-post-meta">
                            <span>${post.date}</span>
                            <span>${post.readingTime} min read</span>
                        </div>
                    </div>
                </a>
            </div>
        `).join('');
    }
}

// ============================================
// Initialize Everything
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize blog
    window.blog = new Blog();
    
    // Initialize blog posts on blog detail page
    const blogPost = document.querySelector('.blog-post-detail');
    if (blogPost) {
        new BlogPost(blogPost);
    }
    
    // Initialize comments on blog detail page
    const commentsContainer = document.querySelector('.comments');
    if (commentsContainer) {
        new Comments(commentsContainer);
    }
    
    // Initialize related posts
    const relatedPostsContainer = document.querySelector('.related-posts');
    if (relatedPostsContainer) {
        new RelatedPosts(relatedPostsContainer);
    }
});

// ============================================
// Export for use in other modules
// ============================================
window.BlogModule = {
    Blog,
    BlogPost,
    Comments,
    RelatedPosts
};
