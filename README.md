# Online Quiz System with Auto Evaluation

A modern, full-stack online quiz system built with Python (Flask) and Vanilla HTML/CSS/JS.

## Features
- **Quiz Creation**: dynamic MCQ and Short Answer questions.
- **Auto Evaluation**: Instant scoring and feedback.
- **Timer**: Real-time countdown for each quiz session.
- **Leaderboard**: Rank tracking for participants.
- **Interactive UI**: Responsive design with glassmorphism and modern aesthetics.

## Installation
1. Clone the repository:
   ```bash
   git clone <REPO_URL>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

## Configuration
- To use Firebase Firestore, place your `serviceAccountKey.json` in the root directory.
- If no credentials are provided, the system will use a local mock database for simulation.

## License
MIT
