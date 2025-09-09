// Vedic Story Generator - Main JavaScript functionality

let currentStoryId = null;

// Initialize story generator
function initializeStoryGenerator() {
    const form = document.getElementById('storyForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingSection = document.getElementById('loadingSection');
    const storyResult = document.getElementById('storyResult');
    
    if (form) {
        form.addEventListener('submit', handleStoryGeneration);
    }
}

// Handle story generation form submission
async function handleStoryGeneration(event) {
    event.preventDefault();
    
    const prompt = document.getElementById('storyPrompt').value.trim();
    if (!prompt) {
        showAlert('Please enter a story prompt', 'warning');
        return;
    }
    
    const generateBtn = document.getElementById('generateBtn');
    const loadingSection = document.getElementById('loadingSection');
    const storyResult = document.getElementById('storyResult');
    
    // Show loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    loadingSection.style.display = 'block';
    storyResult.style.display = 'none';
    
    try {
        // Update loading text periodically
        updateLoadingText();
        
        const response = await fetch('/generate_story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        const data = await response.json();

        if (data.success) {
            displayStory(data.story);
            currentStoryId = data.story.id;
        } else {
            // Handle specific error types with better messages
            let errorMessage = data.error || 'Failed to generate story';
            let alertType = 'danger';

            if (data.error === 'AI Service Quota Exceeded') {
                errorMessage = 'AI Service Limit Reached. The daily quota has been exceeded. If you have a Pro API key, please check:\n\n1. Verify your API key is correct in .env file\n2. Ensure your Google Cloud project has billing enabled\n3. Check if your Pro subscription is active\n4. Try refreshing your API quota in Google AI Studio\n\nPlease try again tomorrow or contact support for increased limits.';
                alertType = 'warning';
            } else if (data.error === 'AI Service Access Denied') {
                errorMessage = 'Service Configuration Issue. Please contact support to resolve the access problem.';
                alertType = 'warning';
            } else if (data.error === 'AI Service Timeout') {
                errorMessage = 'Service Timeout. The AI service is taking too long to respond. Please try again.';
                alertType = 'warning';
            } else if (data.message) {
                // Use the more detailed message if available
                errorMessage = data.message;
            }

            showAlert(errorMessage, alertType);
        }
        
    } catch (error) {
        console.error('Story generation error:', error);
        showAlert('An error occurred while generating the story. Please try again.', 'danger');
    } finally {
        // Reset UI state
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Story';
        loadingSection.style.display = 'none';
    }
}

// Display generated story
function displayStory(story) {
    const storyResult = document.getElementById('storyResult');
    const storyTitle = document.getElementById('storyTitle');
    const storyContent = document.getElementById('storyContent');
    const storyImages = document.getElementById('storyImages');
    const audioSection = document.getElementById('audioSection');
    const storyAudio = document.getElementById('storyAudio');
    const storyCharacters = document.getElementById('storyCharacters');
    const storyMoral = document.getElementById('storyMoral');
    const downloadBtn = document.getElementById('downloadBtn');
    const playAudioBtn = document.getElementById('playAudioBtn');
    
    // Set story content
    storyTitle.textContent = story.title;
    storyContent.innerHTML = story.content.replace(/\n/g, '<br>');
    
    // Set metadata if available
    if (storyCharacters && story.characters) {
        storyCharacters.textContent = Array.isArray(story.characters) ? 
            story.characters.join(', ') : story.characters;
    }
    
    if (storyMoral && story.moral) {
        storyMoral.textContent = story.moral;
    }
    
    // Display images
    if (story.images && story.images.length > 0) {
        storyImages.innerHTML = '';
        story.images.forEach((imagePath, index) => {
            const imageDiv = document.createElement('div');
            imageDiv.className = 'col-md-4';
            imageDiv.innerHTML = `
                <div class="position-relative">
                    <img src="${imagePath}" 
                         class="img-fluid rounded shadow-sm story-image" 
                         alt="Story illustration ${index + 1}"
                         onclick="openImageModal('${imagePath}')">
                    <button class="btn btn-sm btn-primary position-absolute top-0 end-0 m-2" 
                            onclick="openImageModal('${imagePath}')">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            `;
            storyImages.appendChild(imageDiv);
        });
    }
    
    // Setup audio
    if (story.audio_path) {
        storyAudio.src = story.audio_path;
        playAudioBtn.style.display = 'block';
        setupAudioControls();
    } else {
        playAudioBtn.style.display = 'none';
    }
    
    // Setup download button
    if (downloadBtn) {
        downloadBtn.onclick = () => {
            window.location.href = `/download_story/${story.id}`;
        };
    }
    
    // Show the result
    storyResult.style.display = 'block';
    storyResult.scrollIntoView({ behavior: 'smooth' });
}

// Setup audio controls
function setupAudioControls() {
    const playAudioBtn = document.getElementById('playAudioBtn');
    const audioSection = document.getElementById('audioSection');
    const storyAudio = document.getElementById('storyAudio');
    
    if (!playAudioBtn || !audioSection || !storyAudio) return;
    
    playAudioBtn.addEventListener('click', function() {
        if (storyAudio.paused) {
            audioSection.style.display = 'block';
            storyAudio.play();
            this.innerHTML = '<i class="fas fa-pause me-1"></i>Pause Audio';
        } else {
            storyAudio.pause();
            this.innerHTML = '<i class="fas fa-play me-1"></i>Play Audio';
        }
    });
    
    storyAudio.addEventListener('play', function() {
        playAudioBtn.innerHTML = '<i class="fas fa-pause me-1"></i>Pause Audio';
    });
    
    storyAudio.addEventListener('pause', function() {
        playAudioBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Audio';
    });
    
    storyAudio.addEventListener('ended', function() {
        playAudioBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Audio';
    });
}

// Update loading text with different phases
function updateLoadingText() {
    const loadingText = document.getElementById('loadingText');
    if (!loadingText) return;

    const phases = [
        'Generating story content...',
        'Creating beautiful illustrations...',
        'Preparing audio narration...',
        'Crafting divine video narration...',
        'Finalizing your Vedic story...'
    ];

    let currentPhase = 0;
    const interval = setInterval(() => {
        if (loadingText.closest('#loadingSection').style.display === 'none') {
            clearInterval(interval);
            return;
        }

        loadingText.textContent = phases[currentPhase];
        currentPhase = (currentPhase + 1) % phases.length;
    }, 3000);
}

// Open image in modal
function openImageModal(imageSrc) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('imageModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'imageModal';
        modal.tabIndex = -1;
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Story Illustration</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img id="modalImage" src="" class="img-fluid" alt="Story illustration">
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    document.getElementById('modalImage').src = imageSrc;
    new bootstrap.Modal(modal).show();
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertContainer.style.zIndex = '9999';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.parentNode.removeChild(alertContainer);
        }
    }, 5000);
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Copy story text to clipboard
function copyStoryText(storyContent) {
    navigator.clipboard.writeText(storyContent).then(() => {
        showAlert('Story copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showAlert('Failed to copy story', 'danger');
    });
}

// Share story functionality
function shareStory(storyId) {
    const url = `${window.location.origin}/story/${storyId}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Vedic Story',
            url: url
        });
    } else {
        copyStoryText(url);
        showAlert('Story link copied to clipboard!', 'success');
    }
}

// ===== ADVANCED THEME SYSTEM =====

// Theme management
let currentTheme = 'dark';

// Initialize theme on page load
function initializeTheme() {
    const savedTheme = localStorage.getItem('mythoscribe-theme') || 'dark';
    setTheme(savedTheme);
}

// Toggle between light and dark themes
function toggleTheme() {
    console.log('Theme toggle button clicked!');
    console.log('Current theme:', currentTheme);
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    console.log('New theme will be:', newTheme);
    setTheme(newTheme);
    console.log('Theme toggled successfully');

    // Add smooth transition effect
    document.body.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';

    // Update theme icon with animation
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.style.transform = 'rotate(180deg) scale(1.2)';
        setTimeout(() => {
            themeIcon.style.transform = '';
        }, 300);
    }

    // Show theme change notification
    const themeName = newTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
    showAlert(`✨ Switched to ${themeName}`, 'info');
}

// Set theme with smooth transitions
function setTheme(theme) {
    console.log('Setting theme to:', theme);
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    console.log('HTML data-theme:', document.documentElement.getAttribute('data-theme'));
    console.log('Body data-theme:', document.body.getAttribute('data-theme'));

    // Update theme icon
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-moon theme-toggle-icon' : 'fas fa-sun theme-toggle-icon';
    }

    // Save to localStorage
    localStorage.setItem('mythoscribe-theme', theme);

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a202c' : '#f8f9fa');
    }

    // Trigger theme change animations
    triggerThemeAnimations(theme);
}

// Trigger theme-specific animations
function triggerThemeAnimations(theme) {
    const cards = document.querySelectorAll('.card');
    const buttons = document.querySelectorAll('.btn');

    // Stagger card animations
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.animation = 'none';
            setTimeout(() => {
                card.style.animation = theme === 'dark' ? 'pulse-glow 0.6s ease-out' : 'breathe 0.6s ease-out';
            }, 10);
        }, index * 100);
    });

    // Animate buttons
    buttons.forEach((button, index) => {
        setTimeout(() => {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = '';
            }, 200);
        }, index * 50);
    });
}

// ===== ADVANCED UI ENHANCEMENTS =====

// Enhanced smooth scrolling with easing
function smoothScrollToElement(element, duration = 800) {
    const start = window.pageYOffset;
    const end = element.getBoundingClientRect().top + window.pageYOffset;
    const distance = end - start;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);

        // Easing function (ease-in-out cubic)
        const easeInOutCubic = progress < 0.5
            ? 4 * progress * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 3) / 2;

        window.scrollTo(0, start + distance * easeInOutCubic);

        if (progress < 1) {
            requestAnimationFrame(animation);
        }
    }

    requestAnimationFrame(animation);
}

// Enhanced hover effects
function initializeHoverEffects() {
    // Card hover effects
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Button hover effects
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.2)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Image hover effects
    document.querySelectorAll('.story-image').forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.08) rotate(2deg)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
        });

        img.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

// Enhanced loading animations
function showLoadingAnimation(element, text = 'Loading...') {
    const loadingHTML = `
        <div class="loading-overlay" style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 15px;
            z-index: 10;
        ">
            <div class="loading-spinner"></div>
            <div class="loading-text" style="
                color: white;
                margin-top: 1rem;
                font-weight: 500;
                animation: pulse 2s infinite;
            ">${text}</div>
        </div>
    `;

    element.style.position = 'relative';
    element.insertAdjacentHTML('beforeend', loadingHTML);

    return {
        hide: () => {
            const overlay = element.querySelector('.loading-overlay');
            if (overlay) {
                overlay.style.animation = 'fade-out 0.3s ease-out';
                setTimeout(() => overlay.remove(), 300);
            }
        }
    };
}

// Enhanced alert system with animations
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertContainer.style.zIndex = '9999';
    alertContainer.style.borderRadius = '15px';
    alertContainer.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
    alertContainer.style.backdropFilter = 'blur(10px)';
    alertContainer.style.animation = 'slide-in-bounce 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';

    // Add appropriate icon based on type
    let icon = '';
    switch(type) {
        case 'success': icon = '✨'; break;
        case 'warning': icon = '🪔'; break;
        case 'danger': icon = '🙏'; break;
        case 'info': icon = '🕉️'; break;
        default: icon = '✨';
    }

    alertContainer.innerHTML = `
        <span style="font-size: 1.2rem; margin-right: 0.5rem;">${icon}</span>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" style="filter: invert(1);"></button>
    `;

    document.body.appendChild(alertContainer);

    // Auto-remove with fade animation
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.style.animation = 'slide-out-bounce 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            setTimeout(() => {
                if (alertContainer.parentNode) {
                    alertContainer.parentNode.removeChild(alertContainer);
                }
            }, 400);
        }
    }, duration);
}

// ===== ADVANCED INITIALIZATION =====

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize core systems
    initializeTheme();
    initializeStoryGenerator();
    initializeVideoFeatures();
    initializeHoverEffects();

    // Add theme toggle button event listener
    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleTheme();
        });
    }

    // Handle example prompt clicks with animation
    document.querySelectorAll('.example-prompt').forEach(prompt => {
        prompt.addEventListener('click', function() {
            const promptInput = document.getElementById('storyPrompt');
            if (promptInput) {
                // Add click animation
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                    promptInput.value = this.dataset.prompt;
                    promptInput.focus();
                    promptInput.style.animation = 'pulse-glow 0.6s ease-out';
                }, 100);
            }
        });
    });

    // Enhanced smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                smoothScrollToElement(target);
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Theme toggle shortcut (Ctrl/Cmd + Shift + T)
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            toggleTheme();
        }

        // Focus search shortcut (Ctrl/Cmd + K)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const promptInput = document.getElementById('storyPrompt');
            if (promptInput) {
                promptInput.focus();
                promptInput.select();
            }
        }
    });

    // Add performance monitoring
    if ('performance' in window && 'mark' in window.performance) {
        performance.mark('app-initialized');
    }

    // Show welcome message
    setTimeout(() => {
        showAlert('🕉️ Welcome to Mythoscribe - Your Vedic Story Companion ✨', 'info', 3000);
    }, 1000);
});

// ===== GLOBAL FUNCTIONS =====

// Make functions globally available
window.toggleTheme = toggleTheme;
window.showAlert = showAlert;
window.smoothScrollToElement = smoothScrollToElement;

// Setup video controls
function setupVideoControls() {
    const playVideoBtn = document.getElementById('playVideoBtn');
    const video = document.getElementById('storyVideo');

    if (!playVideoBtn || !video) return;

    // Add loading state
    video.addEventListener('loadstart', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        playVideoBtn.disabled = true;
    });

    video.addEventListener('canplay', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Video';
        playVideoBtn.disabled = false;
    });

    playVideoBtn.addEventListener('click', function() {
        if (video.paused) {
            // Scroll to video section smoothly
            video.closest('.card').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // Add a small delay to ensure scrolling is complete
            setTimeout(() => {
                video.play();
                this.innerHTML = '<i class="fas fa-pause me-1"></i>Pause Video';
                this.classList.remove('btn-success');
                this.classList.add('btn-warning');
            }, 300);
        } else {
            video.pause();
            this.innerHTML = '<i class="fas fa-play me-1"></i>Play Video';
            this.classList.remove('btn-warning');
            this.classList.add('btn-success');
        }
    });

    video.addEventListener('play', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-pause me-1"></i>Pause Video';
        playVideoBtn.classList.remove('btn-success');
        playVideoBtn.classList.add('btn-warning');
    });

    video.addEventListener('pause', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Video';
        playVideoBtn.classList.remove('btn-warning');
        playVideoBtn.classList.add('btn-success');
    });

    video.addEventListener('ended', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Video';
        playVideoBtn.classList.remove('btn-warning');
        playVideoBtn.classList.add('btn-success');

        // Show completion message
        showAlert('Video completed! 🎉', 'success');
    });

    // Add video quality indicator
    video.addEventListener('loadedmetadata', function() {
        const quality = `${video.videoWidth}x${video.videoHeight}`;
        const qualityIndicator = document.createElement('div');
        qualityIndicator.className = 'video-quality';
        qualityIndicator.textContent = quality;
        video.parentElement.appendChild(qualityIndicator);
    });

    // Handle video errors
    video.addEventListener('error', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Video Error';
        playVideoBtn.disabled = true;
        showAlert('Video failed to load. Please try refreshing the page.', 'danger');
    });
}

// Enhanced image modal for videos
function openVideoModal(videoSrc) {
    let modal = document.getElementById('videoModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'videoModal';
        modal.tabIndex = -1;
        modal.innerHTML = `
            <div class="modal-dialog modal-xl modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Story Video</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center p-0">
                        <video id="modalVideo" controls class="w-100" style="max-height: 70vh;">
                            <source src="" type="video/mp4">
                            Your browser does not support the video element.
                        </video>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById('modalVideo').src = videoSrc;
    new bootstrap.Modal(modal).show();
}

// Add video thumbnail hover effects
function initializeVideoThumbnails() {
    const videoContainers = document.querySelectorAll('.video-container');

    videoContainers.forEach(container => {
        const video = container.querySelector('video');

        if (video) {
            // Add hover overlay
            const overlay = document.createElement('div');
            overlay.className = 'video-thumbnail-overlay';
            overlay.innerHTML = '<i class="fas fa-play-circle play-icon"></i>';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
                border-radius: 1rem;
                cursor: pointer;
            `;

            container.style.position = 'relative';
            container.appendChild(overlay);

            // Show overlay on hover
            container.addEventListener('mouseenter', () => {
                overlay.style.opacity = '1';
            });

            container.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
            });

            // Click to play/pause
            overlay.addEventListener('click', () => {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            });
        }
    });
}

// Video progress tracking
function initializeVideoProgress() {
    const videos = document.querySelectorAll('video');

    videos.forEach(video => {
        const progressBar = document.createElement('div');
        progressBar.className = 'video-progress';
        progressBar.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            height: 4px;
            background: var(--bs-primary);
            width: 0%;
            transition: width 0.1s ease;
            border-radius: 0 0 1rem 1rem;
        `;

        video.parentElement.style.position = 'relative';
        video.parentElement.appendChild(progressBar);

        video.addEventListener('timeupdate', () => {
            const progress = (video.currentTime / video.duration) * 100;
            progressBar.style.width = progress + '%';
        });

        video.addEventListener('ended', () => {
            progressBar.style.width = '100%';
        });
    });
}

// Initialize all video features
function initializeVideoFeatures() {
    setupVideoControls();
    initializeVideoThumbnails();
    initializeVideoProgress();
    initializeSacredAnimations();
    initializeDivineParticles();
    initializeQuantumParticles();

    // Add keyboard shortcuts for video
    document.addEventListener('keydown', function(e) {
        const video = document.getElementById('storyVideo');
        if (!video) return;

        switch(e.key) {
            case ' ':
                e.preventDefault();
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
                break;
            case 'ArrowLeft':
                e.preventDefault();
                video.currentTime = Math.max(0, video.currentTime - 10);
                break;
            case 'ArrowRight':
                e.preventDefault();
                video.currentTime = Math.min(video.duration, video.currentTime + 10);
                break;
            case 'm':
                e.preventDefault();
                video.muted = !video.muted;
                showAlert(video.muted ? '🔇 Audio muted' : '🔊 Audio unmuted', 'info');
                break;
            case 'f':
                e.preventDefault();
                if (video.requestFullscreen) {
                    video.requestFullscreen();
                }
                break;
        }
    });
}

// Initialize sacred animations
function initializeSacredAnimations() {
    // Add sacred geometry animations to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.5}s`;
    });

    // Add lotus bloom effect to images
    const images = document.querySelectorAll('.story-image');
    images.forEach((img, index) => {
        img.addEventListener('mouseenter', function() {
            this.style.animation = 'lotusBloom 0.6s ease-out';
        });

        img.addEventListener('mouseleave', function() {
            this.style.animation = '';
        });
    });

    // Add divine light effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 30px rgba(255, 215, 0, 0.5), 0 0 60px rgba(32, 201, 151, 0.3)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });
}

