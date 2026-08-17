import io
import base64
import os
from flask import Flask, render_template_string, request, send_file
from PIL import Image

app = Flask(__name__)

# --- ADVANCED STEGANOGRAPHY LOGIC ---

def message_to_bin(message):
    # UTF-8 encoding ensures Hindi/Emojis work perfectly
    data = message.encode('utf-8')
    return ''.join(format(byte, '08b') for byte in data)

def encode_logic(input_image_stream, secret_data):
    try:
        img = Image.open(input_image_stream).convert("RGB")
        # Unique Marker to identify end of message: #####
        binary_secret_data = message_to_bin(secret_data) + '0010001100100011001000110010001100100011' 
        
        data_index = 0
        pixels = img.load()
        width, height = img.size

        if len(binary_secret_data) > width * height * 3:
            return None # Message too large

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                channels = list((r, g, b))
                for i in range(3):
                    if data_index < len(binary_secret_data):
                        channels[i] = (channels[i] & ~1) | int(binary_secret_data[data_index])
                        data_index += 1
                pixels[x, y] = tuple(channels)
                if data_index >= len(binary_secret_data): break
            if data_index >= len(binary_secret_data): break
        
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        return output_buffer
    except Exception as e:
        print(f"Encode Error: {e}")
        return None

def decode_logic(input_image_stream):
    try:
        img = Image.open(input_image_stream).convert("RGB")
        binary_data = ""
        pixels = img.load()
        width, height = img.size

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                binary_data += str(r & 1) + str(g & 1) + str(b & 1)

        all_bytes = []
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            all_bytes.append(int(byte, 2))
            # Check for ##### marker
            if len(all_bytes) >= 5 and all_bytes[-5:] == [35, 35, 35, 35, 35]:
                return bytes(all_bytes[:-5]).decode('utf-8')
        return "No hidden message found."
    except Exception as e:
        return f"Decoding Error: {str(e)}"

