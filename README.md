# RT Agent Monitor Visualization App

A modern web application for visualizing RT Agent Monitor conversation transcripts and analysis results.

## Features

- Upload JSON transcript files
- View conversation analysis verdicts
- Interactive chat-like interface for conversation flow
- Modern dark theme UI
- Real-time metrics display

## Local Development

```bash
pip install -r requirements.txt
python visualizer_functional.py
```

The app will run on `http://localhost:8050`

## Vercel Deployment

This project is configured for Vercel deployment:

1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the `vercel.json` configuration
3. Deploy with one click

The app uses:
- `vercel.json` for deployment configuration
- `requirements.txt` for Python dependencies
- `api/index.py` as the serverless function entry point

## Usage

1. Visit the deployed app
2. Upload a JSON transcript file
3. View the analysis results and conversation flow
4. Explore the interactive chat interface

## File Structure

```
├── visualizer_functional.py   # Main Dash application
├── api/
│   └── index.py              # Vercel serverless function
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
``` 