// Initialize divine particles
function initializeDivineParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.id = 'divine-particles';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    `;

    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'divine-particle';
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: radial-gradient(circle, #FFD700, #20C997);
            border-radius: 50%;
            opacity: 0;
            animation: divineParticleFloat ${3 + Math.random() * 4}s linear infinite;
            animation-delay: ${Math.random() * 5}s;
            left: ${Math.random() * 100}%;
            top: 100vh;
        `;
        particleContainer.appendChild(particle);
    }

    document.body.appendChild(particleContainer);
}

// Initialize quantum particles
function initializeQuantumParticles() {
    const quantumContainer = document.getElementById('quantumParticles');
    if (!quantumContainer) return;

    // Create 15 quantum particles with advanced animations
    for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        particle.className = 'quantum-particle';
        particle.style.cssText = `
            position: absolute;
            width: 6px;
            height: 6px;
            background: radial-gradient(circle, var(--accent-gold), var(--accent-teal), transparent);
            border-radius: 50%;
            opacity: 0;
            animation: quantum-particle ${4 + Math.random() * 4}s linear infinite;
            animation-delay: ${Math.random() * 8}s;
            left: ${Math.random() * 100}%;
            top: 100vh;
            box-shadow: 0 0 10px var(--accent-gold);
        `;
        quantumContainer.appendChild(particle);
    }

    // Add quantum field effect
    const quantumField = document.createElement('div');
    quantumField.className = 'quantum-field';
    quantumField.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center,
            rgba(255, 215, 0, 0.02) 0%,
            rgba(32, 201, 151, 0.02) 50%,
            transparent 100%);
        animation: quantum-field 12s ease-in-out infinite;
        pointer-events: none;
    `;
    quantumContainer.appendChild(quantumField);
}

// Add CSS for divine particles
const divineParticleStyle = document.createElement('style');
divineParticleStyle.textContent = `
    @keyframes divineParticleFloat {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }

    @keyframes lotusBloom {
        0% {
            transform: scale(1);
            filter: brightness(1);
        }
        50% {
            transform: scale(1.1);
            filter: brightness(1.2) saturate(1.3);
        }
        100% {
            transform: scale(1);
            filter: brightness(1);
        }
    }
