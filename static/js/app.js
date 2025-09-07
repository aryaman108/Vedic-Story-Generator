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
            showAlert(data.error || 'Failed to generate story', 'danger');
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeStoryGenerator();
    
    // Handle example prompt clicks
    document.querySelectorAll('.example-prompt').forEach(prompt => {
        prompt.addEventListener('click', function() {
            const promptInput = document.getElementById('storyPrompt');
            if (promptInput) {
                promptInput.value = this.dataset.prompt;
                promptInput.focus();
            }
        });
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Export functions for global use
window.openImageModal = openImageModal;
window.shareStory = shareStory;
window.copyStoryText = copyStoryText;