def image_to_base64(image_bytes_io):
    encoded_string = base64.b64encode(image_bytes_io.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

# --- MODERN CYBER-THEME HTML TEMPLATE ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StegoVault | Ultra Secure Steganography</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --accent: #00f2fe;
            --secondary: #7000ff;
            --dark-bg: #030712;
            --card-bg: rgba(15, 23, 42, 0.7);
        }

        body {
            background-color: var(--dark-bg);
            background-image: 
                radial-gradient(at 0% 0%, rgba(112, 0, 255, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(0, 242, 254, 0.15) 0px, transparent 50%);
            color: #e2e8f0;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .navbar {
            background: rgba(3, 7, 18, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 35px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            border-color: var(--accent);
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0, 242, 254, 0.2);
        }

        .btn-cyber {
            background: linear-gradient(135deg, var(--secondary), var(--accent));
            border: none;
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 14px;
            border-radius: 12px;
            transition: 0.3s;
        }

        .btn-cyber:hover {
            filter: brightness(1.2);
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
            transform: scale(1.02);
        }

        .form-control {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white !important;
            border-radius: 12px;
            padding: 12px;
        }

        .form-control:focus {
            background: rgba(0, 0, 0, 0.4);
            border-color: var(--accent);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
        }

        .img-preview {
            max-width: 100%;
            max-height: 250px;
            border-radius: 15px;
            border: 2px solid rgba(0, 242, 254, 0.3);
            margin: 15px 0;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

        .filename-badge {
            background: rgba(0, 242, 254, 0.1);
            color: var(--accent);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            border: 1px solid rgba(0, 242, 254, 0.3);
        }

        .result-box {
            background: rgba(0, 0, 0, 0.4);
            border-left: 4px solid var(--accent);
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
            font-family: 'Courier New', monospace;
            color: #00f2fe;
        }

        .hero-title {
            background: linear-gradient(to right, #fff, #00f2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
</head>
<body>
    <nav class="navbar py-3">
        <div class="container">
            <a class="navbar-brand fw-bold text-white animate__animated animate__fadeInLeft" href="/">
                <i class="fas fa-shield-halved me-2 text-info"></i>🔐STEGO SHIELD
            </a>
        </div>
    </nav>

    <div class="container py-5">
        <div class="text-center mb-5 animate__animated animate__fadeIn">
            <h2 class="display-3 hero-title">🕵️Hide Secret Data</h2>
            <p class="lead text-secondary">Hide sensitive information inside images with LSB encryption.</p>
        </div>

        <div class="row g-5">
            <!-- ENCODE SIDE -->
            <div class="col-lg-6 animate__animated animate__fadeInLeft">
                <div class="glass-card">
                    <h3 class="mb-4"><i class="fas fa-lock me-2"></i>Encode Data</h3>
                    <form action="/encode" method="post" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label class="form-label text-secondary small">SELECT IMAGE (PNG/JPG)</label>
                            <input type="file" name="image" class="form-control" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label text-secondary small">SECRET MESSAGE</label>
                            <textarea name="message" class="form-control" rows="3" placeholder="Enter your encrypted text here..." required></textarea>
                        </div>
                        <button type="submit" class="btn btn-cyber w-100">ENCRYPT</button>
                    </form>

                    {% if encoded_img_b64 %}
                    <div class="mt-4 text-center animate__animated animate__zoomIn">
                        <div class="mb-2"><span class="filename-badge"><i class="fas fa-file-image me-2"></i>{{ orig_filename }}</span></div>
                        <img src="{{ encoded_img_b64 }}" class="img-preview">
                        <a href="{{ encoded_img_b64 }}" download="encoded_{{ orig_filename }}" class="btn btn-outline-info w-100 mt-2">
                            <i class="fas fa-download me-2"></i>Download Secure Image
                        </a>
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- DECODE SIDE -->
            <div class="col-lg-6 animate__animated animate__fadeInRight">
                <div class="glass-card">
                    <h3 class="mb-4"><i class="fas fa-unlock-alt me-2"></i>Decode Data</h3>
                    <form action="/decode" method="post" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label class="form-label text-secondary small">UPLOAD ENCODED IMAGE</label>
                            <input type="file" name="image" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-cyber w-100" style="background: linear-gradient(135deg, #f50057, #7000ff);">DECRYPT</button>
                    </form>

                    {% if decoded_msg %}
                    <div class="mt-4 animate__animated animate__zoomIn">
                        <div class="text-center mb-2"><span class="filename-badge"><i class="fas fa-file-image me-2"></i>{{ decode_filename }}</span></div>
                        <img src="{{ decoded_img_b64 }}" class="img-preview">
                        <div class="result-box">
                            <small class="text-secondary d-block mb-2">HIDDEN MESSAGE FOUND:</small>
                            <strong>{{ decoded_msg }}</strong>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <footer class="text-center py-5 text-secondary small">
    <p>&copy; 2026 Stego Shield &bull; Made with 🤍 by kk's</p>
    </footer>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/encode', methods=['POST'])
def encode():
    file = request.files.get('image')
    message = request.form.get('message', '')
    if not file: return "No file", 400
    
    filename = file.filename
    output_buffer = encode_logic(file, message)
    
    if output_buffer:
        b64_img = image_to_base64(output_buffer)
        return render_template_string(HTML_TEMPLATE, 
                                      encoded_img_b64=b64_img, 
                                      orig_filename=filename)
    return "Error: Image too small or invalid.", 400

@app.route('/decode', methods=['POST'])
def decode():
    file = request.files.get('image')
    if not file: return "No file", 400
    
    filename = file.filename
    # Read to memory for double usage
    file_bytes = io.BytesIO(file.read())
    
    # Process Decoding
    message = decode_logic(file_bytes)
    
    # Preview Image
    file_bytes.seek(0)
    b64_img = image_to_base64(file_bytes)
    
    return render_template_string(HTML_TEMPLATE, 
                                  decoded_msg=message, 
                                  decoded_img_b64=b64_img, 
                                  decode_filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
