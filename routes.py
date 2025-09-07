from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app, db
from models import Story
from story_generator import generate_vedic_story
from image_generator import generate_story_images
from audio_generator import generate_audio_narration
import os
import json
import logging

@app.route('/')
def index():
    """Main page for story generation"""
    return render_template('index.html')

@app.route('/generate_story', methods=['POST'])
def generate_story():
    """Generate a new Vedic mythology story"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Please provide a prompt'}), 400
        
        # Generate the story
        story_data = generate_vedic_story(prompt)
        if not story_data:
            return jsonify({'error': 'Failed to generate story'}), 500
        
        # Create new story record
        story = Story()
        story.title = story_data['title']
        story.prompt = prompt
        story.content = story_data['content']
        
        db.session.add(story)
        db.session.commit()
        
        # Generate images for the story
        try:
            image_paths = generate_story_images(story_data, story.id)
            story.set_images(image_paths)
        except Exception as e:
            logging.error(f"Image generation failed: {e}")
            story.set_images([])
        
        # Generate audio narration
        try:
            audio_path = generate_audio_narration(story_data['content'], story.id)
            story.audio_path = audio_path
        except Exception as e:
            logging.error(f"Audio generation failed: {e}")
            story.audio_path = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'story': story.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Story generation error: {e}")
        return jsonify({'error': 'An error occurred while generating the story'}), 500

@app.route('/story/<int:story_id>')
def view_story(story_id):
    """View a specific story"""
    story = Story.query.get_or_404(story_id)
    return render_template('story.html', story=story)

@app.route('/library')
def library():
    """View all generated stories"""
    stories = Story.query.order_by(Story.created_at.desc()).all()
    return render_template('library.html', stories=stories)

@app.route('/api/stories')
def api_stories():
    """API endpoint to get all stories"""
    stories = Story.query.order_by(Story.created_at.desc()).all()
    return jsonify([story.to_dict() for story in stories])

@app.route('/api/story/<int:story_id>')
def api_story(story_id):
    """API endpoint to get a specific story"""
    story = Story.query.get_or_404(story_id)
    return jsonify(story.to_dict())

@app.route('/download_story/<int:story_id>')
def download_story(story_id):
    """Download story as text file"""
    story = Story.query.get_or_404(story_id)
    
    # Create a text file with the story content
    filename = f"story_{story_id}_{story.title.replace(' ', '_')}.txt"
    filepath = os.path.join('static', 'stories', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Title: {story.title}\n")
        f.write(f"Prompt: {story.prompt}\n")
        f.write(f"Created: {story.created_at}\n")
        f.write("\n" + "="*50 + "\n\n")
        f.write(story.content)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/delete_story/<int:story_id>', methods=['POST'])
def delete_story(story_id):
    """Delete a story"""
    try:
        story = Story.query.get_or_404(story_id)
        
        # Delete associated files
        if story.audio_path and os.path.exists(story.audio_path):
            os.remove(story.audio_path)
        
        for image_path in story.get_images():
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(story)
        db.session.commit()
        
        flash('Story deleted successfully', 'success')
        return redirect(url_for('library'))
        
    except Exception as e:
        logging.error(f"Delete story error: {e}")
        flash('Error deleting story', 'error')
        return redirect(url_for('library'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500