`;
document.head.appendChild(divineParticleStyle);

// Enhanced video controls with sacred effects
function setupVideoControls() {
    const playVideoBtn = document.getElementById('playVideoBtn');
    const video = document.getElementById('storyVideo');

    if (!playVideoBtn || !video) return;

    // Add loading state with sacred animation
    video.addEventListener('loadstart', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i><span style="animation: sacredGlow 1s ease-in-out infinite;">Loading Divine Wisdom...</span>';
        playVideoBtn.disabled = true;

        // Add sacred loading effect
        playVideoBtn.style.animation = 'sacredGlow 2s ease-in-out infinite';
    });

    video.addEventListener('canplay', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Sacred Video';
        playVideoBtn.disabled = false;
        playVideoBtn.style.animation = '';
    });

    playVideoBtn.addEventListener('click', function() {
        if (video.paused) {
            // Scroll to video section smoothly with sacred effect
            video.closest('.card').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // Add divine light effect
            video.closest('.card').style.boxShadow = '0 0 50px rgba(255, 215, 0, 0.3)';

            // Add sacred delay for dramatic effect
            setTimeout(() => {
                video.play();
                this.innerHTML = '<i class="fas fa-pause me-1"></i>Pause Sacred Narration';
                this.classList.remove('btn-success');
                this.classList.add('btn-warning');

                // Add Om symbol during playback
                this.innerHTML = '<i class="fas fa-pause me-1"></i>ॐ Pause Sacred Narration';
            }, 500);
        } else {
            video.pause();
            this.innerHTML = '<i class="fas fa-play me-1"></i>Play Sacred Video';
            this.classList.remove('btn-warning');
            this.classList.add('btn-success');

            // Remove divine light effect
            video.closest('.card').style.boxShadow = '';
        }
    });

    video.addEventListener('play', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-pause me-1"></i>ॐ Pause Sacred Narration';
        playVideoBtn.classList.remove('btn-success');
        playVideoBtn.classList.add('btn-warning');

        // Add divine aura to video container
        video.closest('.video-container').style.boxShadow =
            '0 0 30px rgba(255, 215, 0, 0.4), 0 0 60px rgba(32, 201, 151, 0.2)';
    });

    video.addEventListener('pause', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play Sacred Video';
        playVideoBtn.classList.remove('btn-warning');
        playVideoBtn.classList.add('btn-success');

        // Remove divine aura
        video.closest('.video-container').style.boxShadow = '';
    });

    video.addEventListener('ended', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-play me-1"></i>ॐ Play Again';
        playVideoBtn.classList.remove('btn-warning');
        playVideoBtn.classList.add('btn-success');

        // Remove divine aura
        video.closest('.video-container').style.boxShadow = '';

        // Show completion message with sacred text
        showAlert('🎉 Sacred narration completed! ॐ May divine wisdom fill your heart.', 'success');
    });

    // Add video quality indicator with sacred styling
    video.addEventListener('loadedmetadata', function() {
        const quality = `${video.videoWidth}x${video.videoHeight}`;
        const qualityIndicator = document.createElement('div');
        qualityIndicator.className = 'video-quality';
        qualityIndicator.innerHTML = `📐 ${quality} <span style="animation: sacredGlow 2s ease-in-out infinite;">✨</span>`;
        video.parentElement.appendChild(qualityIndicator);
    });

    // Handle video errors with sacred message
    video.addEventListener('error', function() {
        playVideoBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Divine Error';
        playVideoBtn.disabled = true;
        showAlert('🙏 The divine video could not be loaded. Please refresh and try again.', 'warning');
    });
}

// Enhanced alert system with sacred styling
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertContainer.style.zIndex = '9999';
    alertContainer.style.borderRadius = '1rem';
    alertContainer.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';

    // Add sacred symbols based on type
    let sacredSymbol = '';
    switch(type) {
        case 'success': sacredSymbol = '✨'; break;
        case 'warning': sacredSymbol = '🪔'; break;
        case 'danger': sacredSymbol = '🙏'; break;
        default: sacredSymbol = '🕉️';
    }

    alertContainer.innerHTML = `
        <span style="animation: sacredGlow 2s ease-in-out infinite;">${sacredSymbol}</span>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertContainer);

    // Auto-remove after 5 seconds with sacred fade
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.style.animation = 'lotusBloom 0.5s ease-out reverse';
            setTimeout(() => {
                if (alertContainer.parentNode) {
                    alertContainer.parentNode.removeChild(alertContainer);
                }
            }, 500);
        }
    }, 5000);
}

// Export functions for global use
window.openImageModal = openImageModal;
window.openVideoModal = openVideoModal;
window.shareStory = shareStory;
window.copyStoryText = copyStoryText;
