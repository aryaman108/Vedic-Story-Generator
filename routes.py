from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app
from database import db
from models import Story
from story_service import create_story_from_prompt, delete_story_files, create_story_download_text
import os
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

        # Use the story service to handle the complete workflow
        story, error_message = create_story_from_prompt(prompt)

        if story:
            return jsonify({
                'success': True,
                'story': story.to_dict()
            })
        else:
            return jsonify({'error': error_message}), 500

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

    # Use the service to create the download file
    filepath, filename = create_story_download_text(story)

    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/delete_story/<int:story_id>', methods=['POST'])
def delete_story(story_id):
    """Delete a story"""
    try:
        story = Story.query.get_or_404(story_id)

        # Delete associated files using the service
        delete_story_files(story)

        # Delete the story record
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
