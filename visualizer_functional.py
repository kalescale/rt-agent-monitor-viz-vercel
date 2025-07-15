import base64
import io
import json
from datetime import datetime
import re

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# --- Modern Theme & Styles ---
modern_theme = {
    'background': '#0f172a',  # Dark blue-gray
    'surface': '#1e293b',     # Lighter blue-gray
    'primary': '#3b82f6',     # Blue
    'secondary': '#64748b',   # Gray
    'accent': '#06b6d4',      # Cyan
    'success': '#10b981',     # Green
    'warning': '#f59e0b',     # Amber
    'danger': '#ef4444',      # Red
    'text': '#f8fafc',        # Light gray
    'text_secondary': '#94a3b8',
    'border': '#334155'
}

styles = {
    'body': {
        'backgroundColor': modern_theme['background'],
        'color': modern_theme['text'],
        'fontFamily': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'margin': 0,
        'padding': 0,
        'minHeight': '100vh'
    },
    'container': {
        'maxWidth': '1400px',
        'margin': 'auto',
        'padding': '0'  # Removed 20px padding to eliminate white trim around edges
    },
    'header': {
        'textAlign': 'center',
        'marginBottom': '40px',
        'margin': '0 20px 40px 20px',  # Added horizontal margins
        'padding': '30px 20px',  # Added horizontal padding to prevent edge sticking
        'background': f'linear-gradient(135deg, {modern_theme["surface"]}, {modern_theme["background"]})',
        'borderRadius': '16px',
        'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    },
    'upload': {
        'width': '100%',
        'height': '120px',
        'borderWidth': '2px',
        'borderStyle': 'dashed',
        'borderRadius': '12px',
        'textAlign': 'center',
        'margin': '0 20px 30px 20px',  # Added horizontal margins
        'cursor': 'pointer',
        'borderColor': modern_theme['primary'],
        'backgroundColor': modern_theme['surface'],
        'color': modern_theme['text'],
        'transition': 'all 0.3s ease',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'flexDirection': 'column'
    },
    'upload_hover': {
        'borderColor': modern_theme['accent'],
        'backgroundColor': f'{modern_theme["surface"]}dd',
        'transform': 'translateY(-2px)',
        'boxShadow': '0 8px 25px -5px rgba(0, 0, 0, 0.2)'
    },
    'chat_container': {
        'backgroundColor': modern_theme['surface'],
        'borderRadius': '16px',
        'padding': '24px',
        'margin': '20px 20px 0 20px',  # Added horizontal margins and top margin
        'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'border': f'1px solid {modern_theme["border"]}'
    },
    'message': {
        'marginBottom': '20px',
        'padding': '16px 20px',
        'borderRadius': '12px',
        'maxWidth': '85%',
        'wordWrap': 'break-word',
        'lineHeight': '1.6',
        'position': 'relative'
    },
    'message_user': {
        'backgroundColor': 'transparent',
        'color': modern_theme['text'],
        'marginLeft': 'auto',
        'borderBottomRightRadius': '4px',
        'border': f'2px solid {modern_theme["primary"]}'
    },
    'message_assistant': {
        'backgroundColor': 'transparent',
        'color': modern_theme['text'],
        'border': f'2px solid {modern_theme["border"]}',
        'marginRight': 'auto',
        'borderBottomLeftRadius': '4px'
    },
    'message_tool': {
        'backgroundColor': 'transparent',
        'border': 'none',
        'color': modern_theme['text'],
        'marginRight': 'auto',
        'padding': '0', # Remove padding from container
        'maxWidth': '100%', # Allow tool output to take full width if needed
    },
    'message_header': {
        'display': 'flex',
        'alignItems': 'center',
        'marginBottom': '8px',
        'fontSize': '14px',
        'fontWeight': '600'
    },
    'message_content': {
        'whiteSpace': 'pre-wrap',
        'fontSize': '15px'
    },
    'verdict_card': {
        'backgroundColor': modern_theme['surface'],
        'borderRadius': '12px',
        'padding': '20px',
        'marginBottom': '20px',
        'border': f'1px solid {modern_theme["border"]}',
        'textAlign': 'center'
    },
    'metrics_grid': {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
        'gap': '16px',
        'marginBottom': '30px'
    },
    'metric_card': {
        'backgroundColor': modern_theme['surface'],
        'borderRadius': '12px',
        'padding': '20px',
        'textAlign': 'center',
        'border': f'1px solid {modern_theme["border"]}',
        'transition': 'transform 0.2s ease'
    },
    'metric_value': {
        'fontSize': '32px',
        'fontWeight': '700',
        'marginBottom': '8px'
    },
    'metric_label': {
        'fontSize': '14px',
        'color': modern_theme['text_secondary'],
        'textTransform': 'uppercase',
        'letterSpacing': '0.5px'
    }
}

# --- Helper Functions ---
def get_verdict_color(verdict):
    """Get color based on verdict value"""
    try:
        verdict_num = float(verdict)
        if verdict_num < 1.66:
            return modern_theme['success']
        elif verdict_num < 3.33:
            return modern_theme['warning']
        else:
            return modern_theme['danger']
    except:
        return modern_theme['secondary']

def get_verdict_text(verdict):
    """Get text based on verdict value"""
    return verdict

# --- MODIFIED FUNCTION ---
def create_tool_cards(raw_text):
    """
    Displays the raw tool output text in a preformatted block,
    preserving newlines and whitespace.
    """
    # Style for the raw text block, smaller and more condensed with scrolling
    pre_style = {
        'backgroundColor': modern_theme['background'],
        'color': modern_theme['text'],
        'padding': '8px',  # Reduced padding
        'borderRadius': '6px',  # Smaller border radius
        'border': f'1px solid {modern_theme["border"]}',
        'fontFamily': 'monospace',
        'fontSize': '12px',  # Smaller font size
        'lineHeight': '1.2',  # Reduced line height for condensed spacing
        'overflowX': 'auto',
        'overflowY': 'auto',  # Enable vertical scrolling
        'maxHeight': '480px',  # Roughly 40 lines (12px * 1.2 * 40 = 576px, reduced for compactness)
        'whiteSpace': 'pre-wrap',
        'wordWrap': 'break-word',
        'margin': 0
    }
    # Use html.Pre to display the raw text with formatting preserved
    return html.Pre(raw_text.strip(), style=pre_style)

def create_chat_interface(conversation):
    """Create a chat-like interface for the conversation"""
    if not conversation:
        return html.Div("No conversation data available")
    
    messages = []
    
    for i, turn in enumerate(conversation):
        role = turn.get('role', 'unknown')
        content = turn.get('content', '')
        tool_calls = turn.get('tool_calls')
        
        # Determine message styling
        if role == 'user':
            message_style = {**styles['message'], **styles['message_user']}
            icon = "👤"
            header_text = "User"
        elif role == 'assistant':
            message_style = {**styles['message'], **styles['message_assistant']}
            icon = "🤖"
            header_text = "Assistant"
        elif role == 'tool':
            # For tool role, the main style is on the header and the content block itself.
            message_style = {**styles['message'], **styles['message_tool']}
            icon = "🔧"
            header_text = "Tool Output"
        else:
            message_style = {**styles['message'], **styles['message_assistant']}
            icon = "❓"
            header_text = role.title()
        
        # Create message header
        # For 'tool' role, the header will sit above the raw text block
        header = html.Div([
            html.Span(icon, style={'marginRight': '8px'}),
            html.Span(header_text),
            html.Span(f"Turn {i+1}", style={
                'marginLeft': 'auto',
                'color': modern_theme['text_secondary'],
                'fontSize': '12px'
            })
        ], style=styles['message_header'])

        # --- UNIFIED CONTENT HANDLING ---
        content_div = None
        if role == 'tool':
            # Use the new raw text rendering function for tool outputs
            content_div = create_tool_cards(content)
        elif role == 'assistant':
            # For assistant messages, only show content within model_thinking tags
            thinking_match = re.search(r'<model_thinking>(.*?)</model_thinking>', content, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                content_div = html.Div(thinking_content, style=styles['message_content'])
            else:
                # If no model_thinking tags found, show the full content
                content_div = html.Div(content, style=styles['message_content'])
        else:
            # Default for user messages
            content_div = html.Div(content, style=styles['message_content'])
        
        # Combine elements
        message_elements = [header, content_div]
        
        # For assistant messages, add tool calls as code blocks after the content
        if role == 'assistant' and tool_calls:
            tool_code_block = html.Pre(tool_calls, style={
                'backgroundColor': modern_theme['background'],
                'color': modern_theme['accent'],
                'padding': '8px',  # Reduced padding
                'borderRadius': '6px',  # Smaller border radius
                'border': f'1px solid {modern_theme["border"]}',
                'fontFamily': 'monospace',
                'fontSize': '12px',  # Smaller font size
                'lineHeight': '1.2',  # Reduced line height for condensed spacing
                'overflowX': 'auto',
                'overflowY': 'auto',  # Enable vertical scrolling
                'maxHeight': '480px',  # Roughly 40 lines, same as tool output
                'margin': '8px 0 0 0',  # Reduced margin
                'whiteSpace': 'pre-wrap',
                'wordWrap': 'break-word'
            })
            message_elements.append(tool_code_block)
        
        # For 'tool' role, message_style is now on a container Div
        if role == 'tool':
            messages.append(html.Div(message_elements, style=message_style))
        else:
            messages.append(html.Div(message_elements, style=message_style))
    
    return html.Div(messages)

# --- Dash App Initialization ---
app = dash.Dash(__name__)
app.title = "RT Monitor - Conversation Analysis"

# Expose the Flask server for Vercel
server = app.server

# --- App Layout ---
app.layout = html.Div(style=styles['body'], children=[
    html.Div(style=styles['container'], children=[
        # Header
        html.Div(style=styles['header'], children=[
            html.H1("🤖 RT Monitor Dashboard", style={
                'margin': '0 0 10px 0',
                'fontSize': '2.5rem',
                'fontWeight': '700',
                'background': f'linear-gradient(135deg, {modern_theme["primary"]}, {modern_theme["accent"]})',
                'backgroundClip': 'text',
                'WebkitBackgroundClip': 'text',
                'WebkitTextFillColor': 'transparent'
            }),
            html.P("Upload JSON transcript files to analyze conversation trajectories and monitor responses", 
                   style={'color': modern_theme['text_secondary'], 'fontSize': '1.1rem', 'margin': 0})
        ]),
        
        # File Upload
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.Div("📁", style={'fontSize': '2rem', 'marginBottom': '10px'}),
                html.Div("Drag and Drop or Click to Upload", style={'fontSize': '1.2rem', 'fontWeight': '600'}),
                html.Div("JSON transcript files", style={'fontSize': '0.9rem', 'color': modern_theme['text_secondary']})
            ]),
            style=styles['upload'],
            multiple=False
        ),
        
        # Main Content Area
        html.Div(id='output-data-upload')
    ])
])

# --- Callback to Handle File Upload and Display ---
@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return html.Div([
            html.Div(style=styles['chat_container'], children=[
                html.Div("📊", style={'fontSize': '3rem', 'textAlign': 'center', 'marginBottom': '20px'}),
                html.H3("Welcome to RT Monitor Dashboard", style={'textAlign': 'center', 'marginBottom': '10px'}),
                html.P("Upload a JSON transcript file to begin analysis. The file should contain conversation data with tool calls and monitor responses.", 
                       style={'textAlign': 'center', 'color': modern_theme['text_secondary']})
            ])
        ])
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'json' in filename:
            data = json.loads(decoded.decode('utf-8'))
            
            # Extract data
            verdict = data.get('verdict', 'Unknown')
            trajectory_length = data.get('trajectory_length', 0)
            conversation = data.get('conversation_for_visualizer', [])
            
            return html.Div([
                # Verdict Card
                html.Div(style=styles['verdict_card'], children=[
                    html.H3("🔍 Analysis Verdict", style={'margin': '0 0 15px 0', 'fontSize': '1.5rem'}),
                    html.Div([
                        html.Span(get_verdict_text(verdict), style={
                            'backgroundColor': get_verdict_color(verdict),
                            'color': 'white',
                            'padding': '12px 24px',
                            'borderRadius': '25px',
                            'fontWeight': '700',
                            'fontSize': '1.2rem',
                            'display': 'inline-block'
                        })
                    ])
                ]),
                
                # Metrics Grid
                html.Div(style=styles['metrics_grid'], children=[
                    html.Div(style=styles['metric_card'], children=[
                        html.Div(trajectory_length, style=styles['metric_value']),
                        html.Div("Trajectory Length", style=styles['metric_label'])
                    ]),
                    html.Div(style=styles['metric_card'], children=[
                        html.Div(sum(len(t.get('content', '').split()) for t in conversation), style=styles['metric_value']),
                        html.Div("Word Count", style=styles['metric_label'])
                    ]),
                    html.Div(style=styles['metric_card'], children=[
                        html.Div(len([t for t in conversation if t.get('tool_calls')]), style=styles['metric_value']),
                        html.Div("Tool Calls", style=styles['metric_label'])
                    ]),
                    html.Div(style=styles['metric_card'], children=[
                        html.Div(len([t for t in conversation if t.get('role') == 'user']), style=styles['metric_value']),
                        html.Div("User Messages", style=styles['metric_label'])
                    ])
                ]),
                
                # Conversation Chat Interface
                html.Div(style=styles['chat_container'], children=[
                    html.H3("💭 Conversation Flow", style={'margin': '0 0 20px 0', 'fontSize': '1.3rem'}),
                    create_chat_interface(conversation)
                ])
            ])
        else:
            return html.Div([
                html.Div(style=styles['chat_container'], children=[
                    html.H3("❌ Invalid File Type", style={'color': modern_theme['danger'], 'textAlign': 'center'}),
                    html.P(f"Please upload a JSON file. '{filename}' is not supported.", 
                           style={'textAlign': 'center', 'color': modern_theme['text_secondary']})
                ])
            ])
    except Exception as e:
        return html.Div([
            html.Div(style=styles['chat_container'], children=[
                html.H3("❌ Error Processing File", style={'color': modern_theme['danger'], 'textAlign': 'center'}),
                html.P(f"An error occurred while processing '{filename}':", 
                       style={'textAlign': 'center', 'color': modern_theme['text_secondary']}),
                html.Pre(str(e), style={
                    'backgroundColor': modern_theme['background'],
                    'padding': '16px',
                    'borderRadius': '8px',
                    'overflowX': 'auto',
                    'fontSize': '14px',
                    'color': modern_theme['danger']
                })
            ])
        ])

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)